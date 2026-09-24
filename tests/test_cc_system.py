# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Agentic OS index of an installed kit, recommendations, health, metrics connectors."""
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402
from cc.server import (creator, health, lab, life, metrics_metricool, metrics_zernio,  # noqa: E402
                       recommendations, system_index, tasks)


def installed_project(tmp_path):
    (tmp_path / ".claude/skills/hooks").mkdir(parents=True)
    (tmp_path / ".claude/skills/hooks/SKILL.md").write_text(
        "---\nname: hooks\ndescription: Escribe hooks.\n---\nLee `.kit/knowledge/hooks-storytelling.md`.\n")
    (tmp_path / ".agents/skills/hooks").mkdir(parents=True)
    (tmp_path / ".agents/skills/hooks/SKILL.md").write_text("---\nname: hooks\n---\n")
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/agents/copywriter.md").write_text(
        "---\nname: copywriter\ndescription: Texto corto.\nskills: [hooks, falta]\n---\n"
        "Ver `.kit/knowledge/hooks-storytelling.md` y `.kit/knowledge/no-existe.md`.\n")
    (tmp_path / ".kit/knowledge").mkdir(parents=True)
    (tmp_path / ".kit/knowledge/hooks-storytelling.md").write_text("# Hooks y relato\nVer [[idea-madre]].\n")
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki/idea-madre.md").write_text("---\ntitle: Idea madre\n---\ntexto\n")
    return tmp_path


def test_index_reads_only_the_installed_kit(tmp_path):
    target = installed_project(tmp_path)
    index = system_index.build(target)
    assert [a["id"] for a in index["agents"]] == ["agent:copywriter"]
    assert index["skills"][0]["tools"] == ["claude", "codex"]
    assert [k["label"] for k in index["knowledge"]] == ["Hooks y relato"]
    assert [w["label"] for w in index["wiki"]] == ["Idea madre"]
    kinds = {(r["kind"], r["source"], r["target"]) for r in index["relationships"]}
    assert ("uses_skill", "agent:copywriter", "skill:hooks") in kinds
    assert ("knows", "agent:copywriter", "knowledge:hooks-storytelling.md") in kinds
    assert ("knows", "skill:hooks", "knowledge:hooks-storytelling.md") in kinds
    assert ("links_to", "knowledge:hooks-storytelling.md", "wiki:idea-madre.md") in kinds
    diag = index["diagnostics"]
    assert diag["dangling_declared_skills"] == [{"agent": "copywriter", "skill": "falta"}]
    assert diag["dangling_knowledge_paths"] == [{"agent": "copywriter", "path": "no-existe.md"}]
    assert diag["task_links"]["status"] == "omitted"
    src = system_index.source(target, index, "wiki:idea-madre.md")
    assert "texto" in src["content"]
    with pytest.raises(FileNotFoundError):
        system_index.source(target, index, "wiki:../../etc/passwd")


def test_index_codex_only_roles_and_empty_project(tmp_path):
    assert system_index.build(tmp_path)["agents"] == []
    (tmp_path / ".kit").mkdir()
    (tmp_path / ".kit/roles.md").write_text("### copywriter\n\nTexto.\n\n### screenwriter\n\nGuiones.\n")
    assert [a["label"] for a in system_index.build(tmp_path)["agents"]] == ["copywriter", "screenwriter"]


def test_task_link_validation(tmp_path):
    target = installed_project(tmp_path)
    data = str(tmp_path / "data")
    prefixes = {"vida": "VIDA"}
    task = tasks.save_task(data, {"source_id": "a", "ecosystem": "vida", "title": "t"}, prefixes)
    tasks.link_task(data, task["code"], "skill:hooks")
    tasks.link_task(data, task["code"], "skill:borrada")
    result = system_index.build(target, tasks.db_path(data))["diagnostics"]["task_links"]
    assert result == {"status": "validated", "danglers": [{"task_code": "VIDA-1", "node_id": "skill:borrada"}]}


def test_recommendations_are_evidence_based(tmp_path):
    root = str(tmp_path)
    cfg = config.normalize({"brands": [{"id": "canal", "name": "Canal", "task_prefix": "CAN",
                                        "kind": "personal-brand"}],
                            "vida": {"income_goal": 1000}})
    item = lab.save_item(root, {"tipo": "reel", "tema": "vieja"}, "canal")
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=9)).isoformat()
    path = tmp_path / "lab/canal/activos" / f"{item['id']}.json"
    path.write_text(json.dumps({**item, "actualizado": old}))
    kinds = {r["kind"] for r in recommendations.run(root, cfg)["items"]}
    assert "stalled_piece" in kinds and "weekly_goal" in kinds
    today = config.today(cfg)
    if today.day > 5:  # early in the month nobody is behind pace yet
        assert "income_pace" in kinds
    for _ in range(3):
        creator.add_recording(root, cfg, {"title": "v"})
    life.add_income_entry(root, cfg, {"kind": "recibido", "amount": 5000})
    kinds = {r["kind"] for r in recommendations.run(root, cfg)["items"]}
    assert "weekly_goal" not in kinds and "income_pace" not in kinds
    assert all(r["source"] for r in recommendations.run(root, cfg)["items"])


def test_health(tmp_path):
    cfg = config.normalize({})
    assert health.collect(str(tmp_path), cfg)["overall"] == "failed"  # no log yet
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/server.log").write_text("{}\n")
    assert health.collect(str(tmp_path), cfg)["overall"] == "ok"
    assert health.collect(str(tmp_path), config.normalize({"x": 1}))["overall"] == "degraded"


def fake_fetch(responses, seen):
    def fetch(request):
        seen.append(request)
        for fragment, payload in responses.items():
            if fragment in request.full_url:
                return payload
        return {}
    return fetch


def test_metricool_uses_config_account_and_given_key():
    brand = config.normalize({"brands": [{"id": "canal", "name": "C", "task_prefix": "CAN", "metrics": {
        "provider": "metricool", "account": {"blog_id": "111", "user_id": "222"}}}]})["brands"][0]
    seen = []
    feed = metrics_metricool.fetch(brand, "k-test", "UTC", dt.datetime(2026, 3, 18), fake_fetch({
        "reels": {"data": [{"reach": 100, "likes": 5, "text": "a"}]},
        "posts": [{"reach": 50, "likes": 1, "comments": 1, "saved": 2}]}, seen))
    assert feed["posts"] == 2 and feed["totals"]["reach"] == 150 and feed["top"][0]["reach"] == 100
    assert all("blogId=111" in r.full_url and r.get_header("X-mc-auth") == "k-test" for r in seen)
    assert all("k-test" not in r.full_url for r in seen)  # key travels in a header, never in the URL
    with pytest.raises(ValueError):
        metrics_metricool.fetch(brand, None)
    with pytest.raises(ValueError):
        metrics_metricool.fetch({**brand, "metrics": {"provider": "metricool", "account": {}}}, "k")


def test_zernio_resolves_handle_from_config():
    brand = {"id": "canal", "metrics": {"provider": "zernio", "account": {"handle": "@canal.demo"}}}
    seen = []
    feed = metrics_zernio.fetch(brand, "k", fetch=fake_fetch({
        "/accounts": {"accounts": [{"_id": "acc1", "profileUrl": "https://x/canal.demo", "followersCount": 9}]},
        "/analytics": {"posts": [{"analytics": {"reach": 10, "engagementRate": 2.0}}], "overview": {"publishedPosts": 1}},
    }, seen))
    assert feed["followers"] == 9 and feed["totals"]["reach"] == 10 and "accountId=acc1" in seen[-1].full_url
    with pytest.raises(ValueError):
        metrics_zernio.fetch({"id": "x", "metrics": {"account": {}}}, "k", fetch=fake_fetch({}, []))
