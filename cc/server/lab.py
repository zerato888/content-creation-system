# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Content Lab storage (pure functions, no HTTP).

Items (references and pieces): <root>/lab/<brand>/{activos,archivados}/<id>.json;
the folder IS the state. Media: <root>/lab/<brand>/media/<id>/. Productions,
templates and orders (advanced module) are versioned JSON under <root>/lab/.
`brand` is always a configured brand id, checked by the caller. There is no
default brand. Every id is a single safe path component.

Faithful translation (personal brand): `translation_packet` hands an agent the
original transcript with a PURE FIDELITY contract; `apply_translation` writes
back only whitelisted text fields. Nothing here writes creative text itself.
"""
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import threading
import sys
import uuid
from pathlib import Path

if __package__ in (None, ""):  # `python .kit/launch.py lab ...` / `python .kit/cc/server/lab.py ...`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

TIPOS = ("reel", "carrusel", "youtube")
_LOCK = threading.Lock()  # ponytail: one global lock; single-user local tool
CONTENT_STATES = ("draft", "content_review", "ready_to_produce")
PRODUCTION_STATES = ("not_started", "in_production", "delivery_review", "finished")
PUBLICATION_STATES = ("not_required", "ready_to_publish", "scheduled", "published", "closed")
FORMATS = ("video", "carousel")
FAMILIES = ("camera", "editorial")
INPUT_MODES = ("script", "freestyle", "selection", "single")
MEDIA_NAMES = re.compile(r"^(cover|ref|final|poster)\.(jpg|jpeg|png|webp|mp4)$")
PLAYLIST_EXT = {".m3u8", ".m3u", ".ffconcat", ".txt", ".concat", ".sdp"}
MAX_ITEM_BYTES = 2 * 1024 * 1024

TRANSLATION_CONTRACT = (
    "TRADUCCIÓN FIEL PURA: traducir transcript_original al idioma de destino de forma natural, "
    "conservando exactamente el narrador, el contenido, el orden, los ejemplos, los nombres, las cifras "
    "y los recursos retóricos del original. Sin giro, sin adaptación, sin opinión propia, sin CTA nuevo, "
    "sin agregar ni quitar ideas y sin inyectar la voz, la marca ni la historia de nadie. No generar "
    "Talking Points. Es una referencia privada: la persona la edita antes de grabar o publicar.")
TRANSLATION_FIELDS = ("hook", "full_script", "headline", "titulo")
_SLIDE_RE = re.compile(r"^pieza\.slides\[(\d+)\]$")


class RevisionConflict(ValueError):
    pass


def slugify(text, maxlen=60):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:maxlen] or "pieza"


def safe_id(value, label="id"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,150}", value) or ".." in value:
        raise ValueError(f"{label} inválido")
    return value


def default_pieza(tipo):
    if tipo == "carrusel":
        return {"headline": "", "slides": []}
    base = {"hook": "", "full_script": "", "full_script_actualizado": None,
            "talking_points": "", "talking_points_actualizado": None}
    return {"titulo": "", "capitulos": [], **base} if tipo == "youtube" else base


def _brand_base(root, brand):
    return os.path.join(root, "lab", safe_id(brand, "brand"))


def _item_dirs(root, brand):
    base = _brand_base(root, brand)
    return os.path.join(base, "activos"), os.path.join(base, "archivados")


def _atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ items
def get_item(root, item_id, brand):
    safe_id(item_id)
    for d in _item_dirs(root, brand):
        path = os.path.join(d, f"{item_id}.json")
        if os.path.isfile(path):
            return _read_json(path)
    raise FileNotFoundError(item_id)


def media_path(root, brand, item_id, name):
    """A media file of an item, confined to <brand>/media/<id>/."""
    safe_id(item_id)
    if not isinstance(name, str) or not MEDIA_NAMES.fullmatch(name):
        raise ValueError("archivo inválido")
    media_root = os.path.realpath(os.path.join(_brand_base(root, brand), "media"))
    resolved = os.path.realpath(os.path.join(media_root, item_id, name))
    if os.path.commonpath((media_root, resolved)) != media_root:
        raise ValueError("ruta fuera de media")
    if not os.path.isfile(resolved):
        raise FileNotFoundError(name)
    return resolved


def final_media_path(root, item_id, brand):
    item = get_item(root, item_id, brand)
    relative = (item.get("final_video") or {}).get("media_local")
    if not relative:
        raise FileNotFoundError(f"video final no registrado: {item_id}")
    parts = Path(relative).parts
    if len(parts) != 3 or parts[0] != "media" or parts[1] != item_id:
        raise ValueError("ruta de video final fuera de media")
    return media_path(root, brand, item_id, parts[2])


def list_items(root, brand):
    items = []
    for d, archived in zip(_item_dirs(root, brand), (False, True)):
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            try:
                item = _read_json(os.path.join(d, fn))
            except (OSError, ValueError):
                continue  # a corrupt file must not hide the whole grid
            item["archivada"] = archived
            if item.get("final_video"):
                try:
                    item["final_video"]["available"] = bool(final_media_path(root, item["id"], brand))
                except (OSError, ValueError, KeyError):
                    item["final_video"]["available"] = False
            items.append(item)
    items.sort(key=lambda i: i.get("creado") or "", reverse=True)
    items.sort(key=lambda i: (i["archivada"], not i.get("pineada", False)))
    return items


def _new_item(item_id, tipo, now):
    return {
        "id": item_id, "tipo": tipo, "creado": now, "actualizado": now, "pineada": False,
        "origen": {"url": "", "plataforma": "", "handle": "", "autor": "", "cover_local": "", "media_local": "",
                   "metricas": {"likes": None, "comentarios": None, "duracion_s": None, "fecha": ""}},
        "tema": "", "resumen_original": "", "angulo": "", "hechos": [],
        "estructura": {"format_type": "", "sections": []},
        "hook_original": {"ejemplo": "", "formula": ""},
        "transcript_original": "", "visual_layout": "",
        "redaccion": {"modo": "", "idioma_destino": "", "fuente": ""},
        "pieza": default_pieza(tipo),
        "hooks_grabacion": {"generado_en": None, "opciones": []},
        "notas": "",
    }


def save_item(root, body, brand):
    if len(json.dumps(body, ensure_ascii=False)) > MAX_ITEM_BYTES:
        raise ValueError("item demasiado grande")
    activos, archivados = _item_dirs(root, brand)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    with _LOCK:
        item_id, path, existing = body.get("id"), None, None
        if item_id:
            safe_id(item_id)
            for d in (activos, archivados):
                p = os.path.join(d, f"{item_id}.json")
                if os.path.isfile(p):
                    path, existing = p, _read_json(p)
                    break
            if existing is None:
                raise FileNotFoundError(item_id)
        else:
            tipo = body.get("tipo")
            if tipo not in TIPOS:
                raise ValueError("tipo inválido o faltante")
            base_id = item_id = f"{dt.date.today():%Y-%m-%d}-{slugify(body.get('tema'))}"
            n = 2
            while any(os.path.isfile(os.path.join(d, f"{item_id}.json")) for d in (activos, archivados)):
                item_id, n = f"{base_id}-{n}", n + 1
            existing, path = _new_item(item_id, tipo, now), os.path.join(activos, f"{item_id}.json")
        for k, v in body.items():
            if k in ("id", "tipo", "archivada", "final_video"):  # final_video is written by the pipeline only
                continue
            if isinstance(v, dict) and isinstance(existing.get(k), dict):
                existing[k].update(v)
            else:
                existing[k] = v
        existing.update({"id": item_id, "actualizado": now})
        _atomic_json(path, existing)
        return existing


def archive_item(root, item_id, archive, brand):
    safe_id(item_id)
    activos, archivados = _item_dirs(root, brand)
    src_dir, dst_dir = (activos, archivados) if archive else (archivados, activos)
    src = os.path.join(src_dir, f"{item_id}.json")
    with _LOCK:
        if not os.path.isfile(src):
            raise FileNotFoundError(item_id)
        os.makedirs(dst_dir, exist_ok=True)
        os.replace(src, os.path.join(dst_dir, f"{item_id}.json"))
    return {"id": item_id, "archivada": bool(archive)}


def delete_item(root, item_id, brand):
    safe_id(item_id)
    with _LOCK:
        deleted = False
        for d in _item_dirs(root, brand):
            src = os.path.join(d, f"{item_id}.json")
            if os.path.isfile(src):
                os.remove(src)
                deleted = True
        if not deleted:
            raise FileNotFoundError(item_id)
        media_dir = os.path.join(_brand_base(root, brand), "media", item_id)
        if os.path.isdir(media_dir) and not os.path.islink(media_dir):
            shutil.rmtree(media_dir, ignore_errors=True)
    return {"id": item_id, "deleted": True}


# ------------------------------------------------------------------ faithful translation
def translation_packet(root, item_id, brand, target_language="es"):
    """What an agent needs to write a faithful translation, and nothing more."""
    item = get_item(root, item_id, brand)
    if not (item.get("transcript_original") or "").strip():
        raise ValueError("el item no tiene transcript_original")
    return {"id": item["id"], "brand": brand, "tipo": item.get("tipo"), "target_language": target_language,
            "contrato": TRANSLATION_CONTRACT, "transcript_original": item["transcript_original"],
            "writable_fields": [f"pieza.{k}" for k in TRANSLATION_FIELDS] + ["pieza.slides[N]"]}


def apply_translation(root, item_id, brand, campos, target_language="es"):
    """Write the translated fields back. Anything outside the whitelist is rejected
    before anything is written (all or nothing)."""
    if not isinstance(campos, dict) or not campos:
        raise ValueError("campos vacío")
    with _LOCK:
        item = get_item(root, item_id, brand)
        pieza = item.setdefault("pieza", default_pieza(item.get("tipo")))
        plan = []
        for key, value in campos.items():
            if not isinstance(value, str) or len(value) > 100_000:
                raise ValueError(f"valor inválido: {key}")
            slide = _SLIDE_RE.match(key)
            if key.startswith("pieza.") and key[6:] in TRANSLATION_FIELDS:
                plan.append((key[6:], None, value))
            elif slide and int(slide.group(1)) < len(pieza.get("slides") or []):
                plan.append(("slides", int(slide.group(1)), value))
            else:
                raise ValueError(f"campo fuera de la whitelist: {key}")
        for field, index, value in plan:
            if index is None:
                pieza[field] = value
            else:
                pieza["slides"][index] = value
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        if "pieza.full_script" in campos:
            pieza["full_script_actualizado"] = now
        item["redaccion"] = {"modo": "traduccion_fiel", "idioma_destino": target_language,
                             "fuente": "transcript_original"}
        item["actualizado"] = now
        for d in _item_dirs(root, brand):
            path = os.path.join(d, f"{item_id}.json")
            if os.path.isfile(path):
                _atomic_json(path, item)
        return item


def create_idea_request(root, body):
    request = {
        "purpose": "ideas", "brand": safe_id(str(body.get("brand") or ""), "brand"),
        "topic": str(body.get("topic") or "").strip()[:2000],
        "reference": str(body.get("reference") or "").strip()[:2000],
        "proposal_fields": ["angle", "emotion", "tentative_hook", "interaction_reason"],
        "requirements": ["verify_trends", "flag_undocumented_personal_stances"],
    }
    key = hashlib.sha256(json.dumps(request, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    path = _versioned_dir(root, "orders") / f"{key}.json"
    with _LOCK:
        if path.is_file():
            return _read_json(path)
        request.update({"id": f"idea-{key[:16]}", "idempotency_key": key, "execution_state": "not_started",
                        "created_at": dt.datetime.now(dt.timezone.utc).isoformat()})
        _atomic_json(path, request)
        return request


# ------------------------------------------------------------------ productions (advanced module)
def _versioned_dir(root, kind):
    return Path(root) / "lab" / "_versioned" / kind


def _load_versioned(root, kind, document_id):
    path = _versioned_dir(root, kind) / f"{safe_id(document_id)}.json"
    if not path.is_file():
        raise FileNotFoundError(document_id)
    return _read_json(path)


def _list_versioned(root, kind):
    directory = _versioned_dir(root, kind)
    documents = []
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else ():
        try:
            documents.append(_read_json(path))
        except (OSError, ValueError):
            continue
    return sorted(documents, key=lambda d: d.get("updated_at", d.get("created_at", "")), reverse=True)


def _save_versioned(root, kind, body, prefix, allowed_fields, defaults):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    with _LOCK:
        document_id = body.get("id")
        existing = _load_versioned(root, kind, document_id) if document_id else None
        if existing:
            if body.get("expected_revision") != existing["revision"]:
                raise RevisionConflict(f"revisión desactualizada: esperada {existing['revision']}")
            document, revision = dict(existing), existing["revision"] + 1
        else:
            title = str(body.get("title") or body.get("name") or "").strip()
            if not title:
                raise ValueError("title/name es obligatorio")
            document_id = f"{prefix}-{dt.date.today():%Y-%m-%d}-{slugify(title, 36)}-{uuid.uuid4().hex[:8]}"
            document, revision = {"id": document_id, **defaults, "created_at": now}, 1
        for key in allowed_fields:
            if key in body:
                document[key] = body[key]
        if existing and all(document.get(k) == existing.get(k) for k in allowed_fields):
            return existing
        document.update({"id": document_id, "revision": revision, "updated_at": now})
        _atomic_json(_versioned_dir(root, f"{kind}-revisions") / document_id / f"{revision}.json", document)
        _atomic_json(_versioned_dir(root, kind) / f"{document_id}.json", document)
        return document


def list_productions(root, brand=None):
    return [p for p in _list_versioned(root, "productions") if not brand or p.get("ecosystem") == brand]


def get_production(root, production_id, revision=None):
    if revision is None:
        return _load_versioned(root, "productions", production_id)
    path = _versioned_dir(root, "productions-revisions") / safe_id(production_id) / f"{int(revision)}.json"
    if not path.is_file():
        raise FileNotFoundError(f"{production_id}@{revision}")
    return _read_json(path)


def list_production_revisions(root, production_id):
    directory = _versioned_dir(root, "productions-revisions") / safe_id(production_id)
    if not directory.is_dir():
        raise FileNotFoundError(production_id)
    return [_read_json(p) for p in sorted(directory.glob("*.json"), key=lambda p: int(p.stem))]


_MATERIAL_FIELDS = ("title", "ecosystem", "format", "family", "input_mode", "source_paths", "piece_ids",
                    "approved_content", "components", "delivery")
_DELIVERY_FIELDS = ("delivery_approval", "delivery_approved_at")
_SAVE_FIELDS = {"title", "ecosystem", "format", "family", "input_mode", "source_paths", "piece_ids",
                "approved_content", "components", "delivery", "review_point", "content_state",
                "production_state", "publication_state", "publication", "delivery_approval",
                "delivery_approved_at", "results", "incidents", "corrections", "events", "credits"}
_PRODUCTION_DEFAULTS = {
    "format": "video", "family": "camera", "input_mode": "script", "source_paths": [], "piece_ids": [],
    "approved_content": [], "components": {}, "delivery": {"networks": [], "editable_project": False},
    "review_point": "Revisar piloto", "content_state": "draft", "production_state": "not_started",
    "publication_state": "not_required", "publication": {"authorized": False, "destinations": []},
}


def _string_list(value, field):
    if not isinstance(value, list) or any(not isinstance(i, str) or not i.strip() for i in value):
        raise ValueError(f"{field} debe ser una lista de textos no vacíos")


def _validate_production_schema(production):
    for field, allowed in (("format", FORMATS), ("family", FAMILIES), ("input_mode", INPUT_MODES)):
        if production.get(field) not in allowed:
            raise ValueError(f"{field} inválido")
    for field in ("source_paths", "piece_ids"):
        _string_list(production.get(field), field)
    content = production.get("approved_content")
    if not isinstance(content, list):
        raise ValueError("approved_content debe ser una lista")
    for item in content:
        if not ((isinstance(item, str) and item.strip()) or (
                isinstance(item, dict) and isinstance(item.get("text"), str) and item["text"].strip()
                and item.get("role") in {"cover", "content", "closing"})):
            raise ValueError("approved_content contiene un elemento inválido")
    for field in ("delivery", "components", "publication"):
        if not isinstance(production.get(field), dict):
            raise ValueError(f"{field} debe ser un objeto")
    if "result_paths" in production["delivery"]:
        _string_list(production["delivery"]["result_paths"], "delivery.result_paths")
    if "destinations" in production["publication"]:
        _string_list(production["publication"]["destinations"], "publication.destinations")


def _material_fingerprint(production):
    material = {k: production.get(k) for k in _MATERIAL_FIELDS}
    material["destinations"] = (production.get("publication") or {}).get("destinations", [])
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _valid_input(root, production):
    if production.get("content_state") != "ready_to_produce":
        return
    mode = production.get("input_mode")
    if mode == "script":
        if production.get("approved_content"):
            return
        if production.get("piece_ids"):
            try:
                for piece_id in production["piece_ids"]:
                    get_item(root, piece_id, production["ecosystem"])
                return
            except (FileNotFoundError, ValueError):
                raise ValueError("script requiere piezas vinculadas existentes")
        raise ValueError("script requiere contenido aprobado o una pieza vinculada")
    if not production.get("source_paths"):
        raise ValueError(f"{mode} requiere source_paths")


def confined_file(root, raw):
    """A final file must live inside the data dir and must not be a playlist/concat input."""
    base = os.path.realpath(root)
    path = os.path.realpath(os.path.join(base, raw))
    if os.path.commonpath((base, path)) != base:
        raise ValueError("archivo fuera de la carpeta de datos")
    if Path(path).suffix.lower() in PLAYLIST_EXT:
        raise ValueError("listas de reproducción y concat no se aceptan")
    if not os.path.isfile(path):
        raise ValueError("archivo final no encontrado")
    return Path(path)


def probe(path, *entries):
    """ffprobe with an argument list (no shell), local files only."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise ValueError("ffprobe no está instalado")
    out = subprocess.run([ffprobe, "-v", "error", "-protocol_whitelist", "file,pipe", *entries,
                          "-of", "json", "file:" + str(path)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, timeout=20)
    return json.loads(out.stdout)


def _approval_for(root, production):
    paths = (production.get("delivery") or {}).get("result_paths") or []
    if not paths:
        raise ValueError("la aprobación de entrega requiere archivos finales")
    carousel = production.get("format") == "carousel"
    if carousel and len(paths) > 8:
        raise ValueError("el carrusel supera 8 archivos finales")
    files, duration = [], None
    for raw in paths:
        path = confined_file(root, raw)
        if carousel and path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise ValueError("el carrusel requiere imágenes finales")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            if carousel:
                stream = probe(path, "-select_streams", "v:0", "-show_entries", "stream=width,height")["streams"][0]
                width, height = int(stream["width"]), int(stream["height"])
                if width <= 0 or height <= 0:
                    raise ValueError
                files.append({"path": raw, "sha256": digest, "width": width, "height": height})
            else:
                measured = float(probe(path, "-show_entries", "format=duration")["format"]["duration"])
                if not math.isfinite(measured) or not 0 < measured <= 60:
                    raise ValueError
                duration = max(duration or 0, measured)
                files.append({"path": raw, "sha256": digest, "duration_s": measured})
        except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, IndexError):
            raise ValueError(f"no se pudo verificar archivo final: {raw}")
    return {"files": files, "duration_s": duration, "material_fingerprint": _material_fingerprint(production)}


def save_production(root, body, brands):
    existing = get_production(root, body["id"]) if body.get("id") else None
    client = {k: v for k, v in body.items() if k not in _DELIVERY_FIELDS}
    effective = {**_PRODUCTION_DEFAULTS, **(existing or {}), **client}
    if effective.get("ecosystem") not in brands:
        raise ValueError("ecosystem debe ser una marca configurada")
    for field, allowed in (("content_state", CONTENT_STATES), ("production_state", PRODUCTION_STATES),
                           ("publication_state", PUBLICATION_STATES)):
        if effective.get(field) not in allowed:
            raise ValueError(f"{field} inválido")
    _validate_production_schema(effective)
    _valid_input(root, effective)
    supplied = (effective.get("delivery") or {}).get("duration_s")
    if supplied is not None:
        try:
            supplied = float(supplied)
        except (TypeError, ValueError):
            raise ValueError("duration_s debe ser un número finito positivo")
        if not math.isfinite(supplied) or supplied <= 0:
            raise ValueError("duration_s debe ser un número finito positivo")
        if supplied > 60:
            raise ValueError("el archivo final supera 60 segundos; condensar o dividir antes de producir")
    material_changed = bool(existing and (
        any(effective.get(k) != existing.get(k) for k in _MATERIAL_FIELDS)
        or (effective.get("publication") or {}).get("destinations", [])
        != (existing.get("publication") or {}).get("destinations", [])))
    for field in _DELIVERY_FIELDS:
        if field in body and (not existing or body[field] != existing.get(field)) and not material_changed:
            raise ValueError(f"{field} lo administra el servidor")
    if material_changed:  # any material change invalidates approval and publication
        effective.update({"content_state": "draft", "delivery_approval": None, "delivery_approved_at": None,
                          "publication": {**(effective.get("publication") or {}), "authorized": False}})
        if effective.get("production_state") == "finished":
            effective["production_state"] = "not_started"
        if effective.get("publication_state") in {"scheduled", "published", "closed"}:
            effective["publication_state"] = "not_required"
    if effective.get("production_state") == "finished" and not effective.get("delivery_approved_at"):
        raise ValueError("finalizar requiere aprobación humana de la entrega")
    state = effective.get("publication_state")
    if state in {"scheduled", "published", "closed"} and (not existing or state != existing.get("publication_state")):
        raise ValueError("programación/publicación no disponible sin verificación del proveedor")
    if body.get("approve_delivery"):
        if material_changed:
            raise ValueError("guarde cambios materiales antes de aprobar la entrega")
        approval = _approval_for(root, effective)
        if not existing or approval != existing.get("delivery_approval"):
            effective["delivery_approval"] = approval
            effective["delivery_approved_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_body = {k: effective[k] for k in _SAVE_FIELDS if k in effective}
    if existing:
        save_body.update({"id": existing["id"], "expected_revision": body.get("expected_revision")})
    return _save_versioned(root, "productions", save_body, "prod", _SAVE_FIELDS, {
        **_PRODUCTION_DEFAULTS, "credits": {"count": 0, "cost": "", "retries": 0},
        "results": [], "incidents": [], "corrections": [], "events": []})


def list_templates(root):
    return _list_versioned(root, "templates")


def save_template(root, body):
    if "ecosystem" in body:
        raise ValueError("las plantillas son independientes de la marca")
    cfg = body.get("config", {})
    if not isinstance(cfg, dict) or set(cfg) - {"format", "family", "input_mode", "components"}:
        raise ValueError("config de plantilla contiene campos no reutilizables")
    components = cfg.get("components", {})
    if not isinstance(components, dict) or set(components) - {"layout", "broll", "max_duration_s"}:
        raise ValueError("components de plantilla contiene campos no reutilizables")
    if any(k != "components" and not isinstance(v, str) for k, v in cfg.items()) or any(
            isinstance(v, (dict, list)) for v in components.values()):
        raise ValueError("la plantilla debe usar valores escalares")
    if "max_duration_s" in components:
        try:
            maximum = float(components["max_duration_s"])
        except (TypeError, ValueError):
            raise ValueError("max_duration_s debe ser finito")
        if not math.isfinite(maximum) or not 0 < maximum <= 60:
            raise ValueError("max_duration_s debe ser finito y hasta 60")
    return _save_versioned(root, "templates", body, "tpl", {"name", "description", "config", "validated"},
                           {"description": "", "config": {}, "validated": False})


_NUMBERS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
            "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12}
# ponytail: lexical promise parser; swap for editorial metadata if claims need broader coverage.
_PROMISE = re.compile(r"\b(\d+|" + "|".join(_NUMBERS) + r")\s+(?:razones?|consejos?|errores?|soluciones?|tips?|"
                      r"pasos?|ideas?|trucos?|claves?|formas?|puntos?|beneficios?|mitos?|señales?|h[aá]bitos?|"
                      r"t[eé]cnicas?|estrategias?)\b")


def _validate_order_content(production):
    if production.get("format") != "carousel":
        return
    slides = production.get("approved_content") or []
    if len(slides) > 8:
        raise ValueError("el carrusel supera 8 slides; condensar, dividir o cambiar de formato")
    role = lambda s: s.get("role") if isinstance(s, dict) else None  # noqa: E731
    text = lambda s: str(s.get("text", "") if isinstance(s, dict) else s)  # noqa: E731
    body = [text(s).strip().lower() for s in slides if role(s) not in {"cover", "closing"}]
    distinct = len({re.sub(r"\W+", " ", t).strip() for t in body if t})
    promise = (str(production.get("title") or "") + " " + " ".join(text(s) for s in slides if role(s) == "cover")).lower()
    for raw in _PROMISE.findall(promise):
        promised = int(raw) if raw.isdigit() else _NUMBERS[raw]
        if promised != distinct:
            raise ValueError(f"la promesa enumera {promised} elementos pero hay {distinct} distintos")


def create_order(root, production_id, expected_revision=None, purpose="production"):
    with _LOCK:
        production = get_production(root, production_id)
        if expected_revision is not None and expected_revision != production["revision"]:
            raise RevisionConflict(f"revisión desactualizada: esperada {production['revision']}")
        if purpose not in {"production", "publication"}:
            raise ValueError("purpose inválido")
        _validate_production_schema(production)
        if production["content_state"] != "ready_to_produce":
            raise ValueError("el contenido debe aprobarse antes de copiar la orden")
        _valid_input(root, production)
        _validate_order_content(production)
        if purpose == "publication":
            publication = production.get("publication") or {}
            if not publication.get("authorized") or not publication.get("destinations"):
                raise ValueError("la orden de publicación requiere autorización y destinos")
            approval = production.get("delivery_approval") or {}
            if approval.get("material_fingerprint") != _material_fingerprint(production):
                raise ValueError("la orden de publicación requiere aprobación vigente de entrega")
            if _approval_for(root, production).get("files") != approval.get("files"):
                raise ValueError("los archivos finales cambiaron desde la aprobación")
        key = hashlib.sha256(f"{production_id}:{production['revision']}:{purpose}".encode()).hexdigest()
        path = _versioned_dir(root, "orders") / f"{key}.json"
        if path.is_file():
            return _read_json(path)
        order = {
            "id": f"order-{key[:16]}", "idempotency_key": key, "purpose": purpose,
            "production_id": production_id, "production_revision": production["revision"],
            "ecosystem": production["ecosystem"], "sources": production["source_paths"],
            **{k: production[k] for k in ("format", "family", "input_mode", "piece_ids", "approved_content",
                                          "components", "delivery")},
            "publication": production.get("publication"), "credits": production.get("credits"),
            "next_review": production["review_point"], "execution_state": "not_started",
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        _atomic_json(path, order)
        return order


def list_orders(root, production_id=None):
    return [o for o in _list_versioned(root, "orders") if not production_id or o.get("production_id") == production_id]


# ------------------------------------------------------------------ library (installed kit catalog)
def component_catalog(kit_dir):
    """Read what the INSTALLED kit ships (.kit/presets/...). Empty when nothing is there."""
    kit = Path(kit_dir)

    def names(folder, kind):
        out = []
        for p in sorted((kit / folder).glob("*.json")) if (kit / folder).is_dir() else ():
            try:
                data = _read_json(p)
            except (OSError, ValueError):
                continue
            out.append({"id": p.stem, "kind": kind, "label": data.get("name", p.stem) if isinstance(data, dict) else p.stem,
                        "status": data.get("status") if isinstance(data, dict) else None})
        return out
    return {"captions": names("presets/captions/presets", "caption"),
            "broll_modes": names("presets/broll", "broll"),
            "carousel": names("presets/carousel", "carousel"),
            "hooks_bank": (kit / "presets/hooks/hooks-bank.json").is_file(),
            "voices": [], "components": []}


def main(argv=None):
    """CLI for the translation handoff the Ideas view copies: writes only whitelisted fields."""
    import argparse
    from cc.config import config

    here = Path(__file__).resolve()
    default = here.parents[3] if here.parents[2].name == ".kit" else Path.cwd()
    ap = argparse.ArgumentParser(prog="lab")
    ap.add_argument("--target", default=str(default), help="carpeta del proyecto (tiene .kit-personal/)")
    sub = ap.add_subparsers(dest="command", required=True)
    t = sub.add_parser("apply-translation", help="guardar una traducción fiel en una ficha del Content Lab")
    t.add_argument("--brand", required=True)
    t.add_argument("--id", required=True)
    t.add_argument("--campos", required=True, help="archivo JSON {\"pieza.hook\": ..., ...} o - para stdin")
    t.add_argument("--lang", default="es")
    a = ap.parse_args(argv)
    try:
        if a.brand not in {b["id"] for b in config.load(a.target)["brands"]}:
            raise ValueError(f"marca desconocida: {a.brand}")
        raw = sys.stdin.read() if a.campos == "-" else Path(a.campos).read_text(encoding="utf-8")
        item = apply_translation(str(Path(a.target) / ".kit-personal" / "data"), a.id, a.brand, json.loads(raw),
                                 a.lang)
    except (OSError, ValueError) as e:
        print(f"lab: {e}", file=sys.stderr)
        return 2
    print(f"Traducción guardada en la ficha {item['id']}. Revisala en Ideas del Command Center.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
