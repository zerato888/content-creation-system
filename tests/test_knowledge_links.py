# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Relative markdown links in agents/ and knowledge/ resolve; agent files carry required frontmatter."""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DOCS = sorted([*(REPO / "agents").glob("*.md"), *(REPO / "knowledge").glob("*.md")])
AGENTS = sorted(p for p in (REPO / "agents").glob("*.md") if p.name != "README.md")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
ROLES = {"copywriter", "creative-director", "dp-cinematographer", "editor-video", "fact-checker",
         "strategist", "motion-designer", "screenwriter", "social-media-manager"}


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_relative_links_resolve(doc):
    for target in LINK.findall(doc.read_text(encoding="utf-8")):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        path = (doc.parent / target.split("#")[0]).resolve()
        assert path.is_relative_to(REPO) and path.exists(), f"{doc.name}: broken link {target}"


def test_all_roles_present():
    assert {p.stem for p in AGENTS} == ROLES


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.name)
def test_agent_frontmatter(agent):
    text = agent.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "missing frontmatter"
    fm = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    fm = {k.strip(): v.strip() for k, v in fm.items()}
    assert fm.get("name") == agent.stem
    assert len(fm.get("description", "")) > 20
    assert re.fullmatch(r"\[[a-z0-9, -]*\]", fm.get("skills", "")), "skills must be an inline list"
