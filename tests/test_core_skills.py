# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Offline checks for the text-only core skills and their presets."""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engines"))
import skill_check  # noqa: E402

SKILLS = ["web-research", "trend-research", "deep-research", "idea", "humanizer", "hooks",
          "brand-onboarding", "broll-plan", "reference-clone", "story-plan", "kickoff-lite", "wiki",
          "task", "task-checkpoint", "finish-session", "simple"]
_ROOTS = ["Users", "home", "private", "Volumes"]  # split so the guard does not flag this file
ABS_PATH = re.compile(r"(?<![\w.`])(" + "|".join("/" + r + "/" for r in _ROOTS) + r"|[A-Za-z]:\\)")


@pytest.mark.parametrize("name", SKILLS)
def test_skill(name):
    folder = ROOT / "skills" / name
    assert skill_check.check(folder) == []
    role = skill_check.frontmatter((folder / "SKILL.md").read_text(encoding="utf-8"))["role"]
    for f in folder.rglob("*.md"):
        body = f.read_text(encoding="utf-8")
        assert "innerHTML" not in body, f
        assert not ABS_PATH.search(body), f
    body = (folder / "SKILL.md").read_text(encoding="utf-8")
    assert "## Delegación" in body
    assert f"use the Agent tool with subagent_type `{role}`" in body
    assert f"adopt the `{role}` role from AGENTS.md" in body


def test_hooks_bank():
    bank = json.loads((ROOT / "presets/hooks/hooks-bank.json").read_text(encoding="utf-8"))
    assert bank["schema_version"] == 1 and "principles" in bank
    ids = [c["id"] for c in bank["categories"]]
    assert len(ids) == len(set(ids)) >= 10
    for c in bank["categories"]:
        assert c["name"] and c["emotion"] and c["templates"] and c["examples"]
    for pool in bank["principles"]["selection"].values():
        assert set(pool) <= set(ids)


def test_broll_presets():
    names = sorted(p.stem for p in (ROOT / "presets/broll").glob("*.json"))
    assert names == ["full_screen", "split_screen", "subject_gradient"]
    for n in names:
        p = json.loads((ROOT / f"presets/broll/{n}.json").read_text(encoding="utf-8"))
        assert p["name"] == p["mode"] == n
        assert {"a_roll", "b_roll", "start", "duration", "fps"} <= set(p["inputs"])
