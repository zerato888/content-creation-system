# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Control de maqueta de un reel YA ARMADO, cuadro por cuadro, antes de exportar.

    python .kit/launch.py reel9 layout <carpeta-del-reel>      (sale 1 si algo falla)

El control de datos (reel9_gate.py) mira el data.json; no puede ver cómo quedó el texto en pantalla.
Este abre el index.html armado en un navegador sin pantalla (Playwright: Chrome o el Chromium del kit),
espera a las tipografías y revisa:

1. El título del hook entró en su zona (900 px hasta la línea de tarjetas) sin pasar el tamaño mínimo
   (window.__introFit, lo escribe la plantilla). Si no entró: TITULO_LARGO, hay que acortarlo.
2. Cuadro por cuadro, a 30 fps: ningún texto visible (hook, tarjetas, retrato, cierre, destello) termina
   por debajo de la línea de tarjetas (cards.bottom_px), y el hook no sube de 900 px.
3. El retrato y la tarjeta que lo acompaña nunca se pisan.

También aquí vive el navegador que usa el render (reel9.py render): mismo servidor, misma página.
"""
from __future__ import annotations

import contextlib
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel9_gate  # noqa: E402

ZONE_TOP = 900
FPS = 30
TITLE_TOO_LONG = "TITULO_LARGO"

# Nodos con texto que se ven en pantalla.
PROBE = r"""
([bottom, top, fps]) => {
  const sels = ["#intro", ".cw", ".stat", ".person", "#lockup", "#flashkicker"];
  const tl = window.__timelines.reel;
  const alpha = el => { let a = 1; for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
    const cs = getComputedStyle(n); if (cs.display === "none" || cs.visibility === "hidden") return 0;
    a *= parseFloat(cs.opacity); } return a; };
  const dur = parseFloat(document.querySelector('[data-composition-id="reel"]').dataset.duration) || tl.duration();
  const out = [];
  for (let f = 0; f <= Math.ceil(dur * fps); f++) {
    const t = f / fps; tl.seek(t, false);
    const people = [], cards = [];
    for (const sel of sels) for (const el of document.querySelectorAll(sel)) {
      if (alpha(el) < 0.01 || !el.textContent.trim()) continue;
      const r = el.getBoundingClientRect();
      if (r.bottom > bottom + 1) out.push({t, sel, edge: "bottom", px: Math.round(r.bottom)});
      if (sel === "#intro" && r.top < top - 1) out.push({t, sel, edge: "top", px: Math.round(r.top)});
      if (sel === ".person") people.push(r); else if (sel === ".cw" || sel === ".stat") cards.push(r);
    }
    for (const a of people) for (const b of cards)
      if (a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom)
        out.push({t, sel: ".person", edge: "overlap", px: Math.round(b.top)});
  }
  return {fit: window.__introFit || null, out};
}
"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class BrowserMissing(RuntimeError):
    pass


@contextlib.contextmanager
def open_reel(reel_dir):
    """Abre <reel>/index.html en un navegador sin pantalla y entrega la página con la línea de tiempo lista."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserMissing("falta Playwright (pip install playwright); el kit lo trae en .kit/venv") from exc
    reel = Path(reel_dir).resolve()
    if not (reel / "index.html").is_file():
        raise FileNotFoundError(f"no hay index.html armado en {reel}")
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(reel)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = None
            for kwargs in ({"channel": "chrome"}, {}):  # Chrome instalado; si no, el Chromium de Playwright
                try:
                    browser = p.chromium.launch(headless=True, **kwargs)
                    break
                except Exception:  # noqa: BLE001
                    continue
            if browser is None:
                raise BrowserMissing("no hay navegador para Playwright: instalá Chrome o corré "
                                     "'python -m playwright install chromium'")
            try:
                page = browser.new_page(viewport={"width": 1080, "height": 1920})
                page.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html")
                page.wait_for_function("!!(window.__timelines && window.__timelines.reel)", timeout=60000)
                yield page
            finally:
                browser.close()
    finally:
        srv.shutdown()
        srv.server_close()


def check(reel_dir, standard=None) -> list[str]:
    """Fallas de maqueta del reel armado (vacía = pasa). Lanza BrowserMissing si no hay navegador."""
    std = standard if isinstance(standard, dict) else reel9_gate.load_standard(standard)
    bottom = std["cards"]["bottom_px"]
    with open_reel(reel_dir) as page:
        res = page.evaluate(PROBE, [bottom, ZONE_TOP, FPS])
    errors = []
    fit = res["fit"]
    if not fit:
        errors.append("la plantilla no anotó el ajuste del título (window.__introFit): el index.html no viene de reel9")
    elif not fit["fits"]:
        errors.append(f"{TITLE_TOO_LONG}: el título no entra en la zona del hook ({fit['zone_px']} px) ni al mínimo de "
                      f"{fit['min_px']} px (queda en {fit['height_px']} px). Acortalo (máx. 2 intentos, mismo sentido) y volvé a armar.")
    seen = set()
    for v in res["out"]:
        key = (v["sel"], v["edge"])
        if key in seen:
            continue
        seen.add(key)
        if v["edge"] == "overlap":
            errors.append(f"el retrato y su tarjeta se pisan en pantalla (la tarjeta sube hasta {v['px']} px en {v['t']:.2f} s): acortá la tarjeta")
            continue
        limit = f"por debajo de {bottom}" if v["edge"] == "bottom" else f"por encima de {ZONE_TOP}"
        errors.append(f"{v['sel']} queda {limit} px (llega a {v['px']} px en {v['t']:.2f} s)")
    return errors


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        errors = check(argv[0])
    except (BrowserMissing, FileNotFoundError) as exc:
        print(f"MAQUETA — no se pudo revisar: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("MAQUETA — NO pasa:\n  - " + "\n  - ".join(errors), file=sys.stderr)
        return 1
    print(f"MAQUETA OK: {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
