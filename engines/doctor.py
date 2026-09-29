#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Revisión de salud del kit, en lenguaje simple: qué anda, qué falta y cómo arreglarlo.

    python .kit/launch.py doctor [--root DIR]

Revisa: Python 3.11 a 3.13, el entorno del proyecto (venv), ffmpeg con soporte de subtítulos
(libass; en Mac, ffmpeg-full), el navegador de Playwright, el modelo de Whisper, las fuentes,
las claves de servicios (solo dice si están, NUNCA las muestra) y las skills instaladas.
No cambia nada. Sale 1 si algo FALLA (los AVISOS no cuentan: son cosas opcionales).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_platform  # noqa: E402
import kit_secrets  # noqa: E402

OK, WARN, FAIL = "OK", "AVISO", "FALLA"
KIT = Path(__file__).resolve().parent.parent


def check_python(version=None):
    v = version or sys.version_info[:3]
    txt = ".".join(map(str, v))
    if (3, 11) <= tuple(v[:2]) <= (3, 13):
        return OK, f"Python {txt}", ""
    return FAIL, f"Python {txt} (el kit pide 3.11 a 3.13)", "Instalá Python 3.12 desde python.org y volvé a instalar el kit."


def check_venv(kit=KIT):
    p = kit / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if p.is_file():
        return OK, "entorno del proyecto (.kit/venv) listo", ""
    return WARN, "no hay .kit/venv (dependencias sin instalar)", "Volvé a correr el instalador del kit."


def check_ffmpeg(run=subprocess.run):
    exe = kit_platform.ffmpeg()
    try:
        r = run([exe, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return FAIL, "no encuentro ffmpeg", "Mac: `brew install ffmpeg-full`. Windows: `winget install Gyan.FFmpeg`."
    if r.returncode != 0:
        return FAIL, "ffmpeg no arranca", "Reinstalalo (Mac: `brew install ffmpeg-full`)."
    if any(ln.split()[1:2] == ["subtitles"] for ln in r.stdout.splitlines()):
        return OK, "ffmpeg con subtítulos (libass)", ""
    return (FAIL, "ffmpeg sin subtítulos (falta libass): no puede grabar captions en el video",
            "Mac: `brew install ffmpeg-full` (el común no trae libass). Windows: usá la versión 'full' de Gyan.FFmpeg.")


def check_playwright(cache=None):
    d = (cache or kit_platform.cache_root()) / "ms-playwright"
    if d.is_dir() and any(p.name.startswith("chromium") for p in d.iterdir()):
        return OK, "navegador de Playwright (Chromium) listo", ""
    return WARN, "falta el navegador de Playwright (lo usan carruseles y logos)", \
        "Corré: python -m playwright install chromium"


def check_whisper(cache=None):
    d = (cache or kit_platform.cache_root()) / "whisper"
    if d.is_dir() and (any(d.rglob("model.bin")) or any(d.rglob("ggml-*.bin"))):
        return OK, "modelo de Whisper descargado (transcripción)", ""
    return WARN, "falta el modelo de Whisper (transcripción y captions)", \
        "Descargalo una vez, con tu permiso: python .kit/launch.py models small"


def check_fonts(fonts_dir=None, lock=None):
    lock = lock or KIT / "presets/captions/fonts.lock.json"
    fdir = fonts_dir or kit_platform.kit_fonts_dir()
    try:
        files = [f["file"] for f in json.loads(lock.read_text(encoding="utf-8"))["fonts"]]
    except (OSError, ValueError, KeyError):
        return WARN, "no pude leer la lista de fuentes del kit", ""
    missing = [f for f in files if not (fdir / f).is_file()]
    if not missing:
        return OK, f"{len(files)} fuentes del kit instaladas", ""
    return WARN, f"faltan {len(missing)} de {len(files)} fuentes del kit (los captions usarían otra letra)", \
        "Volvé a correr el instalador con permiso para descargar las fuentes."


def check_keys(services=None, lookup=kit_secrets.lookup):
    if services is None:
        try:
            from onboard_write import SERVICES as services
        except Exception:
            services = {}
    have = []
    for svc, name in services.items():
        try:
            if lookup(name)[0]:
                have.append(svc)
        except ValueError:
            pass
    if have:
        return OK, "claves presentes: " + ", ".join(sorted(have)) + " (no se muestran)", ""
    return WARN, "no hay ninguna clave de servicios guardada", \
        "Solo hace falta si usás un servicio pago: python .kit/launch.py secrets"


def check_skills(root, kit=KIT):
    names = set()
    for d in (".claude/skills", ".agents/skills"):
        b = root / d
        if b.is_dir():
            names |= {p.name for p in b.iterdir() if (p / "SKILL.md").is_file()}
    try:
        core = {s["name"] for s in json.loads((kit / "catalog.json").read_text(encoding="utf-8"))["skills"]
                if s.get("tier") == "core"}
    except (OSError, ValueError, KeyError):
        core = set()
    lack = sorted(core - names) if names or core else []
    if not names:
        return WARN, "no hay skills instaladas en este proyecto", "Corré el instalador del kit en tu proyecto."
    if lack:
        return WARN, f"{len(names)} skills instaladas; faltan del núcleo: {', '.join(lack[:6])}", \
            "Volvé a correr el instalador."
    return OK, f"{len(names)} skills instaladas", ""


def run_checks(root: Path):
    return [check_python(), check_venv(), check_ffmpeg(), check_playwright(), check_whisper(), check_fonts(),
            check_keys(), check_skills(root)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(KIT.parent), help="carpeta del proyecto")
    rows = run_checks(Path(ap.parse_args(argv).root))
    for st, msg, fix in rows:
        print(f"[{st}] {msg}" + (f"\n        -> {fix}" if fix else ""))
    bad = sum(r[0] == FAIL for r in rows)
    print("\nTodo lo esencial anda." if not bad else f"\nHay {bad} cosa(s) esencial(es) por arreglar (marcadas FALLA).")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
