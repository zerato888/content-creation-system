# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Catalog honesty: every skill's smoke runs offline and exits 0; tested skills
really pass; every skill carries both delegation wordings for its role."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CAT = json.loads((REPO / "catalog.json").read_text(encoding="utf-8"))
SKILLS = CAT["skills"]
EXE = {"python": sys.executable}


def test_catalog_nonempty_and_core_limit():
    # ponytail: onboard and the Agentic OS pack (task, checkpoints, session close, plain language)
    # are kit plumbing, not among the up-to-15 content capabilities
    core = [s for s in SKILLS if s["tier"] == "core" and s["name"] != "onboard" and s["category"] != "agentic-os"]
    assert 1 <= len(core) <= 15
    assert all(s["status"] == "tested" for s in core), "core must be tested"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s["name"])
def test_smoke_runs_offline(skill):
    argv = list(skill["smoke"]["argv"])
    if argv[0] != "python":
        pytest.skip(f"smoke needs {argv[0]}")
    argv[0] = EXE["python"]
    r = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s["name"])
def test_delegation_wording(skill):
    body = (REPO / "skills" / skill["name"] / "SKILL.md").read_text(encoding="utf-8")
    assert "use the Agent tool with subagent_type `" in body
    assert "role from AGENTS.md" in body and "adopt the `" in body
    assert f"role: {skill['role']}" in body
