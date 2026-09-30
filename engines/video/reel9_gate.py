# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Control de un reel de contenido ANTES de armarlo: lee data.json y presets/reel/standard.json.

    python3 .kit/launch.py reel9 check <carpeta-del-reel> [--standard reglas.json] [--batch <otro-reel> ...]

Devuelve la lista de fallas (vacía = se puede armar) y deja el resultado en <reel>/.reel-gate.json.
Un dato que falta es una falla con su motivo, nunca un pase silencioso. Solo stdlib (+ ffprobe
para medir el audio y el tamaño de las imágenes).

Lo que revisa: hook de 3 tramos con su imagen de portada y el título encima; ninguna imagen quieta
más de max_static_s ni repetida (en el reel y en el lote); una tarjeta por idea del guion, sin huecos
largos después del hook; tarjetas de a una con tiempo para leerse; el retrato (dossier) siempre
acompañado de una tarjeta; duración del reel y ritmo de la voz (palabras por segundo de vo.txt).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kit_platform  # noqa: E402

KIT = kit_platform.KIT_ROOT
STANDARD = KIT / "presets" / "reel" / "standard.json"
RESULT = ".reel-gate.json"
CHROME_CARDS = {"intro", "outro"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_CARDS = {"lower-third", "stat"}
PAIRED_DOSSIER = True  # el retrato nunca sale solo: entra y sale con la tarjeta de su idea


def load_standard(path=None) -> dict:
    return json.loads(Path(path or STANDARD).read_text(encoding="utf-8"))


def _words(card) -> int:
    """Palabras que se leen en la tarjeta (sin etiquetas HTML)."""
    parts = [card.get(k) or "" for k in ("html", "val", "label", "tag", "caption")]
    return len(re.findall(r"[\wÀ-ÿ%$€']+", re.sub(r"<[^>]+>", " ", " ".join(map(str, parts)))))


def pair_dossiers(cards, blocks):
    """Cada retrato (dossier) se muestra junto con una tarjeta de texto/dato de su misma idea del guion.

    Pareja = la próxima tarjeta de esa idea (se adelanta su entrada al inicio del retrato) o, si no
    hay, la anterior (se estira su salida hasta el fin del retrato).
    Devuelve (tarjetas ajustadas, [(índice retrato, índice pareja)], errores). No toca las originales.
    """
    cards, pairs, errs, eps = [dict(c) for c in cards], [], [], 1e-3
    for i, c in enumerate(cards):
        if c.get("type") != "dossier":
            continue
        s, e = float(c.get("start", 0)), float(c.get("end", 0))
        blk = next((b for b in blocks or [] if b["start"] - eps <= s < b["end"] - eps), None)
        if blk is None:
            errs.append(f"retrato en {s} s: no cae dentro de ninguna idea del guion (script_blocks)")
            continue
        same = [k for k, x in enumerate(cards) if x.get("type") in TEXT_CARDS
                and blk["start"] - eps <= float(x.get("start", 0)) < blk["end"] - eps]
        nxt = [k for k in same if float(cards[k]["start"]) >= s - eps]
        prv = [k for k in same if float(cards[k]["start"]) < s - eps]
        if nxt:
            k = min(nxt, key=lambda k: float(cards[k]["start"]))
            cards[k]["start"] = s
        elif prv:
            k = max(prv, key=lambda k: float(cards[k]["start"]))
            cards[k]["end"] = max(float(cards[k].get("end", 0)), e)
        else:
            errs.append(f"retrato en {s} s: su idea del guion ({blk['start']}–{blk['end']} s) no tiene tarjeta de "
                        "texto o de dato que lo acompañe (el retrato nunca sale solo)")
            continue
        pairs.append((i, k))
    return cards, pairs, errs


def card_schedule(cards, std, paired_dossiers=False) -> list[dict]:
    """Tarjetas de a una: entrada, permanencia y salida de cada tarjeta, encadenadas.

    La entrada arranca en el inicio de la tarjeta o, si la anterior todavía está, cuando terminó
    su salida. La permanencia dura al menos la lectura (palabras/words_per_s + read_pad_s).
    """
    seq = std["cards"]["sequential"]
    out, prev_end = [], None
    types = set(seq["types"]) - ({"dossier"} if paired_dossiers else set())
    items = sorted(((i, c) for i, c in enumerate(cards) if c.get("type") in types),
                   key=lambda ic: (ic[1].get("start", 0), ic[0]))
    for i, c in items:
        dossier = c["type"] == "dossier"
        ent = seq["dossier_entry_s"] if dossier else seq["entry_s"]
        ex = seq["dossier_exit_s"] if dossier else seq["exit_s"]
        t_in = float(c.get("start", 0)) if prev_end is None else max(float(c.get("start", 0)), prev_end)
        n = _words(c)
        read = round(n / seq["words_per_s"] + seq["read_pad_s"], 3)
        t_out = max(float(c.get("end", 0)) - ex, t_in + ent + read)
        out.append({"index": i, "type": c["type"], "words": n, "read": read,
                    "in": round(t_in, 3), "in_end": round(t_in + ent, 3),
                    "out": round(t_out, 3), "out_end": round(t_out + ex, 3), "hold": round(t_out - t_in - ent, 3)})
        prev_end = t_out + ex
    return out


def sequence_errors(schedule, std, outro_start=None) -> list[str]:
    """Rechaza tarjetas superpuestas, permanencia menor a la lectura y huecos largos."""
    errs, gap, eps = [], std["cards"]["max_gap_s"], 1e-3
    for k, s in enumerate(schedule):
        at = f"tarjeta {s['type']} en {s['in']:.2f} s"
        if s["hold"] < s["read"] - eps:
            errs.append(f"{at}: se queda {s['hold']:.2f} s y su lectura pide {s['read']:.2f} s ({s['words']} palabras)")
        if k:
            p = schedule[k - 1]
            if s["in"] < p["out_end"] - eps:
                errs.append(f"{at}: entra antes de que termine de salir la anterior ({p['out_end']:.2f} s): dos tarjetas a la vez")
            elif s["in"] - p["out_end"] > gap + eps:
                errs.append(f"{at}: hueco de {s['in'] - p['out_end']:.2f} s desde la salida de la anterior (máximo {gap} s)")
    if schedule and outro_start is not None and schedule[-1]["out_end"] > outro_start + eps:
        errs.append(f"las tarjetas no entran antes del cierre: la última termina de salir en {schedule[-1]['out_end']:.2f} s "
                    f"y el cierre empieza en {outro_start:.2f} s (acortá textos o juntá ideas)")
    return errs


# ---------- medidas con ffprobe ----------

def _probe(path: Path, *entries: str, stream: str | None = None):
    """Valores de ffprobe, o None si ffprobe no está instalado. Un archivo ilegible lanza ValueError."""
    cmd = [kit_platform.ffprobe(), "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream, "-show_entries", f"stream={','.join(entries)}"]
    else:
        cmd += ["-show_entries", f"format={','.join(entries)}"]
    try:
        r = subprocess.run(cmd + ["-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return None
    if r.returncode != 0 or not r.stdout.strip():
        raise ValueError(f"no se pudo leer {Path(path).name}")
    return r.stdout.strip().splitlines()[0].split(",")


def audio_duration(path: Path):
    v = _probe(path, "duration")
    try:
        return None if v is None else float(v[0])
    except ValueError:
        raise ValueError(f"no se pudo medir la duración de {Path(path).name}")


def image_size(path: Path):
    """(ancho, alto). PNG se lee de su cabecera; el resto con ffprobe (None si no está instalado)."""
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    v = _probe(path, "width", "height", stream="v:0")
    return None if v is None else (int(v[0]), int(v[1]))


# ---------- reglas ----------

def _hook(visuals, title, std):
    errs, spec = [], std["hook"]
    tol, want = spec["tolerance_s"], spec["segments"]
    hook_end = want[-1]["end"]
    segs = [v for v in visuals if v["start"] < hook_end - tol]
    if len(segs) != len(want):
        errs.append(f"el hook tiene {len(segs)} tramo(s) en los primeros {hook_end} s; el estándar pide "
                    f"{len(want)}: " + ", ".join(f"{w['start']}–{w['end']} s {w['role']}" for w in want))
    for i, (got, w) in enumerate(zip(segs, want), 1):
        if abs(got["start"] - w["start"]) > tol or abs(got["end"] - w["end"]) > tol:
            errs.append(f"tramo {i} del hook va de {got['start']:.2f} a {got['end']:.2f} s; debe ir de {w['start']} a {w['end']} s")
        if got["role"] != w["role"]:
            errs.append(f"tramo {i} del hook es {got['role']!r}; debe ser {w['role']!r}")
    if spec.get("hook_image_required"):
        first = segs[0] if segs else None
        if not first or first["role"] != "hook_image" or not first["asset"] or not first["asset"].is_file():
            errs.append("falta la imagen de portada del hook: el tramo 1 tiene que ser role 'hook_image' con su archivo")
    if spec.get("title_over_whole_hook") and (not title or title[0] > 0.5 or title[1] < hook_end - tol):
        errs.append(f"el título (tarjeta intro) no cubre todo el hook (0–{hook_end} s): {title}")
    return errs


def _visuals(visuals, root: Path, rules):
    errs = []
    for v in visuals:
        a = v["asset"]
        label = a.name if a else v["id"]
        dur = v["end"] - v["start"]
        if dur > rules["max_static_s"] + 1e-6:
            errs.append(f"la imagen {label} queda quieta {dur:.1f} s ({v['start']:.2f}–{v['end']:.2f}); máximo {rules['max_static_s']} s")
        if not a:
            errs.append(f"el tramo {v['id']} no declara imagen (asset)")
        elif root not in a.resolve().parents:
            errs.append(f"la imagen {label} está fuera de la carpeta del reel: el render la dibuja en negro")
        elif not a.is_file():
            errs.append(f"falta el archivo {a}")
        elif a.suffix.lower() in IMAGE_EXT:
            try:
                size = image_size(a)
            except ValueError:
                errs.append(f"la imagen {label} no se puede leer: ¿está dañada?")
                continue
            if size and min(size) < rules["min_photo_side_px"]:
                errs.append(f"la imagen {label} mide {size[0]}×{size[1]}; el lado menor debe tener al menos "
                            f"{rules['min_photo_side_px']} px (pedila más grande, no la estires)")
    return errs


def _fingerprints(visuals, tag=""):
    out = []
    for v in visuals:
        a = v["asset"]
        if a and a.is_file():
            out.append((f"{tag}{a.name} ({v['start']:.2f} s)", hashlib.sha256(a.read_bytes()).hexdigest()))
    return out


def _repeats(visuals, batch_dirs, rules):
    errs, mine = [], _fingerprints(visuals)
    if rules.get("no_repeats_in_reel", True):
        for i, (label, sha) in enumerate(mine):
            for other, osha in mine[:i]:
                if sha == osha:
                    errs.append(f"imagen repetida en el reel: {label} es el mismo archivo que {other}")
    if rules.get("no_repeats_in_batch", True):
        for bdir in batch_dirs:
            bdir = Path(bdir)
            try:
                theirs = _fingerprints(normalize(bdir)["visuals"], f"{bdir.name}/")
            except (ValueError, KeyError, OSError, TypeError) as exc:
                errs.append(f"no se pudo leer el reel del lote {bdir}: {exc}")
                continue
            for label, sha in mine:
                for other, osha in theirs:
                    if sha == osha:
                        errs.append(f"imagen repetida en el lote: {label} también está en {other}")
    return errs


def _coverage(cards, duration, std):
    """Después del hook y hasta el cierre siempre hay una tarjeta visible (huecos <= max_gap_s)."""
    rules = std["cards"]
    if not rules.get("continuous_after_hook"):
        return []
    gap = rules["max_gap_s"]
    start = std["hook"]["segments"][-1]["end"]
    outro = next((c["start"] for c in cards if c["type"] == "outro"), None)
    end = outro if outro is not None else duration
    if not isinstance(end, (int, float)):
        return ["no se sabe dónde termina el cuerpo (sin outro ni duración) para medir huecos de tarjetas"]
    spans = sorted((c["start"], c["end"]) for c in cards if c["type"] not in CHROME_CARDS)
    errs, t = [], start
    for s, e in spans:
        if s - t > gap + 1e-6 and t < end:
            errs.append(f"hueco sin tarjeta de {t:.2f} a {min(s, end):.2f} s ({min(s, end) - t:.2f} s; máximo {gap} s)")
        t = max(t, e)
    if end - t > gap + 1e-6:
        errs.append(f"hueco sin tarjeta de {t:.2f} a {end:.2f} s ({end - t:.2f} s; máximo {gap} s)")
    return errs


def _dossiers(dossiers, root: Path, need):
    errs = []
    if len(dossiers) < need:
        errs.append(f"{len(dossiers)} tarjeta(s) dossier (mínimo {need}): el retrato citado, "
                    "con {type: dossier, start, end, asset, caption, subject: person|concept}")
    for d in dossiers:
        a, at = d["asset"], f"dossier en {d['start']} s"
        if d.get("subject") not in ("person", "concept"):
            errs.append(f"{at}: subject tiene que ser 'person' o 'concept', no {d.get('subject')!r}")
        if not (d.get("caption") or "").strip():
            errs.append(f"{at}: falta caption (el pie del retrato)")
        if not a:
            errs.append(f"{at}: falta asset (la imagen del retrato)")
        elif root not in Path(a).resolve().parents:
            errs.append(f"{at}: la imagen {Path(a).name} está fuera de la carpeta del reel")
        elif not Path(a).is_file():
            errs.append(f"{at}: falta el archivo {a}")
    return errs


def _cards(view, std):
    errs, rules = [], std["cards"]
    content = [c for c in view["cards"] if c["type"] not in CHROME_CARDS]
    blocks = view["blocks"]
    if not blocks:
        errs.append("faltan script_blocks (las ideas del guion, cada una con start y end)")
    elif rules.get("one_per_script_block"):
        for i, b in enumerate(blocks, 1):
            if not any(b["start"] <= c["start"] < b["end"] for c in content):
                errs.append(f"la idea {i} del guion ({b['start']}–{b['end']} s) no tiene tarjeta")
    errs += _coverage(view["cards"], view["duration"], std)
    errs += _dossiers(view["dossiers"], Path(view["root"]).resolve(), rules.get("min_dossier", 0))
    return errs


def _sequence(view, std):
    outro = next((c["start"] for c in view["cards"] if c["type"] == "outro"), None)
    cards, _, errs = pair_dossiers(view["raw_cards"], view["blocks"])
    return errs + sequence_errors(card_schedule(cards, std, paired_dossiers=True), std, outro)


def _audio(view, std, root: Path):
    errs = []
    lo, hi = std["duration_s"]
    d = view["duration"]
    if not isinstance(d, (int, float)):
        errs.append("no se sabe cuánto dura el reel (falta audio.duration en data.json)")
    elif not lo <= d <= hi:
        errs.append(f"el reel dura {d:.1f} s; debe durar entre {lo} y {hi} s")
    src = view["audio_src"]
    if not src:
        errs.append("falta audio.src: el archivo de voz (con música ya mezclada, si lleva) del reel")
    elif not (root / src).is_file():
        errs.append(f"falta el archivo de audio {src}")
    elif isinstance(d, (int, float)):
        try:
            real = audio_duration(root / src)
        except ValueError as exc:
            errs.append(str(exc))
            real = None
        if real is not None and abs(real - d) > 0.5:
            errs.append(f"audio.duration dice {d:.1f} s pero {src} dura {real:.1f} s: poné la duración real")
    if view["script"] is None:
        errs.append("falta vo.txt (el texto de la voz) para medir el ritmo")
    elif isinstance(d, (int, float)) and d > 0:
        n = len(re.findall(r"[\wÀ-ÿ']+", view["script"]))
        lo_w, hi_w = std["words_per_s"]
        rate = n / d
        if not lo_w <= rate <= hi_w:
            errs.append(f"la voz lleva {n} palabras en {d:.0f} s ({rate:.1f} por segundo); "
                        f"lo natural es entre {lo_w} y {hi_w}: ajustá el guion o la duración")
    m = view["music"]
    if m and not (root / m).is_file():
        errs.append(f"falta el archivo de música {m}")
    if std.get("music", {}).get("required") and not m:
        errs.append("no hay música declarada (audio.music)")
    return errs


# ---------- entrada ----------

def _json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"falta {Path(path).name}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"{Path(path).name} no es JSON válido: {exc.msg}")


def normalize(reel: Path) -> dict:
    """data.json -> la vista que revisan las reglas."""
    reel = Path(reel).resolve()
    data = _json(reel / "data.json")
    audio = data.get("audio") or {}
    visuals = [{"asset": reel / s["asset"] if s.get("asset") else None, "start": float(s["start"]), "end": float(s["end"]),
                "role": s.get("role"), "id": s.get("id")} for s in data.get("visual_slots", [])]
    visuals.sort(key=lambda v: v["start"])
    raw = data.get("cards", [])
    cards = [{"type": c.get("type"), "start": c.get("start", 0), "end": c.get("end", 0)} for c in raw]
    intro = next((c for c in cards if c["type"] == "intro"), None)
    dossiers = [{"asset": reel / c["asset"] if c.get("asset") else None, "start": c.get("start", 0),
                 "caption": c.get("caption"), "subject": c.get("subject")} for c in raw if c.get("type") == "dossier"]
    vo = reel / "vo.txt"
    return {"root": str(reel), "duration": audio.get("duration"), "visuals": visuals, "cards": cards, "raw_cards": raw,
            "dossiers": dossiers, "blocks": data.get("script_blocks"),
            "title": (intro["start"], intro["end"]) if intro else None,
            "audio_src": audio.get("src"), "music": audio.get("music"),
            "script": vo.read_text(encoding="utf-8") if vo.is_file() else None}


def resolve_reel_dir(reel_dir) -> Path:
    """Acepta la carpeta del reel o una que la contenga en reel/."""
    reel_dir = Path(reel_dir)
    if not (reel_dir / "data.json").exists() and (reel_dir / "reel" / "data.json").exists():
        return reel_dir / "reel"
    return reel_dir


def check(reel_dir, batch_dirs=(), standard=None) -> list[str]:
    """Fallas del reel contra las reglas; vacía = se puede armar."""
    reel = resolve_reel_dir(reel_dir).resolve()
    errors = []
    try:
        std = standard if isinstance(standard, dict) else load_standard(standard)
    except (ValueError, OSError) as exc:
        std, errors = None, [f"no se pudieron leer las reglas: {exc}"]
    view = None
    if std:
        try:
            view = normalize(reel)
        except (ValueError, KeyError, OSError, TypeError) as exc:
            errors.append(f"no se pudieron leer los datos del reel: {exc}")
    if view:
        errors += _hook(view["visuals"], view["title"], std)
        errors += _visuals(view["visuals"], reel, std["visuals"])
        errors += _repeats(view["visuals"], batch_dirs, std["visuals"])
        errors += _cards(view, std)
        errors += _sequence(view, std)
        errors += _audio(view, std, reel)
    if reel.is_dir():
        (reel / RESULT).write_text(json.dumps({
            "ok": not errors, "errors": errors, "checked_at": time.time(),
            "standard_version": (std or {}).get("version"),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return errors


def report(errors, reel_dir) -> None:
    if errors:
        print(f"CONTROL DEL REEL — NO se arma {reel_dir}:")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"CONTROL DEL REEL OK: {reel_dir}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reel_dir", type=Path)
    ap.add_argument("--standard", type=Path)
    ap.add_argument("--batch", type=Path, nargs="*", default=[], help="otros reels del lote (control de repetición)")
    args = ap.parse_args(argv)
    errors = check(args.reel_dir, args.batch, args.standard)
    report(errors, args.reel_dir)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
