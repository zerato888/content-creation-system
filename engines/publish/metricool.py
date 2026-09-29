# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Schedule a reel or a carousel on Instagram / Facebook / TikTok through Metricool, with YOUR account.

    python .kit/launch.py publish --via metricool accounts
    python .kit/launch.py publish --via metricool post --images out/slide-*.png --caption caption.txt \
        --at 2026-10-01T18:00 [--tz America/Costa_Rica] [--platforms instagram,facebook] \
        [--first-comment "¿Qué harías vos?"] [--blog-id 123456] [--confirm]
    python .kit/launch.py publish --via metricool post --video reel.mp4 --caption caption.txt --at ...

Without --confirm nothing is sent and no key is read: it prints exactly what would be scheduled.
Three values live in the kit secrets store (never in files of the project):
  METRICOOL_API_KEY   your API token (Metricool > Account > API)
  METRICOOL_USER_ID   your user number
  METRICOOL_BLOG_ID   the brand (blog) to publish on; --blog-id overrides it for one run
    Mac:      security add-generic-password -s content-kit -a METRICOOL_API_KEY -w
    Windows:  cmdkey /generic:content-kit:METRICOOL_API_KEY /user:kit /pass
A sent post leaves `<caption>.metricool.json` next to the caption; the same piece is not sent twice
unless you pass --again.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_secrets  # noqa: E402
import zernio  # noqa: E402  (same date, zone, file and caption checks as the Zernio publisher)

BASE = "https://app.metricool.com/api"
PART_SIZE = 5 * 1024 * 1024
CTYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4"}
FIRST_COMMENT_NETWORKS = ("instagram", "facebook")
FACEBOOK_SINGLE = "Facebook: se usa solo la primera imagen del carrusel"

SETUP = ("Guárdalos una vez (te los pide sin mostrarlos): "
         "security add-generic-password -s content-kit -a {name} -w")


def _need(name: str) -> str:
    v = kit_secrets.get_secret(name)
    if not v:
        raise SystemExit(f"ERROR: falta {name} de Metricool. " + SETUP.format(name=name))
    return v.strip()


class Metricool:
    def __init__(self, key=None, user=None, blog=None, opener=None):
        self.key, self.user = key or _need("METRICOOL_API_KEY"), user or _need("METRICOOL_USER_ID")
        self.blog = blog or _need("METRICOOL_BLOG_ID")
        self.send = opener or (lambda req: urllib.request.urlopen(req, timeout=300, context=zernio._ssl()))

    def _do(self, req):
        try:
            with self.send(req) as r:
                txt = r.read().decode("utf-8")
                return r.status, (json.loads(txt) if txt[:1] in ("{", "[") else txt), r
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8") if e.fp else "")[:500], None
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise SystemExit(f"ERROR: sin conexión con Metricool ({type(e).__name__}); revisa internet y repite. "
                             "Antes de repetir mira en Metricool si el post ya quedó programado.")

    def api(self, method, endpoint, body=None, blog=True):
        q = {"userId": self.user, **({"blogId": self.blog} if blog else {})}
        url = f"{BASE}{endpoint}{'&' if '?' in endpoint else '?'}{urllib.parse.urlencode(q)}"
        headers = {"X-Mc-Auth": self.key, **({"Content-Type": "application/json"} if body is not None else {})}
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8") if body is not None else None,
                                     headers=headers, method=method)
        st, payload, _ = self._do(req)
        if st in (401, 403):
            raise SystemExit("ERROR: Metricool rechazó la clave (401/403). Revisa METRICOOL_API_KEY y METRICOOL_USER_ID.")
        return st, payload

    def _put(self, url, chunk, ctype):
        sha = base64.b64encode(hashlib.sha256(chunk).digest()).decode()
        req = urllib.request.Request(url, data=chunk, method="PUT",
                                     headers={"Content-Type": ctype, "x-amz-checksum-sha256": sha})
        st, payload, resp = self._do(req)
        if st >= 400:
            raise SystemExit(f"ERROR: la subida a Metricool falló ({st}): {str(payload)[:200]}")
        return (resp.headers.get("ETag", "") if resp is not None and getattr(resp, "headers", None) else "")

    def blogs(self) -> list:
        st, p = self.api("GET", "/admin/simpleProfiles", blog=False)
        if st >= 400:
            raise SystemExit(f"ERROR: Metricool respondió {st}: {str(p)[:200]}")
        rows = p.get("data", p) if isinstance(p, dict) else p
        if not isinstance(rows, list):
            raise SystemExit("ERROR: Metricool devolvió una respuesta inesperada al pedir tus marcas")
        return rows

    def upload(self, f: Path) -> str:
        ctype = CTYPES.get(f.suffix.lower())
        if not ctype:
            raise SystemExit(f"ERROR: {f.name}: solo png, jpg, webp o mp4")
        data, parts = f.read_bytes(), []
        for i in range(max(1, math.ceil(len(data) / PART_SIZE))):
            chunk = data[i * PART_SIZE:(i + 1) * PART_SIZE]
            parts.append({"size": len(chunk), "startByte": i * PART_SIZE, "endByte": i * PART_SIZE + len(chunk),
                          "hash": base64.b64encode(hashlib.sha256(chunk).digest()).decode()})
        st, resp = self.api("PUT", "/v2/media/s3/upload-transactions",
                            {"resourceType": "planner", "contentType": ctype, "fileExtension": f.suffix.lower().lstrip("."),
                             "parts": parts})
        td = resp.get("data", resp) if isinstance(resp, dict) else None
        if st >= 400 or not isinstance(td, dict):
            raise SystemExit(f"ERROR: Metricool no aceptó {f.name} ({st}): {str(resp)[:300]}")
        if td.get("uploadType") == "MULTIPART":
            done = [{"partNumber": p["partNumber"],
                     "etag": self._put(p["presignedUrl"], data[p["startByte"]:p["startByte"] + p["partSize"]], ctype)}
                    for p in td["parts"]]
            st, resp = self.api("PATCH", "/v2/media/s3/upload-transactions",
                                {"multipart": {"uploadId": td["uploadId"], "key": td["key"], "parts": done}})
            cd = resp.get("data", resp) if isinstance(resp, dict) else {}
            url = cd.get("fileUrl") or cd.get("location")
        else:
            self._put(td["presignedUrl"], data, ctype)
            url = td.get("fileUrl") or f"https://{td['bucket']}.s3.amazonaws.com/{td['key']}"
            st, _ = self.api("PATCH", "/v2/media/s3/upload-transactions", {"simple": {"fileUrl": url}})
        if st >= 400 or not url:
            raise SystemExit(f"ERROR: Metricool no cerró la subida de {f.name} ({st})")
        return url

    def schedule(self, network, body) -> str:
        st, resp = self.api("POST", "/v2/scheduler/posts", body)
        pid = resp.get("data", {}).get("id") if isinstance(resp, dict) and isinstance(resp.get("data"), dict) else None
        if st >= 400 or not pid:
            raise RuntimeError(f"Metricool no programó {network} ({st}): {str(resp)[:300]}")
        return str(pid)


def build_body(network, caption, media, at, tz, kind, first_comment):
    body = {"text": caption, "publicationDate": {"dateTime": at + ":00" if len(at) == 16 else at, "timezone": tz},
            "providers": [{"network": network}], "media": media if network != "facebook" or kind == "video" else media[:1],
            "autoPublish": True, "saveExternalMediaFiles": False, "shortener": False, "draft": False}
    if network == "instagram":
        body["instagramData"] = {"type": "REEL", "showReelOnFeed": True} if kind == "video" else {"type": "POST", "autoPublish": True}
    elif network == "facebook" and kind == "video":
        body["facebookData"] = {"type": "VIDEO"}
    elif network == "tiktok" and kind == "video":
        body["tiktokData"] = {"privacyOption": "PUBLIC_TO_EVERYONE"}
    if first_comment and network in FIRST_COMMENT_NETWORKS:
        body["firstCommentText"] = first_comment
    return body


def fingerprint(files, caption, at, platforms, blog) -> str:
    h = hashlib.sha256()
    for f in files:
        h.update(hashlib.sha256(f.read_bytes()).digest())
    h.update(json.dumps([caption, at, sorted(platforms), str(blog or "")]).encode("utf-8"))
    return h.hexdigest()


def cmd_post(a) -> int:
    platforms = [p.strip() for p in a.platforms.split(",") if p.strip()]
    files, caption = zernio.check_inputs(a.video, a.images, a.caption, a.at, platforms, a.tz)
    kind = "video" if a.video else "image"
    print(f"Programar en Metricool: {len(files)} archivo(s) ({'reel' if a.video else 'carrusel'}) · "
          f"{', '.join(platforms)} · {a.at} ({a.tz}) · marca {a.blog_id or '(METRICOOL_BLOG_ID)'}")
    print(f"Caption: {caption[:120]}{'…' if len(caption) > 120 else ''}")
    if a.first_comment:
        print(f"Primer comentario: {a.first_comment}" + ("" if set(platforms) & set(FIRST_COMMENT_NETWORKS)
                                                        else " (TikTok no lo admite: no se envía)"))
    if kind == "image" and "facebook" in platforms:
        print(FACEBOOK_SINGLE)
    receipt = Path(a.caption).with_suffix(".metricool.json")
    fp = fingerprint(files, caption, a.at, platforms, a.blog_id)
    if not a.confirm:
        print("Prueba: no se envió nada. Si está bien, repite el comando con --confirm.")
        return 0
    if not a.again and receipt.is_file():
        try:
            prev = json.loads(receipt.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
        if prev.get("fingerprint") == fp and prev.get("results"):
            raise SystemExit(f"ERROR: esta pieza ya se programó ({receipt.name}). Si quieres repetirla, agrega --again.")
    m = Metricool(blog=a.blog_id)
    media = [m.upload(f) for f in files]
    results, errors = {}, {}
    for net in platforms:
        try:
            results[net] = m.schedule(net, build_body(net, caption, media, a.at, a.tz, kind, a.first_comment))
        except RuntimeError as e:
            errors[net] = str(e)
    if results:  # keep the ids even when another network failed: never re-send the ones that worked
        receipt.write_text(json.dumps({"fingerprint": fp, "at": a.at, "tz": a.tz, "results": results, "errors": errors},
                                      indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for net, pid in results.items():
        print(f"Programado en {net}. id {pid}")
    if errors:
        raise SystemExit("ERROR: " + " | ".join(errors.values()) +
                         ("\nLo que sí salió quedó guardado; no lo repitas." if results else ""))
    print("Revísalo en Metricool antes de la hora.")
    return 0


def selftest() -> int:
    b = build_body("instagram", "hola", ["u1", "u2"], "2026-10-01T18:00", "America/Costa_Rica", "image", "¿Y vos?")
    assert b["publicationDate"]["dateTime"] == "2026-10-01T18:00:00" and b["firstCommentText"] == "¿Y vos?"
    assert b["instagramData"]["type"] == "POST" and b["media"] == ["u1", "u2"]
    assert build_body("facebook", "h", ["u1", "u2"], "2026-10-01T18:00", "UTC", "image", "")["media"] == ["u1"]
    t = build_body("tiktok", "h", ["u"], "2026-10-01T18:00", "UTC", "video", "c")
    assert "firstCommentText" not in t and t["tiktokData"]
    return 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("accounts", help="marcas (blogs) de tu Metricool")
    p = sub.add_parser("post", help="programar un reel o un carrusel")
    p.add_argument("--handle", help="solo para tu referencia; Metricool publica en la marca (blog)")
    p.add_argument("--video")
    p.add_argument("--images", nargs="+")
    p.add_argument("--caption", required=True, help="archivo de texto con el caption")
    p.add_argument("--at", required=True, help="fecha y hora local: 2026-10-01T18:00")
    p.add_argument("--tz", default="America/Costa_Rica")
    p.add_argument("--platforms", default="instagram")
    p.add_argument("--first-comment")
    p.add_argument("--blog-id", help="marca de Metricool para esta corrida (por defecto METRICOOL_BLOG_ID)")
    p.add_argument("--again", action="store_true", help="repetir una pieza que ya se programó")
    p.add_argument("--confirm", action="store_true", help="enviar de verdad (sin esto es una prueba)")
    a = ap.parse_args(argv)
    if a.selftest:
        print(f"metricool selftest OK ({selftest()} casos)")
        return 0
    if a.cmd == "accounts":
        m = Metricool(blog="0")
        for r in m.blogs():
            print(f"{r.get('id')}: {r.get('label') or r.get('title') or r.get('name')}")
        return 0
    if a.cmd == "post":
        return cmd_post(a)
    ap.error("usar --selftest, accounts o post")
    return 2


if __name__ == "__main__":
    sys.exit(main())
