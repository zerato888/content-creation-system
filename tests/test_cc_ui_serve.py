# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""The real UI served by the real server: login link -> shell, every module loads, the API
calls of the default views answer 200, and toggled-off views' routes stay 404."""
import http.client
import json
import re
import shutil
import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.server import app as ccapp  # noqa: E402

CONFIG = {
    "brands": [{"id": "canal", "name": "Canal Demo", "task_prefix": "CAN", "kind": "personal-brand", "accent": "#3fb8a9"}],
    "vida": {"currency": "EUR", "income_goal": 3000, "habits": [{"id": "leer", "label": "Leer"}],
             "milestones": [{"id": "m1", "label": "Primer video"}]},
    "locale": {"timezone": "UTC", "language": "es", "date_format": "DD/MM/YYYY"},
}
DEFAULT_GETS = ["/api/config", "/api/creator/summary", "/api/guiones", "/api/lab/items?brand=canal",
                "/api/tasks?ecosystem=canal", "/api/recommendations", "/api/creator/recordings",
                "/api/creator/hook-winner", "/api/tasks?ecosystem=vida", "/api/life/tasks", "/api/hooks-bank",
                "/api/life/habits", "/api/life/income", "/api/life/income-history", "/api/life/goals"]
OFF_GETS = ["/api/lab/productions", "/api/library", "/api/v2/system", "/api/metrics?brand=canal",
            "/api/captions/presets", "/api/captions/videos"]


@pytest.fixture
def served(tmp_path):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/cc.config.json").write_text(json.dumps(CONFIG), encoding="utf-8")
    (tmp_path / ".kit/cc").mkdir(parents=True)
    shutil.copytree(REPO / "cc/web", tmp_path / ".kit/cc/web")
    shutil.copytree(REPO / "cc/server", tmp_path / ".kit/cc/server")
    srv, app = ccapp.make_server(tmp_path)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    host = f"127.0.0.1:{app.port}"

    def get(path, cookie=None):
        conn = http.client.HTTPConnection("127.0.0.1", app.port, timeout=5)
        conn.request("GET", path, headers={"Host": host, **({"Cookie": cookie} if cookie else {})})
        r = conn.getresponse()
        body = r.read()
        conn.close()
        return r.status, dict(r.getheaders()), body

    status, headers, _ = get(f"/?token={app.mint_token()}")
    assert status == 303 and headers["Location"] == "/"
    cookie = headers["Set-Cookie"].split(";", 1)[0]
    yield lambda path: get(path, cookie)
    srv.shutdown()
    srv.server_close()


def test_login_serves_the_shell_and_every_module(served):
    status, headers, body = served("/")
    assert status == 200 and headers["Content-Type"].startswith("text/html") and b'src="app.js"' in body
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    web = REPO / "cc/web"
    for path in sorted(web.rglob("*")):
        if path.is_file():
            rel = path.relative_to(web).as_posix()
            assert served(f"/{rel}")[0] == 200, rel
    # the server's own code next to the UI is never reachable
    for bad in ("/server/app.py", "/%2e%2e/server/app.py", "/../server/app.py"):
        assert served(bad)[0] == 404, bad


def test_imports_resolve(served):
    web = REPO / "cc/web"
    for path in web.rglob("*.js"):
        for spec in re.findall(r"(?:from|import\()\s*[\"'](\.[^\"']+)[\"']", path.read_text(encoding="utf-8")):
            target = (path.parent / spec).resolve().relative_to(web.resolve()).as_posix()
            assert served(f"/{target}")[0] == 200, f"{path.name} -> {spec}"


def test_default_view_api_calls_answer(served):
    for path in DEFAULT_GETS:
        status, _, body = served(path)
        assert status == 200, (path, body[:200])
    for path in OFF_GETS:
        assert served(path)[0] == 404, path
