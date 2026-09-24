# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Local Whisper transcription with word timestamps -> flat_words_v1.

Backend chain (first one available wins):
  faster-whisper -> openai-whisper -> mlx-whisper (only if already importable)
  -> whisper.cpp CLI (`whisper-cli` / `whisper-cpp` / `main` on PATH).
Models live in the shared kit cache (kit_platform.whisper_model_dir()) and are ONLY the
pinned artifacts of models.lock.json (repo + revision + SHA-256 per file), downloaded with
consent (`python .kit/launch.py models small`, which says the size and the folder first).
Backends get a local path, never a model name they could download on their own; a model
that is not downloaded yet is a clear error, not a surprise download. Default model is
`small`; larger models need an explicit allow_large / --allow-large-model.

Media input is always decoded by our own ffmpeg call (argv list,
`-protocol_whitelist file,pipe`) into a temp 16 kHz WAV; backends only ever see
that WAV. Playlists, concat lists and URLs are rejected before anything runs.

Public API: transcribe_words(media_path, lang=None) -> [{"text","start","end"}].
CLI:  python engines/video/transcribe.py MEDIA [OUT.json] [--lang es] [--model small]
      python engines/video/transcribe.py download-model small [--backend faster-whisper] [--yes]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kit_platform  # noqa: E402

SCHEMA = "flat_words_v1"
MODELS_LOCK = Path(__file__).resolve().parent / "models.lock.json"
DOWNLOADABLE = ("faster-whisper", "whisper.cpp")
SMALL_MODELS = {"tiny", "tiny.en", "base", "base.en", "small", "small.en"}
PROTOCOL_WHITELIST = ["-protocol_whitelist", "file,pipe"]
WHISPER_CPP_BINARIES = ("whisper-cli", "whisper-cpp", "main")
PUNCT_RE = re.compile(r"[.,;:!?¿¡…\"“”«»()\[\]]")
_BLOCKED_SUFFIXES = {".m3u8", ".m3u", ".ffconcat", ".concat", ".pls"}
_BLOCKED_HEADERS = (b"#EXTM3U", b"ffconcat", b"[playlist]")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]+:")  # 2+ chars: never a drive letter


class MediaRejected(ValueError):
    """Input is not a plain local media file."""


class BackendMissing(RuntimeError):
    """A transcription backend is not installed or not usable."""


def check_media_input(path) -> Path:
    """Refuse URLs, protocol prefixes (concat:, http:, ...), playlists and
    concat lists. Returns the resolved local file path."""
    raw = str(path)
    if "://" in raw or _SCHEME_RE.match(raw):
        raise MediaRejected(f"solo archivos locales, no URLs ni protocolos: {raw!r}")
    p = Path(raw)
    if p.suffix.lower() in _BLOCKED_SUFFIXES:
        raise MediaRejected(f"listas de reproducción/concat no permitidas: {p.name}")
    if not p.is_file():
        raise MediaRejected(f"no existe o no es un archivo: {raw!r}")
    with p.open("rb") as fh:
        head = fh.read(64).lstrip(b"\xef\xbb\xbf \t\r\n")
    if any(head.startswith(h) for h in _BLOCKED_HEADERS):
        raise MediaRejected(f"el archivo es una playlist/concat, no un medio: {p.name}")
    return p.resolve()


def ffmpeg_decode_argv(src: Path, wav: Path) -> list[str]:
    # ponytail: `-f wav` pinned on output; input demuxer is auto-probed but the
    # protocol whitelist + header check above keep it on the local file only.
    return [kit_platform.ffmpeg(), "-nostdin", "-y", "-v", "error", *PROTOCOL_WHITELIST,
            "-i", str(src), "-vn", "-ar", "16000", "-ac", "1", "-f", "wav", str(wav)]


def ffprobe_argv(src: Path) -> list[str]:
    return [kit_platform.ffprobe(), "-v", "quiet", *PROTOCOL_WHITELIST, "-print_format", "json",
            "-show_streams", "-show_format", str(src)]


def probe(media) -> dict:
    """{w,h,fps,dur}; audio-only sources get a 1080x1920 @30 canvas."""
    src = check_media_input(media)
    info = json.loads(subprocess.run(ffprobe_argv(src), capture_output=True, text=True, encoding="utf-8", errors="replace",
                                     check=True).stdout)
    dur = float(info["format"]["duration"])
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if v:
        num, den = (int(x) for x in v["r_frame_rate"].split("/"))
        return {"w": int(v["width"]), "h": int(v["height"]), "fps": round(num / den, 3), "dur": dur}
    return {"w": 1080, "h": 1920, "fps": 30.0, "dur": dur}


def resolve_model(model: str | None, allow_large: bool = False) -> str:
    name = model or os.environ.get("KIT_WHISPER_MODEL") or "small"
    if name not in SMALL_MODELS and not allow_large:
        raise BackendMissing(f"el modelo {name!r} es más grande que 'small'; pasá "
                             "--allow-large-model para descargarlo/usarlo a propósito")
    return name


# --- pinned models ------------------------------------------------------------------

def pinned(backend: str, model: str) -> dict:
    try:
        lock = json.loads(MODELS_LOCK.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        lock = {}
    entry = lock.get(backend, {}).get(model)
    if not entry:
        raise BackendMissing(f"{backend}: el kit no tiene una versión fijada del modelo {model!r} "
                             f"(fijados: {', '.join(lock.get(backend, {})) or 'ninguno'})")
    return entry


def model_dir(backend: str, model: str) -> Path:
    entry = pinned(backend, model)
    return kit_platform.whisper_model_dir() / backend / f"{model}-{entry['revision'][:12]}"


def _mb(entry: dict) -> int:
    return round(sum(f["size"] for f in entry["files"]) / 2**20)


def local_model(backend: str, model: str) -> Path:
    """Folder (faster-whisper) or file (whisper.cpp) of a downloaded pinned model; BackendMissing if absent."""
    entry, d = pinned(backend, model), model_dir(backend, model)
    missing = [f["name"] for f in entry["files"]
               if not (d / f["name"]).is_file() or (d / f["name"]).stat().st_size != f["size"]]
    if missing:
        raise BackendMissing(f"{backend} sin modelo: falta {', '.join(missing)} en la caché compartida. "
                             f"Descargalo una vez (~{_mb(entry)} MB, con tu permiso): "
                             f"python .kit/launch.py models {model} --backend {backend}")
    return d if backend == "faster-whisper" else d / entry["files"][0]["name"]


def download_model(model: str, backend: str, confirm, opener=None) -> Path | None:
    """Consented download of the pinned artifacts, each verified by SHA-256. None if declined."""
    entry, d = pinned(backend, model), model_dir(backend, model)
    todo = [f for f in entry["files"] if not (d / f["name"]).is_file() or (d / f["name"]).stat().st_size != f["size"]]
    if todo:
        mb = round(sum(f["size"] for f in todo) / 2**20)
        if not confirm(f"Descargar el modelo {model} para {backend} (~{mb} MB, {entry['repo']} @ "
                       f"{entry['revision'][:12]}) a {d}? Se reutiliza entre proyectos."):
            return None
        for f in todo:
            kit_platform.fetch_verified(f["url"], f["sha256"], f["size"], d / f["name"], opener)
    return local_model(backend, model)


# --- adapters -----------------------------------------------------------------

def adapt_flat_words(result) -> list[dict]:
    """{"segments":[{"text","start","end","words":[{"word","start","end"}]}]} -> flat words."""
    words = [{"text": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
             for seg in result["segments"] for w in (seg.get("words") or [])]
    if not words:
        words = [{"text": s["text"].strip(), "start": round(s["start"], 3), "end": round(s["end"], 3)}
                 for s in result["segments"]]
    return [w for w in words if w["text"]]


def adapt_whisper_cpp(result) -> list[dict]:
    """whisper.cpp `-ml 1 -oj` rows (offsets in ms) -> flat words."""
    words = []
    for row in result.get("transcription", []):
        text = row["text"].strip()
        if not text or text.startswith("[") or not PUNCT_RE.sub("", text).strip():
            continue
        words.append({"text": text, "start": round(row["offsets"]["from"] / 1000, 3),
                      "end": round(row["offsets"]["to"] / 1000, 3)})
    return words


# --- backends (each raises BackendMissing if unusable) ---------------------------

def _faster(wav, lang, model):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise BackendMissing("faster-whisper") from None
    path = local_model("faster-whisper", model)  # a local folder: WhisperModel never downloads
    segs, _ = WhisperModel(str(path), device="auto", compute_type="auto", local_files_only=True
                           ).transcribe(str(wav), language=lang, word_timestamps=True)
    return adapt_flat_words({"segments": [
        {"text": s.text, "start": s.start, "end": s.end,
         "words": [{"word": w.word, "start": w.start, "end": w.end} for w in (s.words or [])]}
        for s in segs]})


def _openai(wav, lang, model):
    try:
        import whisper
    except ImportError:
        raise BackendMissing("openai-whisper") from None
    # ponytail: no pinned openai-whisper checkpoints; add them to models.lock.json to enable this backend
    raise BackendMissing("openai-whisper: el kit no fija sus modelos (descargaría por su cuenta); "
                         "usá faster-whisper (ya viene en .kit/venv) o whisper.cpp")


def _mlx(wav, lang, model):
    try:
        import mlx_whisper
    except ImportError:
        raise BackendMissing("mlx-whisper") from None
    raise BackendMissing("mlx-whisper: el kit no fija sus modelos (descargaría por su cuenta); "
                         "usá faster-whisper (ya viene en .kit/venv) o whisper.cpp")


def whisper_cpp_binary() -> str | None:
    return next((b for b in map(shutil.which, WHISPER_CPP_BINARIES) if b), None)


def whisper_cpp_argv(binary, model_file, wav, out_base, lang=None) -> list[str]:
    argv = [binary, "-m", str(model_file)]
    if lang:
        argv += ["-l", lang]
    return argv + ["-ml", "1", "-sow", "-oj", "-of", str(out_base), "-np", str(wav)]


def _cpp(wav, lang, model):
    binary = whisper_cpp_binary()
    if not binary:
        raise BackendMissing("whisper.cpp")
    model_file = local_model("whisper.cpp", model)
    out_base = Path(wav).with_name("tx")
    subprocess.run(whisper_cpp_argv(binary, model_file, wav, out_base, lang), check=True,
                   capture_output=True)
    return adapt_whisper_cpp(json.loads(out_base.with_suffix(".json").read_text(encoding="utf-8")))


BACKENDS = [("faster-whisper", _faster), ("openai-whisper", _openai),
            ("mlx-whisper", _mlx), ("whisper.cpp", _cpp)]


def run_backends(wav, lang, model):
    """Try each backend in order; returns (backend_name, words)."""
    missing = []
    for name, fn in BACKENDS:
        try:
            return name, fn(wav, lang, model)
        except BackendMissing as exc:
            missing.append(str(exc))
    raise BackendMissing("ningún backend de Whisper disponible (" + "; ".join(missing) +
                         "). Instalá faster-whisper en .kit/venv o whisper.cpp en el PATH.")


def transcribe(media_path, lang=None, model=None, allow_large=False) -> dict:
    """Full artifact: {"schema","backend","model","lang","words"}."""
    src = check_media_input(media_path)
    model = resolve_model(model, allow_large)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        subprocess.run(ffmpeg_decode_argv(src, wav), check=True)
        backend, words = run_backends(wav, lang, model)
    return {"schema": SCHEMA, "backend": backend, "model": model, "lang": lang, "words": words}


def transcribe_words(media_path, lang=None) -> list[dict]:
    """The Lab worker contract: flat [{"text","start","end"}]."""
    return transcribe(media_path, lang)["words"]


# --- shared helpers used by captions.py -----------------------------------------

def norm_word(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", text)


def group_blocks(words, max_words_per_line=4, pause_break=0.6):
    """[{t,s,e}] -> blocks of up to 2 lines, breaking on pause / punctuation / length."""
    lines, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        end_line = len(cur) >= max_words_per_line or re.search(r"[.!?,;:]$", w["t"])
        if not end_line and i + 1 < len(words):
            end_line = words[i + 1]["s"] - w["e"] > pause_break
        if end_line:
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    blocks, i = [], 0
    while i < len(lines):
        pair = lines[i:i + 2]
        if len(pair) == 2 and pair[1][0]["s"] - pair[0][-1]["e"] > pause_break:
            pair = pair[:1]
        blocks.append({"lines": pair})
        i += len(pair)
    return blocks


def download_main(argv) -> int:
    ap = argparse.ArgumentParser(prog="download-model", description="Descarga fijada y con permiso de un modelo Whisper.")
    ap.add_argument("model", nargs="?", default=os.environ.get("KIT_WHISPER_MODEL") or "small")
    ap.add_argument("--backend", choices=DOWNLOADABLE, default=None,
                    help="por defecto: faster-whisper si está instalado, si no whisper.cpp")
    ap.add_argument("--yes", action="store_true", help="aceptar la descarga sin preguntar")
    a = ap.parse_args(argv)
    backend = a.backend
    if backend is None:
        try:
            import faster_whisper  # noqa: F401
            backend = "faster-whisper"
        except ImportError:
            backend = "whisper.cpp"

    def confirm(msg):
        if a.yes:
            return True
        if not sys.stdin.isatty():
            print(f"{msg} -> no (sin terminal; repetí con --yes)")
            return False
        return input(f"{msg} [s/N] ").strip().lower() in ("s", "si", "sí", "y", "yes")

    try:
        path = download_model(a.model, backend, confirm)
    except (BackendMissing, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if path is None:
        print("No descargué nada.")
        return 1
    print(f"Modelo listo: {path}")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["download-model"]:
        return download_main(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--lang", default=None, help="omitido = autodetección")
    ap.add_argument("--model", default=None, help="default: small (o KIT_WHISPER_MODEL)")
    ap.add_argument("--allow-large-model", action="store_true")
    args = ap.parse_args(argv)
    try:
        art = transcribe(args.media, args.lang, args.model, args.allow_large_model)
    except (MediaRejected, BackendMissing) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(art, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
