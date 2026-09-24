# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Small read-only kit assets (hooks bank) and the user's brand logos.

Logos live in TARGET/.kit-personal/data/logos/<brand-id>.<png|jpg|webp>. An upload is
checked by its first bytes (never by its name), capped at 1 MB, and written atomically.
No SVG: a logo is an image, not a document that can carry script.
"""
import base64
import binascii
import json
import os
import re

MAX_LOGO = 1024 * 1024
LOGO_EXTS = ("png", "jpg", "webp")
_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def hooks_bank(kit):
    try:
        with open(os.path.join(kit, "presets", "hooks", "hooks-bank.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _sniff(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _logos_dir(data_root):
    d = os.path.join(data_root, "logos")
    if os.path.islink(d):
        raise ValueError("la carpeta de logos es un enlace simbólico; no la uso")
    return d


def logo_path(data_root, brand):
    """The brand's logo file, or None. `brand` is an already-validated brand id."""
    if not _ID.fullmatch(str(brand or "")):
        return None
    d = _logos_dir(data_root)
    for ext in LOGO_EXTS:
        p = os.path.join(d, f"{brand}.{ext}")
        if os.path.isfile(p) and not os.path.islink(p):
            return p
    return None


def brands_with_logo(data_root, brand_ids):
    try:
        return [b for b in brand_ids if logo_path(data_root, b)]
    except ValueError:
        return []


def save_logo(data_root, brand, b64):
    if not _ID.fullmatch(str(brand or "")):
        raise ValueError("marca inválida")
    if not isinstance(b64, str) or len(b64) > (MAX_LOGO * 4) // 3 + 8:
        raise ValueError("el logo pesa más de 1 MB")
    try:
        data = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("el logo no llegó bien (base64 inválido)")
    if not data or len(data) > MAX_LOGO:
        raise ValueError("el logo pesa más de 1 MB")
    ext = _sniff(data)
    if not ext:
        raise ValueError("solo PNG, JPG o WEBP")
    d = _logos_dir(data_root)
    os.makedirs(d, exist_ok=True)
    final = os.path.join(d, f"{brand}.{ext}")
    if os.path.islink(final):
        raise ValueError("el destino es un enlace simbólico; no lo toco")
    tmp = final + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, final)
    for other in LOGO_EXTS:  # one logo per brand
        p = os.path.join(d, f"{brand}.{other}")
        if other != ext and os.path.isfile(p) and not os.path.islink(p):
            os.remove(p)
    return {"brand": brand, "type": ext, "bytes": len(data)}
