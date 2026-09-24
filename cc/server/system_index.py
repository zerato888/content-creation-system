# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Agentic OS map of the INSTALLED kit: agents, skills, knowledge and the project's wiki.

Read-only and deterministic. Scans only these places under TARGET:
  .claude/agents/*.md  (or the role headings in .kit/roles.md for Codex-only installs)
  .claude/skills/*/SKILL.md and .agents/skills/*/SKILL.md
  .kit/knowledge/**/*.md
  wiki/**/*.md         (only if the user's project has one)
Symlinks are skipped, so the scan never leaves the project.
"""
import datetime as dt
import os
import re
import sqlite3
from pathlib import Path

SKILL_DIRS = (".claude/skills", ".agents/skills")
KNOWLEDGE_REF = re.compile(r"\.kit/knowledge/([A-Za-z0-9._/-]+\.md)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)")
MAX_DOC_BYTES = 512 * 1024


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else ()):
        f = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if f:
            v = f.group(2).strip()
            out[f.group(1)] = v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'" else v
    return out


def parse_list(value):
    value = (value or "").strip().removeprefix("[").removesuffix("]")
    return [v.strip().strip("\"'") for v in value.split(",") if v.strip()]


def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_DOC_BYTES:
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _updated(path):
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds")


def _walk_md(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not os.path.islink(os.path.join(root, d)))
        for name in sorted(files):
            if name.endswith(".md"):
                yield Path(root) / name


def _node(kind, key, label, rel, updated=None, **extra):
    return {"id": f"{kind}:{key}", "kind": kind, "label": label, "path": rel, "updated_at": updated,
            "relationships": [], **extra}


def build(target, tasks_db=None):
    target = Path(target).resolve()
    rel = lambda p: p.relative_to(target).as_posix()  # noqa: E731
    texts, agents, skills, knowledge, wiki = {}, [], {}, [], []

    for d in SKILL_DIRS:
        for path in sorted((target / d).glob("*/SKILL.md")):
            text = _read(path)
            if text is None:
                continue
            fm = parse_frontmatter(text)
            name = fm.get("name") or path.parent.name
            tool = "claude" if d.startswith(".claude") else "codex"
            if name in skills:
                skills[name]["tools"].append(tool)
                continue
            skills[name] = _node("skill", name, name, rel(path), _updated(path), tools=[tool],
                                 description=fm.get("description", ""), command=f"/{name}")
            texts[skills[name]["id"]] = text

    for path in sorted((target / ".claude/agents").glob("*.md")):
        text = _read(path)
        if text is None:
            continue
        fm = parse_frontmatter(text)
        name = fm.get("name") or path.stem
        agents.append(_node("agent", name, name, rel(path), _updated(path), description=fm.get("description", ""),
                            declared_skills=parse_list(fm.get("skills"))))
        texts[agents[-1]["id"]] = text
    roles = target / ".kit/roles.md"
    if not agents and (text := _read(roles)) is not None:  # Codex-only install
        for m in re.finditer(r"^### ([a-z0-9-]+)\s*$\n(.*?)(?=^### [a-z0-9-]+\s*$|\Z)", text, re.M | re.S):
            agents.append(_node("agent", m.group(1), m.group(1), rel(roles), _updated(roles), description="",
                                declared_skills=[]))
            texts[agents[-1]["id"]] = m.group(2)

    for kind, base, bucket in (("knowledge", target / ".kit/knowledge", knowledge), ("wiki", target / "wiki", wiki)):
        if base.is_dir() and not base.is_symlink():
            for path in _walk_md(base):
                text = _read(path)
                if text is None:
                    continue
                heading = re.search(r"^#\s+(.+?)\s*$", text, re.M)
                key = path.relative_to(base).as_posix()
                bucket.append(_node(kind, key, parse_frontmatter(text).get("title") or
                                    (heading.group(1) if heading else path.stem), rel(path), _updated(path)))
                texts[bucket[-1]["id"]] = text

    nodes = {n["id"]: n for n in agents + list(skills.values()) + knowledge + wiki}
    relations, dangling_skills, dangling_knowledge = set(), [], []

    def relate(kind, source, targ):
        if source in nodes and targ in nodes and source != targ:
            relations.add((kind, source, targ))

    by_stem = {Path(n["path"]).stem: n["id"] for n in knowledge + wiki}
    for agent in agents:
        for name in agent["declared_skills"]:
            (relate("uses_skill", agent["id"], f"skill:{name}") if f"skill:{name}" in nodes
             else dangling_skills.append({"agent": agent["label"], "skill": name}))
        for ref in sorted(set(KNOWLEDGE_REF.findall(texts[agent["id"]]))):
            (relate("knows", agent["id"], f"knowledge:{ref}") if f"knowledge:{ref}" in nodes
             else dangling_knowledge.append({"agent": agent["label"], "path": ref}))
    for node_id, text in texts.items():
        for link in WIKI_LINK.findall(text):
            if link.strip() in by_stem:
                relate("links_to", node_id, by_stem[link.strip()])
        if node_id.startswith("skill:"):
            for ref in set(KNOWLEDGE_REF.findall(text)):
                relate("knows", node_id, f"knowledge:{ref}")

    relationships = []
    for number, (kind, source, targ) in enumerate(sorted(relations), 1):
        relationships.append({"id": f"relationship:{number:05d}", "kind": kind, "source": source, "target": targ})
        nodes[source]["relationships"].append(targ)
        nodes[targ]["relationships"].append(source)
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "agents": agents, "skills": list(skills.values()), "knowledge": knowledge, "wiki": wiki,
        "relationships": relationships,
        "diagnostics": {"dangling_declared_skills": dangling_skills, "dangling_knowledge_paths": dangling_knowledge,
                        "task_links": task_link_validation(tasks_db, set(nodes))},
    }


def task_link_validation(db_path, node_ids):
    if not db_path or not Path(db_path).is_file():
        return {"status": "omitted", "danglers": []}
    try:
        with sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True) as conn:
            rows = conn.execute("SELECT task_code,node_id FROM task_links ORDER BY task_code,node_id").fetchall()
        conn.close()
    except sqlite3.Error as error:
        return {"status": "omitted", "error": str(error), "danglers": []}
    return {"status": "validated",
            "danglers": [{"task_code": c, "node_id": n} for c, n in rows if n not in node_ids]}


def source(target, index, node_id):
    """Text of one indexed node, only if it is in the index and still inside TARGET."""
    node = next((n for group in ("agents", "skills", "knowledge", "wiki") for n in index[group]
                 if n["id"] == node_id), None)
    if node is None:
        raise FileNotFoundError(node_id)
    base = Path(target).resolve()
    path = (base / node["path"]).resolve()
    path.relative_to(base)  # ValueError if it escaped
    text = _read(path)
    if text is None:
        raise FileNotFoundError(node_id)
    return {"id": node_id, "path": node["path"], "content": text}
