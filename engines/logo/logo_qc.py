# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Quality check for AI-made logos (ChatGPT, Higgsfield, Magnific) before a member uses them.
Stdlib only: reads PNGs itself, never edits or upscales the image.

  perfil    square Instagram profile icon on a solid brand background; the mark must stay
            inside the circle Instagram crops to, and the background must be one flat color
  logotipo  wordmark with a REAL transparent background (alpha channel), not white or a
            painted checkerboard

Usage:
  python logo_qc.py perfil   FILE.png [--brand brand.json]
  python logo_qc.py logotipo FILE.png [--brand brand.json]
  python logo_qc.py --selftest
Exit 0 = pass, 1 = fails (with the reason to put in the next prompt), 2 = unreadable file.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import brand as brandmod  # noqa: E402

MIN_SIDE = 1000       # ChatGPT gives 1024; Instagram shows profiles at 320
CIRCLE_SAFE = 0.46    # radius (fraction of the side) the mark must stay inside
BG_TOL = 40           # RGB distance that still counts as "the background color"
COLOR_TOL = 90        # RGB distance to count a pixel as one of the brand colors


class PNGError(ValueError):
    pass


def read_png(path: Path) -> tuple[int, int, int, list[bytearray]]:
    """-> (width, height, channels, rows); 8-bit gray/gray+alpha/RGB/RGBA, non-interlaced."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PNGError("no es un PNG (exportá o descargá el logo como .png)")
    pos, idat, w = 8, b"", 0
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or interlace or ctype not in (0, 2, 4, 6):
                raise PNGError("formato PNG no soportado (volvé a exportar como PNG de 8 bits)")
            ch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
        elif kind == b"IDAT":
            idat += chunk
        pos += 12 + n
    if not w:
        raise PNGError("PNG sin encabezado")
    raw, stride = zlib.decompress(idat), w * ch
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - ch] if i >= ch else 0
            b, c = prev[i], (prev[i - ch] if i >= ch else 0)
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    return w, h, ch, rows


def pixel(rows, ch, x, y) -> tuple[int, int, int, int]:
    r = rows[y]
    i = x * ch
    if ch == 1:
        return r[i], r[i], r[i], 255
    if ch == 2:
        return r[i], r[i], r[i], r[i + 1]
    return (r[i], r[i + 1], r[i + 2], r[i + 3] if ch == 4 else 255)


def dist(a, b) -> float:
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


def hex_rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def sample(w, h, step):
    return ((x, y) for y in range(0, h, step) for x in range(0, w, step))


def brand_color_hits(rows, ch, w, h, colors: dict, step: int, keep) -> list[str]:
    """Brand colors that actually appear in the mark (pixels selected by keep)."""
    counts, total = {k: 0 for k in colors}, 0
    for x, y in sample(w, h, step):
        p = pixel(rows, ch, x, y)
        if not keep(p):
            continue
        total += 1
        for k, c in colors.items():
            if dist(p, c) <= COLOR_TOL:
                counts[k] += 1
    return [k for k, n in counts.items() if total and n / total >= 0.02]


def check(kind: str, path: Path, b: dict) -> dict:
    w, h, ch, rows = read_png(path)
    probs, notes = [], []
    # ponytail: a horizontal logotipo is naturally wide; only its long side must reach MIN_SIDE
    if (min(w, h) if kind == "perfil" else max(w, h)) < MIN_SIDE or min(w, h) < MIN_SIDE // 2:
        probs.append(f"mide {w}x{h}: pedilo de nuevo a 1024x1024 (nunca lo agrandes después)")
    step = max(1, min(w, h) // 256)
    colors = {k: hex_rgb(v) for k, v in b["colors"].items()}
    if kind == "perfil":
        if w != h:
            probs.append(f"no es cuadrado ({w}x{h}): pedilo 1:1")
        corners = [pixel(rows, ch, x, y) for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
        bg = corners[0]
        if min(c[3] for c in corners) < 250:  # transparent corners all "match" each other: check alpha first
            probs.append("el fondo es transparente: la foto de perfil necesita fondo sólido del color de la marca (pedí 'solid opaque background')")
        elif any(dist(c, bg) > BG_TOL for c in corners):
            probs.append("el fondo no es de un solo color: pedí fondo sólido del color de la marca")
        cx, cy, r = w / 2, h / 2, CIRCLE_SAFE * min(w, h)
        out = sum(1 for x, y in sample(w, h, step)
                  if math.hypot(x - cx, y - cy) > r and dist(pixel(rows, ch, x, y), bg) > BG_TOL)
        if out > 3:
            probs.append("el dibujo toca el borde: Instagram lo recorta en círculo; pedí el símbolo más chico y centrado")
        if dist(bg, colors["background"]) > COLOR_TOL:
            notes.append(f"el fondo no es el color 'background' de la marca ({b['colors']['background']})")
        keep = lambda p: dist(p, bg) > BG_TOL  # noqa: E731
    else:
        if ch not in (2, 4):
            probs.append("no tiene fondo transparente (el PNG no tiene canal alfa): pedí 'transparent background PNG'")
            keep = lambda p: True  # noqa: E731
        else:
            px = [pixel(rows, ch, x, y) for x, y in sample(w, h, step)]
            clear = sum(1 for p in px if p[3] < 10) / len(px)
            corners = [pixel(rows, ch, x, y)[3] for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
            if clear < 0.2 or max(corners) > 10:
                probs.append("el fondo no es transparente de verdad (hay un fondo pintado): pedí 'transparent background PNG'")
            keep = lambda p: p[3] > 200  # noqa: E731
    hits = brand_color_hits(rows, ch, w, h, {k: v for k, v in colors.items() if k != "background" or kind == "logotipo"}, step, keep)
    if not hits:
        notes.append("no se ve ningún color de la marca: revisá los colores que pusiste en el pedido")
    return {"file": str(path), "kind": kind, "size": [w, h], "ok": not probs,
            "problemas": probs, "avisos": notes, "colores_de_marca": hits}


def write_png(path: Path, w: int, h: int, px) -> None:
    """Tiny RGBA writer for the selftest."""
    raw = b"".join(b"\0" + bytes(v for x in range(w) for v in px(x, y)) for y in range(h))
    def chunk(k, d):
        return struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def selftest() -> int:
    b = brandmod.load_brand(None)
    bg, ac = hex_rgb(b["colors"]["background"]), hex_rgb(b["colors"]["accent"])
    n = 1024
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        disc = lambda R: lambda x, y: (*ac, 255) if math.hypot(x - n / 2, y - n / 2) < R else (*bg, 255)  # noqa: E731
        write_png(d / "ok.png", n, n, disc(300))
        write_png(d / "big.png", n, n, disc(520))
        write_png(d / "t.png", n, 300, lambda x, y: (*ac, 255) if 300 < x < 700 and 100 < y < 200 else (0, 0, 0, 0))
        write_png(d / "white.png", n, 300, lambda x, y: (*ac, 255) if 300 < x < 700 and 100 < y < 200 else (255, 255, 255, 255))
        assert check("perfil", d / "ok.png", b)["ok"]
        assert any("borde" in p for p in check("perfil", d / "big.png", b)["problemas"])
        assert check("logotipo", d / "t.png", b)["ok"] is False  # 1024x300: short side too small
        t = check("logotipo", d / "t.png", b)
        assert not any("transparente" in p for p in t["problemas"]) and "accent" in t["colores_de_marca"]
        assert any("transparente" in p for p in check("logotipo", d / "white.png", b)["problemas"])
        (d / "x.jpg").write_bytes(b"\xff\xd8\xff")
        try:
            read_png(d / "x.jpg")
            raise AssertionError("jpg accepted")
        except PNGError:
            pass
    print("logo_qc selftest OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Revisa un logo hecho con IA antes de usarlo.")
    ap.add_argument("kind", nargs="?", choices=["perfil", "logotipo"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--brand")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.kind and a.file):
        ap.error("kind and file are required")
    try:
        r = check(a.kind, Path(a.file), brandmod.load_brand(a.brand))
    except (OSError, PNGError, zlib.error) as e:
        print(f"logo_qc: {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
