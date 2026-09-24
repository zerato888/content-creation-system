#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""SessionStart after a context compaction (Claude Code, matcher "compact"): remind the model
where the working state lives, so it re-reads instead of guessing."""
from _common import ROOT, run, say


def main():
    lines = ["Recordatorio del kit: el contexto se compactó. Antes de seguir, releé:"]
    if (ROOT / ".kit-personal/hot.md").is_file():
        lines.append("- .kit-personal/hot.md (en qué estamos y qué sigue)")
    cps = ROOT / ".kit-personal/checkpoints"
    current = sorted(cps.glob("*/CURRENT.md"), key=lambda p: p.stat().st_mtime, reverse=True) if cps.is_dir() else []
    if current:
        lines.append(f"- .kit-personal/checkpoints/{current[0].parent.name}/CURRENT.md (último punto de control)")
    lines.append("- el plan aprobado de la tarea en curso, si lo había. No rehagas lo que ya está hecho.")
    say("\n".join(lines))


if __name__ == "__main__":
    run(main)
