# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Vida Personal notebooks (diario, recordatorios, ideas): empty on install, local SQLite, API on/off by toggle."""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402
from cc.server import life  # noqa: E402
from test_cc_server import server, set_config, CONFIG  # noqa: E402,F401  (fixture + helper)

EMPTY = config.normalize({})


def test_empty_on_install(tmp_path):
    for kind in life.NOTEBOOKS:
        assert life.list_notes(str(tmp_path), kind) == []
    assert life.export_csv(str(tmp_path), "journal") == ""


def test_journal_defaults_today_and_filters_by_month(tmp_path):
    root = str(tmp_path)
    today = life.save_note(root, EMPTY, "journal", {"text": "hoy"})
    assert today["date"] == config.today(EMPTY).isoformat()
    life.save_note(root, EMPTY, "journal", {"text": "antes", "date": "2026-01-05", "mood": 4})
    assert [e["text"] for e in life.list_notes(root, "journal", month="2026-01")] == ["antes"]
    with pytest.raises(ValueError):
        life.save_note(root, EMPTY, "journal", {"text": "x", "mood": 9})
    with pytest.raises(ValueError):
        life.save_note(root, EMPTY, "journal", {"text": "  "})
    with pytest.raises(ValueError):
        life.complete_note(root, "journal", today["id"])


def test_reminders_order_edit_done_delete(tmp_path):
    root = str(tmp_path)
    late = life.save_note(root, EMPTY, "reminders", {"title": "B", "due_date": "2026-05-02", "due_time": "09:30"})
    life.save_note(root, EMPTY, "reminders", {"title": "A", "due_date": "2026-05-01"})
    assert [r["title"] for r in life.list_notes(root, "reminders")] == ["A", "B"]
    life.save_note(root, EMPTY, "reminders", {"id": late["id"], "title": "B2"})
    assert life.complete_note(root, "reminders", late["id"])["done"] == 1
    assert [r["title"] for r in life.list_notes(root, "reminders", done=False)] == ["A"]
    with pytest.raises(ValueError):
        life.save_note(root, EMPTY, "reminders", {"title": "x", "due_date": "no"})
    assert life.delete_note(root, "reminders", late["id"])["deleted"]
    with pytest.raises(FileNotFoundError):
        life.delete_note(root, "reminders", late["id"])
    with pytest.raises(ValueError):
        life.list_notes(root, "gastos")


def test_csv_neutralizes_formulas(tmp_path):
    life.save_note(str(tmp_path), EMPTY, "ideas", {"text": "=HYPERLINK(1)"})
    assert "'=HYPERLINK(1)" in life.export_csv(str(tmp_path), "ideas")


def test_api_and_toggle(server):
    client, tmp_path = server
    client.login()
    assert client.get("/api/life/ideas")[2]["items"] == []
    status, _, body = client.post("/api/life/ideas", {"text": "hacer pan"})
    assert status == 200
    item = body["item"]
    assert client.post("/api/life/ideas/complete", {"id": item["id"], "done": True})[2]["item"]["done"] == 1
    assert client.post("/api/life/journal", {"text": ""})[0] == 400
    assert client.post("/api/life/journal/complete", {"id": 1})[0] == 404  # journal has no "done"
    assert client.post("/api/life/ideas/delete", {"id": 999})[0] == 404
    assert client.post("/api/life/reminders", {"title": "x", "due_date": "mañana"})[0] == 400
    assert client.post("/api/life/ideas/delete", {"id": item["id"]})[0] == 200
    set_config(tmp_path, {**CONFIG, "toggles": {"vida": False}})
    for kind in ("journal", "reminders", "ideas"):
        assert client.get(f"/api/life/{kind}")[0] == 404
        assert client.post(f"/api/life/{kind}", {"text": "x", "title": "x"})[0] == 404


def test_creator_first_run_survives_parallel_requests(tmp_path):
    """Regression: three views hit an empty creator.db at once; the migration raised OperationalError."""
    import threading
    from cc.server import creator
    errors = []

    def go():
        try:
            creator._conn(str(tmp_path)).close()
        except Exception as e:  # noqa: BLE001
            errors.append(e)
    threads = [threading.Thread(target=go) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors
