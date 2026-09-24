# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Scripts (guiones) as Markdown files: frontmatter + known sections.

<root>/guiones/<estado-dir>/<file>.md, root = TARGET/.kit-personal/data. The
folder IS the state. File names are never taken as paths (basename + pattern),
so a request can only touch files inside these folders, and every path is walked
component by component: a symlink (or anything resolving outside the data dir) is
refused for reads, writes, moves and deletes alike. A "## Parte 2" typed
inside a script does not end its section: section headings the writer knows are
escaped with "\\" on save and restored on read.
"""
import datetime as dt
import json
import os
import re
import threading

_LOCK = threading.Lock()
ESTADO_DIR = {"en_proceso": "en_proceso", "aprobado": "aprobados", "grabando": "grabando",
              "grabado": "grabados", "editado": "editados"}
DIRS = tuple(ESTADO_DIR.values())
SECTION_END = r"^## (?:Hook|Guion|Talking points|Caption|Notas)\n|\Z"
WRITTEN_META = {"titulo", "hook", "formato", "estructura", "estado", "favorito", "actualizado"}
KEEP_META = ("serie", "ep", "creado", "fuente", "tema", "brand", "brief_pedido", "convertido", "task_code")
TASK_CODE_RE = re.compile(r"^[A-Z]{2,6}-\d{1,9}$")
FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,150}\.md$")
MAX_SECTION = 100_000


def _base(root):
    return _checked(root, "guiones")


def _checked(root, *parts):
    """root/<parts...>, refusing a symlink at any component and anything that resolves outside root."""
    p = str(root)
    for part in parts:
        p = os.path.join(p, part)
        if os.path.islink(p):
            raise ValueError("hay un enlace simbólico en la carpeta de guiones; no lo sigo")
    real_root = os.path.realpath(root)
    if os.path.commonpath([os.path.realpath(p), real_root]) != real_root:
        raise ValueError("ruta fuera de la carpeta de datos")
    return p


def _escape(text):
    return re.sub(r"(?m)^(\\*## )", r"\\\1", text or "")


def _unescape(text):
    return re.sub(r"(?m)^\\(\\*## )", r"\1", text)


def _clean(value):
    return str(value or "").replace('"', "'").replace("\n", " ").strip()[:200]


def _safe_name(name):
    name = os.path.basename(str(name or ""))
    if not FILE_RE.fullmatch(name):
        raise ValueError("file inválido")
    return name


def parse(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    meta, body = {}, raw
    m = re.match(r"^---\n(.*?)\n---\n?", raw, re.S)
    if m:
        body = raw[m.end():]
        for line in m.group(1).splitlines():
            kv = re.match(r"^(\w+):\s*\"?(.*?)\"?\s*$", line)
            if kv:
                meta[kv.group(1)] = kv.group(2)

    def section(name):
        s = re.search(rf"^## {name}\n(.*?)(?={SECTION_END})", body, re.S | re.M)
        return _unescape(s.group(1).strip()) if s else ""
    return meta, {k: section(n) for k, n in (("hook", "Hook"), ("cuerpo", "Guion"), ("caption", "Caption"),
                                              ("talking_points", "Talking points"), ("notas", "Notas"))}


def render(front, s):
    """The only writer of a script body: re-saving never drops a section."""
    s = {k: _escape(v) for k, v in s.items()}
    out = front + (f"## Hook\n{s['hook']}\n\n" if s["hook"] else "") + f"## Guion\n{s['cuerpo']}\n"
    for key, name in (("talking_points", "Talking points"), ("caption", "Caption"), ("notas", "Notas")):
        if s[key]:
            out += f"\n## {name}\n{s[key]}\n"
    return out


def _frontmatter(meta, estado, favorito, now):
    fm = (f"---\ntitulo: \"{_clean(meta.get('titulo'))}\"\nhook: \"{_clean(meta.get('hook'))}\"\n"
          f"formato: \"{_clean(meta.get('formato'))}\"\nestructura: \"{_clean(meta.get('estructura'))}\"\n"
          f"estado: \"{estado}\"\nfavorito: \"{favorito}\"\n")
    fm += "".join(f"{k}: \"{_clean(meta[k])}\"\n" for k in KEEP_META if meta.get(k))
    # unknown fields from older files are kept verbatim so no save ever drops them
    fm += "".join(f"{k}: \"{_clean(v)}\"\n" for k, v in meta.items()
                  if k not in WRITTEN_META and k not in KEEP_META and re.fullmatch(r"\w{1,40}", k))
    return fm + f"actualizado: {now.isoformat()}\n---\n\n"


def find(root, name):
    name = _safe_name(name)
    for d in DIRS:
        p = _checked(root, "guiones", d, name)
        if os.path.isfile(p):
            return p
    return None


def _hooks(root):
    try:
        with open(_checked(root, "hooks-visuales.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def list_all(root):
    hv = _hooks(root).get("byGuion", {})
    out = []
    for d in DIRS:
        try:
            folder = _checked(root, "guiones", d)
        except ValueError:
            continue  # a symlinked folder is not listed (and never written)
        if not os.path.isdir(folder):
            continue
        for fn in sorted(os.listdir(folder)):
            path = os.path.join(folder, fn)
            if not FILE_RE.fullmatch(fn) or os.path.islink(path) or not os.path.isfile(path):
                continue
            try:
                meta, s = parse(path)
            except (OSError, UnicodeDecodeError):
                continue
            out.append({"file": fn, "dir": d, "titulo": meta.get("titulo") or fn,
                        "estado": meta.get("estado") or d.rstrip("s"),
                        "favorito": meta.get("favorito") == "true",
                        **{k: meta.get(k) or "" for k in ("serie", "ep", "tema", "estructura", "brand", "formato")},
                        "task_code": meta.get("task_code") if TASK_CODE_RE.fullmatch(meta.get("task_code") or "") else None,
                        **s, "hooks": hv.get(fn), "mtime": int(os.path.getmtime(path))})
    out.sort(key=lambda g: -g["mtime"])
    return out


def save(root, body):
    for k in ("hook", "cuerpo", "full_script", "caption", "talking_points", "notas"):
        if body.get(k) is not None and (not isinstance(body[k], str) or len(body[k]) > MAX_SECTION):
            raise ValueError(f"{k} inválido")
    titulo = re.sub(r"\s+", " ", str(body.get("titulo") or body.get("tema") or "")).replace('"', "'").strip()[:200]
    if body.get("task_code") is not None and not TASK_CODE_RE.fullmatch(str(body["task_code"])):
        raise ValueError("task_code inválido (ejemplo: CAN-12)")
    estado = body.get("estado")
    if estado is not None and estado not in ESTADO_DIR:
        raise ValueError("estado inválido")
    now = dt.datetime.now()
    with _LOCK:
        old_path, meta, sections = None, {}, {k: "" for k in ("hook", "cuerpo", "caption", "talking_points", "notas")}
        if body.get("file"):
            fname = _safe_name(body["file"])
            old_path = find(root, fname)
            if not old_path:
                raise FileNotFoundError(fname)
            meta, sections = parse(old_path)  # partial save keeps everything else
        else:
            if not titulo:
                raise ValueError("título requerido")
            slug = re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-")[:60] or "guion"
            fname, n = f"{now:%Y-%m-%d}-{slug}.md", 2
            while find(root, fname):  # never overwrite another script from the same day
                fname, n = f"{now:%Y-%m-%d}-{slug}-{n}.md", n + 1
            meta = {"creado": now.isoformat(), "fuente": "command-center"}
        for k in ("hook", "caption", "talking_points", "notas"):
            if k in body:
                sections[k] = body[k] or ""
        if "cuerpo" in body or "full_script" in body:
            sections["cuerpo"] = body.get("cuerpo") or body.get("full_script") or ""
        for k in ("formato", "estructura", *KEEP_META):
            if k in body:
                meta[k] = ("true" if body[k] else "false") if isinstance(body[k], bool) else _clean(body[k])
        meta["titulo"] = titulo or meta.get("titulo") or fname
        meta["hook"] = sections["hook"]
        estado = estado or (meta.get("estado") if meta.get("estado") in ESTADO_DIR else "en_proceso")
        favorito = ("true" if body["favorito"] else "false") if "favorito" in body else (meta.get("favorito") or "false")
        target = _checked(root, "guiones", ESTADO_DIR[estado])
        os.makedirs(target, exist_ok=True)
        target = _checked(root, "guiones", ESTADO_DIR[estado])  # re-check after creating
        path = _checked(root, "guiones", ESTADO_DIR[estado], fname)
        tmp = _checked(root, "guiones", ESTADO_DIR[estado], fname + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(render(_frontmatter(meta, estado, favorito, now), sections))
        os.replace(tmp, path)
        if old_path and os.path.abspath(old_path) != os.path.abspath(path):
            os.remove(_checked(root, "guiones", os.path.basename(os.path.dirname(old_path)), fname))  # moved
    return {"file": fname, "estado": estado}


def toggle_favorite(root, name):
    path = find(root, name)
    if not path:
        raise FileNotFoundError(name)
    meta, _ = parse(path)
    return {**save(root, {"file": name, "favorito": meta.get("favorito") != "true"}),
            "favorito": meta.get("favorito") != "true"}


def delete(root, name):
    with _LOCK:
        path = find(root, name)  # checked: never follows a symlinked folder out of the data dir
        if not path:
            raise FileNotFoundError(name)
        os.remove(path)
    return {"file": os.path.basename(path), "deleted": True}


def save_hooks(root, body):
    """3 hook versions per script: {"file", "opciones": [str...], "elegida": index|null}."""
    fname = _safe_name(body.get("file"))
    if "opciones" in body:
        opts = body["opciones"]
        if not isinstance(opts, list) or len(opts) > 10 or not all(isinstance(o, str) and len(o) <= 2000 for o in opts):
            raise ValueError("opciones inválidas")
    with _LOCK:  # the whole read-modify-write: two saves at once never erase each other's versions
        data = _hooks(root)
        entry = data.setdefault("byGuion", {}).setdefault(fname, {"elegida": None, "opciones": []})
        if "opciones" in body:
            entry["opciones"] = body["opciones"]
        if "elegida" in body:
            entry["elegida"] = body["elegida"]
        el = entry["elegida"]
        if el is not None and not (isinstance(el, int) and not isinstance(el, bool) and 0 <= el < len(entry["opciones"])):
            raise ValueError("elegida no está entre las opciones")
        os.makedirs(root, exist_ok=True)
        tmp = _checked(root, "hooks-visuales.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, _checked(root, "hooks-visuales.json"))
    return {"file": fname, **entry}
