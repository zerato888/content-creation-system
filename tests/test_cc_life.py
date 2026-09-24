# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Vida Personal: works with an empty config; every constant comes from the config."""
import datetime as dt
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402
from cc.server import life  # noqa: E402

EMPTY = config.normalize({})
CFG = config.normalize({"vida": {
    "currency": "EUR", "fx_rate": 1.1, "income_goal": 1000,
    "habits": [{"id": "leer", "label": "Leer 10 páginas", "weekdays": [0, 1, 2, 3, 4]},
               {"id": "estirar", "label": "Estirar"}],
    "fixed_payments": [{"id": "renta", "label": "Renta ficticia", "amount": 300, "day": 31},
                       {"id": "tel", "label": "Teléfono", "amount": 20}],
    "recurring_income": [{"id": "cliente", "label": "Cliente A", "amount": 400}],
    "milestones": [{"id": "curso", "label": "Terminar el curso"}],
}})


def test_empty_config_everything_works_and_is_empty(tmp_path):
    root = str(tmp_path)
    assert life.list_tasks(root, EMPTY) == []
    today = life.today_summary(root, EMPTY)
    assert today["habits_today"] == [] and today["tasks_open"] == 0
    assert life.week_matrix(root, EMPTY, "2026-03-04")["habits"] == []
    assert life.consistency(root, EMPTY)["overall_pct"] == 0
    view = life.income_month_view(root, EMPTY)
    assert view["recurring"] == [] and view["total_recibido"] == 0 and view["goal"] is None
    assert [r["total"] for r in life.income_history(root, EMPTY)] == [0]
    assert life.seed_milestones(root, EMPTY) == []
    with pytest.raises(ValueError):
        life.toggle_habit(root, EMPTY, "leer", "2026-03-04", True)


def test_fixed_payments_seed_per_period_and_tombstone(tmp_path):
    root = str(tmp_path)
    life.ensure_fixed_payments(root, CFG, "2026-02")
    life.ensure_fixed_payments(root, CFG, "2026-02")
    rows = [t for t in life.list_tasks(root, CFG, areas=None) if t["period"] == "2026-02"]
    assert sorted(t["title"] for t in rows) == ["Renta ficticia", "Teléfono"]
    renta = next(t for t in rows if t["title"] == "Renta ficticia")
    assert renta["due_date"] == "2026-02-28" and renta["amount"] == 300  # day 31 clamps to month end
    life.delete_task(root, CFG, renta["id"])
    life.ensure_fixed_payments(root, CFG, "2026-03")
    march = {t["title"] for t in life.list_tasks(root, CFG, areas=None) if t["period"] == "2026-03"}
    assert march == {"Teléfono"}


def test_shopping_list_tasks_and_area_whitelist(tmp_path):
    root = str(tmp_path)
    item = life.save_task(root, {"title": "Café", "area": life.AREA_SHOPPING, "category": "Cocina"})
    with pytest.raises(ValueError):
        life.save_task(root, {"title": "x", "area": "Otra"})
    with pytest.raises(ValueError):
        life.save_task(root, {"title": "x", "area": life.AREA_SHOPPING, "amount": "mucho"})
    done = life.complete_task(root, item["id"])
    assert done["status"] == "done" and done["completed_at"]
    edited = life.save_task(root, {"id": item["id"], "status": "open"})
    assert edited["completed_at"] is None
    with pytest.raises(FileNotFoundError):
        life.complete_task(root, 999)
    (tmp_path / "tasks-maintenance.lock").write_text("x", encoding="utf-8")
    with pytest.raises(RuntimeError):
        life.save_task(root, {"title": "y", "area": life.AREA_SHOPPING})


def test_habits_matrix_and_consistency_follow_config_weekdays(tmp_path):
    root = str(tmp_path)
    monday = "2026-03-02"
    life.toggle_habit(root, CFG, "leer", monday, True)
    life.toggle_habit(root, CFG, "leer", "2026-03-07", True)  # saturday: does not apply
    matrix = life.week_matrix(root, CFG, "2026-03-05")
    assert matrix["week_start"] == monday
    leer = matrix["habits"][0]
    assert leer["days"][0] == {"date": monday, "applies": True, "done": True}
    assert leer["days"][5]["applies"] is False and leer["days"][5]["done"] is False
    life.toggle_habit(root, CFG, "leer", monday, False)
    assert not life.week_matrix(root, CFG, monday)["habits"][0]["days"][0]["done"]
    today = config.today(CFG).isoformat()
    life.toggle_habit(root, CFG, "estirar", today, True)
    stats = life.consistency(root, CFG, since_days=1)
    assert next(h for h in stats["habits"] if h["id"] == "estirar")["pct"] == 100
    with pytest.raises(ValueError):
        life.toggle_habit(root, CFG, "leer", "ayer", True)


def test_income_view_uses_configured_recurring_and_goal(tmp_path):
    root = str(tmp_path)
    today = config.today(CFG)
    life.add_income_entry(root, CFG, {"kind": "recibido", "amount": 150, "source": "Venta"})
    life.add_income_entry(root, CFG, {"kind": "proyectado", "amount": "50"})
    with pytest.raises(ValueError):
        life.add_income_entry(root, CFG, {"kind": "regalo", "amount": 1})
    view = life.income_month_view(root, CFG, today.year, today.month)
    assert view["recurring_total"] == 400 and view["total_recibido"] == 550 and view["total_proyectado"] == 50
    assert view["currency"] == "EUR" and view["goal"] == 1000 and view["fx_rate"] == 1.1
    assert life.income_history(root, CFG)[-1] == {"period": today.strftime("%Y-%m"), "total": 550}


def test_goals_and_milestones_seed_once(tmp_path):
    root = str(tmp_path)
    assert [g["title"] for g in life.seed_milestones(root, CFG)] == ["Terminar el curso"]
    assert len(life.seed_milestones(root, CFG)) == 1
    goal = life.save_goal(root, {"title": "Ahorrar", "budget": 200, "due_date": "2026-12-31"})
    assert life.complete_goal(root, goal["id"])["done"] == 1
    assert life.save_goal(root, {"id": goal["id"], "budget": 250})["budget"] == 250
    life.delete_goal(root, goal["id"])
    with pytest.raises(FileNotFoundError):
        life.delete_goal(root, goal["id"])


def test_export_csv_neutralizes_formulas(tmp_path):
    root = str(tmp_path)
    life.save_task(root, {"title": "=HYPERLINK(1)", "area": life.AREA_SHOPPING})
    out = life.export_csv(root, "tasks")
    assert "'=HYPERLINK(1)" in out
    assert life.export_json(root)["tasks"][0]["title"] == "=HYPERLINK(1)"
    with pytest.raises(ValueError):
        life.export_csv(root, "sqlite_master")


def test_today_uses_configured_timezone():
    far = config.normalize({"locale": {"timezone": "Pacific/Kiritimati"}})
    utc = dt.datetime.now(dt.timezone.utc).date()
    assert config.today(far) in (utc, utc + dt.timedelta(days=1))
