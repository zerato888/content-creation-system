# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Every text-mode open()/read_text()/write_text() names its encoding.

Without it Python uses the locale codec (cp1252 on Windows) and UTF-8 files with accents crash."""
import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__"}


def _mode(call, pos):
    if len(call.args) > pos and isinstance(call.args[pos], ast.Constant):
        return call.args[pos].value
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            return kw.value.value
    return "r"


def offenders(tree):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or any(k.arg == "encoding" or k.arg is None for k in node.keywords):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if name in ("read_text", "write_text"):
            yield node.lineno
        elif name in ("open", "fdopen"):
            owner = getattr(f.value, "id", "") if isinstance(f, ast.Attribute) else None
            if owner in ("os", "tarfile", "zipfile", "webbrowser", "gzip"):
                continue
            # builtin open(file, mode) / os.fdopen(fd, mode); Path.open(mode)
            mode = _mode(node, 0 if owner not in (None, "os") and name == "open" else 1)
            if isinstance(mode, str) and "b" not in mode:
                yield node.lineno


def test_all_text_io_names_encoding():
    bad = []
    for p in REPO.rglob("*.py"):
        if SKIP & set(p.relative_to(REPO).parts):
            continue
        bad += [f"{p.relative_to(REPO)}:{n}" for n in offenders(ast.parse(p.read_text(encoding="utf-8")))]
    assert not bad, "text I/O without encoding=:\n" + "\n".join(bad)


def test_scanner_catches_and_allows():
    src = 'open("a")\nopen("a","rb")\nPath("a").read_text()\nPath("a").read_text(encoding="utf-8")\nopen("a","w",encoding="utf-8")\nPath("a").open("rb")\nos.open("a", 1)\nPath("a").open()\n'
    assert list(offenders(ast.parse(src))) == [1, 3, 8]
