# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Audit that roles, skills and knowledge pages are wired to each other.

Checks (all offline, stdlib only):
  - every skill declares a `role` that exists in agents/ and its `## Delegación` names that role
  - every skill and role in catalog.json exists on disk, and every skill on disk is in the catalog
  - every skill a role lists in its frontmatter `skills:` exists
  - every knowledge path a role or skill points to exists
  - every knowledge page is reachable: cited by a role or skill, listed in
    knowledge/README.md, or declared in knowledge/no-agent-owner.json
    (pages inside a subfolder that has its own README.md are owned by that index)

Usage: python engines/agent_wiring_audit.py [--root DIR] [--json] [--lint]
Exit 0 when clean, 1 when --lint finds problems.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_check import frontmatter  # noqa: E402

KNOW_REF = re.compile(r"knowledge/([A-Za-z0-9_./-]+?\.md)")
LINK_REF = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _norm(p: str) -> str:
    """Path relative to knowledge/, without leading ./ or ../ segments."""
    parts = [x for x in p.split("/") if x not in ("", ".", "..")]
    return "/".join(parts)


def _refs(text: str, base: Path, know: Path) -> set[str]:
    """Knowledge pages (relative to knowledge/) that `text` points to."""
    found = {_norm(m) for m in KNOW_REF.findall(text)}
    for m in LINK_REF.findall(text):
        target = (base / m).resolve()
        try:
            found.add(target.relative_to(know.resolve()).as_posix())
        except ValueError:
            pass
    return found


def audit(root: Path) -> dict:
    root = Path(root)
    know = root / "knowledge"
    role_files = sorted(p for p in (root / "agents").glob("*.md") if p.name != "README.md")
    roles = {p.stem for p in role_files}
    skill_dirs = sorted(d for d in (root / "skills").iterdir() if (d / "SKILL.md").is_file()) \
        if (root / "skills").is_dir() else []
    skills = {d.name for d in skill_dirs}

    problems: dict[str, list] = {k: [] for k in (
        "skills_sin_rol", "skills_sin_delegacion", "roles_con_skills_fantasma",
        "catalogo_sin_carpeta", "carpeta_sin_catalogo", "roles_del_catalogo_sin_archivo",
        "referencias_rotas", "paginas_huerfanas")}

    cited: set[str] = set()
    for d in skill_dirs:
        text = _read(d / "SKILL.md")
        fm = frontmatter(text)
        role = fm.get("role")
        if not role or role not in roles:
            problems["skills_sin_rol"].append(d.name)
        elif f"`{role}`" not in text.split("## Delegación", 1)[-1] or "## Delegación" not in text:
            problems["skills_sin_delegacion"].append(d.name)
        for f in d.rglob("*.md"):
            for ref in _refs(_read(f), f.parent, know):
                cited.add(ref)
    for p in role_files:
        text = _read(p)
        fm = frontmatter(text)
        missing = [s for s in fm.get("skills", []) if s not in skills]
        if missing:
            problems["roles_con_skills_fantasma"].append({p.stem: missing})
        cited |= _refs(text, p.parent, know)

    cat_path = root / "catalog.json"
    if cat_path.is_file():
        cat = json.loads(_read(cat_path))
        in_cat = {s["name"] for s in cat.get("skills", [])}
        problems["catalogo_sin_carpeta"] = sorted(in_cat - skills)
        problems["carpeta_sin_catalogo"] = sorted(skills - in_cat)
        problems["roles_del_catalogo_sin_archivo"] = sorted(
            r["name"] for r in cat.get("roles", []) if r["name"] not in roles)

    pages = sorted(p.relative_to(know).as_posix() for p in know.rglob("*.md")) if know.is_dir() else []
    problems["referencias_rotas"] = sorted(r for r in cited if r not in pages)

    indexed: set[str] = set()
    for readme in know.rglob("README.md"):
        indexed |= {(readme.parent / t).resolve().relative_to(know.resolve()).as_posix()
                    for t in LINK_REF.findall(_read(readme))
                    if (readme.parent / t).resolve().is_relative_to(know.resolve())}
        indexed |= _refs(_read(readme), readme.parent, know)
    declared: set[str] = set()
    owner = know / "no-agent-owner.json"
    if owner.is_file():
        declared = set(json.loads(_read(owner)).get("pages", {}))
    # A subfolder with its own README.md is a curated bundle (e.g. a course): its index owns the pages.
    bundles = {r.parent.relative_to(know).as_posix() + "/" for r in know.rglob("README.md") if r.parent != know}
    problems["paginas_huerfanas"] = sorted(
        p for p in pages
        if not p.endswith("README.md") and p not in cited and p not in indexed and p not in declared
        and not any(p.startswith(b) for b in bundles))

    return {"roles": sorted(roles), "skills_total": len(skills), "knowledge_pages": len(pages),
            "knowledge_cited_by_agents_or_skills": len(cited & set(pages)), **problems}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lint", action="store_true", help="exit 1 if anything is unwired")
    args = ap.parse_args(argv)
    r = audit(Path(args.root))
    bad = {k: v for k, v in r.items() if isinstance(v, list) and v and k not in ("roles",)}
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print(f"roles: {len(r['roles'])} | skills: {r['skills_total']} | "
              f"páginas de conocimiento: {r['knowledge_pages']} "
              f"(citadas por roles o skills: {r['knowledge_cited_by_agents_or_skills']})")
        for k, v in bad.items():
            print(f"  {k}: {len(v)}")
            for item in v:
                print(f"    - {item}")
        if not bad:
            print("OK: todo está cableado")
    return 1 if (args.lint and bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
