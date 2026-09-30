# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Trae datos públicos de redes con Apify, con TU token (opcional; sin token el kit funciona igual).

    python3 .kit/launch.py apify posts @cuenta [-n 20]        # posts/reels recientes de un perfil de Instagram
    python3 .kit/launch.py apify profile @cuenta              # seguidores, bio
    python3 .kit/launch.py apify hashtag tema [-n 20]         # posts de un hashtag
    python3 .kit/launch.py apify run <actor> '<json>' [--confirm]   # cualquier actor de la tienda de Apify

Guardar el token una vez (Apify > Settings > API & Integrations):
    Mac:      security add-generic-password -s content-kit -a APIFY_TOKEN -w
    Windows:  cmdkey /generic:content-kit:APIFY_TOKEN /user:kit /pass

Apify cobra por resultado: cada corrida muestra primero qué actor y cuántos resultados pide y NO corre sin
--confirm. La salida es un arreglo JSON por pantalla (o a --out archivo). Instagram bloquea a veces el
acceso anónimo: si un actor devuelve error, no insistas; probá otro actor o bajá el límite.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kit_secrets  # noqa: E402

BASE = "https://api.apify.com/v2"


def ig_url(handle: str) -> str:
    h = handle.strip().lstrip("@")
    return h if h.startswith("http") else f"https://www.instagram.com/{h}/"


def plan(a) -> tuple[str, dict]:
    """(actor, input) para cada subcomando; sin red."""
    if a.cmd == "posts":
        return "apify~instagram-scraper", {"directUrls": [ig_url(a.handle)], "resultsType": "posts", "resultsLimit": a.n}
    if a.cmd == "profile":
        return "apify~instagram-profile-scraper", {"usernames": [a.handle.strip().lstrip("@")]}
    if a.cmd == "hashtag":
        return "apify~instagram-hashtag-scraper", {"hashtags": [a.tag.lstrip("#")], "resultsLimit": a.n}
    return a.actor.replace("/", "~"), json.loads(a.input)


def run_sync(actor: str, payload: dict, token: str, timeout=300, opener=None):
    url = f"{BASE}/acts/{urllib.parse.quote(actor, safe='~')}/run-sync-get-dataset-items"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    ctx = ssl.create_default_context()
    try:
        with (opener or (lambda r: urllib.request.urlopen(r, timeout=timeout, context=ctx)))(req) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ERROR de Apify: HTTP {e.code} (revisá el token y el nombre del actor)")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise SystemExit(f"ERROR: sin conexión con Apify ({type(e).__name__}); no se cobró nada.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("posts", "profile"):
        s = sub.add_parser(name)
        s.add_argument("handle")
        s.add_argument("-n", type=int, default=20)
    h = sub.add_parser("hashtag")
    h.add_argument("tag")
    h.add_argument("-n", type=int, default=20)
    r = sub.add_parser("run")
    r.add_argument("actor")
    r.add_argument("input")
    for s in sub.choices.values():
        s.add_argument("--confirm", action="store_true")
        s.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        actor, payload = plan(a)
    except json.JSONDecodeError:
        print("apify: el input de `run` no es JSON válido", file=sys.stderr)
        return 2
    if not a.confirm:
        print(f"Prueba (no se corrió nada ni se cobró): actor {actor}\ninput: {json.dumps(payload, ensure_ascii=False)}\n"
              "Apify cobra por resultado. Repetí con --confirm para correrlo.")
        return 0
    token = kit_secrets.get_secret("APIFY_TOKEN")
    if not token:
        print("ERROR: falta APIFY_TOKEN en tu llavero (pasos en el encabezado de este archivo).", file=sys.stderr)
        return 1
    text = json.dumps(run_sync(actor, payload, token), ensure_ascii=False, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"guardado en {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
