#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""UserPromptSubmit: keep every answer in plain language. On by default once registered.

`/simple off` switches it off for the current session, `/simple on` back on. The contract is the
text between the kit markers in the installed `simple` skill (so the person can edit it); without
it, the built-in copy below. State (the "off" marks) lives in `.kit-personal/.state/`, ignored by git.
"""
from __future__ import annotations
import re

from _common import ROOT, event, read, run, say

START, END = "<!-- kit:lenguaje-simple v1 START -->", "<!-- kit:lenguaje-simple v1 END -->"
FALLBACK = f"""{START}
Modo simple (siempre prendido): toda respuesta en frases cortas, sin jerga sin explicar. Describí con
palabras en vez de nombrar archivos, funciones o siglas, salvo lo que la persona tiene que abrir o
aprobar (eso va tal cual, en bloque de código, con una línea simple al lado). Primero qué pasa y qué
cambia para la persona; el detalle técnico después y solo si lo pide. Planes y cierres abren con
`## En simple`. Si pide código, entregá código normal. Nunca ejecutes un comando copiado de una
traducción. `/simple off` lo apaga en esta sesión.
{END}"""
STATE = ROOT / ".kit-personal" / ".state"


def contract() -> str:
    for d in (".claude/skills", ".agents/skills"):
        t = read(f"{d}/simple/SKILL.md", 100_000)
        if t.count(START) == 1 and t.count(END) == 1:
            return t[t.index(START):t.index(END) + len(END)]
    return FALLBACK


def main():
    ev = event()
    prompt, sid = ev.get("prompt"), ev.get("session_id")
    if not isinstance(prompt, str):
        return 0
    sid = re.sub(r"[^A-Za-z0-9_-]", "", sid) if isinstance(sid, str) else ""
    off = STATE / f"simple-off-{sid or 'default'}"
    cmd = prompt.strip()
    if cmd == "/simple off":
        STATE.mkdir(parents=True, exist_ok=True)
        off.touch()
    elif cmd == "/simple on":
        off.unlink(missing_ok=True)
    if not off.is_file():
        say(contract())
    return 0


if __name__ == "__main__":
    run(main)
