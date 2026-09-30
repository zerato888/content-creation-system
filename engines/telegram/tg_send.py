# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Manda una pieza (o un texto) a tu celular con TU bot de Telegram. Reemplaza a tg-send.sh.

    python3 .kit/launch.py telegram text "mensaje"
    python3 .kit/launch.py telegram file pieza.mp4 ["pie de foto"] [--confirm]
    python3 .kit/launch.py telegram check

Una sola vez (la clave y el chat nunca van en archivos del proyecto; el llavero los guarda):
  1. En Telegram hablá con @BotFather, creá un bot y copiá el token.
  2. Escribile un mensaje a tu bot; luego abrí https://api.telegram.org/bot<TOKEN>/getUpdates y copiá el "id" del chat.
  3. Mac:      security add-generic-password -s content-kit -a TELEGRAM_BOT_TOKEN -w
               security add-generic-password -s content-kit -a TELEGRAM_CHAT_ID -w
     Windows:  cmdkey /generic:content-kit:TELEGRAM_BOT_TOKEN /user:kit /pass
               cmdkey /generic:content-kit:TELEGRAM_CHAT_ID /user:kit /pass

Videos y audios se mandan reproducibles, imágenes como foto y el resto como archivo. Tope de Telegram: 50 MB.
Sin --confirm `file` solo muestra qué mandaría (prueba). El archivo original nunca se modifica.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import ssl
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kit_secrets  # noqa: E402

LIMIT = 50 * 1024 * 1024
PHOTO_LIMIT = 10 * 1024 * 1024
VIDEO = {".mp4", ".mov", ".m4v", ".webm"}
AUDIO = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac"}
PHOTO = {".jpg", ".jpeg", ".png", ".webp"}


def kind_of(path: Path) -> str:
    ext, size = path.suffix.lower(), path.stat().st_size
    if size > LIMIT:
        raise SystemExit(f"ERROR: pesa {size // 1048576} MB y Telegram acepta hasta 50 MB. Mandá una copia más liviana "
                         "(por ejemplo un .mp4 más comprimido); el original no se toca.")
    if ext in VIDEO:
        return "video"
    if ext in AUDIO:
        return "audio"
    if ext in PHOTO and size <= PHOTO_LIMIT:
        return "photo"
    return "document"


METHOD = {"video": ("sendVideo", "video"), "audio": ("sendAudio", "audio"), "photo": ("sendPhoto", "photo"),
          "document": ("sendDocument", "document")}


def multipart(fields: dict, fname: str, fieldname: str, data: bytes):
    b = uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8")
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    out += (f'--{b}\r\nContent-Disposition: form-data; name="{fieldname}"; filename="{fname}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n").encode("utf-8") + data + f"\r\n--{b}--\r\n".encode("utf-8")
    return out, f"multipart/form-data; boundary={b}"


class Bot:
    def __init__(self, token=None, chat=None, opener=None):
        self.token = token or kit_secrets.get_secret("TELEGRAM_BOT_TOKEN")
        self.chat = chat or kit_secrets.get_secret("TELEGRAM_CHAT_ID")
        if not self.token or not self.chat:
            raise SystemExit("ERROR: faltan TELEGRAM_BOT_TOKEN y/o TELEGRAM_CHAT_ID en tu llavero. "
                             "Pasos: mirá el encabezado de este archivo o la skill `telegram`.")
        ctx = ssl.create_default_context()
        self.send = opener or (lambda req: urllib.request.urlopen(req, timeout=300, context=ctx))

    def call(self, method: str, fields: dict, fname=None, fieldname=None, data=None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        fields = {"chat_id": self.chat, **fields}
        if data is None:
            body, ctype = json.dumps(fields).encode("utf-8"), "application/json"
        else:
            body, ctype = multipart(fields, fname, fieldname, data)
        req = urllib.request.Request(url, data=body, headers={"Content-Type": ctype}, method="POST")
        try:
            with self.send(req) as r:
                res = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            res = {"ok": False, "description": f"HTTP {e.code}"}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise SystemExit(f"ERROR: sin conexión con Telegram ({type(e).__name__}); no se envió nada.")
        if not res.get("ok"):  # el mensaje de error no incluye el token
            raise SystemExit(f"ERROR de Telegram: {res.get('description', 'desconocido')}")
        return res

    def send_file(self, path: Path, caption: str = "") -> str:
        kind = kind_of(path)
        method, field = METHOD[kind]
        extra = {"caption": caption} if caption else {}
        if kind == "video":
            extra["supports_streaming"] = "true"
        try:
            self.call(method, extra, path.name, field, path.read_bytes())
        except SystemExit:
            if kind == "document":
                raise
            self.call("sendDocument", {"caption": caption} if caption else {}, path.name, "document", path.read_bytes())
            return "document"
        return kind


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    t = sub.add_parser("text")
    t.add_argument("message")
    t.add_argument("--confirm", action="store_true")
    f = sub.add_parser("file")
    f.add_argument("path")
    f.add_argument("caption", nargs="?", default="")
    f.add_argument("--confirm", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        for n in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            print(f"{n}: {kit_secrets.lookup(n)[1]}")
        return 0
    if a.cmd == "text":
        if not a.confirm:
            print(f"Prueba: mandaría a tu Telegram: {a.message[:120]}. Si está bien, repetí con --confirm.")
            return 0
        Bot().call("sendMessage", {"text": a.message})
        print("ok")
        return 0
    p = Path(a.path).expanduser()
    if not p.is_file():
        print(f"telegram: no existe {p}", file=sys.stderr)
        return 2
    if not a.confirm:
        print(f"Prueba (no se envió nada): mandaría {p.name} como {kind_of(p)}"
              f"{' con pie: ' + a.caption if a.caption else ''}. Repetí con --confirm para enviarlo.")
        return 0
    print(f"ok ({Bot().send_file(p, a.caption)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
