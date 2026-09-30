#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""PreToolUse (ExitPlanMode, solo Claude Code): avisa si el plan no abre con `## En simple` o si esa
sección trae jerga. Avisa, nunca bloquea (siempre sale 0). Solo juzga la apertura; el detalle técnico
de abajo queda libre. Lee el plan más nuevo de ~/.claude/plans (si tiene menos de una hora)."""
from __future__ import annotations
import re
import sys
import time
from pathlib import Path

from _common import event, run

HEADING = "## En simple"
JERGA = re.compile(
    r"\b(idempotente|at[oó]mic\w+|preflight|sandbox|payload|runner|span|symlink|hook|schema|"
    r"concurrencia|migraci[oó]n|refactor|wrapper|stub|mock|pathspec|worktree|stdout|stderr|"
    r"exit code|regex|parse\w*|commit|merge|endpoint|deploy|middleware)\b", re.I)
SNAKE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
CALL = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\(\)")
PATHY = re.compile(r"(?:^|\s)[~/.]?[\w.-]+/[\w./-]+")


def newest_plan(now=None):
    d = Path.home() / ".claude" / "plans"
    plans = [p for p in d.glob("*.md") if p.is_file()] if d.is_dir() else []
    if not plans:
        return None
    p = max(plans, key=lambda x: x.stat().st_mtime)
    return p if (now or time.time()) - p.stat().st_mtime <= 3600 else None


def opening(text: str):
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower() == HEADING.lower():
            body = []
            for nxt in lines[i + 1:]:
                if nxt.startswith("## "):
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


def offences(section: str) -> list:
    prose, fence = [], False
    for ln in section.splitlines():
        if ln.lstrip().startswith("```"):
            fence = not fence
        elif not fence:
            prose.append(ln)
    prose = "\n".join(prose)
    out = []
    for label, rx in (("jerga", JERGA), ("nombres internos", SNAKE), ("funciones()", CALL), ("rutas", PATHY)):
        hits = sorted({m.group(0).strip() for m in rx.finditer(prose)})
        if hits:
            out.append(f"{label}: {', '.join(hits[:5])}")
    return out


def check(text: str) -> str:
    """Empty string if the plan is fine, else the warning."""
    sec = opening(text)
    if sec is None:
        return (f"PLAN_SIN_LENGUAJE_SIMPLE: el plan no abre con «{HEADING}». Agregá esa sección antes de "
                "mostrarlo: 3-6 líneas con qué vamos a hacer, quién lo hace y qué pasa si sale mal. "
                "El detalle técnico sigue abajo, intacto.")
    bad = offences(sec)
    return ("PLAN_JERGA_EN_LA_APERTURA: la sección «En simple» todavía trae " + " · ".join(bad) +
            ". Reescribila sin eso; los nombres y rutas van abajo.") if bad else ""


def main():
    if event().get("tool_name") != "ExitPlanMode":
        return 0
    plan = newest_plan()
    if plan is None:
        return 0
    msg = check(plan.read_text(encoding="utf-8"))
    if msg:
        print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    run(main)
