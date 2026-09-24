# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Vida Personal storage: fixed payments and shopping list, habits, income, goals.

One SQLite file at <root>/life.db (root = TARGET/.kit-personal/data). Every
personal constant (habits, fixed payments, recurring income, currency, exchange
rate, income goal, milestones) comes from `cfg["vida"]`; with an empty config
everything works and simply shows nothing. "Today" follows the configured
timezone.
"""
import csv
import datetime as dt
import io
import os
import sqlite3
import threading

from cc.config import config

_LOCK = threading.Lock()  # ponytail: one global lock; single-user local tool
AREA_FIXED, AREA_SHOPPING = "Pagos Fijos", "Compras"
UI_AREAS = (AREA_FIXED, AREA_SHOPPING)
EXPORT_TABLES = {"tasks": "life_tasks", "habit_log": "habit_log", "income_manual": "income_manual"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS fixed_payment_exclusions (title TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS milestone_exclusions (title TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS life_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    area TEXT,
    due_date TEXT,
    priority TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    amount REAL,
    period TEXT,
    category TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS habit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id TEXT NOT NULL,
    date TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 1,
    UNIQUE(habit_id, date)
);
CREATE TABLE IF NOT EXISTS income_manual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    amount REAL NOT NULL,
    source TEXT,
    date TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS life_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    priority TEXT,
    budget REAL,
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS income_history_monthly (period TEXT PRIMARY KEY, total REAL NOT NULL);
"""
TASK_FIELDS = ("title", "area", "due_date", "priority", "status", "amount", "period", "category", "notes")


class _Conn:
    def __init__(self, root):
        os.makedirs(root, exist_ok=True)
        self.conn = sqlite3.connect(os.path.join(root, "life.db"))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(SCHEMA)

    def __enter__(self):
        return self.conn

    def __exit__(self, kind, *_):
        self.conn.rollback() if kind else self.conn.commit()
        self.conn.close()


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _check_maintenance(root):
    if os.path.exists(os.path.join(root, "tasks-maintenance.lock")):
        raise RuntimeError("task store maintenance lock is active")


def _amount(value, field="amount"):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} inválido")
    if number != number or abs(number) > 1e15:
        raise ValueError(f"{field} inválido")
    return number


def _str(value, field, limit=500):
    if value is not None and (not isinstance(value, str) or len(value) > limit):
        raise ValueError(f"{field} inválido")
    return value


def _date(value):
    if value is not None:
        dt.date.fromisoformat(value)
    return value


def ensure_fixed_payments(root, cfg, period=None):
    """Insert this period's configured fixed payments if missing. Idempotent by
    (title, period); a new month starts unpaid; deleted ones stay deleted."""
    _check_maintenance(root)
    period = period or config.today(cfg).strftime("%Y-%m")
    payments = cfg["vida"]["fixed_payments"]
    if not payments:
        return
    now = _now()
    with _LOCK, _Conn(root) as conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = {r["title"] for r in conn.execute(
            "SELECT title FROM life_tasks WHERE area=? AND period=?", (AREA_FIXED, period))}
        existing |= {r["title"] for r in conn.execute("SELECT title FROM fixed_payment_exclusions")}
        for item in payments:
            if item["label"] in existing:
                continue
            due = None
            day = item.get("day")
            if isinstance(day, int) and not isinstance(day, bool) and 1 <= day <= 31:
                year, month = (int(p) for p in period.split("-"))
                last = (dt.date(year + month // 12, month % 12 + 1, 1) - dt.timedelta(days=1)).day
                due = dt.date(year, month, min(day, last)).isoformat()
            conn.execute(
                "INSERT INTO life_tasks (title, area, status, amount, period, due_date, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (item["label"], AREA_FIXED, "open", item["amount"], period, due, now, now))


# ------------------------------------------------------------------ tasks
def list_tasks(root, cfg, status=None, areas=UI_AREAS):
    ensure_fixed_payments(root, cfg)
    with _Conn(root) as conn:
        q, args = "SELECT * FROM life_tasks WHERE 1=1", []
        if areas:
            q += " AND area IN (%s)" % ",".join("?" for _ in areas)
            args.extend(areas)
        if status:
            q += " AND status = ?"
            args.append(status)
        q += " ORDER BY (due_date IS NULL), due_date, id DESC"
        return [dict(r) for r in conn.execute(q, args)]


def _find(conn, task_id, areas):
    q, args = "SELECT * FROM life_tasks WHERE id = ?", [task_id]
    if areas:
        q += " AND area IN (%s)" % ",".join("?" for _ in areas)
        args.extend(areas)
    row = conn.execute(q, args).fetchone()
    if row is None:
        raise FileNotFoundError(task_id)
    return row


def save_task(root, body, allowed_areas=UI_AREAS):
    _check_maintenance(root)
    task_id = body.get("id")
    if allowed_areas and ("area" in body or not task_id) and body.get("area") not in allowed_areas:
        raise ValueError("area inválida")
    for k in ("title", "area", "priority", "status", "period", "category"):
        _str(body.get(k), k)
    _str(body.get("notes"), "notes", 20_000)
    _date(body.get("due_date"))
    if body.get("status") not in (None, "open", "done"):
        raise ValueError("status inválido")
    now = _now()
    with _LOCK, _Conn(root) as conn:
        conn.execute("BEGIN IMMEDIATE")
        _check_maintenance(root)
        if task_id:
            row = _find(conn, task_id, allowed_areas)
            fields = dict(row)
            fields.update({k: body[k] for k in TASK_FIELDS if k in body})
            fields["amount"] = _amount(fields.get("amount"))
            if not (fields["title"] or "").strip():
                raise ValueError("title requerido")
            completed = now if fields["status"] == "done" and row["status"] != "done" else (
                None if fields["status"] != "done" else row["completed_at"])
            conn.execute(
                "UPDATE life_tasks SET title=?, area=?, due_date=?, priority=?, status=?, amount=?, period=?, "
                "category=?, notes=?, updated_at=?, completed_at=? WHERE id=?",
                tuple(fields[k] for k in TASK_FIELDS) + (now, completed, task_id))
        else:
            title = (body.get("title") or "").strip()
            if not title:
                raise ValueError("title requerido")
            cur = conn.execute(
                "INSERT INTO life_tasks (title, area, due_date, priority, status, amount, period, category, notes, "
                "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (title, body.get("area"), body.get("due_date"), body.get("priority"), body.get("status") or "open",
                 _amount(body.get("amount")), body.get("period"), body.get("category"), body.get("notes"), now, now))
            task_id = cur.lastrowid
        return dict(conn.execute("SELECT * FROM life_tasks WHERE id = ?", (task_id,)).fetchone())


def complete_task(root, task_id, done=True, allowed_areas=UI_AREAS):
    _check_maintenance(root)
    now = _now()
    with _LOCK, _Conn(root) as conn:
        conn.execute("BEGIN IMMEDIATE")
        _find(conn, task_id, allowed_areas)
        conn.execute("UPDATE life_tasks SET status=?, completed_at=?, updated_at=? WHERE id=?",
                     ("done" if done else "open", now if done else None, now, task_id))
        return dict(conn.execute("SELECT * FROM life_tasks WHERE id = ?", (task_id,)).fetchone())


def delete_task(root, cfg, task_id, allowed_areas=UI_AREAS):
    _check_maintenance(root)
    configured = {p["label"] for p in cfg["vida"]["fixed_payments"]}
    with _LOCK, _Conn(root) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = _find(conn, task_id, allowed_areas)
        conn.execute("DELETE FROM life_tasks WHERE id = ?", (task_id,))
        if row["area"] == AREA_FIXED and row["title"] in configured:
            # tombstone so next month's seed does not resurrect a payment the user removed
            conn.execute("INSERT OR IGNORE INTO fixed_payment_exclusions (title) VALUES (?)", (row["title"],))
    return {"id": task_id, "deleted": True}


# ------------------------------------------------------------------ habits
def toggle_habit(root, cfg, habit_id, date, done):
    if habit_id not in {h["id"] for h in cfg["vida"]["habits"]}:
        raise ValueError("habit_id inválido")
    if not isinstance(date, str):
        raise ValueError("date inválida")
    dt.date.fromisoformat(date)
    with _LOCK, _Conn(root) as conn:
        if done:
            conn.execute("INSERT INTO habit_log (habit_id, date, done) VALUES (?,?,1) "
                         "ON CONFLICT(habit_id, date) DO UPDATE SET done=1", (habit_id, date))
        else:
            conn.execute("DELETE FROM habit_log WHERE habit_id=? AND date=?", (habit_id, date))
    return {"habit_id": habit_id, "date": date, "done": bool(done)}


def _done_between(root, start, end):
    with _Conn(root) as conn:
        return {(r["habit_id"], r["date"]) for r in conn.execute(
            "SELECT habit_id, date FROM habit_log WHERE date BETWEEN ? AND ? AND done=1",
            (start.isoformat(), end.isoformat()))}


def week_matrix(root, cfg, week_start):
    """7-day matrix for the week (Monday first) containing `week_start`."""
    anchor = dt.date.fromisoformat(week_start)
    monday = anchor - dt.timedelta(days=anchor.weekday())
    days = [monday + dt.timedelta(days=i) for i in range(7)]
    done = _done_between(root, days[0], days[-1])
    habits = []
    for habit in cfg["vida"]["habits"]:
        cells = [{"date": d.isoformat(), "applies": d.weekday() in habit["weekdays"],
                  "done": d.weekday() in habit["weekdays"] and (habit["id"], d.isoformat()) in done}
                 for d in days]
        habits.append({"id": habit["id"], "label": habit["label"], "days": cells})
    return {"week_start": monday.isoformat(), "habits": habits}


def consistency(root, cfg, since_days=30):
    """% of applicable habit-days completed in the trailing window, per habit and overall."""
    today = config.today(cfg)
    start = today - dt.timedelta(days=since_days - 1)
    done = _done_between(root, start, today)
    per_habit, total_applicable, total_done = [], 0, 0
    for habit in cfg["vida"]["habits"]:
        days = [start + dt.timedelta(days=i) for i in range(since_days)]
        applicable = [d for d in days if d.weekday() in habit["weekdays"]]
        hits = sum((habit["id"], d.isoformat()) in done for d in applicable)
        total_applicable += len(applicable)
        total_done += hits
        per_habit.append({"id": habit["id"], "label": habit["label"], "done": hits,
                          "applicable": len(applicable),
                          "pct": round(100 * hits / len(applicable)) if applicable else 0})
    overall = round(100 * total_done / total_applicable) if total_applicable else 0
    return {"since_days": since_days, "overall_pct": overall, "habits": per_habit}


# ------------------------------------------------------------------ income
def add_income_entry(root, cfg, body):
    if body.get("kind") not in ("recibido", "proyectado"):
        raise ValueError("kind debe ser 'recibido' o 'proyectado'")
    amount = _amount(body.get("amount"))
    if amount is None:
        raise ValueError("amount inválido")
    date = body.get("date") or config.today(cfg).isoformat()
    _date(date)
    _str(body.get("source"), "source")
    _str(body.get("notes"), "notes", 5000)
    with _LOCK, _Conn(root) as conn:
        cur = conn.execute(
            "INSERT INTO income_manual (kind, amount, source, date, notes, created_at) VALUES (?,?,?,?,?,?)",
            (body["kind"], amount, body.get("source"), date, body.get("notes"), _now()))
        return dict(conn.execute("SELECT * FROM income_manual WHERE id = ?", (cur.lastrowid,)).fetchone())


def list_income(root, year=None, month=None):
    q, args = "SELECT * FROM income_manual", ()
    if year and month:
        q, args = q + " WHERE date LIKE ?", (f"{int(year):04d}-{int(month):02d}%",)
    elif year:
        q, args = q + " WHERE date LIKE ?", (f"{int(year):04d}%",)
    with _Conn(root) as conn:
        entries = [dict(r) for r in conn.execute(q + " ORDER BY date DESC, id DESC", args)]
    return {"entries": entries, "summary": {
        "recibido": sum(e["amount"] for e in entries if e["kind"] == "recibido"),
        "proyectado": sum(e["amount"] for e in entries if e["kind"] == "proyectado")}}


def income_month_view(root, cfg, year=None, month=None):
    today = config.today(cfg)
    year, month = int(year or today.year), int(month or today.month)
    vida = cfg["vida"]
    recurring = [{"label": r["label"], "amount": r["amount"]} for r in vida["recurring_income"]]
    recurring_total = sum(r["amount"] for r in recurring)
    manual = list_income(root, year, month)
    return {"year": year, "month": month, "currency": vida["currency"], "fx_rate": vida["fx_rate"],
            "goal": vida["income_goal"], "recurring": recurring, "recurring_total": recurring_total,
            "manual": manual, "total_recibido": recurring_total + manual["summary"]["recibido"],
            "total_proyectado": manual["summary"]["proyectado"]}


def income_history(root, cfg):
    """Settled months from the table, then every later month through today computed live
    (recurring + manual), so the history never goes stale. Empty table = current month only."""
    with _Conn(root) as conn:
        rows = [dict(r) for r in conn.execute("SELECT period, total FROM income_history_monthly ORDER BY period")]
    today = config.today(cfg)
    year, month = (int(p) for p in rows[-1]["period"].split("-")) if rows else (today.year, today.month - 1)
    while True:
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        if (year, month) > (today.year, today.month):
            return rows
        rows.append({"period": f"{year:04d}-{month:02d}",
                     "total": income_month_view(root, cfg, year, month)["total_recibido"]})


# ------------------------------------------------------------------ goals / milestones
def list_goals(root):
    with _Conn(root) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM life_goals ORDER BY done, (due_date IS NULL), due_date, id")]


def save_goal(root, body):
    goal_id = body.get("id")
    for k in ("title", "priority"):
        _str(body.get(k), k)
    _date(body.get("due_date"))
    budget = _amount(body.get("budget"), "budget")
    now = _now()
    with _LOCK, _Conn(root) as conn:
        if goal_id:
            row = conn.execute("SELECT * FROM life_goals WHERE id = ?", (goal_id,)).fetchone()
            if row is None:
                raise FileNotFoundError(goal_id)
            fields = dict(row)
            fields.update({k: body[k] for k in ("title", "priority", "due_date") if k in body})
            if "budget" in body:
                fields["budget"] = budget
            if not (fields["title"] or "").strip():
                raise ValueError("title requerido")
            conn.execute("UPDATE life_goals SET title=?, priority=?, budget=?, due_date=?, updated_at=? WHERE id=?",
                         (fields["title"], fields["priority"], fields["budget"], fields["due_date"], now, goal_id))
        else:
            title = (body.get("title") or "").strip()
            if not title:
                raise ValueError("title requerido")
            goal_id = conn.execute(
                "INSERT INTO life_goals (title, done, priority, budget, due_date, created_at, updated_at) "
                "VALUES (?,0,?,?,?,?,?)", (title, body.get("priority"), budget, body.get("due_date"), now, now)
            ).lastrowid
        return dict(conn.execute("SELECT * FROM life_goals WHERE id = ?", (goal_id,)).fetchone())


def complete_goal(root, goal_id, done=True):
    with _LOCK, _Conn(root) as conn:
        if conn.execute("SELECT id FROM life_goals WHERE id = ?", (goal_id,)).fetchone() is None:
            raise FileNotFoundError(goal_id)
        conn.execute("UPDATE life_goals SET done=?, updated_at=? WHERE id=?", (1 if done else 0, _now(), goal_id))
        return dict(conn.execute("SELECT * FROM life_goals WHERE id = ?", (goal_id,)).fetchone())


def delete_goal(root, goal_id, cfg=None):
    configured = {m["label"] for m in (cfg or {}).get("vida", {}).get("milestones", [])}
    with _LOCK, _Conn(root) as conn:
        row = conn.execute("SELECT id, title FROM life_goals WHERE id = ?", (goal_id,)).fetchone()
        if row is None:
            raise FileNotFoundError(goal_id)
        conn.execute("DELETE FROM life_goals WHERE id = ?", (goal_id,))
        if row["title"] in configured:
            # tombstone, like fixed payments: the next load must not seed the deleted milestone again
            conn.execute("INSERT OR IGNORE INTO milestone_exclusions (title) VALUES (?)", (row["title"],))
    return {"id": goal_id, "deleted": True}


def seed_milestones(root, cfg):
    """Create the configured milestones as goals, once, matching by title; deleted ones stay deleted."""
    existing = {g["title"] for g in list_goals(root)}
    with _Conn(root) as conn:
        existing |= {r["title"] for r in conn.execute("SELECT title FROM milestone_exclusions")}
    for m in cfg["vida"]["milestones"]:
        if m["label"] not in existing:
            save_goal(root, {"title": m["label"]})
    return list_goals(root)


# ------------------------------------------------------------------ dashboard + export
def today_summary(root, cfg):
    today = config.today(cfg).isoformat()
    week_end = (config.today(cfg) + dt.timedelta(days=7)).isoformat()
    tasks = [t for t in list_tasks(root, cfg, status="open") if t.get("area") != AREA_FIXED]
    week = week_matrix(root, cfg, today)
    month = config.today(cfg)
    return {
        "date": today,
        "tasks_open": len(tasks),
        "due_today": [t for t in tasks if t["due_date"] == today],
        "overdue": [t for t in tasks if t["due_date"] and t["due_date"] < today],
        "upcoming_7d": [t for t in tasks if t["due_date"] and today < t["due_date"] <= week_end],
        "habits_today": [{"id": h["id"], "label": h["label"], **next(c for c in h["days"] if c["date"] == today)}
                         for h in week["habits"]],
        "income_month": list_income(root, month.year, month.month)["summary"],
    }


def export_json(root):
    with _Conn(root) as conn:
        return {"generated_at": _now(), **{name: [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY id")]
                                           for name, table in EXPORT_TABLES.items()}}


def export_csv(root, table):
    if table not in EXPORT_TABLES:
        raise ValueError("tabla inválida")
    with _Conn(root) as conn:
        rows = [dict(r) for r in conn.execute(f"SELECT * FROM {EXPORT_TABLES[table]} ORDER BY id")]
    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
        writer.writeheader()
        # neutralize spreadsheet formulas in user text (=, +, -, @ at the start of a cell)
        writer.writerows({k: ("'" + v if isinstance(v, str) and v[:1] in "=+-@" else v) for k, v in r.items()}
                         for r in rows)
    return buf.getvalue()
