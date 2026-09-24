# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Cross-platform helpers for the kit (macOS + Windows). Stdlib only.

One place for: kit root, Lab data dir, shared heavy-cache dir, ffmpeg/ffprobe
discovery, font discovery (kit fonts first), a generated fontconfig file for
libass, reveal-in-file-manager, and Whisper word-timestamp transcription.

Env overrides:
  KIT_ROOT        kit root (default: parent of engines/; `.kit/` when installed)
  KIT_DATA        Lab/project data dir (default: <kit>/data)
  KIT_CACHE       shared heavy cache (default: ~/.cache/content-kit or
                  %LOCALAPPDATA%\\content-kit) -- Playwright browsers, whisper models
  KIT_FFMPEG / KIT_FFPROBE   binaries
  KIT_FONTS_DIR   fonts folder (default: <kit>/fonts)
  KIT_WHISPER_MODEL          model size (default: small)
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

IS_MAC = sys.platform == "darwin"
IS_WIN = os.name == "nt"

KIT_ROOT = Path(os.environ.get("KIT_ROOT") or Path(__file__).resolve().parent.parent)


def data_root() -> Path:
    return Path(os.environ.get("KIT_DATA") or KIT_ROOT / "data")


def cache_root() -> Path:
    """User-level shared cache for heavy, version-pinned downloads (never per project)."""
    if os.environ.get("KIT_CACHE"):
        return Path(os.environ["KIT_CACHE"])
    if IS_WIN and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "content-kit"
    return Path.home() / ".cache" / "content-kit"


def find_binary(name: str, env_vars=(), fallbacks=()) -> str | None:
    """env var -> PATH -> known install locations. None if nothing exists."""
    for var in env_vars:
        val = os.environ.get(var)
        if val and Path(val).exists():
            return val
    found = shutil.which(name)
    if found:
        return found
    for cand in fallbacks:
        if Path(cand).exists():
            return str(cand)
    return None


_BREW_DIRS = ("/opt/homebrew/bin", "/usr/local/bin")


def ffmpeg() -> str:
    return find_binary("ffmpeg", ("KIT_FFMPEG",), [f"{d}/ffmpeg" for d in _BREW_DIRS]) or "ffmpeg"


def ffprobe() -> str:
    return find_binary("ffprobe", ("KIT_FFPROBE",), [f"{d}/ffprobe" for d in _BREW_DIRS]) or "ffprobe"


def kit_fonts_dir() -> Path:
    return Path(os.environ.get("KIT_FONTS_DIR") or KIT_ROOT / "fonts")


def font_dirs() -> list[Path]:
    dirs = [kit_fonts_dir()]
    if IS_WIN:
        dirs.append(Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts")
        if os.environ.get("LOCALAPPDATA"):
            dirs.append(Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts")
    else:
        dirs += [Path.home() / "Library/Fonts", Path("/Library/Fonts"),
                 Path("/System/Library/Fonts"), Path("/System/Library/Fonts/Supplemental"),
                 Path.home() / ".fonts", Path("/usr/share/fonts")]
    return [d for d in dirs if d.is_dir()]


def _norm(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())


def find_font_file(name: str) -> str | None:
    """Best-effort file lookup for a family/style name ('Inter', 'Inter Bold').
    ponytail: filename heuristic, not a font-name table; add fontTools name-table
    parsing if a font's file name does not resemble its family."""
    want = _norm(name.split(":")[0])
    if not want:
        return None
    files = [p for d in font_dirs() for p in d.rglob("*")
             if p.suffix.lower() in (".ttf", ".otf", ".ttc")]
    for p in files:
        if _norm(p.stem) in (want, want + "regular"):
            return str(p)
    prefixed = sorted((p for p in files if _norm(p.stem).startswith(want)), key=lambda p: len(p.stem))
    return str(prefixed[0]) if prefixed else None


def write_fontconfig(dest_dir: Path, fonts_dir: Path | None = None) -> Path:
    """Write a minimal fonts.conf pointing only at the kit font dir, so libass /
    fontconfig find kit fonts without a system install. Use with FONTCONFIG_FILE."""
    fonts_dir = Path(fonts_dir or kit_fonts_dir()).resolve()
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    from xml.sax.saxutils import escape
    conf = dest_dir / "fonts.conf"
    conf.write_text(
        '<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n<fontconfig>\n'
        f"  <dir>{escape(str(fonts_dir))}</dir>\n"
        f"  <cachedir>{escape(str((dest_dir / 'fc-cache').resolve()))}</cachedir>\n"
        "</fontconfig>\n", encoding="utf-8")
    return conf


def reveal(path) -> None:
    """Show a file in Finder/Explorer. No-op elsewhere."""
    path = str(path)
    if IS_MAC:
        subprocess.run(["open", "-R", path], check=False)
    elif IS_WIN:
        subprocess.run(["explorer", "/select,", path], check=False)


def open_path(path) -> None:
    path = str(path)
    if IS_MAC:
        subprocess.run(["open", path], check=False)
    elif IS_WIN:
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", path], check=False)


def whisper_model_dir() -> Path:
    return cache_root() / "whisper"


def fetch_verified(url: str, sha256: str, size: int, dest: Path, opener=None) -> Path:
    """HTTPS download into the shared cache, streamed and SHA-256-checked before it is kept.
    `dest` appears only complete and verified (temp file + rename); a mismatch is discarded."""
    import urllib.request
    if not url.startswith("https://"):
        raise ValueError(f"solo descargo por HTTPS: {url}")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if opener is None:
        import ssl
        try:
            import certifi  # the kit venv has it; some Pythons (python.org macOS) have no CA bundle
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
        opener = lambda u: urllib.request.urlopen(  # noqa: E731,S310 (https enforced above)
            urllib.request.Request(u, headers={"User-Agent": "content-kit"}), timeout=120, context=ctx)
    tmp = dest.with_name(f".{dest.name}.part")
    h, got = hashlib.sha256(), 0
    try:
        with opener(url) as r, open(tmp, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                got += len(chunk)
                if got > size:
                    raise ValueError(f"{dest.name}: más grande que lo fijado; descarga descartada")
                h.update(chunk)
                fh.write(chunk)
        if got != size or h.hexdigest() != sha256:
            raise ValueError(f"{dest.name}: el hash no coincide con el fijado; descarga descartada")
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest


def whisper_transcribe(audio, lang=None):
    """Word-timestamp Whisper, output shape
    {"segments": [{"text", "start", "end", "words": [{"word", "start", "end"}]}]}.
    Delegates to engines/video/transcribe.py: only pinned models already downloaded with consent
    (`python .kit/launch.py models small`), never an automatic download."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("kit_transcribe", Path(__file__).resolve().parent / "video" /
                                                  "transcribe.py")
    tx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tx)
    art = tx.transcribe(audio, lang)
    return {"segments": [{"text": w["text"], "start": w["start"], "end": w["end"],
                          "words": [{"word": w["text"], "start": w["start"], "end": w["end"]}]}
                         for w in art["words"]]}


if __name__ == "__main__":
    print("kit:", KIT_ROOT, "\ndata:", data_root(), "\ncache:", cache_root(),
          "\nffmpeg:", ffmpeg(), "\nffprobe:", ffprobe(), "\nfonts:", kit_fonts_dir())
