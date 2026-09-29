#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""PreToolUse (terminal): en corridas desatendidas (KIT_HEADLESS=1) frena `open` / `start` / `xdg-open`,
que abren ventanas que nadie va a cerrar. Sin esa variable no hace nada."""
import os
import re
import sys

from _common import event, run

OPEN = re.compile(r"(^|[;&|(]\s*)(open|xdg-open|start|explorer(\.exe)?)(\s|$)", re.I)


def main():
    if os.environ.get("KIT_HEADLESS") != "1":
        return 0
    tool = event().get("tool_input")
    cmd = tool.get("command") if isinstance(tool, dict) else None
    if isinstance(cmd, list):
        cmd = " ".join(map(str, cmd))
    if isinstance(cmd, str) and OPEN.search(cmd):
        print("Bloqueado por el kit: esta corrida es desatendida (KIT_HEADLESS=1), nadie mira la pantalla. "
              "No abras archivos ni carpetas; avisá por el canal de entrega o dejá el resultado en disco.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    run(main)
