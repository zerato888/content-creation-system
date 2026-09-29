#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""PostToolUse (Read, solo Claude Code): anota cuándo se leyó la ficha de una marca
(`.kit-personal/brands/*.json`) o el perfil. `brand_gate` usa esa anotación. Nunca bloquea."""
import time
from pathlib import Path

from _common import ROOT, event, run

STATE = ROOT / ".kit-personal" / ".state"


def main():
    ti = event().get("tool_input") or {}
    fp = ti.get("file_path") or ti.get("path")
    if not isinstance(fp, str) or not fp:
        return 0
    p = Path(fp)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    base = (ROOT / ".kit-personal").resolve()
    if p == base / "profile.md" or (p.parent == base / "brands" and p.suffix == ".json"):
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / "tracking").write_text("on", encoding="utf-8")  # marks: this tool does report reads
        (STATE / "grounded").write_text(str(time.time()), encoding="utf-8")
    return 0


if __name__ == "__main__":
    run(main)
