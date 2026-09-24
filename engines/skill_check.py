# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Offline smoke check for a skill folder: SKILL.md exists, frontmatter has
name/description/role/files, the name matches the folder, every declared file
exists inside the folder, and the role is one of the kit roles. Stdlib only.

Usage: python engines/skill_check.py skills/<name>
Exit 0 ok, 1 problems.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROLES = {"copywriter", "creative-director", "dp-cinematographer", "editor-video", "fact-checker",
         "strategist", "motion-designer", "screenwriter", "social-media-manager"}


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}
    out, key = {}, None
    for line in m.group(1).splitlines():
        item = re.match(r"^\s+-\s+(.+)$", line)
        if item and key:
            out.setdefault(key, [])
            if isinstance(out[key], list):
                out[key].append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                out[key] = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
            else:
                out[key] = val.strip("'\"") if val else []
    return out


def check(folder: Path) -> list[str]:
    errs = []
    sk = folder / "SKILL.md"
    if not sk.is_file():
        return [f"{sk} missing"]
    fm = frontmatter(sk.read_text(encoding="utf-8"))
    for k in ("name", "description", "role", "files"):
        if k not in fm or fm[k] in ("", None):
            errs.append(f"frontmatter missing '{k}'")
    if fm.get("name") and fm["name"] != folder.name:
        errs.append(f"name '{fm['name']}' != folder '{folder.name}'")
    if fm.get("role") and fm["role"] not in ROLES:
        errs.append(f"unknown role '{fm['role']}'")
    files = fm.get("files") or []
    if not isinstance(files, list):
        errs.append("files must be a list")
        files = []
    base = folder.resolve()
    for rel in files:
        t = (folder / rel).resolve()
        if base not in t.parents and t != base or not t.exists():
            errs.append(f"declared file missing or outside skill: {rel}")
    return errs


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    errs = check(Path(argv[0]))
    for e in errs:
        print(f"skill_check: {argv[0]}: {e}", file=sys.stderr)
    if not errs:
        print(f"skill_check: {argv[0]}: ok")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
