#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Presupuesto de lectura: avisa cuando un documento que se lee al arrancar es demasiado grande.

    python .kit/launch.py docsizes [--root DIR] [PATRON ...]
    python .kit/launch.py docsizes --rotate ARCHIVO.md [--keep 15]

Por qué: la herramienta de lectura corta a ~25.000 tokens; un documento que la pasa se lee a
medias sin que nadie lo note. Qué se vigila: los patrones que pases, o si no pasás ninguno los de
`.kit-personal/read-budget.txt` (uno por línea, `#` comenta), o si tampoco existe, la lista básica
(CLAUDE.md, AGENTS.md y los archivos de `.kit-personal`). Umbrales: con `tiktoken` instalado se
cuentan tokens reales (aviso 18k, falla 22k); sin él, bytes (aviso 35 KB, falla 50 KB, calibrados
para el peor caso medido de ~2,7 bytes por token). Sale 1 si algo FALLA.

Rotar (`--rotate`): mueve las secciones `## ` más viejas a `<doc>-archive.md` y deja un puntero.
Supone que lo NUEVO está arriba; se conservan las primeras `--keep` secciones. No borra nada.
"""
import argparse
import sys
from pathlib import Path

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENC = None

WARN_BYTES, FAIL_BYTES = 35_000, 50_000
WARN_TOKENS, FAIL_TOKENS = 18_000, 22_000
DEFAULT_PATTERNS = ["CLAUDE.md", "AGENTS.md", ".kit-personal/*.md", ".kit-personal/brands/*.md"]
ARCHIVE = ("*-archive.md", "*-archive-*.md")


def classify(size: int, tokens: int | None = None) -> str:
    warn, fail, v = (WARN_TOKENS, FAIL_TOKENS, tokens) if tokens is not None else (WARN_BYTES, FAIL_BYTES, size)
    return "fail" if v >= fail else "warn" if v >= warn else "ok"


def patterns(root: Path, given: list) -> list:
    if given:
        return given
    f = root / ".kit-personal" / "read-budget.txt"
    if f.is_file():
        lines = [ln.strip() for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()]
        got = [ln for ln in lines if ln and not ln.startswith("#")]
        if got:
            return got
    return DEFAULT_PATTERNS


def hot_files(root: Path, pats: list) -> list:
    found = {}
    for pat in pats:
        if Path(pat).is_absolute() or pat[:1] in ("/", "\\") or ".." in Path(pat).parts:
            continue  # only inside the project ("/etc/*" is not "absolute" on Windows: no drive letter)
        try:
            matches = sorted(root.glob(pat))
        except (NotImplementedError, ValueError, OSError):
            continue  # a pattern pathlib cannot use is skipped, never fatal
        for p in matches:
            if p.is_file() and not p.is_symlink() and not any(p.match(a) for a in ARCHIVE):
                found[p] = None
    return list(found)


def report(root: Path, pats: list):
    rows, code = [], 0
    for p in hot_files(root, pats):
        size = p.stat().st_size
        tokens = len(_ENC.encode(p.read_text(encoding="utf-8", errors="replace"))) if _ENC else None
        v = classify(size, tokens)
        code = 1 if v == "fail" else code
        rows.append((p.relative_to(root).as_posix(), size, v))
    return rows, code


def rotate(path: Path, keep: int) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    if len(heads) <= keep:
        return f"{path.name}: tiene {len(heads)} secciones; nada que rotar (se conservan {keep})."
    cut = heads[keep]
    arch = path.with_name(path.stem + "-archive.md")
    old = "".join(lines[cut:])
    prev = arch.read_text(encoding="utf-8") if arch.is_file() else f"# {path.stem} — archivo\n\n"
    arch.write_text(prev.rstrip("\n") + "\n\n" + old.rstrip("\n") + "\n", encoding="utf-8")
    pointer = f"\n> Secciones anteriores movidas a `{arch.name}` (no se leen al arrancar).\n"
    path.write_text("".join(lines[:cut]).rstrip("\n") + "\n" + pointer, encoding="utf-8")
    return f"{path.name}: {len(heads) - keep} secciones movidas a {arch.name}."


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patterns", nargs="*")
    ap.add_argument("--root", default=".")
    ap.add_argument("--rotate")
    ap.add_argument("--keep", type=int, default=15)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if a.rotate:
        p = (root / a.rotate).resolve()
        if root not in p.parents or not p.is_file():
            print("Ese archivo no está dentro del proyecto.", file=sys.stderr)
            return 2
        print(rotate(p, max(1, a.keep)))
        return 0
    rows, code = report(root, patterns(root, a.patterns))
    bad = [r for r in rows if r[2] != "ok"]
    if not bad:
        print(f"[OK] {len(rows)} documento(s) dentro del presupuesto de lectura.")
    for rel, size, v in bad:
        print(f"[{'FALLA' if v == 'fail' else 'AVISO'}] {rel}: {size // 1000} KB. "
              f"Rotalo: python .kit/launch.py docsizes --rotate {rel}")
    return code


if __name__ == "__main__":
    sys.exit(main())
