# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Shared SQLite task store for the Command Center.

`root` is the data dir (TARGET/.kit-personal/data). Ecosystems and their code
prefixes come from the config (`config.task_prefixes(cfg)`), passed in as
`prefixes` = {ecosystem_id: "PREFIX"}. There is no SQL CHECK on the ecosystem:
a new brand is a new config row, never a migration. Codes are immutable
(`PREFIX-N`), so moving a task to another brand keeps its code.
"""
import datetime as dt
import json
import os
import sqlite3
import sys
import tempfile
import threading

if __package__ in (None, ""):  # `python .kit/cc/server/tasks.py ...` from the project root
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

_LOCK = threading.Lock()
SCHEMA_VERSION = 1
STATUSES = ("backlog", "open", "in_progress", "done")
PRIORITIES = ("high", "medium", "low")
STAGES = ("idea", "guion_listo", "grabado", "editado", "publicado")
MUTABLE_FIELDS = {"ecosystem", "title", "status", "priority", "stage", "area",
                  "due_date", "notes", "handoff"}
MAX_TEXT = 20_000
SCHEMA = """
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE,
  source TEXT NOT NULL,
  source_id TEXT NOT NULL,
  ecosystem TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'backlog',
  priority TEXT NOT NULL DEFAULT 'medium',
  stage TEXT,
  area TEXT,
  due_date TEXT,
  notes TEXT,
  handoff TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT,
  deleted_at TEXT,
  last_actor TEXT,
  parent_id TEXT REFERENCES tasks(code) CHECK(parent_id IS NULL OR parent_id <> code),
  CHECK ((status = 'done') = (completed_at IS NOT NULL)),
  CHECK (code GLOB '[A-Z][A-Z]*-[1-9]*' AND code NOT GLOB '*[^A-Z0-9-]*'),
  CHECK (status IN ('backlog','open','in_progress','done')),
  CHECK (priority IN ('high','medium','low')),
  CHECK (handoff IS NULL OR (json_valid(handoff) AND json_type(handoff) = 'object'))
);
CREATE INDEX idx_tasks_eco_status ON tasks(ecosystem, status) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_tasks_source_id ON tasks(source, source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tasks_parent_id ON tasks(parent_id);
CREATE TABLE task_links (
  task_code TEXT NOT NULL REFERENCES tasks(code) ON DELETE CASCADE,
  node_id TEXT NOT NULL,
  PRIMARY KEY (task_code, node_id)
);
CREATE INDEX idx_task_links_node ON task_links(node_id);
PRAGMA user_version = 1;
"""


def db_path(root):
    return os.path.join(root, "tasks.db")


def _maintenance_path(root):
    return os.path.join(root, "tasks-maintenance.lock")


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _validate_date(value):
    if value is not None:
        dt.date.fromisoformat(value)
    return value


def _validate_timestamp(value):
    if value is not None:
        try:
            dt.datetime.fromisoformat(value)
        except (TypeError, ValueError) as error:
            raise ValueError("timestamp inválido") from error
    return value


def _text(value, field):
    if value is not None and (not isinstance(value, str) or len(value) > MAX_TEXT):
        raise ValueError(f"{field} inválido")
    return value


def _ecosystem(value, prefixes):
    if value not in prefixes:
        raise ValueError("ecosystem inválido")
    return value


def initialize(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        # Seed in a temp file and hard-link into place: two first writers never see
        # a half-created schema, and the loser of the race just uses the winner's.
        descriptor, temporary = tempfile.mkstemp(prefix="tasks-schema.", suffix=".db",
                                                 dir=os.path.dirname(path))
        os.close(descriptor)
        try:
            with sqlite3.connect(temporary) as seed:
                seed.executescript("BEGIN;\n" + SCHEMA + "\nCOMMIT;")
            seed.close()
            os.chmod(temporary, 0o600)
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass
            except OSError:  # filesystems without hard links
                if not os.path.exists(path):
                    os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    conn = sqlite3.connect(path)
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version != SCHEMA_VERSION:
            raise RuntimeError(f"tasks.db schema {version}; expected {SCHEMA_VERSION}")
        return conn
    except Exception:
        conn.close()
        raise


class _Conn:
    """sqlite3's own context manager commits but never closes; this one does both."""

    def __init__(self, root):
        self.conn = initialize(db_path(root))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=DELETE")

    def __enter__(self):
        return self.conn

    def __exit__(self, kind, *_):
        if kind:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


def _write_allowed(root):
    if os.path.exists(_maintenance_path(root)):
        raise RuntimeError("task store maintenance lock is active")


def _begin_write(conn, root):
    conn.execute("BEGIN IMMEDIATE")
    _write_allowed(root)  # re-checked after the write lock: no check-then-write gap


def _row(conn, code):
    return conn.execute("SELECT * FROM tasks WHERE code=? AND deleted_at IS NULL", (code,)).fetchone()


def _task_dict(conn, row, children_map=None):
    item = dict(row)
    item["handoff"] = json.loads(item["handoff"]) if item["handoff"] else None
    item["links"] = [r[0] for r in conn.execute(
        "SELECT node_id FROM task_links WHERE task_code=? ORDER BY node_id", (item["code"],))]
    if children_map is None:
        item["children"] = [r[0] for r in conn.execute(
            "SELECT code FROM tasks WHERE parent_id=? AND deleted_at IS NULL ORDER BY id", (item["code"],))]
    else:
        item["children"] = children_map.get(item["code"], [])
    return item


def list_tasks(root, prefixes, ecosystem=None, statuses=None, code=None):
    with _Conn(root) as conn:
        query, args = "SELECT * FROM tasks WHERE deleted_at IS NULL", []
        if ecosystem:
            query += " AND ecosystem=?"
            args.append(_ecosystem(ecosystem, prefixes))
        if statuses is not None:
            if isinstance(statuses, str):
                statuses = statuses.split(",")
            if not statuses or any(token not in STATUSES for token in statuses):
                raise ValueError("status inválido")
            query += " AND status IN (%s)" % ",".join("?" for _ in statuses)
            args.extend(statuses)
        if code:
            query += " AND code=?"
            args.append(code)
        rows = conn.execute(query + " ORDER BY id", args).fetchall()
        children = {}
        for parent, child in conn.execute(
                "SELECT parent_id, code FROM tasks WHERE parent_id IS NOT NULL AND deleted_at IS NULL ORDER BY id"):
            children.setdefault(parent, []).append(child)
        return [_task_dict(conn, row, children) for row in rows]


def allocate_code(conn, prefix):
    row = conn.execute(
        "SELECT COALESCE(MAX(CAST(substr(code, instr(code, '-') + 1) AS INTEGER)), 0) "
        "FROM tasks WHERE code GLOB ?", (prefix + "-[0-9]*",)).fetchone()
    return f"{prefix}-{row[0] + 1}"


def save_task(root, body, prefixes, source="cli", actor="cli"):
    _write_allowed(root)
    source_id = str(body.get("source_id") or "").strip()
    title = str(body.get("title") or "").strip()
    ecosystem = _ecosystem(body.get("ecosystem"), prefixes)
    if not source_id or len(source_id) > 200:
        raise ValueError("source_id requerido")
    if not title or len(title) > 500:
        raise ValueError("title requerido")
    status = body.get("status") or "backlog"
    priority = str(body.get("priority") or "medium").lower()
    stage = body.get("stage")
    if status not in STATUSES:
        raise ValueError("status inválido")
    if priority not in PRIORITIES:
        raise ValueError("priority inválida")
    if stage is not None and stage not in STAGES:
        raise ValueError("stage inválido")
    due_date = _validate_date(body.get("due_date"))
    area, notes = _text(body.get("area"), "area"), _text(body.get("notes"), "notes")
    handoff = body.get("handoff")
    if handoff is not None and not isinstance(handoff, dict):
        raise ValueError("handoff debe ser objeto")
    parent_id = body.get("parent_id") or None
    created = _validate_timestamp(body.get("created_at")) or _now()
    updated = _validate_timestamp(body.get("updated_at")) or created
    completed = _validate_timestamp(body.get("completed_at"))
    if status == "done":
        completed = completed or updated
    elif completed is not None:
        raise ValueError("completed_at requiere status done")
    with _LOCK, _Conn(root) as conn:
        _begin_write(conn, root)
        existing = conn.execute("SELECT * FROM tasks WHERE source=? AND source_id=? AND deleted_at IS NULL",
                                (source, source_id)).fetchone()
        if existing:  # idempotent create: same source_id returns the same task
            return _task_dict(conn, existing)
        if parent_id is not None:
            parent = _row(conn, parent_id)
            if parent is None:
                raise ValueError("parent_id no existe o está borrado")
            if parent["ecosystem"] != ecosystem:
                raise ValueError("parent_id debe ser del mismo ecosystem")
        code = allocate_code(conn, prefixes[ecosystem])
        conn.execute(
            "INSERT INTO tasks(code,source,source_id,ecosystem,title,status,priority,stage,area,due_date,"
            "notes,handoff,parent_id,created_at,updated_at,completed_at,last_actor) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (code, source, source_id, ecosystem, title, status, priority, stage, area, due_date, notes,
             json.dumps(handoff, ensure_ascii=False, sort_keys=True) if handoff is not None else None,
             parent_id, created, updated, completed, actor))
        return _task_dict(conn, _row(conn, code))


def update_task(root, code, field, value, prefixes, actor="cli"):
    _write_allowed(root)
    if field == "status":
        return set_status(root, code, value, actor)
    if field not in MUTABLE_FIELDS:
        raise ValueError("campo no editable")
    if field == "ecosystem":
        _ecosystem(value, prefixes)
    elif field == "priority":
        value = str(value or "").lower()
        if value not in PRIORITIES:
            raise ValueError("priority inválida")
    elif field == "stage":
        if value is not None and value not in STAGES:
            raise ValueError("stage inválido")
    elif field == "due_date":
        value = _validate_date(value)
    elif field == "title":
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError("title requerido")
        value = value.strip()
    elif field == "handoff":
        if value is not None and not isinstance(value, dict):
            raise ValueError("handoff debe ser objeto")
        value = json.dumps(value, ensure_ascii=False, sort_keys=True) if value is not None else None
    else:
        _text(value, field)
    with _LOCK, _Conn(root) as conn:
        _begin_write(conn, root)
        row = _row(conn, code)
        if row is None:
            raise FileNotFoundError(code)
        if field == "ecosystem":
            has_children = conn.execute(
                "SELECT 1 FROM tasks WHERE parent_id=? AND deleted_at IS NULL LIMIT 1", (row["code"],)).fetchone()
            if row["parent_id"] is not None or has_children:
                raise ValueError("no se puede cambiar ecosystem: la tarea tiene parent o hijos")
        conn.execute(f"UPDATE tasks SET {field}=?, updated_at=?, last_actor=? WHERE id=?",
                     (value, _now(), actor, row["id"]))
        return _task_dict(conn, _row(conn, row["code"]))


def set_status(root, code, desired, actor="cli"):
    _write_allowed(root)
    if desired not in STATUSES:
        raise ValueError("status inválido")
    with _LOCK, _Conn(root) as conn:
        _begin_write(conn, root)
        row = _row(conn, code)
        if row is None:
            raise FileNotFoundError(code)
        if desired != "done":
            completed = None
        elif row["status"] == "done":
            completed = row["completed_at"]  # completing twice keeps the first timestamp
        else:
            completed = _now()
        conn.execute("UPDATE tasks SET status=?,completed_at=?,updated_at=?,last_actor=? WHERE id=?",
                     (desired, completed, _now(), actor, row["id"]))
        return _task_dict(conn, _row(conn, row["code"]))


def complete_task(root, code, done=True, actor="cli"):
    return set_status(root, code, "done" if done else "open", actor)


def delete_task(root, code, actor="cli"):
    _write_allowed(root)
    with _LOCK, _Conn(root) as conn:
        _begin_write(conn, root)
        row = _row(conn, code)
        if row is None:
            raise FileNotFoundError(code)
        if conn.execute("SELECT 1 FROM tasks WHERE parent_id=? AND deleted_at IS NULL LIMIT 1",
                        (row["code"],)).fetchone():
            raise ValueError("no se puede borrar: la tarea tiene subtareas activas")
        now = _now()
        conn.execute("UPDATE tasks SET deleted_at=?,updated_at=?,last_actor=? WHERE id=?",
                     (now, now, actor, row["id"]))
        return {"code": row["code"], "deleted": True}


def link_task(root, code, node_id, action="add", actor="cli"):
    _write_allowed(root)
    if not isinstance(node_id, str) or not node_id or len(node_id) > 300:
        raise ValueError("node_id requerido")
    if action not in ("add", "remove"):
        raise ValueError("action inválida")
    with _LOCK, _Conn(root) as conn:
        _begin_write(conn, root)
        row = _row(conn, code)
        if row is None:
            raise FileNotFoundError(code)
        if action == "add":
            conn.execute("INSERT OR IGNORE INTO task_links(task_code,node_id) VALUES(?,?)", (row["code"], node_id))
        else:
            conn.execute("DELETE FROM task_links WHERE task_code=? AND node_id=?", (row["code"], node_id))
        conn.execute("UPDATE tasks SET updated_at=?,last_actor=? WHERE id=?", (_now(), actor, row["id"]))
        return _task_dict(conn, _row(conn, row["code"]))


def stale_tasks(root, prefixes, days=14):
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat()
    return [t for t in list_tasks(root, prefixes) if t["status"] != "done" and t["updated_at"] < cutoff]


def main(argv=None):
    """CLI for the /task skill, from the project root: `python .kit/cc/server/tasks.py add "título" --ecosystem ID`."""
    import argparse
    import uuid
    from pathlib import Path
    from cc.config import config

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=os.getcwd(), help="carpeta del proyecto (tiene .kit-personal/)")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--ecosystem", required=True)
    add.add_argument("--priority", default="medium")
    add.add_argument("--area")
    add.add_argument("--due-date")
    add.add_argument("--parent")
    listing = sub.add_parser("list")
    listing.add_argument("--ecosystem")
    listing.add_argument("--status")
    move = sub.add_parser("move")
    move.add_argument("code")
    move.add_argument("ecosystem")
    close = sub.add_parser("close")
    close.add_argument("code")
    close.add_argument("--reopen", action="store_true")
    sub.add_parser("stale").add_argument("--days", type=int, default=14)
    args = parser.parse_args(argv)
    prefixes = config.task_prefixes(config.load(args.target))
    root = str(Path(args.target) / ".kit-personal" / "data")
    if args.command == "add":
        result = save_task(root, {"title": args.title, "ecosystem": args.ecosystem, "priority": args.priority,
                                  "area": args.area, "due_date": args.due_date, "parent_id": args.parent,
                                  "source_id": str(uuid.uuid4())}, prefixes)
    elif args.command == "list":
        result = list_tasks(root, prefixes, args.ecosystem, args.status)
    elif args.command == "move":
        result = update_task(root, args.code, "ecosystem", args.ecosystem, prefixes)
    elif args.command == "close":
        result = complete_task(root, args.code, not args.reopen)
    else:
        result = stale_tasks(root, prefixes, args.days)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
