# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Task store with config-defined brands (ported from the original store's tests)."""
import multiprocessing
import sqlite3
import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402
from cc.server import tasks  # noqa: E402

CFG = config.normalize({"brands": [{"id": "canal", "name": "Canal", "task_prefix": "CAN", "kind": "personal-brand"},
                                   {"id": "estudio", "name": "Estudio", "task_prefix": "EST"}]})
P = config.task_prefixes(CFG)


def created(root, source_id="one", ecosystem="vida", **values):
    return tasks.save_task(root, {"source_id": source_id, "ecosystem": ecosystem,
                                  "title": "Tarea <img src=x onerror=alert(1)>", **values}, P)


def add_process(root, source_id, barrier):
    barrier.wait()
    tasks.save_task(root, {"source_id": source_id, "ecosystem": "estudio", "title": f"t {source_id}"}, P)


def test_codes_come_from_config_prefixes_and_are_immutable(tmp_path):
    root = str(tmp_path)
    task = created(root, stage="idea")
    assert task["code"] == "VIDA-1"
    assert created(root, "b", "canal")["code"] == "CAN-1"
    assert created(root, "c", "canal")["code"] == "CAN-2"
    moved = tasks.update_task(root, task["code"], "ecosystem", "estudio", P)
    assert moved["code"] == "VIDA-1" and moved["ecosystem"] == "estudio"
    assert created(root, "d", "estudio")["code"] == "EST-1"
    assert task["title"].startswith("Tarea <img")  # stored as text; escaping is the UI's job


def test_unknown_ecosystem_rejected_in_code_not_sql(tmp_path):
    root = str(tmp_path)
    with pytest.raises(ValueError):
        created(root, ecosystem="no-existe")
    created(root)
    # a brand added later needs no migration: a new prefix map is enough
    more = {**P, "nueva": "NEW"}
    assert tasks.save_task(root, {"source_id": "n", "ecosystem": "nueva", "title": "x"}, more)["code"] == "NEW-1"
    with sqlite3.connect(tmp_path / "tasks.db") as conn:
        schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='tasks'").fetchone()[0]
    assert "ecosystem IN" not in schema


def test_transitions_idempotency_and_soft_delete(tmp_path):
    root = str(tmp_path)
    task = created(root, stage="guion_listo")
    assert created(root)["id"] == task["id"]  # same source_id = same task
    done = tasks.complete_task(root, task["code"])
    again = tasks.complete_task(root, task["code"])
    assert done["completed_at"] == again["completed_at"]
    reopened = tasks.complete_task(root, task["code"], False)
    assert reopened["status"] == "open" and reopened["completed_at"] is None and reopened["stage"] == "guion_listo"
    tasks.delete_task(root, task["code"])
    assert not tasks.list_tasks(root, P, code=task["code"])
    for mutation in (lambda: tasks.complete_task(root, task["code"]),
                     lambda: tasks.update_task(root, task["code"], "title", "x", P),
                     lambda: tasks.link_task(root, task["code"], "node:x")):
        with pytest.raises(FileNotFoundError):
            mutation()
    assert created(root)["id"] != task["id"]


def test_validation(tmp_path):
    root = str(tmp_path)
    for bad in ({"status": "urgent"}, {"priority": "urgent"}, {"stage": "nope"}, {"due_date": "mañana"},
                {"handoff": [1]}, {"status": "open", "completed_at": "2026-01-01T00:00:00"}):
        with pytest.raises(ValueError):
            created(root, "v", **bad)
    task = created(root)
    for field, value in (("code", "X-1"), ("priority", "zzz"), ("title", " "), ("ecosystem", "zzz")):
        with pytest.raises(ValueError):
            tasks.update_task(root, task["code"], field, value, P)
    with pytest.raises(ValueError):
        tasks.list_tasks(root, P, statuses="open,bogus")


def test_subtasks(tmp_path):
    root = str(tmp_path)
    parent = created(root, "p", "canal")
    child = created(root, "c", "canal", parent_id=parent["code"])
    assert tasks.list_tasks(root, P, code=parent["code"])[0]["children"] == [child["code"]]
    with pytest.raises(ValueError):
        created(root, "x", "estudio", parent_id=parent["code"])
    with pytest.raises(ValueError):
        tasks.delete_task(root, parent["code"])
    with pytest.raises(ValueError):
        tasks.update_task(root, child["code"], "ecosystem", "estudio", P)


def test_links_schema_version_and_maintenance_lock(tmp_path):
    root = str(tmp_path)
    task = created(root)
    tasks.link_task(root, task["code"], "skill:hooks")
    tasks.link_task(root, task["code"], "skill:hooks")
    assert tasks.list_tasks(root, P)[0]["links"] == ["skill:hooks"]
    tasks.link_task(root, task["code"], "skill:hooks", "remove")
    assert tasks.list_tasks(root, P)[0]["links"] == []
    with sqlite3.connect(tmp_path / "tasks.db") as conn:
        conn.execute("PRAGMA user_version=0")
    with pytest.raises(RuntimeError, match="schema 0"):
        tasks.list_tasks(root, P)
    with sqlite3.connect(tmp_path / "tasks.db") as conn:
        conn.execute("PRAGMA user_version=1")
    (tmp_path / "tasks-maintenance.lock").write_text("x")
    with pytest.raises(RuntimeError, match="maintenance"):
        created(root, "locked")


def test_lock_is_rechecked_after_sqlite_write_access(tmp_path):
    root = str(tmp_path)
    tasks.initialize(str(tmp_path / "tasks.db")).close()
    blocker = sqlite3.connect(tmp_path / "tasks.db")
    blocker.execute("BEGIN IMMEDIATE")
    errors = []
    worker = threading.Thread(target=lambda: errors.append(pytest.raises(RuntimeError, created, root, "toctou")))
    worker.start()
    try:
        threading.Event().wait(0.3)
        (tmp_path / "tasks-maintenance.lock").write_text("x")
        blocker.rollback()
        worker.join(timeout=6)
        assert not worker.is_alive() and errors
    finally:
        blocker.close()
    (tmp_path / "tasks-maintenance.lock").unlink()
    assert not tasks.list_tasks(root, P)


def test_concurrent_processes_get_distinct_codes(tmp_path):
    root = str(tmp_path)
    ctx = multiprocessing.get_context("spawn")
    barrier = ctx.Barrier(2)
    procs = [ctx.Process(target=add_process, args=(root, str(i), barrier)) for i in range(2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(30)
        assert p.exitcode == 0
    assert {t["code"] for t in tasks.list_tasks(root, P)} == {"EST-1", "EST-2"}


def test_cli_uses_target_config(tmp_path, capsys):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal" / "cc.config.json").write_text(
        '{"brands": [{"id": "canal", "name": "Canal", "task_prefix": "CAN"}]}', encoding="utf-8")
    tasks.main(["--target", str(tmp_path), "add", "Grabar intro", "--ecosystem", "canal"])
    assert '"code": "CAN-1"' in capsys.readouterr().out
    assert (tmp_path / ".kit-personal" / "data" / "tasks.db").is_file()
