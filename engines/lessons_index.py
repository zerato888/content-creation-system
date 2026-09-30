#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Índice de lecciones: `.kit-personal/lessons.md` -> `.kit-personal/lessons-index.json`.

    python3 .kit/launch.py lessons [--root DIR]

Cada lección es un encabezado (`## 2026-05-01 — título`, con o sin fecha) o un punto de lista; el
texto de abajo aporta la regla (`**Regla:** ...`) y las palabras clave. El aviso `knowledge_router`
lee ese índice para recordarte la lección justa cuando escribís un pedido parecido.
Correlo después de agregar una lección. Python estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

STOP = set("""para con los las del que una uno the and for este esta solo cada cuando porque como sobre
misma mismo veces hacer usar with this that from into your what have will should""".split())
HEAD = re.compile(r"^#{2,4}\s+(?:(\d{4}-\d{2}-\d{2}[a-z]?)\s*[—–-]\s*)?(\S.*)$")
BULLET = re.compile(r"^\s*[-*]\s+(\S.*)$")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def keywords(title: str, body: str) -> list:
    freq = {}
    for w in re.findall(r"[a-z0-9-]{4,}", f"{_norm(title)} {_norm(title)} {_norm(body)}"):
        if w not in STOP:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=lambda w: (-freq[w], w))[:12]


def build(text: str) -> dict:
    lines = text.splitlines()
    marks = []  # (line index, date, title, is_heading)
    for i, ln in enumerate(lines):
        m = HEAD.match(ln)
        if m:
            marks.append((i, m.group(1) or "", m.group(2).strip(), True))
    if not marks:  # a plain bullet list
        for i, ln in enumerate(lines):
            m = BULLET.match(ln)
            if m:
                marks.append((i, "", m.group(1).strip()[:200], False))
    out = []
    for n, (i, date, title, is_head) in enumerate(marks):
        end = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
        body = "\n".join(lines[i + 1:end]) if is_head else ""
        rule = re.search(r"\*\*Regla:?\*\*:?\s*(.+)", body)
        out.append({"date": date, "title": title, "line": i + 1,
                    "keywords": keywords(title, body), "regla": rule.group(1).strip()[:240] if rule else ""})
    return {"generated_at": datetime.now().isoformat(timespec="seconds"), "lessons": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="carpeta del proyecto (donde está .kit-personal)")
    root = Path(ap.parse_args(argv).root).resolve()
    src = root / ".kit-personal" / "lessons.md"
    if not src.is_file() or src.is_symlink():
        print("No hay .kit-personal/lessons.md todavía: nada que indexar.")
        return 0
    idx = build(src.read_text(encoding="utf-8", errors="replace"))
    dest = root / ".kit-personal" / "lessons-index.json"
    dest.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(idx['lessons'])} lecciones -> {dest.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
