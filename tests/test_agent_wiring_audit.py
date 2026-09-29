# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""The wiring audit passes on the real kit and catches each kind of broken wiring on a tiny fake kit."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engines"))
import agent_wiring_audit as aw  # noqa: E402


def w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fake(tmp: Path) -> Path:
    w(tmp / "agents" / "writer.md", "---\nname: writer\ndescription: rol de prueba largo\nskills: [draft]\n---\n"
      "Leé `.kit/knowledge/a.md` cuando escribas.\n")
    w(tmp / "skills" / "draft" / "SKILL.md", "---\nname: draft\ndescription: x\nrole: writer\nfiles: []\n---\n"
      "## Delegación\n- Claude Code: use the Agent tool with subagent_type `writer`.\n")
    w(tmp / "knowledge" / "README.md", "| [a](a.md) | siempre |\n| [b](b.md) | a veces |\n")
    w(tmp / "knowledge" / "a.md", "# a\n")
    w(tmp / "knowledge" / "b.md", "# b\n")
    w(tmp / "catalog.json", json.dumps({"version": "0", "roles": [{"name": "writer"}],
                                         "skills": [{"name": "draft"}]}))
    return tmp


def test_real_kit_is_wired():
    r = aw.audit(ROOT)
    bad = {k: v for k, v in r.items() if isinstance(v, list) and v and k != "roles"}
    assert bad == {}
    assert r["knowledge_cited_by_agents_or_skills"] > 10


def test_clean_fake_kit(tmp_path):
    r = aw.audit(fake(tmp_path))
    assert all(not v for k, v in r.items() if isinstance(v, list) and k != "roles")
    assert aw.main(["--root", str(tmp_path), "--lint"]) == 0


def test_detects_each_problem(tmp_path):
    fake(tmp_path)
    w(tmp_path / "skills" / "ghost" / "SKILL.md", "---\nname: ghost\ndescription: x\nrole: nobody\nfiles: []\n---\n")
    w(tmp_path / "skills" / "nodeleg" / "SKILL.md", "---\nname: nodeleg\ndescription: x\nrole: writer\nfiles: []\n---\nsin nada\n")
    w(tmp_path / "agents" / "writer.md", "---\nname: writer\ndescription: rol de prueba largo\nskills: [draft, missing]\n---\n"
      "Leé `.kit/knowledge/a.md` y `.kit/knowledge/gone.md`.\n")
    w(tmp_path / "knowledge" / "orphan.md", "# huérfana\n")
    w(tmp_path / "knowledge" / "bundle" / "README.md", "# curso\n")
    w(tmp_path / "knowledge" / "bundle" / "p.md", "# p\n")  # owned by its bundle index
    w(tmp_path / "catalog.json", json.dumps({"version": "0", "roles": [{"name": "writer"}, {"name": "phantom"}],
                                              "skills": [{"name": "draft"}, {"name": "lost"}]}))
    r = aw.audit(tmp_path)
    assert r["skills_sin_rol"] == ["ghost"]
    assert r["skills_sin_delegacion"] == ["nodeleg"]
    assert r["roles_con_skills_fantasma"] == [{"writer": ["missing"]}]
    assert r["referencias_rotas"] == ["gone.md"]
    assert r["paginas_huerfanas"] == ["orphan.md"]
    assert r["catalogo_sin_carpeta"] == ["lost"]
    assert sorted(r["carpeta_sin_catalogo"]) == ["ghost", "nodeleg"]
    assert r["roles_del_catalogo_sin_archivo"] == ["phantom"]
    assert aw.main(["--root", str(tmp_path), "--lint"]) == 1


def test_declared_pages_are_not_orphans(tmp_path):
    fake(tmp_path)
    w(tmp_path / "knowledge" / "solo.md", "# sin dueño\n")
    assert aw.audit(tmp_path)["paginas_huerfanas"] == ["solo.md"]
    w(tmp_path / "knowledge" / "no-agent-owner.json", json.dumps({"pages": {"solo.md": "referencia general"}}))
    assert aw.audit(tmp_path)["paginas_huerfanas"] == []
