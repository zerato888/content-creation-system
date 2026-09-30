#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""PreToolUse (terminal): sin ficha de marca no hay pieza creativa.

Frena (exit 2 + motivo en stderr) los comandos que generan una pieza con el kit
(`launch.py carousel|reel|logo`) si no existe ninguna ficha en `.kit-personal/brands/*.json`.
Si además `grounding_track` está activo (Claude Code), exige haber leído una ficha en los últimos
45 minutos: no se genera "de memoria". En Codex ese aviso no ve las lecturas, así que ahí solo
cuenta la existencia de la ficha. Salida de emergencia: variable KIT_NO_GATE=1.
"""
from __future__ import annotations
import os
import re
import sys
import time

from _common import ROOT, event, run

CREATIVE = re.compile(r"launch\.py[\"']?\s+(carousel|reel|logo)\b")
WINDOW = 45 * 60
STATE = ROOT / ".kit-personal" / ".state"


def verdict(cmd: str, now=None) -> str:
    """'' = allowed, else the reason."""
    if os.environ.get("KIT_NO_GATE") == "1" or not CREATIVE.search(cmd):
        return ""
    if not list((ROOT / ".kit-personal" / "brands").glob("*.json")):
        return ("Bloqueado por el kit: no hay ficha de marca. Corré primero la skill `brand-onboarding` "
                "(o el onboarding) para crear `.kit-personal/brands/<nombre>.json`; sin ficha no se genera la pieza.")
    if (STATE / "tracking").is_file():
        try:
            age = (now or time.time()) - float((STATE / "grounded").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            age = WINDOW + 1
        if age > WINDOW:
            return ("Bloqueado por el kit: leé la ficha de la marca (`.kit-personal/brands/<nombre>.json`) "
                    "antes de generar. Si es trabajo de un rol, delegalo al rol creativo que la carga.")
    return ""


def main():
    tool = event().get("tool_input")
    cmd = tool.get("command") if isinstance(tool, dict) else None
    if isinstance(cmd, list):
        cmd = " ".join(map(str, cmd))
    if isinstance(cmd, str):
        why = verdict(cmd)
        if why:
            print(why, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    run(main)
