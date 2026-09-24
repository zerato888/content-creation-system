#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Checkpoints for long tasks: .kit-personal/checkpoints/<code>/CURRENT.md + history/<stamp>.md.

  python checkpoint.py save <code> --file NOTE.md|-   [--project DIR]
  python checkpoint.py show <code>                   [--project DIR]
  python checkpoint.py list                          [--project DIR]
  python checkpoint.py --selftest

The previous CURRENT.md is copied into history/ before it is replaced (history is never
rewritten). Writes are temp -> rename. Stdlib only; Windows and macOS.
"""
import argparse
import datetime as dt
import os
import re
import sys
import tempfile
from pathlib import Path

CODE_RE = re.compile(r"^(?:[A-Z]{2,6}-\d{1,9}|[a-z0-9][a-z0-9-]{0,39})$")
MAX_NOTE = 200_000


def folder(project: Path, code: str) -> Path:
    if not CODE_RE.fullmatch(code or ""):
        raise ValueError("código inválido: usá el de la tarjeta (CAN-12) o minúsculas y guiones")
    base = project / ".kit-personal" / "checkpoints"
    for p in (project / ".kit-personal", base, base / code):
        if p.is_symlink():
            raise ValueError(f"{p.name} es un enlace simbólico; no lo toco")
    return base / code


def _atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".ckpt-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def save(project: Path, code: str, note: str) -> Path:
    if not note.strip() or len(note) > MAX_NOTE:
        raise ValueError("la nota está vacía o es demasiado larga")
    d = folder(project, code)
    current = d / "CURRENT.md"
    if current.is_file():
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        dest, n = d / "history" / f"{stamp}.md", 2
        while dest.exists():  # two saves in the same second never overwrite history
            dest, n = d / "history" / f"{stamp}-{n}.md", n + 1
        _atomic(dest, current.read_text(encoding="utf-8"))
    _atomic(current, note if note.endswith("\n") else note + "\n")
    return current


def show(project: Path, code: str) -> str | None:
    p = folder(project, code) / "CURRENT.md"
    return p.read_text(encoding="utf-8") if p.is_file() else None


def listing(project: Path) -> list[tuple[str, str]]:
    base = project / ".kit-personal" / "checkpoints"
    rows = []
    for p in sorted(base.glob("*/CURRENT.md")) if base.is_dir() else []:
        first = next((ln.strip("# ").strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()), "")
        rows.append((p.parent.name, first[:100]))
    return rows


def selftest() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        save(root, "CAN-1", "# CAN-1 — uno\n")
        save(root, "CAN-1", "# CAN-1 — dos\n")
        save(root, "CAN-1", "# CAN-1 — tres\n")
        d = root / ".kit-personal/checkpoints/CAN-1"
        assert show(root, "CAN-1").startswith("# CAN-1 — tres")
        assert sorted(p.read_text(encoding="utf-8")[:12] for p in (d / "history").iterdir()) == \
            ["# CAN-1 — do", "# CAN-1 — un"]
        assert listing(root) == [("CAN-1", "CAN-1 — tres")]
        for bad in ("../x", "Mayus", "", "a/b"):
            try:
                folder(root, bad)
                raise AssertionError(bad)
            except ValueError:
                pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Puntos de control de tareas")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--project", default=".")
    ap.add_argument("command", nargs="?", choices=("save", "show", "list"))
    ap.add_argument("code", nargs="?")
    ap.add_argument("--file", help="nota en Markdown, o - para la entrada estándar")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    project = Path(a.project).resolve()
    try:
        if a.selftest:
            selftest()
            print("selftest OK")
        elif a.command == "save":
            if not a.file:
                raise ValueError("falta --file")
            note = sys.stdin.read() if a.file == "-" else Path(a.file).read_text(encoding="utf-8")
            print(f"guardado: {save(project, a.code, note).relative_to(project).as_posix()}")
        elif a.command == "show":
            text = show(project, a.code)
            if text is None:
                print(f"No hay punto de control para {a.code}.")
                return 1
            print(text, end="")
        elif a.command == "list":
            rows = listing(project)
            print("\n".join(f"{c}: {t}" for c, t in rows) or "Todavía no hay puntos de control.")
        else:
            ap.error("usar save, show, list o --selftest")
    except (ValueError, OSError) as e:
        print(f"checkpoint: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
