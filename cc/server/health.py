# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Bounded, read-only health snapshot. Never touches anything outside the data dir."""
import datetime as dt
import os

MAX_LOG_BYTES = 2 * 1024 * 1024
LOG_REL = os.path.join("logs", "server.log")


def _record(source_id, label, status, updated_at=None, error=None):
    return {"id": source_id, "label": label, "status": status, "source": source_id,
            "updated_at": updated_at, "error": error}


def _log_health(root):
    try:
        stat = os.stat(os.path.join(root, LOG_REL))
    except FileNotFoundError:
        return _record("server_log", "Registro del servidor", "failed", error="missing")
    except OSError:
        return _record("server_log", "Registro del servidor", "failed", error="unreadable")
    too_big = stat.st_size > MAX_LOG_BYTES
    return _record("server_log", "Registro del servidor", "failed" if too_big else "ok",
                   dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).isoformat(),
                   "log exceeds size limit" if too_big else None)


def _warnings_health(cfg):
    warnings = cfg.get("_warnings") or []
    return _record("config", "Configuración", "stale" if warnings else "ok",
                   error=f"{len(warnings)} campos ignorados" if warnings else None)


def collect(root, cfg, now=None):
    sources = [_log_health(root), _warnings_health(cfg)]
    statuses = {s["status"] for s in sources}
    overall = "failed" if "failed" in statuses else "degraded" if "stale" in statuses else "ok"
    return {"version": 2, "generated_at": (now or dt.datetime.now(dt.timezone.utc)).isoformat(),
            "overall": overall, "sources": sources}
