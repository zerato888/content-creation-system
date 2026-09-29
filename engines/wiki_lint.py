#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Revisión de salud de la wiki (solo lee, nunca edita).

Busca: enlaces [[slug]] rotos, páginas huérfanas (nadie las enlaza), páginas fuera de index.md,
frontmatter incompleto y páginas viejas (aviso, no falla).

Uso: python .kit/launch.py wiki-lint [--wiki wiki] [--stale-days 180]
Salida 0 si no hay problemas (las viejas solo avisan), 1 si los hay.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

LINK = re.compile(r"\[\[([^\]|#]+)")
REQUIRED = ("title", "type", "created", "updated")
SPECIAL = {"index", "log", "hot", "schema", "overview"}  # páginas de estructura: no cuentan como huérfanas


def front(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            out[kv.group(1)] = kv.group(2).split("#")[0].strip()
    return out


def lint(wiki: Path, stale_days: int = 180, today: date | None = None) -> dict:
    today = today or date.today()
    pages = {p.stem: p for p in sorted(wiki.rglob("*.md"))}
    texts = {s: p.read_text(encoding="utf-8") for s, p in pages.items()}
    inbound = {s: set() for s in pages}
    res = {"broken": {}, "orphans": [], "not_in_index": [], "frontmatter": {}, "stale": []}
    for s, t in texts.items():
        for target in {m.group(1).strip() for m in LINK.finditer(t)}:
            if s == "schema":
                continue  # los ejemplos del esquema no son enlaces reales
            if target in pages:
                if target != s:
                    inbound[target].add(s)
            else:
                res["broken"].setdefault(s, []).append(target)
    index_links = {m.group(1).strip() for m in LINK.finditer(texts.get("index", ""))}
    for s, p in pages.items():
        if s.lower() in SPECIAL:
            continue
        if not inbound[s] - {"index"}:
            res["orphans"].append(s)
        if s not in index_links and "index" in pages:
            res["not_in_index"].append(s)
        fm = front(texts[s])
        missing = [k for k in REQUIRED if not fm.get(k)]
        if missing:
            res["frontmatter"][s] = missing
        try:
            age = (today - date.fromisoformat(fm.get("updated", ""))).days
            if age > stale_days:
                res["stale"].append((s, age))
        except ValueError:
            pass
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wiki", default="wiki")
    ap.add_argument("--stale-days", type=int, default=180)
    a = ap.parse_args(argv)
    wiki = Path(a.wiki)
    if not wiki.is_dir():
        print(f"wiki-lint: no existe la carpeta {wiki}", file=sys.stderr)
        return 2
    r = lint(wiki, a.stale_days)
    for s, ts in r["broken"].items():
        print(f"ENLACE ROTO en {s}: {', '.join(sorted(ts))}")
    for s in r["orphans"]:
        print(f"HUÉRFANA: {s} (nadie la enlaza)")
    for s in r["not_in_index"]:
        print(f"FUERA DEL ÍNDICE: {s}")
    for s, m in r["frontmatter"].items():
        print(f"FRONTMATTER en {s}: falta {', '.join(m)}")
    for s, d in r["stale"]:
        print(f"aviso: {s} sin tocar hace {d} días")
    bad = any(r[k] for k in ("broken", "orphans", "not_in_index", "frontmatter"))
    print("Hay problemas: se proponen arreglos, nada se edita solo." if bad else "OK: la wiki está consistente.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
