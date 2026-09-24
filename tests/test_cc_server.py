# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Command Center server: security contract, toggles -> 404, and the main routes end to end."""
import http.client
import json
import sys
import threading
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.server import app as ccapp  # noqa: E402

CONFIG = {
    "brands": [{"id": "canal", "name": "Canal Demo", "task_prefix": "CAN", "kind": "personal-brand"},
               {"id": "tienda", "name": "Tienda Demo", "task_prefix": "TDA"}],
    "vida": {"habits": [{"id": "leer", "label": "Leer"}]},
}


class Client:
    def __init__(self, app):
        self.app, self.cookie = app, None
        self.host = f"127.0.0.1:{app.port}"

    def request(self, method, path, body=None, headers=None, cookie=True, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.app.port, timeout=5)
        h = {"Host": host or self.host}
        if cookie and self.cookie:
            h["Cookie"] = self.cookie
        if body is not None:
            h.update({"Content-Type": "application/json", "Origin": f"http://{self.host}"})
            body = json.dumps(body) if not isinstance(body, (bytes, str)) else body
        h.update(headers or {})
        h = {k: v for k, v in h.items() if v is not None}  # a None header means "do not send it"
        conn.request(method, path, body=body, headers=h)
        r = conn.getresponse()
        data = r.read()
        conn.close()
        try:
            payload = json.loads(data)
        except ValueError:
            payload = data
        return r.status, dict(r.getheaders()), payload

    def login(self):
        status, headers, _ = self.request("GET", f"/?token={self.app.mint_token()}", cookie=False)
        assert status == 303
        self.cookie = headers["Set-Cookie"].split(";", 1)[0]
        return headers

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, body, **kw):
        return self.request("POST", path, body=body, **kw)


@pytest.fixture
def server(tmp_path):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/cc.config.json").write_text(json.dumps(CONFIG), encoding="utf-8")
    (tmp_path / ".kit/cc/server").mkdir(parents=True)
    (tmp_path / ".kit/cc/config").mkdir(parents=True)
    (tmp_path / ".kit/cc/web").mkdir(parents=True)
    (tmp_path / ".kit/cc/web/index.html").write_text("<!doctype html><title>CC</title>", encoding="utf-8")
    (tmp_path / ".kit/cc/server/secret.js").write_text("nope", encoding="utf-8")
    (tmp_path / ".kit/cc/config/defaults.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".kit/cc/web/.hidden.js").write_text("nope", encoding="utf-8")
    srv, app = ccapp.make_server(tmp_path)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    client = Client(app)
    yield client, tmp_path
    srv.shutdown()
    srv.server_close()


def set_config(tmp_path, cfg):
    path = tmp_path / ".kit-personal/cc.config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    t = time.time() + 5
    import os
    os.utime(path, (t, t))  # force a new mtime even on coarse filesystems


# ---------------------------------------------------------------- security
def test_binds_loopback_on_os_assigned_port(server):
    client, _ = server
    assert client.app.port > 0
    srv, app = ccapp.make_server(server[1])
    try:
        assert srv.server_address[0] == "127.0.0.1" and app.port not in (0, client.app.port)
    finally:
        srv.server_close()


def test_host_must_match_exactly(server):
    client, _ = server
    client.login()
    assert client.get("/api/status")[0] == 200
    assert client.get("/api/status", host=f"localhost:{client.app.port}")[0] == 200
    for bad in ("evil.test", f"127.0.0.1:{client.app.port + 1}", "127.0.0.1", f"attacker.test:{client.app.port}"):
        assert client.get("/api/status", host=bad)[0] == 403
        assert client.post("/api/tasks", {"ecosystem": "vida", "title": "x", "source_id": "x"}, host=bad)[0] == 403


def test_token_single_use_expiring_and_cookie_flags(server):
    client, _ = server
    assert client.get("/api/status", cookie=False)[0] == 401
    assert client.get("/")[0] == 401
    token = client.app.mint_token()
    status, headers, _ = client.get(f"/api/status?token={token}&x=1", cookie=False)
    assert status == 303 and headers["Location"] == "/api/status?x=1"
    cookie = headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie and "Path=/" in cookie
    assert client.get(f"/?token={token}", cookie=False)[0] == 403  # already used
    assert client.get("/?token=forged", cookie=False)[0] == 403
    expired = client.app.mint_token()
    client.app._tokens[expired] = time.time() - 1
    assert client.get(f"/?token={expired}", cookie=False)[0] == 403
    assert len(token) >= 43  # 32 random bytes, url-safe base64
    client.cookie = cookie.split(";", 1)[0]
    assert client.get("/api/status")[0] == 200
    client.cookie = "cc_session=forged"
    assert client.get("/api/status")[0] == 401


def test_token_is_consumed_atomically(server):
    client, _ = server
    token = client.app.mint_token()
    results = []
    threads = [threading.Thread(target=lambda: results.append(client.app.consume_token(token))) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results.count(True) == 1


def test_mutations_post_only_with_exact_origin_and_json(server):
    client, _ = server
    client.login()
    body = {"ecosystem": "vida", "title": "x", "source_id": "s"}
    assert client.get("/api/tasks/delete")[0] == 405
    assert client.request("PUT", "/api/tasks", body=body)[0] == 405
    assert client.request("DELETE", "/api/tasks")[0] == 405
    assert client.post("/api/tasks", body, headers={"Origin": "http://evil.test"})[0] == 403
    assert client.post("/api/tasks", body, headers={"Origin": "null"})[0] == 403
    assert client.post("/api/tasks", body, headers={"Origin": None})[0] == 403
    assert client.post("/api/tasks", body, headers={"Sec-Fetch-Site": "cross-site"})[0] == 403
    assert client.post("/api/tasks", body, headers={"Content-Type": "text/plain"})[0] == 415
    assert client.post("/api/tasks", "[1,2]")[0] == 400
    assert client.post("/api/tasks", "{bad")[0] == 400
    assert client.post("/api/tasks", body, cookie=False)[0] == 401
    oversized = {"Content-Length": str(ccapp.MAX_BODY_BYTES + 1)}  # rejected before reading the body
    assert client.post("/api/tasks", "{}", headers=oversized)[0] == 413
    assert client.post("/api/tasks", body)[0] == 200


def test_security_headers_on_every_response(server):
    client, _ = server
    for status, headers, _ in (client.get("/api/status", cookie=False), client.get("/x", host="evil.test")):
        csp = headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp and "script-src 'self'" in csp and "'unsafe-inline'" not in csp
        assert "frame-ancestors 'none'" in csp and "object-src 'none'" in csp
        assert headers["Referrer-Policy"] == "no-referrer" and headers["X-Content-Type-Options"] == "nosniff"


def test_static_is_confined(server):
    client, _ = server
    client.login()
    status, headers, body = client.get("/")
    assert status == 200 and b"<title>CC</title>" in body and headers["Content-Type"].startswith("text/html")
    for bad in ("/server/secret.js", "/.hidden.js", "/../.kit-personal/cc.config.json",
                "/%2e%2e/%2e%2e/.kit-personal/cc.config.json", "/..%2f..%2fetc/passwd", "/x.py", "/missing.html",
                "/%5c..%5c.kit-personal/cc.config.json", "/%2e%2e/server/secret.js", "/..%2fserver%2fsecret.js",
                "/%2e%2e/config/defaults.json", "/config/defaults.json"):
        assert client.get(bad)[0] == 404, bad


def test_lab_media_and_guion_paths_are_confined(server):
    client, _ = server
    client.login()
    item = client.post("/api/lab/item", {"brand": "canal", "tipo": "reel", "tema": "demo"})[2]["item"]
    for q in (f"brand=canal&id={item['id']}&file=../../tasks.db", "brand=canal&id=..&file=cover.jpg",
              "brand=../..&id=x&file=cover.jpg"):
        assert client.get(f"/api/lab/media?{q}")[0] in (400, 404)
    assert client.post("/api/guion/delete", {"file": "../../cc.config.json"})[0] in (400, 404)
    assert client.post("/api/lab/item", {"brand": "canal", "id": "../../x"})[0] == 400


# ---------------------------------------------------------------- toggles -> 404
def test_toggled_off_modules_answer_404_and_toggle_on_needs_no_restart(server):
    client, tmp_path = server
    client.login()
    for path in ("/api/v2/system", "/api/library", "/api/metrics?brand=canal", "/api/lab/productions"):
        assert client.get(path)[0] == 404, path
    assert client.post("/api/metrics/refresh", {"brand": "canal"})[0] == 404
    assert client.get("/api/life/habits")[0] == 200  # vida is on by default
    assert client.get("/api/lab/items?brand=tienda")[0] == 404  # marcas_extra off
    assert client.get("/api/tasks?ecosystem=tienda")[0] == 404
    set_config(tmp_path, {**CONFIG, "toggles": {"agentic": True, "vida": False, "marcas_extra": True,
                                                "biblioteca": True}})
    assert client.get("/api/v2/system")[0] == 200
    assert client.get("/api/library")[0] == 200
    assert client.get("/api/life/habits")[0] == 404
    assert client.post("/api/life/income", {"kind": "recibido", "amount": 1})[0] == 404
    assert client.get("/api/lab/items?brand=tienda")[0] == 200
    assert client.get("/api/status")[2]["modules"]["agentic"] is True


# ---------------------------------------------------------------- routes
def test_tasks_with_config_brands_and_scope(server):
    client, tmp_path = server
    client.login()
    status, _, body = client.post("/api/tasks", {"ecosystem": "canal", "title": "Guion 1", "source_id": "a"})
    assert status == 200 and body["task"]["code"] == "CAN-1"
    assert client.post("/api/tasks", {"ecosystem": "tienda", "title": "x", "source_id": "b"})[0] == 404
    assert client.post("/api/tasks", {"ecosystem": "nada", "title": "x", "source_id": "c"})[0] == 404
    assert client.post("/api/tasks/update", {"code": "CAN-1", "stage": "guion_listo"})[2]["task"]["stage"] == "guion_listo"
    assert client.post("/api/tasks/update", {"code": "CAN-1", "ecosystem": "tienda"})[0] == 404
    assert client.post("/api/tasks/complete", {"code": "CAN-1", "status": "done"})[2]["task"]["status"] == "done"
    assert [t["code"] for t in client.get("/api/tasks?ecosystem=canal")[2]["tasks"]] == ["CAN-1"]
    assert client.post("/api/tasks/delete", {"code": "NOPE-1"})[0] == 404
    assert client.post("/api/tasks/delete", {})[0] == 400


def test_creator_flow_ya_grabe(server):
    client, _ = server
    client.login()
    saved = client.post("/api/guion", {"titulo": "Mi video", "hook": "Nadie te dice esto", "cuerpo": "texto"})[2]
    task = client.post("/api/tasks", {"ecosystem": "canal", "title": "Mi video", "source_id": "v1"})[2]["task"]
    status, _, body = client.post("/api/creator/recorded", {"file": saved["file"], "brand": "canal",
                                                            "task_code": task["code"]})
    assert status == 200 and body["this_week"] == 1 and body["goal"] == 3
    assert body["recording"]["hook"] == "Nadie te dice esto"
    assert client.get("/api/guiones")[2]["guiones"][0]["dir"] == "grabados"
    assert client.get(f"/api/tasks?code={task['code']}")[2]["tasks"][0]["stage"] == "grabado"
    rid = body["recording"]["id"]
    assert client.post("/api/creator/views", {"id": rid, "views_48h": 321})[0] == 200
    assert client.get("/api/creator/hook-winner")[2]["winner"]["views_48h"] == 321
    assert client.post("/api/creator/views", {"id": rid, "views_48h": "mucho"})[0] == 400


def test_vida_and_config_routes(server):
    client, _ = server
    client.login()
    cfg = client.get("/api/config")[2]
    assert cfg["active_brands"] == ["canal"] and cfg["config"]["vida"]["habits"][0]["id"] == "leer"
    assert client.post("/api/life/habits", {"habit_id": "leer", "date": "2026-03-02"})[0] == 200
    assert client.post("/api/life/habits", {"habit_id": "otro", "date": "2026-03-02"})[0] == 400
    assert client.get("/api/life/habits?week=2026-03-04")[2]["habits"][0]["days"][0]["done"] is True
    assert client.get("/api/life/income")[2]["recurring"] == []
    status, headers, body = client.get("/api/life/export?format=csv&table=habit_log")
    assert status == 200 and headers["Content-Type"].startswith("text/csv") and b"leer" in body
    assert client.get("/api/v2/health")[0] == 200
    assert client.get("/api/recommendations")[2]["ok"] is True


def test_open_request_handshake(server, monkeypatch):
    client, tmp_path = server
    stop = threading.Event()
    threading.Thread(target=ccapp._open_request_loop, args=(client.app, stop), daemon=True).start()
    try:
        url = ccapp.request_launch_url(tmp_path)
    finally:
        stop.set()
    assert url.startswith(f"http://127.0.0.1:{client.app.port}/?token=")
    assert not (tmp_path / ".kit/cc.launch").exists()
    status, _, _ = client.get(url.split(str(client.app.port), 1)[1], cookie=False)
    assert status == 303
