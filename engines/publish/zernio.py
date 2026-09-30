# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Schedule a reel or a carousel on Instagram / Facebook / TikTok through Zernio, with YOUR key.

    python3 .kit/launch.py publish accounts        (add --via metricool to use Metricool instead: see metricool.py)
    python3 .kit/launch.py publish post --handle @tu_cuenta --video reel.mp4 --caption caption.txt \
        --at 2026-10-01T18:00 [--tz America/Costa_Rica] [--platforms instagram,facebook] \
        [--first-comment "¿Qué harías vos?"] [--confirm]
    python3 .kit/launch.py publish post --handle @tu_cuenta --images out/slide-*.png --caption c.txt --at ...

Without --confirm nothing is sent: it prints exactly what would be scheduled (dry run).
The key is read once, only when needed, from the kit secrets store (name ZERNIO_API_KEY). Save it once:
    Mac:      security add-generic-password -s content-kit -a ZERNIO_API_KEY -w
    Windows:  cmdkey /generic:content-kit:ZERNIO_API_KEY /user:kit /pass
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kit_secrets  # noqa: E402

BASE = "https://api.zernio.com/v1"
PLATFORMS = {"instagram", "facebook", "tiktok"}


def _ssl():
    try:  # python.org builds on macOS ship without system roots
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class Zernio:
    def __init__(self, key: str | None = None, opener=None):
        self.key = key or kit_secrets.get_secret("ZERNIO_API_KEY")
        if not self.key:
            raise SystemExit("ERROR: falta tu clave de Zernio. Guardala una vez (te la pide sin mostrarla): "
                             "security add-generic-password -s content-kit -a ZERNIO_API_KEY -w")
        self.send = opener or (lambda req: urllib.request.urlopen(req, timeout=600, context=_ssl()))

    def http(self, method, url, body=None, raw=None, ctype=None):
        if raw is not None:  # presigned upload: no auth header
            req = urllib.request.Request(url, data=raw, headers={"Content-Type": ctype}, method=method)
        else:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8") if body is not None else None, method=method,
                                         headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        try:
            with self.send(req) as r:
                txt = r.read().decode("utf-8")
                return r.status, (json.loads(txt) if txt[:1] in ("{", "[") else txt)
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8") if e.fp else "")[:500]
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise SystemExit(f"ERROR: sin conexión con Zernio ({type(e).__name__}); no se programó nada. Revisá internet y repetí.")

    def accounts(self) -> list:
        st, p = self.http("GET", f"{BASE}/accounts")
        if st >= 400:
            raise SystemExit(f"ERROR: Zernio respondió {st}: {p}")
        acc = p.get("accounts", p) if isinstance(p, dict) else p
        if not isinstance(acc, list):
            raise SystemExit("ERROR: Zernio devolvió una respuesta inesperada al pedir las cuentas")
        return acc

    def account_id(self, handle: str, platform: str) -> str:
        want = handle.lower().lstrip("@")
        for a in self.accounts():
            prof = (a.get("profileUrl") or "").rstrip("/").split("/")[-1].lower().lstrip("@")
            if a.get("platform") == platform and want in (prof, (a.get("displayName") or "").lower().lstrip("@"),
                                                          (a.get("username") or "").lower().lstrip("@")):
                return a["_id"]
        raise SystemExit(f"ERROR: @{want} en {platform} no está conectada a tu Zernio (revisá en zernio.com)")

    def upload(self, f: Path) -> str:
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        st, m = self.http("POST", f"{BASE}/media", {"filename": f.name, "contentType": ctype})
        if st >= 400 or not isinstance(m, dict) or not {"uploadUrl", "publicUrl"} <= m.keys():
            raise SystemExit(f"ERROR: Zernio no aceptó {f.name} ({st}): {str(m)[:300]}")
        st, r = self.http("PUT", m["uploadUrl"], raw=f.read_bytes(), ctype=ctype)
        if st >= 400:
            raise SystemExit(f"ERROR: la subida de {f.name} falló ({st}): {r}")
        return m["publicUrl"]


def build_payload(caption, media_urls, kind, targets, when, tz, first_comment):
    plats = []
    for platform, acc in targets:
        t = {"platform": platform, "accountId": acc}
        if first_comment and platform in ("instagram", "facebook"):
            t["platformSpecificData"] = {"firstComment": first_comment}
        plats.append(t)
    return {"content": caption, "mediaItems": [{"type": kind, "url": u} for u in media_urls],
            "platforms": plats, "scheduledFor": when, "timezone": tz, "publishNow": False}


def check_inputs(video, images, caption_file, at, platforms, tz="America/Costa_Rica"):
    if bool(video) == bool(images):
        raise SystemExit("ERROR: pasá --video (reel) o --images (carrusel), uno de los dos")
    files = [Path(video)] if video else [Path(p) for p in images]
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        raise SystemExit(f"ERROR: no encuentro: {', '.join(missing)}")
    if images and not 2 <= len(files) <= 10:
        raise SystemExit("ERROR: un carrusel lleva entre 2 y 10 imágenes")
    bad = set(platforms) - PLATFORMS
    if bad:
        raise SystemExit(f"ERROR: plataforma desconocida: {', '.join(sorted(bad))}")
    try:
        when = datetime.fromisoformat(at)
        zone = ZoneInfo(tz)
    except ValueError:
        raise SystemExit("ERROR: --at va como 2026-10-01T18:00 (hora local de --tz, sin zona pegada)")
    except ZoneInfoNotFoundError:
        raise SystemExit(f"ERROR: zona horaria desconocida: {tz} (ej. America/Costa_Rica, America/Mexico_City)")
    if when.tzinfo is not None:
        raise SystemExit("ERROR: --at va sin zona (ej. 2026-10-01T18:00); la zona va en --tz")
    if when.replace(tzinfo=zone) <= datetime.now(zone):
        raise SystemExit(f"ERROR: {at} ya pasó en {tz}; elegí una fecha futura")
    caption = Path(caption_file).read_text(encoding="utf-8").strip()
    if not caption:
        raise SystemExit("ERROR: el caption está vacío")
    return files, caption


def cmd_post(a) -> int:
    platforms = [p.strip() for p in a.platforms.split(",") if p.strip()]
    files, caption = check_inputs(a.video, a.images, a.caption, a.at, platforms, a.tz)
    kind = "video" if a.video else "image"
    print(f"Programar en Zernio: {len(files)} archivo(s) ({'reel' if a.video else 'carrusel'}) · @{a.handle.lstrip('@')} · "
          f"{', '.join(platforms)} · {a.at} ({a.tz})")
    print(f"Caption: {caption[:120]}{'…' if len(caption) > 120 else ''}")
    if a.first_comment:
        print(f"Primer comentario: {a.first_comment}")
    if not a.confirm:
        print("Prueba: no se envió nada. Si está bien, repetí el comando con --confirm.")
        return 0
    z = Zernio()
    targets = [(p, z.account_id(a.handle, p)) for p in platforms]
    urls = [z.upload(f) for f in files]
    st, resp = z.http("POST", f"{BASE}/posts", build_payload(caption, urls, kind, targets, a.at, a.tz, a.first_comment))
    if st >= 400:
        raise SystemExit(f"ERROR: Zernio no programó el post ({st}): {resp}")
    pid = (resp.get("post") or resp).get("_id") if isinstance(resp, dict) else None
    print(f"Programado. id {pid}. Revisalo en zernio.com antes de la hora.")
    return 0


def selftest() -> int:
    p = build_payload("hola", ["u1", "u2"], "image", [("instagram", "A"), ("tiktok", "B")], "2026-10-01T18:00",
                      "America/Costa_Rica", "¿Y vos?")
    assert p["mediaItems"] == [{"type": "image", "url": "u1"}, {"type": "image", "url": "u2"}]
    assert p["platforms"][0]["platformSpecificData"]["firstComment"] == "¿Y vos?"
    assert "platformSpecificData" not in p["platforms"][1] and p["publishNow"] is False

    class Resp:
        def __init__(self, body, status=200):
            self.body, self.status = body, status

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self.body.encode("utf-8")

    seen = []

    def opener(req):
        seen.append((req.get_method(), req.full_url, req.headers.get("Authorization")))
        if req.full_url.endswith("/accounts"):
            return Resp(json.dumps({"accounts": [{"_id": "X1", "platform": "instagram",
                                                  "profileUrl": "https://instagram.com/mi_marca/"}]}))
        return Resp("")

    z = Zernio(key="sk_test", opener=opener)
    assert z.account_id("@Mi_Marca", "instagram") == "X1"
    assert seen[0][2] == "Bearer sk_test"
    return 3


def pop_via(argv: list[str]) -> tuple[str, list[str]]:
    """--via zernio|metricool (before or after the subcommand); zernio by default."""
    out, via, i = [], "zernio", 0
    while i < len(argv):
        if argv[i] == "--via" and i + 1 < len(argv):
            via, i = argv[i + 1], i + 2
        elif argv[i].startswith("--via="):
            via, i = argv[i][6:], i + 1
        else:
            out.append(argv[i])
            i += 1
    if via not in ("zernio", "metricool"):
        raise SystemExit(f"ERROR: --via {via}: usa zernio o metricool")
    return via, out


def default_tz() -> str:
    """The person's zone from the onboarding (.kit-personal/cc.config.json), else Costa Rica."""
    for base in (Path.cwd(), *Path.cwd().parents):
        cfg = base / ".kit-personal" / "cc.config.json"
        if cfg.is_file():
            try:
                tz = json.loads(cfg.read_text(encoding="utf-8")).get("timezone")
                if isinstance(tz, str) and tz:
                    return tz
            except ValueError:
                pass
            break
    return "America/Costa_Rica"


def main(argv=None) -> int:
    via, argv = pop_via(list(sys.argv[1:] if argv is None else argv))
    if via == "metricool":
        import metricool
        return metricool.main(argv)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("accounts", help="cuentas conectadas a tu Zernio")
    p = sub.add_parser("post", help="programar un reel o un carrusel")
    p.add_argument("--handle", required=True)
    p.add_argument("--video")
    p.add_argument("--images", nargs="+")
    p.add_argument("--caption", required=True, help="archivo de texto con el caption")
    p.add_argument("--at", required=True, help="fecha y hora local: 2026-10-01T18:00")
    p.add_argument("--tz", default=None, help="zona horaria (por defecto la de tu onboarding)")
    p.add_argument("--platforms", default="instagram")
    p.add_argument("--first-comment")
    p.add_argument("--confirm", action="store_true", help="enviar de verdad (sin esto es una prueba)")
    a = ap.parse_args(argv)
    if getattr(a, "tz", "x") is None:
        a.tz = default_tz()
    if a.selftest:
        print(f"publish selftest OK ({selftest()} casos)")
        return 0
    if a.cmd == "accounts":
        for acc in Zernio().accounts():
            print(f"{acc.get('platform')}: {acc.get('displayName') or acc.get('username')}  ({acc.get('profileUrl', '')})")
        return 0
    if a.cmd == "post":
        return cmd_post(a)
    ap.error("usar --selftest, accounts o post")
    return 2


if __name__ == "__main__":
    sys.exit(main())
