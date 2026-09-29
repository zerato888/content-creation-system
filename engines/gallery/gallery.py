# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Galería local de revisión: mirás las piezas de una carpeta y marcás aprobar / rechazar con un comentario.

    python .kit/launch.py gallery serve <carpeta> [--title "Entrega"] [--port 0] [--no-open]
    python .kit/launch.py gallery read  <carpeta>      # imprime las decisiones (JSON) para que el agente las lea
    python .kit/launch.py gallery list  <carpeta>      # imprime las piezas que se ven

Las decisiones se guardan en <carpeta>/decisiones.json:
    {"pieza.png": {"status": "aprobado" | "rechazado" | "", "comment": "texto"}}
Sin dependencias, sin cuentas, sin internet. Solo escucha en 127.0.0.1, en un puerto libre, y la dirección
lleva un código al azar que cambia en cada corrida. Con Ctrl+C se cierra.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import secrets
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote

KINDS = {".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image", ".gif": "image",
         ".mp4": "video", ".mov": "video", ".m4v": "video", ".webm": "video",
         ".mp3": "audio", ".m4a": "audio", ".wav": "audio", ".ogg": "audio"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
        ".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4", ".webm": "video/webm",
        ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav", ".ogg": "audio/ogg"}
DECISIONS = "decisiones.json"
STATUSES = {"", "aprobado", "rechazado"}
MAX_BODY = 20_000
_lock = threading.Lock()

PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><link rel="stylesheet" href="style.css"></head>
<body><header><h1>__TITLE__</h1><div id="sum">Cargando...</div></header><main id="grid"></main>
<script src="app.js"></script></body></html>"""

CSS = """:root{--bg:#f6f5f2;--card:#fff;--ink:#1b1b1b;--mute:#6b6b6b;--line:#e3e1dc;--ok:#1f7a4d;--no:#b3261e}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--card:#1e1e1e;--ink:#eee;--mute:#9a9a9a;--line:#2e2e2e;--ok:#4fc38a;--no:#f07167}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
header{padding:24px 16px 8px;max-width:1200px;margin:auto}h1{margin:0;font-size:22px}#sum{color:var(--mute)}
main{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));padding:16px;max-width:1200px;margin:auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.card.aprobado{border-color:var(--ok)}.card.rechazado{border-color:var(--no)}
.media img,.media video{width:100%;display:block;background:#000;max-height:520px;object-fit:contain}
.media audio{width:100%;margin:16px 0}.body{padding:12px;display:flex;flex-direction:column;gap:8px}
.name{font-weight:600;word-break:break-word}.btns{display:flex;gap:8px}
button{flex:1;padding:8px;border-radius:8px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;font:inherit}
button.on.a{background:var(--ok);color:#fff;border-color:var(--ok)}button.on.r{background:var(--no);color:#fff;border-color:var(--no)}
textarea{width:100%;min-height:56px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--ink);font:inherit;padding:8px;resize:vertical}
.empty{padding:40px 16px;color:var(--mute);text-align:center}"""

JS = """(async () => {
  const grid = document.getElementById('grid'), sum = document.getElementById('sum');
  const post = (name, patch) => fetch('decision', {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, ...patch})}).then(r => { if (!r.ok) throw new Error('no se guardo'); return r.json(); })
    .catch(e => alert('No se pudo guardar: ' + e.message));
  const data = await (await fetch('data')).json();
  const dec = data.decisions;
  const count = () => { const n = Object.values(dec).filter(d => d.status).length;
    sum.textContent = data.items.length ? data.items.length + ' piezas, ' + n + ' revisadas' : ''; };
  if (!data.items.length) { grid.innerHTML = '<div class="empty">No hay piezas en la carpeta.</div>'; sum.textContent = ''; return; }
  for (const it of data.items) {
    const d = dec[it.name] = dec[it.name] || {status: '', comment: ''};
    const card = document.createElement('div'); card.className = 'card ' + d.status;
    const tag = it.kind === 'image' ? 'img' : it.kind;
    const m = document.createElement(tag); m.src = 'file/' + encodeURIComponent(it.name);
    if (tag === 'img') { m.alt = it.name; m.loading = 'lazy'; } else { m.controls = true; m.preload = 'metadata'; }
    const media = document.createElement('div'); media.className = 'media'; media.append(m);
    const body = document.createElement('div'); body.className = 'body';
    const nm = document.createElement('div'); nm.className = 'name'; nm.textContent = it.name;
    const btns = document.createElement('div'); btns.className = 'btns';
    const a = document.createElement('button'); a.className = 'a'; a.textContent = 'Aprobar';
    const r = document.createElement('button'); r.className = 'r'; r.textContent = 'Rechazar';
    const ta = document.createElement('textarea'); ta.placeholder = 'Comentario (opcional)'; ta.value = d.comment || '';
    const paint = () => { card.className = 'card ' + d.status; a.classList.toggle('on', d.status === 'aprobado');
      r.classList.toggle('on', d.status === 'rechazado'); count(); };
    a.onclick = () => { d.status = d.status === 'aprobado' ? '' : 'aprobado'; paint(); post(it.name, {status: d.status}); };
    r.onclick = () => { d.status = d.status === 'rechazado' ? '' : 'rechazado'; paint(); post(it.name, {status: d.status}); };
    let t; ta.oninput = () => { d.comment = ta.value; clearTimeout(t); t = setTimeout(() => post(it.name, {comment: ta.value}), 600); };
    btns.append(a, r); body.append(nm, btns, ta); card.append(media, body); grid.append(card); paint();
  }
})();"""


def list_items(folder: Path) -> list[dict]:
    return [{"name": p.name, "kind": KINDS[p.suffix.lower()]} for p in sorted(folder.iterdir(), key=lambda p: p.name.lower())
            if p.is_file() and p.suffix.lower() in KINDS]


def read_decisions(folder: Path) -> dict:
    f = folder / DECISIONS
    if not f.is_file():
        return {}
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return d if isinstance(d, dict) else {}


def save_decision(folder: Path, name: str, status=None, comment=None) -> dict:
    """Actualiza una pieza (solo nombres que existen en la carpeta). Escritura atómica."""
    if name not in {i["name"] for i in list_items(folder)}:
        raise ValueError("pieza desconocida")
    if status is not None and status not in STATUSES:
        raise ValueError("estado inválido")
    if comment is not None and (not isinstance(comment, str) or len(comment) > 4000):
        raise ValueError("comentario inválido")
    with _lock:
        d = read_decisions(folder)
        cur = d.get(name) if isinstance(d.get(name), dict) else {"status": "", "comment": ""}
        if status is not None:
            cur["status"] = status
        if comment is not None:
            cur["comment"] = comment
        d[name] = cur
        tmp = folder / (DECISIONS + ".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, folder / DECISIONS)
    return cur


def make_handler(folder: Path, title: str, token: str, port_box: list):
    base = f"/{token}/"

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _host_ok(self) -> bool:
            return self.headers.get("Host", "") in (f"127.0.0.1:{port_box[0]}", f"localhost:{port_box[0]}")

        def _send(self, code, body: bytes, ctype="text/plain; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; media-src 'self'; img-src 'self'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0]
            if not self._host_ok() or not path.startswith(base):
                return self._send(404, b"no encontrado")
            rel = path[len(base):]
            if rel in ("", "index.html"):
                return self._send(200, PAGE.replace("__TITLE__", html.escape(title)).encode("utf-8"), "text/html; charset=utf-8")
            if rel == "style.css":
                return self._send(200, CSS.encode("utf-8"), "text/css; charset=utf-8")
            if rel == "app.js":
                return self._send(200, JS.encode("utf-8"), "text/javascript; charset=utf-8")
            if rel == "data":
                return self._send(200, json.dumps({"items": list_items(folder), "decisions": read_decisions(folder)},
                                                   ensure_ascii=False).encode("utf-8"), "application/json")
            if rel.startswith("file/"):
                name = unquote(rel[5:])
                if name in {i["name"] for i in list_items(folder)}:  # solo piezas listadas: sin rutas ni carpetas
                    p = folder / name
                    return self._send(200, p.read_bytes(), MIME[p.suffix.lower()])
            return self._send(404, b"no encontrado")

        def do_POST(self):
            path = self.path.split("?")[0]
            if not self._host_ok() or path != base + "decision":
                return self._send(404, b"no encontrado")
            origin = self.headers.get("Origin")
            if origin not in (f"http://127.0.0.1:{port_box[0]}", f"http://localhost:{port_box[0]}"):
                return self._send(403, b"origen no permitido")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self._send(415, b"solo JSON")
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                return self._send(413, b"muy grande")
            try:
                b = json.loads(self.rfile.read(n).decode("utf-8"))
                cur = save_decision(folder, b["name"], b.get("status"), b.get("comment"))
            except (ValueError, KeyError, TypeError):
                return self._send(400, b"pedido invalido")
            return self._send(200, json.dumps(cur, ensure_ascii=False).encode("utf-8"), "application/json")

    return H


def serve(folder: Path, title="Entrega para revisar", port=0, open_browser=True, ready=None) -> None:
    token = secrets.token_urlsafe(16)
    port_box = [0]
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(folder, title, token, port_box))
    port_box[0] = srv.server_address[1]
    url = f"http://127.0.0.1:{port_box[0]}/{quote(token)}/"
    if ready:
        ready(url, srv)
    print(f"Galería lista: {url}\nLas decisiones quedan en {folder / DECISIONS}. Ctrl+C para cerrar.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["serve", "read", "list"])
    ap.add_argument("folder")
    ap.add_argument("--title", default="Entrega para revisar")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args(argv)
    folder = Path(a.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"gallery: no existe la carpeta {folder}", file=sys.stderr)
        return 2
    if a.cmd == "list":
        print(json.dumps(list_items(folder), ensure_ascii=False, indent=2))
    elif a.cmd == "read":
        print(json.dumps(read_decisions(folder), ensure_ascii=False, indent=2))
    else:
        serve(folder, a.title, a.port, not a.no_open)
    return 0


if __name__ == "__main__":
    sys.exit(main())
