# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Command Center HTTP server (stdlib only).

  python .kit/cc/server/app.py serve [--target DIR] [--port N]
  python .kit/cc/server/app.py open  [--target DIR]      # prints a fresh one-time URL

Security contract (applies to every route, not only the Lab):
- Binds 127.0.0.1 only; port 0 (OS-assigned) unless --port; the port is written to .kit/cc.port.
- Entry needs a single-use 256-bit launch token that expires after 60 s. It is exchanged
  once (atomic compare-and-delete) for an HttpOnly SameSite=Strict session cookie and the
  browser is redirected to a token-free URL.
- Every request, GET included, needs that cookie and a Host of exactly 127.0.0.1:<port>
  or localhost:<port>. Mutations are POST-only, JSON-only, and need an exact Origin.
- CSP `default-src 'self'` with no inline script; Referrer-Policy no-referrer; nosniff.
- Body size capped; every file path is confined to the data dir or the static root;
  no shell anywhere; ffprobe runs with -protocol_whitelist file,pipe.
- Routes of modules toggled off in cc.config.json answer 404, like unknown routes.
Data: TARGET/.kit-personal/data/. Static UI: TARGET/.kit/cc/web/ (repo cc/web/); server and config code
under .kit/cc/ sit outside that root and are never served.
"""
import argparse
import hashlib
import hmac
import importlib.util
import http.cookies
import json
import logging
import mimetypes
import os
import re
import secrets
import signal
import sys
import threading
import time
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import RotatingFileHandler
from pathlib import Path

if __package__ in (None, ""):  # run as a script: make `cc` importable from its parent dir
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cc.config import config  # noqa: E402
from cc.server import (assets, captions_studio, creator, guiones, health, lab, life,  # noqa: E402
                       metrics_metricool, metrics_zernio, recommendations, system_index, tasks)

MAX_BODY_BYTES = 2 * 1024 * 1024
TOKEN_TTL = 60
SESSION_TTL = 12 * 3600
COOKIE = "cc_session"  # prefix; each project gets its own name (cookies are shared across ports)
CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; "
       "media-src 'self' blob:; connect-src 'self'; font-src 'self'; object-src 'none'; "
       "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
STATIC_TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml",
                ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
                ".woff2": "font/woff2", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8"}
FONT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,80}\.woff2$")
STATIC_DENY = {"server", "config"}   # belt and braces: never serve a folder with these names
LOGGER = logging.getLogger("command_center")


class HTTPError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class App:
    def __init__(self, target, port=0):
        self.target = Path(target).resolve()
        self.kit = self.target / ".kit"
        self.data = self.target / ".kit-personal" / "data"
        self.static = self.kit / "cc" / "web"   # the UI only; .kit/cc/server and config are outside
        self.port = port
        # per project: opening project B must not replace project A's session cookie on 127.0.0.1
        self.cookie = f"{COOKIE}_{hashlib.sha256(str(self.target).encode('utf-8')).hexdigest()[:12]}"
        self._lock = threading.Lock()
        self._tokens = {}          # token -> expiry
        self._sessions = {}        # session id -> expiry
        self._cfg, self._cfg_key = None, None
        self.started_at = time.time()

    # ------------------------------------------------------------ config (reloaded on change)
    def cfg(self):
        path = self.target / config.CONFIG_REL
        try:
            key = path.stat().st_mtime_ns
        except OSError:
            key = None
        with self._lock:
            if self._cfg is None or key != self._cfg_key:
                self._cfg, self._cfg_key = config.load(self.target), key
            return self._cfg

    # ------------------------------------------------------------ launch tokens and sessions
    def mint_token(self):
        token = secrets.token_urlsafe(32)  # 256 bits
        with self._lock:
            now = time.time()
            self._tokens = {t: e for t, e in self._tokens.items() if e > now}
            self._tokens[token] = now + TOKEN_TTL
        return token

    def launch_url(self):
        return f"http://127.0.0.1:{self.port}/?token={self.mint_token()}"

    def consume_token(self, token):
        with self._lock:  # compare-and-delete under the lock: a token works exactly once
            expiry = self._tokens.pop(token, None) if isinstance(token, str) else None
        return expiry is not None and expiry > time.time()

    def new_session(self):
        sid = secrets.token_urlsafe(32)
        with self._lock:
            self._sessions[sid] = time.time() + SESSION_TTL
        return sid

    def session_ok(self, sid):
        if not sid:
            return False
        with self._lock:
            now = time.time()
            for known, expiry in list(self._sessions.items()):
                if expiry <= now:
                    del self._sessions[known]
            return any(hmac.compare_digest(sid, known) for known in self._sessions)

    def allowed_hosts(self):
        return {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}

    def allowed_origins(self):
        return {f"http://{h}" for h in self.allowed_hosts()}

    # ------------------------------------------------------------ scope helpers
    def ecosystems(self, cfg):
        """Task ecosystems visible right now (toggles applied)."""
        visible = [b["id"] for b in config.active_brands(cfg)]
        return visible + ([config.VIDA_ECOSYSTEM] if config.enabled(cfg, "vida") else [])

    def brand(self, cfg, value):
        if value not in {b["id"] for b in config.active_brands(cfg)}:
            raise HTTPError(404, "marca no encontrada")
        return value


# ============================================================ route handlers
# Each takes (app, cfg, q) where q is the query dict (GET) or the JSON body (POST).
def _p(q, key, default=None):
    value = q.get(key, default)
    return value[0] if isinstance(value, list) else value


def status(app, cfg, q):
    return {"ok": True, "started_at": app.started_at,
            "modules": {m: config.enabled(cfg, m) for m in config.MODULES}}


def get_config(app, cfg, q):
    active = [b["id"] for b in config.active_brands(cfg)]
    return {"ok": True, "config": cfg, "active_brands": active,
            "logos": assets.brands_with_logo(str(app.data), active)}


def set_toggle(app, cfg, body):
    """Flip one module on or off; the next request already sees it (config reloads on change)."""
    with app._lock:
        config.write_toggle(app.target, body.get("module"), body.get("on"))
        app._cfg = None  # coarse file clocks (FAT, SMB) may keep the same mtime
    return get_config(app, app.cfg(), {})


def hooks_bank(app, cfg, q):
    return {"ok": True, "bank": assets.hooks_bank(str(app.kit))}


def brand_logo(app, cfg, q):
    path = assets.logo_path(str(app.data), app.brand(cfg, _p(q, "brand")))
    if not path:
        raise FileNotFoundError("logo")
    return ("file", path)


def upload_logo(app, cfg, body):
    return {"ok": True, **assets.save_logo(str(app.data), app.brand(cfg, body.get("brand")), body.get("data"))}


# ---- caption studio (module `subtitulos`)
def cs_presets(app, cfg, q):
    return {"ok": True, **captions_studio.list_presets(app.kit, str(app.data))}


def cs_videos(app, cfg, q):
    return {"ok": True, "videos": captions_studio.list_videos(str(app.data)),
            "folder": ".kit-personal/data/captions/"}


def cs_transcript(app, cfg, q):
    return {"ok": True, "transcript": captions_studio.get_transcript(str(app.data), _p(q, "file"))}


def cs_transcript_post(app, cfg, body):
    if "words" in body:
        tr = captions_studio.save_words(str(app.data), body.get("file"), body["words"])
    else:
        tr = captions_studio.transcribe(app.kit, str(app.data), body.get("file"), body.get("lang"))
    return {"ok": True, "transcript": tr}


def cs_video(app, cfg, q):
    return ("file", captions_studio.video_path(str(app.data), _p(q, "file")))


def cs_output(app, cfg, q):
    return ("file", captions_studio.output_path(str(app.data), _p(q, "file")))


def cs_render(app, cfg, body):
    return {"ok": True, **captions_studio.render(app.kit, str(app.data), body)}


def cs_save_preset(app, cfg, body):
    return {"ok": True, **captions_studio.save_preset(app.kit, str(app.data), body.get("name"), body.get("preset"))}


def get_health(app, cfg, q):
    return health.collect(str(app.data), cfg)


def _task_scope(app, cfg, code):
    if not isinstance(code, str) or not code:
        raise ValueError("code requerido")
    found = tasks.list_tasks(str(app.data), config.task_prefixes(cfg), code=code)
    if not found or found[0]["ecosystem"] not in app.ecosystems(cfg):
        raise HTTPError(404, "tarea no encontrada")
    return found[0]


def list_tasks_route(app, cfg, q):
    visible, eco = app.ecosystems(cfg), _p(q, "ecosystem")
    if eco and eco not in visible:
        raise HTTPError(404, "ecosystem no encontrado")
    rows = tasks.list_tasks(str(app.data), config.task_prefixes(cfg), ecosystem=eco,
                            statuses=_p(q, "status"), code=_p(q, "code"))
    return {"ok": True, "tasks": [t for t in rows if t["ecosystem"] in visible]}


def create_task(app, cfg, body):
    if body.get("ecosystem") not in app.ecosystems(cfg):
        raise HTTPError(404, "ecosystem no encontrado")
    allowed = {"source_id", "ecosystem", "title", "status", "priority", "stage", "area", "due_date",
               "notes", "handoff", "parent_id"}
    return {"ok": True, "task": tasks.save_task(str(app.data), {k: v for k, v in body.items() if k in allowed},
                                                config.task_prefixes(cfg), source="ui", actor="ui")}


def update_task(app, cfg, body):
    body = dict(body)
    code = body.pop("code", None)
    if not isinstance(code, str) or len(body) != 1:
        raise ValueError("code y exactamente un campo requeridos")
    _task_scope(app, cfg, code)
    field, value = next(iter(body.items()))
    if field == "ecosystem" and value not in app.ecosystems(cfg):
        raise HTTPError(404, "ecosystem no encontrado")
    return {"ok": True, "task": tasks.update_task(str(app.data), code, field, value,
                                                  config.task_prefixes(cfg), "ui")}


def complete_task(app, cfg, body):
    _task_scope(app, cfg, body.get("code"))
    return {"ok": True, "task": tasks.set_status(str(app.data), body["code"], body.get("status"), "ui")}


def delete_task(app, cfg, body):
    _task_scope(app, cfg, body.get("code"))
    return {"ok": True, **tasks.delete_task(str(app.data), body["code"], "ui")}


def link_task(app, cfg, body):
    _task_scope(app, cfg, body.get("code"))
    return {"ok": True, "task": tasks.link_task(str(app.data), body["code"], body.get("node_id"),
                                                body.get("action", "add"), "ui")}


def list_guiones(app, cfg, q):
    return {"ok": True, "guiones": guiones.list_all(str(app.data))}


def save_guion(app, cfg, body):
    return {"ok": True, **guiones.save(str(app.data), body)}


def favorite_guion(app, cfg, body):
    return {"ok": True, **guiones.toggle_favorite(str(app.data), body.get("file"))}


def delete_guion(app, cfg, body):
    return {"ok": True, **guiones.delete(str(app.data), body.get("file"))}


def save_hooks(app, cfg, body):
    return {"ok": True, **guiones.save_hooks(str(app.data), body)}


def lab_items(app, cfg, q):
    return {"ok": True, "items": lab.list_items(str(app.data), app.brand(cfg, _p(q, "brand")))}


def lab_save_item(app, cfg, body):
    body = dict(body)
    brand = app.brand(cfg, body.pop("brand", None))
    return {"ok": True, "item": lab.save_item(str(app.data), body, brand)}


def lab_archive(app, cfg, body):
    brand = app.brand(cfg, body.get("brand"))
    return {"ok": True, **lab.archive_item(str(app.data), body.get("id"), body.get("archivar", True), brand)}


def lab_delete(app, cfg, body):
    brand = app.brand(cfg, body.get("brand"))
    return {"ok": True, **lab.delete_item(str(app.data), body.get("id"), brand)}


def lab_idea_request(app, cfg, body):
    app.brand(cfg, body.get("brand"))
    return {"ok": True, "order": lab.create_idea_request(str(app.data), body)}


def lab_translation_packet(app, cfg, q):
    brand = app.brand(cfg, _p(q, "brand"))
    return {"ok": True, "packet": lab.translation_packet(str(app.data), _p(q, "id"), brand,
                                                         cfg["locale"]["language"])}


def lab_apply_translation(app, cfg, body):
    brand = app.brand(cfg, body.get("brand"))
    return {"ok": True, "item": lab.apply_translation(str(app.data), body.get("id"), brand, body.get("campos"),
                                                      cfg["locale"]["language"])}


def lab_media(app, cfg, q):
    brand = app.brand(cfg, _p(q, "brand"))
    return ("file", lab.media_path(str(app.data), brand, _p(q, "id"), _p(q, "file")))


def lab_final_video(app, cfg, q):
    brand = app.brand(cfg, _p(q, "brand"))
    return ("file", lab.final_media_path(str(app.data), _p(q, "id"), brand))


def creator_summary(app, cfg, q):
    return {"ok": True, **creator.summary(str(app.data), cfg)}


def creator_recordings(app, cfg, q):
    return {"ok": True, "recordings": creator.list_recordings(str(app.data))}


def creator_hook_winner(app, cfg, q):
    return {"ok": True, **creator.hook_winner(str(app.data), cfg, _p(q, "week"))}


def creator_recorded(app, cfg, body):
    """«Ya grabé»: moves the script to grabados, marks the linked task, adds to the streak."""
    brand = body.get("brand")
    if brand is not None:
        app.brand(cfg, brand)
    title, hook = body.get("title"), body.get("hook")
    task_code = body.get("task_code")
    if body.get("file"):
        guiones.save(str(app.data), {"file": body["file"], "estado": "grabado"})
        found = next(g for g in guiones.list_all(str(app.data)) if g["file"] == os.path.basename(body["file"]))
        title, hook = title or found["titulo"], hook or found["hook"]
        task_code = task_code or found.get("task_code")  # the board card linked when the script was created
    if task_code:
        try:
            _task_scope(app, cfg, task_code)
        except HTTPError:
            if not body.get("task_code"):
                task_code = None  # a stale link in an old script never blocks «Ya grabé»
            else:
                raise
    if task_code:
        tasks.update_task(str(app.data), task_code, "stage", "grabado", config.task_prefixes(cfg), "ui")
    recording = creator.add_recording(str(app.data), cfg, {"title": title, "hook": hook, "brand": brand,
                                                            "script_file": body.get("file"), "date": body.get("date"),
                                                            "task_code": task_code,
                                                            "request_key": body.get("request_key")})
    return {"ok": True, "recording": recording, **creator.summary(str(app.data), cfg)}


def creator_views(app, cfg, body):
    return {"ok": True, "recording": creator.set_views(str(app.data), body.get("id"), body.get("views_48h"))}


def get_recommendations(app, cfg, q):
    return {"ok": True, **recommendations.run(str(app.data), cfg)}


# ---- vida
def life_tasks(app, cfg, q):
    return {"ok": True, "tasks": life.list_tasks(str(app.data), cfg, status=_p(q, "status"))}


def life_habits(app, cfg, q):
    week = _p(q, "week") or config.today(cfg).isoformat()
    return {"ok": True, **life.week_matrix(str(app.data), cfg, week), "consistency": life.consistency(str(app.data), cfg)}


def life_income(app, cfg, q):
    return {"ok": True, **life.income_month_view(str(app.data), cfg, _p(q, "year"), _p(q, "month"))}


def life_today(app, cfg, q):
    return {"ok": True, **life.today_summary(str(app.data), cfg)}


def life_goals(app, cfg, q):
    return {"ok": True, "goals": life.seed_milestones(str(app.data), cfg)}


def life_income_history(app, cfg, q):
    return {"ok": True, "history": life.income_history(str(app.data), cfg), "goal": cfg["vida"]["income_goal"],
            "currency": cfg["vida"]["currency"]}


def life_export(app, cfg, q):
    if _p(q, "format", "json") == "csv":
        table = _p(q, "table", "tasks")
        return ("bytes", life.export_csv(str(app.data), table).encode("utf-8"), "text/csv; charset=utf-8",
                f"{table}.csv")
    return {"ok": True, **life.export_json(str(app.data))}


def life_save_task(app, cfg, body):
    return {"ok": True, "task": life.save_task(str(app.data), body)}


def life_complete_task(app, cfg, body):
    return {"ok": True, "task": life.complete_task(str(app.data), body.get("id"), bool(body.get("done", True)))}


def life_delete_task(app, cfg, body):
    return {"ok": True, **life.delete_task(str(app.data), cfg, body.get("id"))}


def life_toggle_habit(app, cfg, body):
    return {"ok": True, **life.toggle_habit(str(app.data), cfg, body.get("habit_id"), body.get("date"),
                                            bool(body.get("done", True)))}


def life_add_income(app, cfg, body):
    return {"ok": True, "entry": life.add_income_entry(str(app.data), cfg, body)}


def life_save_goal(app, cfg, body):
    return {"ok": True, "goal": life.save_goal(str(app.data), body)}


def life_complete_goal(app, cfg, body):
    return {"ok": True, "goal": life.complete_goal(str(app.data), body.get("id"), bool(body.get("done", True)))}


def life_delete_goal(app, cfg, body):
    return {"ok": True, **life.delete_goal(str(app.data), body.get("id"), cfg)}


# ---- advanced production
def lab_productions(app, cfg, q):
    brand = _p(q, "brand")
    return {"ok": True, "productions": lab.list_productions(str(app.data), app.brand(cfg, brand) if brand else None)}


def lab_production(app, cfg, q):
    return {"ok": True, "production": lab.get_production(str(app.data), _p(q, "id"), _p(q, "revision"))}


def lab_revisions(app, cfg, q):
    return {"ok": True, "revisions": lab.list_production_revisions(str(app.data), _p(q, "id"))}


def lab_templates(app, cfg, q):
    return {"ok": True, "templates": lab.list_templates(str(app.data))}


def lab_orders(app, cfg, q):
    return {"ok": True, "orders": lab.list_orders(str(app.data), _p(q, "production_id"))}


def lab_save_production(app, cfg, body):
    brands = {b["id"] for b in config.active_brands(cfg)}
    return {"ok": True, "production": lab.save_production(str(app.data), body, brands)}


def lab_save_template(app, cfg, body):
    return {"ok": True, "template": lab.save_template(str(app.data), body)}


def lab_create_order(app, cfg, body):
    return {"ok": True, "order": lab.create_order(str(app.data), body.get("production_id"),
                                                  body.get("expected_revision"), body.get("purpose", "production"))}


# ---- library, metrics, agentic
def library(app, cfg, q):
    return {"ok": True, **lab.component_catalog(app.kit)}


def _metrics_path(app, brand):
    return app.data / "metrics" / f"{brand}.json"


def get_metrics(app, cfg, q):
    brand = app.brand(cfg, _p(q, "brand"))
    try:
        return {"ok": True, "metrics": json.loads(_metrics_path(app, brand).read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return {"ok": True, "metrics": None}


def _secret(app, name):
    for engines in (app.kit / "engines", Path(__file__).resolve().parents[2] / "engines"):
        path = engines / "kit_secrets.py"
        if path.is_file():
            import importlib.util
            spec = importlib.util.spec_from_file_location("kit_secrets", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.get_secret(name)
    return None


def refresh_metrics(app, cfg, body):
    brand = next(b for b in cfg["brands"] if b["id"] == app.brand(cfg, body.get("brand")))
    provider = brand["metrics"]["provider"]
    if provider == "metricool":
        feed = metrics_metricool.fetch(brand, _secret(app, metrics_metricool.SECRET), cfg["locale"]["timezone"])
    elif provider == "zernio":
        feed = metrics_zernio.fetch(brand, _secret(app, metrics_zernio.SECRET))
    else:
        raise ValueError("esta marca no tiene conector de métricas; cargá las vistas a mano")
    path = _metrics_path(app, brand["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return {"ok": True, "metrics": feed}


def get_system(app, cfg, q):
    return system_index.build(app.target, tasks.db_path(str(app.data)))


def get_source(app, cfg, q):
    index = system_index.build(app.target)
    try:
        return system_index.source(app.target, index, _p(q, "id"))
    except ValueError:
        raise HTTPError(403, "ruta fuera del proyecto")


GET_ROUTES = {
    "/api/status": ("core", status), "/api/config": ("core", get_config), "/api/v2/health": ("core", get_health),
    "/api/tasks": ("core", list_tasks_route), "/api/guiones": ("core", list_guiones),
    "/api/lab/items": ("core", lab_items), "/api/lab/media": ("core", lab_media),
    "/api/lab/final-video": ("core", lab_final_video), "/api/lab/translation-packet": ("core", lab_translation_packet),
    "/api/creator/summary": ("core", creator_summary), "/api/creator/recordings": ("core", creator_recordings),
    "/api/creator/hook-winner": ("core", creator_hook_winner), "/api/recommendations": ("core", get_recommendations),
    "/api/life/tasks": ("vida", life_tasks), "/api/life/habits": ("vida", life_habits),
    "/api/life/income": ("vida", life_income), "/api/life/today": ("vida", life_today),
    "/api/life/export": ("vida", life_export), "/api/life/goals": ("vida", life_goals),
    "/api/life/income-history": ("vida", life_income_history),
    "/api/lab/productions": ("produccion_avanzada", lab_productions),
    "/api/lab/production": ("produccion_avanzada", lab_production),
    "/api/lab/revisions": ("produccion_avanzada", lab_revisions),
    "/api/lab/templates": ("produccion_avanzada", lab_templates),
    "/api/lab/orders": ("produccion_avanzada", lab_orders),
    "/api/library": ("biblioteca", library),
    "/api/metrics": ("metricas", get_metrics),
    "/api/v2/system": ("agentic", get_system), "/api/v2/source": ("agentic", get_source),
    "/api/hooks-bank": ("core", hooks_bank), "/api/brand/logo": ("core", brand_logo),
    "/api/captions/presets": ("subtitulos", cs_presets), "/api/captions/videos": ("subtitulos", cs_videos),
    "/api/captions/transcript": ("subtitulos", cs_transcript), "/api/captions/video": ("subtitulos", cs_video),
    "/api/captions/output": ("subtitulos", cs_output),
}
POST_ROUTES = {
    "/api/tasks": ("core", create_task), "/api/tasks/update": ("core", update_task),
    "/api/tasks/complete": ("core", complete_task), "/api/tasks/delete": ("core", delete_task),
    "/api/tasks/link": ("core", link_task),
    "/api/guion": ("core", save_guion), "/api/guion/favorite": ("core", favorite_guion),
    "/api/guion/delete": ("core", delete_guion), "/api/guion/hooks": ("core", save_hooks),
    "/api/lab/item": ("core", lab_save_item), "/api/lab/archive": ("core", lab_archive),
    "/api/lab/delete": ("core", lab_delete), "/api/lab/idea-request": ("core", lab_idea_request),
    "/api/lab/translation": ("core", lab_apply_translation),
    "/api/creator/recorded": ("core", creator_recorded), "/api/creator/views": ("core", creator_views),
    "/api/life/tasks": ("vida", life_save_task), "/api/life/tasks/complete": ("vida", life_complete_task),
    "/api/life/tasks/delete": ("vida", life_delete_task), "/api/life/habits": ("vida", life_toggle_habit),
    "/api/life/income": ("vida", life_add_income), "/api/life/goals": ("vida", life_save_goal),
    "/api/life/goals/complete": ("vida", life_complete_goal), "/api/life/goals/delete": ("vida", life_delete_goal),
    "/api/lab/production": ("produccion_avanzada", lab_save_production),
    "/api/lab/template": ("produccion_avanzada", lab_save_template),
    "/api/lab/order": ("produccion_avanzada", lab_create_order),
    "/api/metrics/refresh": ("metricas", refresh_metrics),
    "/api/config/toggle": ("core", set_toggle), "/api/brand/logo": ("core", upload_logo),
    "/api/captions/transcript": ("subtitulos", cs_transcript_post),
    "/api/captions/render": ("subtitulos", cs_render), "/api/captions/save-preset": ("subtitulos", cs_save_preset),
}


# ============================================================ HTTP layer
class Handler(BaseHTTPRequestHandler):
    server_version = "cc"
    sys_version = ""
    app: App = None  # set by make_server

    def log_message(self, fmt, *args):  # never the query string: it may hold a launch token
        LOGGER.info(json.dumps({"at": time.time(), "event": "http", "method": self.command,
                                "path": self.path.split("?", 1)[0], "status": args[1] if len(args) > 1 else None}))

    def end_headers(self):
        for name, value in (("Content-Security-Policy", CSP), ("Referrer-Policy", "no-referrer"),
                            ("X-Content-Type-Options", "nosniff"), ("X-Frame-Options", "DENY"),
                            ("Cross-Origin-Opener-Policy", "same-origin"),
                            ("Cross-Origin-Resource-Policy", "same-origin"), ("Cache-Control", "no-store")):
            self.send_header(name, value)
        super().end_headers()

    def _json(self, code, obj, extra=()):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _host_ok(self):
        return self.headers.get("Host", "") in self.app.allowed_hosts()

    def _session_ok(self):
        jar = http.cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
        except http.cookies.CookieError:
            return False
        name = self.app.cookie
        return name in jar and self.app.session_ok(jar[name].value)

    def _deny(self, code, message):
        self._json(code, {"ok": False, "error": message})

    # ---------------------------------------------------------------- methods
    def do_GET(self):
        path, _, query = self.path.partition("?")
        if not self._host_ok():
            return self._deny(403, "Host no permitido")
        params = urllib.parse.parse_qs(query, keep_blank_values=True)
        if "token" in params:
            if not self.app.consume_token(params["token"][0]):
                return self._deny(403, "enlace vencido o ya usado; abrí el Command Center de nuevo")
            rest = urllib.parse.urlencode([(k, v) for k, vs in params.items() if k != "token" for v in vs])
            self.send_response(303)
            self.send_header("Set-Cookie",
                             f"{self.app.cookie}={self.app.new_session()}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Location", path + ("?" + rest if rest else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if not self._session_ok():
            return self._deny(401, "sesión requerida; abrí el Command Center desde su enlace")
        if path.startswith("/api/"):
            if path in POST_ROUTES and path not in GET_ROUTES:
                return self._deny(405, "usar POST")
            return self._dispatch(GET_ROUTES, path, params)
        return self._static(path)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not self._host_ok():
            return self._deny(403, "Host no permitido")
        if not self._session_ok():
            return self._deny(401, "sesión requerida")
        if self.headers.get("Origin") not in self.app.allowed_origins() or \
                self.headers.get("Sec-Fetch-Site", "same-origin") not in ("same-origin", "none"):
            return self._deny(403, "origen no permitido")
        if (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower() != "application/json":
            return self._deny(415, "Content-Type debe ser application/json")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._deny(400, "Content-Length inválido")
        if length < 0:
            return self._deny(400, "Content-Length inválido")
        if length > MAX_BODY_BYTES:
            return self._deny(413, "cuerpo demasiado grande")
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}") if length else {}
        except (ValueError, UnicodeDecodeError):
            return self._deny(400, "JSON inválido")
        if not isinstance(body, dict):
            return self._deny(400, "se esperaba un objeto JSON")
        if path in GET_ROUTES and path not in POST_ROUTES:
            return self._deny(405, "usar GET")
        return self._dispatch(POST_ROUTES, path, body)

    def _not_allowed(self):
        self._deny(405, "método no permitido")

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _not_allowed

    # ---------------------------------------------------------------- dispatch
    def _dispatch(self, routes, path, q):
        cfg = self.app.cfg()
        route = routes.get(path)
        if route is None or not config.enabled(cfg, route[0]):
            return self._deny(404, "unknown endpoint")  # toggled-off looks exactly like unknown
        try:
            result = route[1](self.app, cfg, q)
        except HTTPError as e:
            return self._deny(e.code, str(e))
        except lab.RevisionConflict as e:
            return self._deny(409, str(e))
        except FileNotFoundError:
            return self._deny(404, "no encontrado")
        except (ValueError, TypeError, KeyError) as e:
            return self._deny(400, str(e) if isinstance(e, ValueError) else "pedido inválido")
        except RuntimeError as e:
            return self._deny(423, str(e))
        except Exception as e:  # noqa: BLE001 - never leak a traceback to the page
            LOGGER.error(json.dumps({"at": time.time(), "event": "handler_error", "path": path,
                                     "error": type(e).__name__}))
            return self._deny(500, "error interno (ver el registro)")
        if isinstance(result, tuple) and result[0] == "file":
            return self._send_file(result[1])
        if isinstance(result, tuple) and result[0] == "bytes":
            _, data, ctype, filename = result
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return self._json(200, result)

    def _send_file(self, path):
        path = str(path)
        size = os.path.getsize(path)
        ctype = STATIC_TYPES.get(Path(path).suffix.lower()) or mimetypes.guess_type(path)[0] or \
            "application/octet-stream"
        if Path(path).suffix.lower() == ".mp4":
            ctype = "video/mp4"
        start, end = 0, size - 1
        range_header = self.headers.get("Range")
        if range_header:
            m = re.fullmatch(r"bytes=(\d+)-(\d*)", range_header)
            if m:
                start, end = int(m.group(1)), int(m.group(2) or size - 1)
            if not m or start > end or end >= size:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as source:
            source.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def _static(self, path):
        rel = urllib.parse.unquote(path).lstrip("/") or "index.html"
        parts = Path(rel).parts
        if parts and parts[0] == "fonts":  # the kit's OFL fonts (.kit/fonts), woff2 only, one level
            name = parts[-1] if len(parts) == 2 else ""
            root = os.path.realpath(self.app.kit / "fonts")
            resolved = os.path.realpath(os.path.join(root, name)) if FONT_RE.fullmatch(name) else ""
            if not resolved or os.path.dirname(resolved) != root or not os.path.isfile(resolved):
                return self._deny(404, "no encontrado")
            return self._send_file(resolved)
        if (not parts or parts[0] in STATIC_DENY or any(p.startswith(".") or p in ("..", "") for p in parts)
                or "\\" in rel or "\x00" in rel or Path(rel).suffix.lower() not in STATIC_TYPES):
            return self._deny(404, "no encontrado")
        root = os.path.realpath(self.app.static)
        resolved = os.path.realpath(os.path.join(root, rel))
        if os.path.commonpath((root, resolved)) != root or not os.path.isfile(resolved):
            return self._deny(404, "no encontrado")
        return self._send_file(resolved)


# ============================================================ process
def configure_logging(app):
    (app.data / "logs").mkdir(parents=True, exist_ok=True)
    for handler in LOGGER.handlers[:]:
        LOGGER.removeHandler(handler)
        handler.close()
    handler = RotatingFileHandler(app.data / "logs" / "server.log", maxBytes=1024 * 1024, backupCount=3,
                                  encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False


def make_server(target, port=0):
    """Bind 127.0.0.1 and record the real port. Returns (server, app)."""
    app = App(target, port)
    handler = type("BoundHandler", (Handler,), {"app": app})
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server.daemon_threads = True
    app.port = server.server_address[1]
    app.data.mkdir(parents=True, exist_ok=True)
    configure_logging(app)
    return server, app


def _write_private(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def _open_request_loop(app, stop):
    """The launcher asks for a fresh one-time URL by creating .kit/cc.open-request."""
    request, answer = app.kit / "cc.open-request", app.kit / "cc.launch"
    while not stop.wait(0.3):
        if request.exists():
            try:
                request.unlink()
            except OSError:
                continue
            _write_private(answer, app.launch_url() + "\n")


def _ow():
    """engines/onboard_write.py next to cc/ (.kit/engines when installed): the kit's lock and marker code."""
    path = Path(__file__).resolve().parents[2] / "engines" / "onboard_write.py"
    spec = importlib.util.spec_from_file_location("kit_onboard_write", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class AlreadyRunning(SystemExit):
    pass


def claim(app):
    """Register this server as the project's one live Command Center, under the kit's lifecycle
    lock (.kit.lock), so install/update/uninstall never race a starting server. Returns the marker."""
    ow = _ow()
    try:
        lock = ow.create_lock(app.target, "serve")
    except FileExistsError:
        raise AlreadyRunning("otro comando del kit está trabajando en este proyecto (.kit.lock); "
                             "esperá a que termine y volvé a abrir el Command Center.")
    lock_path = app.target / ow.LOCK
    try:
        live = ow.cc_live(app.target)
        if live:
            raise AlreadyRunning(f"el Command Center de este proyecto ya está corriendo (pid {live['pid']}"
                                 f"{', puerto ' + str(live['port']) if live.get('port') else ''}). "
                                 "Pedí un enlace con `python .kit/launch.py open --browser`.")
        marker = {"pid": os.getpid(), "start": ow.proc_start(os.getpid()), "nonce": uuid.uuid4().hex,
                  "port": app.port}
        _write_private(app.kit / "cc.running", json.dumps(marker) + "\n")
        _write_private(app.kit / "cc.port", f"{app.port}\n")
        return marker
    finally:
        try:
            if json.loads(lock_path.read_text(encoding="utf-8")).get("nonce") == lock["nonce"]:
                lock_path.unlink()
        except (OSError, ValueError):
            pass


def release(app, marker):
    """Remove the marker and port file only if they are still ours (pid + nonce)."""
    cur = _ow().cc_marker(app.target) or {}
    if cur.get("pid") == marker["pid"] and cur.get("nonce") == marker["nonce"]:
        for name in ("cc.running", "cc.port"):
            try:
                (app.kit / name).unlink()
            except OSError:
                pass


def serve(target, port=0, print_url=True):
    server, app = make_server(target, port)
    try:
        marker = claim(app)
    except AlreadyRunning:
        server.server_close()
        raise
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # service stop still cleans up below
    stop = threading.Event()
    threading.Thread(target=_open_request_loop, args=(app, stop), daemon=True).start()
    LOGGER.info(json.dumps({"at": time.time(), "event": "server_started", "port": app.port}))
    if print_url:
        print(f"Command Center: {app.launch_url()}  (enlace de un solo uso, vence en {TOKEN_TTL} s)", flush=True)
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()
        release(app, marker)


def request_launch_url(target, timeout=5.0):
    kit = Path(target).resolve() / ".kit"
    answer = kit / "cc.launch"
    try:
        answer.unlink()
    except OSError:
        pass
    _write_private(kit / "cc.open-request", "1\n")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if answer.exists():
            url = answer.read_text(encoding="utf-8").strip()
            answer.unlink()
            return url
        time.sleep(0.1)
    return None


def _default_target():
    here = Path(__file__).resolve()  # TARGET/.kit/cc/server/app.py when installed
    return here.parents[3] if here.parents[2].name == ".kit" else Path.cwd()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Command Center local")
    parser.add_argument("command", choices=("serve", "open"), nargs="?", default="serve")
    parser.add_argument("--target", default=None, help="carpeta del proyecto (por defecto, la del kit instalado)")
    parser.add_argument("--port", type=int, default=0, help="0 = el sistema elige un puerto libre")
    parser.add_argument("--no-print-url", action="store_true", help="para el servicio de fondo")
    parser.add_argument("--browser", action="store_true", help="con `open`: abrir el navegador")
    args = parser.parse_args(argv)
    target = Path(args.target) if args.target else _default_target()
    if args.command == "serve":
        try:
            serve(target, args.port, not args.no_print_url)
        except AlreadyRunning as e:
            print(f"No arranco: {e.code}", file=sys.stderr)
            return 3
        return 0
    url = request_launch_url(target)
    if not url:
        print("El Command Center no está corriendo (no respondió en 5 s).", file=sys.stderr)
        return 1
    if args.browser:
        import webbrowser
        webbrowser.open(url)
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
