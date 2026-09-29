# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Baja una imagen de internet y verifica que sea una imagen real y de tamaño usable (sin dependencias).

    python .kit/launch.py fetch-image <url> <destino> [--min-side 720]

Sale con código 1 y el motivo si no baja, no es imagen o es demasiado chica. Nunca la reescala.
"""
from __future__ import annotations

import argparse
import ssl
import struct
import sys
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (compatible; content-kit fetch-image)"


def dimensions(b: bytes):
    """(ancho, alto) leyendo el encabezado de PNG, GIF, JPEG o WebP; None si no es imagen."""
    if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) >= 24:
        return struct.unpack(">II", b[16:24])
    if b[:6] in (b"GIF87a", b"GIF89a") and len(b) >= 10:
        return struct.unpack("<HH", b[6:10])
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP" and len(b) >= 30:
        if b[12:16] == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if b[12:16] == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if b[12:16] == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            n = struct.unpack(">H", b[i + 2:i + 4])[0]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + n
    return None


def fetch(url: str, dest: Path, min_side: int = 720, opener=None):
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("solo URLs http(s)")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    ctx = ssl.create_default_context()
    with (opener or (lambda r: urllib.request.urlopen(r, timeout=30, context=ctx)))(req) as r:
        data = r.read(50_000_000)
    dim = dimensions(data)
    if not dim:
        raise ValueError("no es una imagen (PNG, JPG, GIF o WebP)")
    if min(dim) < min_side:
        raise ValueError(f"imagen chica: {dim[0]}x{dim[1]} (mínimo {min_side}px en el lado corto)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dim


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("dest")
    ap.add_argument("--min-side", type=int, default=720)
    a = ap.parse_args(argv)
    try:
        w, h = fetch(a.url, Path(a.dest), a.min_side)
    except Exception as e:  # noqa: BLE001 - se informa el motivo y se sale con 1
        print(f"falló: {type(e).__name__}: {e}")
        return 1
    print(f"ok {w}x{h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
