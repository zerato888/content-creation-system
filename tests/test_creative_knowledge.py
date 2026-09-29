# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Hooks bank, script formats, playbooks and memory templates are complete and well formed."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROLES = ["copywriter", "creative-director", "dp-cinematographer", "editor-video", "fact-checker",
         "motion-designer", "screenwriter", "social-media-manager", "ui-designer", "revenue-strategist",
         "strategist"]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_hooks_bank_unified_without_duplicates():
    bank = load("presets/hooks/hooks-bank.json")
    ids = [c["id"] for c in bank["categories"]]
    assert len(ids) == len(set(ids)) and len(ids) >= 14
    norm = [re.sub(r"[^a-z0-9]", "", t.lower()) for c in bank["categories"] for t in c["templates"]]
    assert len(norm) == len(set(norm)) and len(norm) >= 150
    assert all(c["templates"] and c["emotion"] for c in bank["categories"])
    assert len(bank["visual_hook_types"]) == 6
    assert all({"name", "description", "use_when"} <= set(v) for v in bank["visual_hook_types"])


def test_script_formats():
    d = load("presets/scripts/script-formats.json")
    assert len(d["structures"]) >= 13
    for s in d["structures"]:
        assert s["key"] and s["when"] and len(s["beats"]) >= 4
        assert all(b["step"] and b["template"] for b in s["beats"])
    assert d["voice"]["default"]["rules"] and d["voice"]["brands"] == {}
    assert len(d["hook_styles"]) == 7 and len(d["process"]) == 7
    assert len(d["cold_open_cinematic"]["acts"]) == 4
    assert {"que_postear_LIFE", "como_contarlo_3_porques", "reglas"} <= set(d["storytelling_wheel"])


def test_playbooks_and_pages_exist_and_are_indexed():
    readme = (ROOT / "knowledge" / "README.md").read_text(encoding="utf-8")
    playbooks = sorted((ROOT / "knowledge" / "playbooks").glob("*.md"))
    assert len(playbooks) == 8
    for p in playbooks:
        assert p.stat().st_size > 1500
        assert f"playbooks/{p.name}" in readme
    for rel in ["guion/estructuras-de-guion.md", "guion/hook-interrupcion-de-patron.md",
                "guion/hooks-con-datos.md", "guion/narrativa-adictiva.md", "guion/rueda-de-historias.md",
                "estrategia/outliers-y-patrones-virales.md", "estrategia/menu-de-tipos-de-contenido.md",
                "visual/direcciones-fotograficas.md", "visual/talking-head-con-ia.md",
                "agentes/hooks-del-harness.md"]:
        assert (ROOT / "knowledge" / rel).is_file() and rel in readme


@pytest.mark.parametrize("role", ROLES)
def test_memory_template(role):
    text = (ROOT / "onboarding" / "memory" / f"{role}.md.tmpl").read_text(encoding="utf-8")
    assert "Registro de correcciones" in text and "Todavía sin correcciones" in text


def test_role_knowledge_blocks_point_to_real_pages():
    for role in ["screenwriter", "copywriter", "dp-cinematographer", "strategist", "editor-video"]:
        text = (ROOT / "agents" / f"{role}.md").read_text(encoding="utf-8")
        assert "## Conocimiento: creación de contenido" in text
        for ref in re.findall(r"`\.kit/knowledge/([^`]+\.md)`", text):
            assert (ROOT / "knowledge" / ref).is_file(), ref
