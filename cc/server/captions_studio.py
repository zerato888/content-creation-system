# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Caption Studio (module `subtitulos`): calibrate word-by-word captions on your own video.

A thin layer over the kit engine (engines/video/captions.py + transcribe.py): the studio
never groups, styles or renders on its own, so what the preview shows is what the engine
renders. Presets are the engine's own nested format (presets/captions, OFL fonts only),
including hooks forced into N balanced lines (layout.line_count, 2 or 3).

Folder: TARGET/.kit-personal/data/captions/
  <video>                      your clips (copy them here; .mp4 .mov .m4v .webm .mp3 .wav .m4a)
  <video>.captions.json        the editable transcript (engine format flat_words_v1)
  presets/<name>.json          presets you saved (the kit's presets are never overwritten)
  out/                         exports: .srt, burned-in .mp4, ProRes 4444 alpha .mov
Every name is a basename checked against a pattern; every path is confined to that folder.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

MEDIA_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mp3", ".wav", ".m4a"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,150}$")
PRESET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
FORMATS = {"srt": ".srt", "video": ".mp4", "alpha": ".mov"}
MAX_WORDS, MAX_WORD_LEN, MAX_ANNOTATED, MAX_PRESET = 20000, 80, 50_000, 64 * 1024
_RENDER = threading.Lock()
_ENGINES = {}


# ------------------------------------------------------------------ engine
def engine(kit):
    """engines/video/captions.py from the installed kit (or the repo when run from source)."""
    for base in (Path(kit) / "engines", Path(__file__).resolve().parents[2] / "engines"):
        path = base / "video" / "captions.py"
        if path.is_file():
            break
    else:
        raise ValueError("falta el motor de subtítulos (.kit/engines/video/captions.py); reinstalá el kit")
    key = str(path.resolve())
    if key not in _ENGINES:
        spec = importlib.util.spec_from_file_location("kit_captions_engine", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _ENGINES[key] = module
    return _ENGINES[key]


def _engine_errors(eng):
    return (eng.ContractViolation, sys.modules["transcribe"].MediaRejected, OSError,
            subprocess.CalledProcessError)


# ------------------------------------------------------------------ paths
def studio_dir(data_root):
    d = Path(data_root) / "captions"
    if d.is_symlink():
        raise ValueError("la carpeta de subtítulos es un enlace simbólico; no la uso")
    return d


def _confined(folder, name, pattern=NAME_RE):
    name = os.path.basename(str(name or ""))
    if not pattern.fullmatch(name) or name.startswith("."):
        raise ValueError("nombre de archivo inválido")
    path = folder / name
    if path.is_symlink():
        raise ValueError("enlace simbólico: no se usa")
    root = os.path.realpath(folder)
    if os.path.commonpath((root, os.path.realpath(path))) != root:
        raise ValueError("ruta fuera de la carpeta de subtítulos")
    return path


def video_path(data_root, name):
    path = _confined(studio_dir(data_root), name)
    if path.suffix.lower() not in MEDIA_EXTS:
        raise ValueError("solo video o audio (.mp4 .mov .m4v .webm .mp3 .wav .m4a)")
    if not path.is_file():
        raise FileNotFoundError(name)
    return path


def output_path(data_root, name):
    path = _confined(studio_dir(data_root) / "out", name)
    if path.suffix.lower() not in FORMATS.values() or not path.is_file():
        raise FileNotFoundError(name)
    return path


def _transcript_path(video):
    return video.with_name(video.name + ".captions.json")


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


# ------------------------------------------------------------------ videos and transcripts
def list_videos(data_root):
    d = studio_dir(data_root)
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.iterdir()):
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in MEDIA_EXTS and NAME_RE.fullmatch(p.name):
            out.append({"file": p.name, "bytes": p.stat().st_size, "has_transcript": _transcript_path(p).is_file()})
    return out


def get_transcript(data_root, name):
    path = _transcript_path(video_path(data_root, name))
    try:
        art = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        raise ValueError("la transcripción no es JSON válido; borrala y transcribí de nuevo")
    return {"words": art.get("words", []), "video": art.get("video"), "lang": art.get("lang")}


def transcribe(kit, data_root, name, lang=None):
    video = video_path(data_root, name)
    eng = engine(kit)
    tr = sys.modules["transcribe"]
    if lang is not None and not re.fullmatch(r"[a-z]{2}", str(lang)):
        raise ValueError("idioma: dos letras, por ejemplo es")
    try:
        art = eng.transcribe(video, lang)
        art["video"] = eng.probe(video)
    except tr.BackendMissing as e:
        raise ValueError(str(e))
    except _engine_errors(eng) as e:
        raise ValueError(f"no pude transcribir: {e}")
    _write_json(_transcript_path(video), art)
    return get_transcript(data_root, name)


def save_words(data_root, name, words):
    """Edited words replace the transcript's words; everything else in the file is kept."""
    video = video_path(data_root, name)
    path = _transcript_path(video)
    try:
        art = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ValueError("primero transcribí el video")
    if not isinstance(words, list) or len(words) > MAX_WORDS:
        raise ValueError("words: lista de hasta 20000 palabras")
    clean = []
    for i, w in enumerate(words):
        ok = (isinstance(w, dict) and isinstance(w.get("text"), str) and len(w["text"]) <= MAX_WORD_LEN
              and all(isinstance(w.get(k), (int, float)) and not isinstance(w.get(k), bool) for k in ("start", "end"))
              and 0 <= w["start"] <= w["end"])
        if not ok:
            raise ValueError(f"words[{i}]: {{text, start, end}} con 0 <= start <= end")
        if w["text"].strip():
            clean.append({"text": w["text"].strip(), "start": round(float(w["start"]), 3),
                          "end": round(float(w["end"]), 3)})
    art["words"] = clean
    _write_json(path, art)
    return get_transcript(data_root, name)


# ------------------------------------------------------------------ presets
def _kit_presets_dir(eng):
    return Path(eng.PRESETS_DIR) / "presets"


def _mine_dir(data_root):
    return studio_dir(data_root) / "presets"


def list_presets(kit, data_root):
    eng = engine(kit)
    out, seen = [], set()
    for source, folder in (("kit", _kit_presets_dir(eng)), ("mine", _mine_dir(data_root))):
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.json")):
            if p.is_symlink() or p.stem in seen or not PRESET_RE.fullmatch(p.stem):
                continue
            try:
                data = eng.load_preset(p)
            except eng.ContractViolation:
                continue
            seen.add(p.stem)
            out.append({"id": p.stem, "kind": data["kind"], "source": source, "data": data})
    return {"presets": out, "font_slots": eng.load_font_map().get("slots", {})}


def _check_preset(eng, data):
    if not isinstance(data, dict) or len(json.dumps(data)) > MAX_PRESET:
        raise ValueError("preset inválido")
    missing = eng.PRESET_REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"al preset le faltan: {sorted(missing)}")
    if data["kind"] not in ("hook", "base"):
        raise ValueError("kind: hook o base")
    lc = data["layout"].get("line_count") if isinstance(data["layout"], dict) else None
    if lc is not None and lc not in (2, 3):
        raise ValueError("layout.line_count: 2 o 3")
    slots = eng.load_font_map().get("slots", {})
    for token in (data["typography_tokens"] or {}).values():
        if not isinstance(token, dict) or token.get("font_slot") not in slots:
            raise ValueError("cada estilo usa un casillero de fuente del kit (fuentes libres OFL)")
    return data


def _preset(eng, data_root, value, kind):
    """A preset by id (kit or yours) or an edited preset object from the studio."""
    if isinstance(value, dict):
        data = _check_preset(eng, value)
    else:
        name = str(value or "")
        if not PRESET_RE.fullmatch(name):
            raise ValueError(f"preset {kind} inválido")
        mine = _mine_dir(data_root) / f"{name}.json"
        path = mine if mine.is_file() and not mine.is_symlink() else _kit_presets_dir(eng) / f"{name}.json"
        try:
            data = eng.load_preset(path)
        except eng.ContractViolation as e:
            raise ValueError(str(e))
    if data["kind"] != kind:
        raise ValueError(f"ese preset es de tipo {data['kind']}, se esperaba {kind}")
    return data


def save_preset(kit, data_root, name, preset):
    eng = engine(kit)
    name = str(name or "")
    if not PRESET_RE.fullmatch(name):
        raise ValueError("nombre: minúsculas, números y guiones")
    if (_kit_presets_dir(eng) / f"{name}.json").is_file():
        raise ValueError("ese nombre es de un preset del kit; elegí otro")
    data = {**_check_preset(eng, preset), "name": name}
    path = _confined(_mine_dir(data_root), f"{name}.json")
    _write_json(path, data)
    return {"id": name, "kind": data["kind"]}


# ------------------------------------------------------------------ build / preview / render
def _build(kit, data_root, body):
    eng = engine(kit)
    video = video_path(data_root, body.get("file"))
    tr = get_transcript(data_root, video.name)
    if not tr or not tr["words"]:
        raise ValueError("primero transcribí el video")
    presets = {"base": _preset(eng, data_root, body.get("base_preset"), "base")}
    presets["hook"] = (_preset(eng, data_root, body["hook_preset"], "hook") if body.get("hook_preset")
                       else presets["base"])
    annotated = body.get("annotated_text")
    if annotated is not None and (not isinstance(annotated, str) or len(annotated) > MAX_ANNOTATED):
        raise ValueError("texto anotado inválido")
    mv = body.get("margin_v_frac")
    if not isinstance(mv, (int, float)) or isinstance(mv, bool) or not 0 < mv < 1:
        raise ValueError("margin_v_frac (altura de los subtítulos) va entre 0 y 1")
    try:
        words = eng.drop_muletillas(tr["words"])
        tagged = eng.align_annotated_text(annotated, words) if annotated else eng.tag_plain(words)
        blocks = eng.group_for_render(tagged, presets)
    except eng.ContractViolation as e:
        raise ValueError(str(e))
    return eng, video, tr, presets, blocks, float(mv)


def _line_style(eng, font_map, preset, line, li, n_lines):
    layout = preset["layout"]
    mults = layout.get("line_size_mult")
    mult = (mults[min(li, len(mults) - 1)] if mults else
            layout.get("first_line_size_mult", 1.0) if li == 0 else 1.0)
    forced = preset["kind"] == "hook" and layout.get("line_count") and "emphasized" in preset["typography_tokens"]
    role = "emphasized" if forced and li in (0, n_lines - 1) else None
    words = []
    for w in line:
        st = eng.resolve_word_style(w, preset, font_map, line_font_role=role)
        words.append({"t": w["t"], "s": w["s"], "e": w["e"], "font": st["font"], "size_frac": st["size_frac"] * mult,
                      "case": st.get("case", "keep"), "italic": bool(st.get("italic")),
                      "bold": st.get("weight") == "bold"})
    sp = layout.get("line_spacing_mult")
    spacing = sp[min(li, len(sp) - 1)] if isinstance(sp, list) and sp else (sp or 1.0)
    return {"words": words, "spacing": spacing}


def preview(kit, data_root, body):
    """The engine's own grouping and styles, as data the page paints over the video."""
    eng, _, tr, presets, blocks, mv = _build(kit, data_root, body)
    font_map = eng.load_font_map()
    out = []
    try:
        for bi, b in enumerate(blocks):
            flat = [w for ln in b["lines"] for w in ln]
            if not flat:
                continue
            preset = presets[flat[0]["segment_type"]]
            end = flat[-1]["e"] + 0.25
            if bi + 1 < len(blocks) and blocks[bi + 1]["lines"]:
                end = min(end, blocks[bi + 1]["lines"][0][0]["s"])
            out.append({"start": flat[0]["s"], "end": end, "kind": preset["kind"],
                        "alignment": preset["layout"].get("alignment", "left"),
                        "lines": [_line_style(eng, font_map, preset, ln, li, len(b["lines"]))
                                  for li, ln in enumerate(b["lines"])]})
    except eng.ContractViolation as e:
        raise ValueError(str(e))
    return {"blocks": out, "margin_v_frac": mv, "video": tr.get("video")}


def _srt_time(t):
    ms = round(max(t, 0) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def to_srt(blocks):
    cues = []
    for bi, b in enumerate(blocks):
        flat = [w for ln in b["lines"] for w in ln]
        if not flat:
            continue
        end = flat[-1]["e"] + 0.25
        if bi + 1 < len(blocks) and blocks[bi + 1]["lines"]:
            end = min(end, blocks[bi + 1]["lines"][0][0]["s"])
        text = "\n".join(" ".join(w["t"] for w in ln) for ln in b["lines"])
        cues.append(f"{len(cues) + 1}\n{_srt_time(flat[0]['s'])} --> {_srt_time(max(end, flat[0]['s'] + 0.05))}\n{text}\n")
    return "\n".join(cues)


def burn_argv(eng, ffmpeg, video, ass_path, fonts_dir, out):
    """Captions burned into a copy of the video (H.264), audio copied untouched."""
    vf = f"subtitles=filename={eng.filter_path(ass_path)}:fontsdir={eng.filter_path(fonts_dir)}"
    return [ffmpeg, "-nostdin", "-y", "-v", "error", *eng.PROTOCOL_WHITELIST, "-i", str(video), "-vf", vf,
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "copy", "-movflags", "+faststart", str(out)]


def render(kit, data_root, body):
    fmt = body.get("format")
    if fmt == "preview":
        return preview(kit, data_root, body)
    if fmt not in FORMATS:
        raise ValueError("format: srt, video o alpha")
    if not _RENDER.acquire(blocking=False):
        raise RuntimeError("ya hay una exportación en curso; esperá a que termine")
    try:
        eng, video, tr, presets, blocks, mv = _build(kit, data_root, body)
        out_dir = studio_dir(data_root) / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = _confined(out_dir, Path(video.name).stem + ".captions" + FORMATS[fmt])
        if fmt == "srt":
            out.write_text(to_srt(blocks), encoding="utf-8", newline="\n")  # same bytes on every OS
            return {"file": out.name, "format": fmt}
        meta = tr.get("video") or eng.probe(video)
        font_map = eng.load_font_map()
        resolved = eng.resolve_fonts(eng.used_families(presets, font_map), font_map)
        ass = eng.build_ass_from_preset({"video": meta, "blocks": blocks}, presets, font_map, mv,
                                        font_names={fam: n for fam, (n, _) in resolved.items()},
                                        font_files={n: f for n, f in resolved.values()})
        ff = eng.ffmpeg_with_libass()
        with tempfile.TemporaryDirectory() as td:
            ass_path = Path(td) / "captions.ass"
            ass_path.write_text(ass, encoding="utf-8", newline="\n")
            fonts_dir = eng.prepare_fonts_dir(resolved, td)
            argv = (burn_argv(eng, ff, video, ass_path, fonts_dir, out) if fmt == "video" else
                    eng.render_argv(ff, ass_path, fonts_dir, out, width=meta["w"], height=meta["h"],
                                    fps=meta["fps"], duration=meta["dur"]))
            subprocess.run(argv, check=True, env=eng.render_env(td, fonts_dir), capture_output=True, timeout=3600)
        return {"file": out.name, "format": fmt}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise ValueError("ffmpeg no pudo exportar (ver que el video abra bien y que ffmpeg tenga libass)")
    except RuntimeError as e:  # the engine's ContractViolation (missing font, no libass, ...)
        raise ValueError(str(e))
    finally:
        _RENDER.release()
