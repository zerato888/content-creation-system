# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Creator home: weekly streak, "views at 48h" per recorded script, weekly hook winner.

Each "Ya grabé" is one row in <root>/creator.db. Weeks run Monday to Sunday.
Rules (goal and grace from cfg["creator"]):
- A week is "met" when it has at least `weekly_goal` recordings.
- Grace: a recording made in the first `grace_days` days of a week counts for the
  previous week when it is exactly the one that week was missing (a Sunday-night
  video that slipped to Monday does not break the streak; an empty week is not
  "rescued" by stealing from the new one).
- The streak is the number of consecutive met weeks ending now. The current week
  only adds once it is met; it never breaks the streak while it is in progress.
  The previous week does not break it either while its grace window is still open.
"""
import datetime as dt
import os
import sqlite3
import threading

from cc.config import config

_LOCK = threading.Lock()
SCHEMA = """
CREATE TABLE IF NOT EXISTS recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    script_file TEXT,
    brand TEXT,
    hook TEXT,
    views_48h INTEGER,
    created_at TEXT NOT NULL
);
"""
# «Ya grabé» is idempotent: one recording per script, per linked task and per request key
UNIQUE = {"script_file": "rec_script", "task_code": "rec_task", "request_key": "rec_request"}


def _conn(root):
    os.makedirs(root, exist_ok=True)
    conn = sqlite3.connect(os.path.join(root, "creator.db"))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(recordings)")}
    for col, index in UNIQUE.items():
        if col not in cols:
            conn.execute(f"ALTER TABLE recordings ADD COLUMN {col} TEXT")
        try:
            conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {index} ON recordings({col}) WHERE {col} IS NOT NULL")
        except sqlite3.IntegrityError:
            pass  # an old db already holds duplicates: add_recording still checks before inserting
    conn.commit()
    return conn


def _existing(conn, keys):
    for col, value in keys.items():
        if value:
            row = conn.execute(f"SELECT * FROM recordings WHERE {col}=? ORDER BY id LIMIT 1", (value,)).fetchone()
            if row is not None:
                return dict(row)
    return None


def _monday(day):
    return day - dt.timedelta(days=day.weekday())


def _str(value, field, limit=500):
    if value is not None and (not isinstance(value, str) or len(value) > limit):
        raise ValueError(f"{field} inválido")
    return value


def add_recording(root, cfg, body):
    title = (_str(body.get("title"), "title") or "").strip()
    if not title:
        raise ValueError("title requerido")
    for k in ("script_file", "brand", "hook", "task_code"):
        _str(body.get(k), k, 2000)
    _str(body.get("request_key"), "request_key", 100)
    date = body.get("date") or config.today(cfg).isoformat()
    dt.date.fromisoformat(date)
    keys = {"request_key": body.get("request_key") or None,
            "script_file": os.path.basename(body["script_file"]) if body.get("script_file") else None,
            "task_code": body.get("task_code") or None}
    with _LOCK, _conn(root) as conn:
        row = _existing(conn, keys)  # a retry or a double click returns the first recording
        if row is None:
            try:
                cur = conn.execute(
                    "INSERT INTO recordings (date, title, script_file, brand, hook, task_code, request_key, "
                    "created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (date, title, keys["script_file"], body.get("brand"), body.get("hook"), keys["task_code"],
                     keys["request_key"], dt.datetime.now(dt.timezone.utc).isoformat()))
                row = dict(conn.execute("SELECT * FROM recordings WHERE id=?", (cur.lastrowid,)).fetchone())
                row["duplicate"] = False
            except sqlite3.IntegrityError:  # another process won the race: same answer
                row = {**_existing(conn, keys), "duplicate": True}
        else:
            row["duplicate"] = True
    conn.close()
    return row


def set_views(root, recording_id, views):
    if isinstance(views, bool) or not isinstance(views, int) or not 0 <= views <= 10**12:
        raise ValueError("views_48h debe ser un entero >= 0")
    with _LOCK, _conn(root) as conn:
        if conn.execute("SELECT 1 FROM recordings WHERE id=?", (recording_id,)).fetchone() is None:
            raise FileNotFoundError(recording_id)
        conn.execute("UPDATE recordings SET views_48h=? WHERE id=?", (views, recording_id))
        row = dict(conn.execute("SELECT * FROM recordings WHERE id=?", (recording_id,)).fetchone())
    conn.close()
    return row


def list_recordings(root, limit=200):
    with _conn(root) as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM recordings ORDER BY date DESC, id DESC LIMIT ?",
                                              (limit,))]
    conn.close()
    return rows


def week_counts(dates, goal, grace_days):
    """{monday: count} after applying grace. Pure; `dates` are datetime.date."""
    counts = {}
    for day in sorted(dates):
        week = _monday(day)
        previous = week - dt.timedelta(days=7)
        if day.weekday() < grace_days and counts.get(previous, 0) == goal - 1:
            week = previous
        counts[week] = counts.get(week, 0) + 1
    return counts


def streak(dates, today, goal=3, grace_days=1):
    counts = week_counts(dates, goal, grace_days)
    current = _monday(today)
    previous = current - dt.timedelta(days=7)
    this_week = counts.get(current, 0)
    weeks = 1 if this_week >= goal else 0
    week = previous
    if counts.get(previous, 0) < goal and today.weekday() < grace_days:
        week = previous - dt.timedelta(days=7)  # previous week can still be rescued: skip, don't break
    while counts.get(week, 0) >= goal:
        weeks += 1
        week -= dt.timedelta(days=7)
    return {"streak_weeks": weeks, "this_week": this_week, "goal": goal,
            "remaining": max(0, goal - this_week), "grace_days": grace_days,
            "week_start": current.isoformat()}


def summary(root, cfg):
    rows = list_recordings(root, limit=100_000)
    creator = cfg["creator"]
    return streak([dt.date.fromisoformat(r["date"]) for r in rows], config.today(cfg),
                  creator["weekly_goal"], creator["grace_days"])


def hook_winner(root, cfg, week=None):
    """Recording with the most views at 48h in the week (Monday-based) that holds `week`."""
    monday = _monday(dt.date.fromisoformat(week) if week else config.today(cfg))
    end = monday + dt.timedelta(days=6)
    with _conn(root) as conn:
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM recordings WHERE date BETWEEN ? AND ? AND views_48h IS NOT NULL "
            "ORDER BY views_48h DESC, id", (monday.isoformat(), end.isoformat()))]
    conn.close()
    return {"week_start": monday.isoformat(), "measured": len(rows),
            "winner": rows[0] if rows else None, "ranking": rows}
