#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""The kit's one launcher. Installed as TARGET/.kit/launch.py; stdlib only, macOS and Windows.

    python .kit/launch.py serve            # Command Center (prints a one-time link)
    python .kit/launch.py open --browser   # a fresh link for the one already running
    python .kit/launch.py onboard --answers - [--dry-run] [--reset]
    python .kit/launch.py captions ...     # engines/video/captions.py
    python .kit/launch.py transcribe ...   # engines/video/transcribe.py
    python .kit/launch.py models small     # download a pinned Whisper model (asks first)
    python .kit/launch.py carousel ... | task ... | lab ... | secrets ...

Whatever Python starts it, the command runs with the project's own environment
(.kit/venv, where the installer put faster-whisper, tzdata, ...). Without .kit/venv it
runs with the current Python and says so.
"""
import os
import runpy
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent  # TARGET/.kit (or the repo when run from source)
COMMANDS = {
    "serve": ("cc/server/app.py", ["serve"]),
    "open": ("cc/server/app.py", ["open"]),
    "onboard": ("engines/onboard_write.py", []),
    "captions": ("engines/video/captions.py", []),
    "transcribe": ("engines/video/transcribe.py", []),
    "models": ("engines/video/transcribe.py", ["download-model"]),
    "carousel": ("engines/carousel/carousel.py", []),
    "task": ("cc/server/tasks.py", []),
    "lab": ("cc/server/lab.py", []),
    "secrets": ("engines/kit_secrets.py", []),
}


def venv_dir() -> Path:
    v = KIT / "venv"
    if (KIT / "venv").is_symlink():
        raise SystemExit("launch: .kit/venv es un enlace simbólico; no lo uso. Reinstalá las dependencias.")
    return v


def venv_python() -> Path | None:
    p = venv_dir() / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return p if p.is_file() else None


def in_venv() -> bool:
    try:
        return Path(sys.prefix).resolve() == venv_dir().resolve()
    except OSError:
        return False


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(__doc__.strip(), file=sys.stderr)
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    cmd, rest = argv[0], argv[1:]
    script, pre = COMMANDS[cmd]
    if cmd == "onboard" and "--project" not in rest:
        rest = [*rest, "--project", str(KIT.parent)]  # works from any subfolder of the project
    vpy = venv_python()
    if vpy and not in_venv():
        args = [str(vpy), str(Path(__file__).resolve()), *argv[:1], *rest]
        if os.name == "nt":
            return subprocess.call(args)
        os.execv(str(vpy), args)  # same process: signals (service stop, Ctrl+C) reach the server
    if not vpy:
        print("launch: no hay .kit/venv (dependencias sin instalar); uso este Python.", file=sys.stderr)
    path = KIT / script
    if not path.is_file():
        print(f"launch: falta .kit/{script}; reinstalá el kit.", file=sys.stderr)
        return 2
    sys.argv = [str(path), *pre, *rest]
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
