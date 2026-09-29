# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Caras completas: detección (macOS Vision, opcional) + matemática pura del recorte.

Sin el detector (Windows, Linux, o Mac sin pyobjc) nada falla: `available()` dice False y el motor avisa.
Instalarlo en Mac: python -m pip install pyobjc-framework-Vision pillow

Cajas y ventanas en coordenadas normalizadas de la imagen (0..1, origen arriba a la izquierda):
(x0, y0, x1, y1). El recorte es el de CSS `background-size:cover` + `background-position:X% Y%`.
"""
from __future__ import annotations

import io
import math
from functools import lru_cache
from pathlib import Path

MIN_FACE = 0.04     # ponytail: caras de menos del 4% del alto de la imagen (público de fondo) se ignoran
MIN_CONF = 0.5
MARGIN = 0.12       # margen alrededor de las cabezas al calcular el foco, en altos de cara
EPS = 0.004         # tolerancia de borde (≈ 2 px en una franja de 560)


class DetectorError(RuntimeError):
    pass


def available() -> bool:
    """¿Hay detector de caras en esta máquina? Nunca lanza."""
    try:
        import Vision  # noqa: F401
        import Foundation  # noqa: F401
        import PIL  # noqa: F401
    except ImportError:
        return False
    return True


def image_size(path: Path) -> tuple[int, int]:
    from PIL import Image, ImageOps
    with getattr(Image, "open")(path) as im:  # getattr: an image, not a text file
        return ImageOps.exif_transpose(im).size


@lru_cache(maxsize=None)
def _detect(path: str, mtime: float) -> tuple[tuple[float, float, float, float], ...]:
    try:
        import Vision
        from Foundation import NSData
        from PIL import Image, ImageOps
    except ImportError as e:
        raise DetectorError(f"no hay detector de caras disponible (macOS Vision vía pyobjc, opcional + Pillow): {e}")
    with getattr(Image, "open")(path) as im:  # getattr: an image, not a text file  # se normaliza la orientación EXIF igual que el navegador
        buf = io.BytesIO()
        ImageOps.exif_transpose(im).convert("RGB").save(buf, "PNG")
    data = NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    req = Vision.VNDetectFaceRectanglesRequest.alloc().init()
    handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(data, None)
    ok, err = handler.performRequests_error_([req], None)
    if not ok:
        raise DetectorError(f"Vision falló con {path}: {err}")
    out = []
    for o in req.results() or []:
        b = o.boundingBox()  # Vision: origen abajo a la izquierda
        x0, w, h = b.origin.x, b.size.width, b.size.height
        y0 = 1 - b.origin.y - h
        if o.confidence() >= MIN_CONF and h >= MIN_FACE:
            out.append(head((x0, y0, x0 + w, y0 + h)))
    return tuple(out)


HEAD_UP, HEAD_DOWN = 0.45, 0.1  # Vision encuadra de cejas a mentón: se agrega frente/pelo y un poco de mentón


def head(f):
    """Caja de la cabeza a partir de la caja de cara de Vision (lo que no se puede cortar)."""
    h = f[3] - f[1]
    return max(0.0, f[0]), max(0.0, f[1] - HEAD_UP * h), min(1.0, f[2]), min(1.0, f[3] + HEAD_DOWN * h)


def detect_faces(path: Path) -> list[tuple[float, float, float, float]]:
    """Cajas de cabeza (cara de Vision + frente/pelo) de la imagen. Sin detector → DetectorError (quien llama decide avisar)."""
    return list(_detect(str(path), Path(path).stat().st_mtime))


def _span(img_wh, box_wh):
    """Tamaño de la ventana visible (normalizado) con background-size:cover."""
    s = max(box_wh[0] / img_wh[0], box_wh[1] / img_wh[1])
    return box_wh[0] / (img_wh[0] * s), box_wh[1] / (img_wh[1] * s)


def window(img_wh, box_wh, pos) -> tuple[float, float, float, float]:
    """Parte visible de la imagen para background-position `pos` = (X%, Y%)."""
    vw, vh = _span(img_wh, box_wh)
    x0, y0 = (1 - vw) * pos[0] / 100, (1 - vh) * pos[1] / 100
    return x0, y0, x0 + vw, y0 + vh


_KW = {"left": 0, "top": 0, "center": 50, "right": 100, "bottom": 100}


def parse_pos(pos: str) -> tuple[float, float]:
    """'30% 20%', 'center top', '40%' → (X, Y) en %."""
    parts = pos.split()
    vals = [float(p[:-1]) if p.endswith("%") else _KW[p] for p in parts]
    if len(vals) == 1:
        vals.append(50.0)
    if parts[0] in ("top", "bottom") or (len(parts) > 1 and parts[1] in ("left", "right")):
        vals.reverse()
    return vals[0], vals[1]


def _fit(lo, hi, span):
    """Posición % que centra [lo, hi] en una ventana de ancho `span`."""
    if span >= 1:
        return 50.0
    start = min(max((lo + hi) / 2 - span / 2, 0.0), 1 - span)
    return round(start / (1 - span) * 100, 1)


def auto_focal(img_wh, box_wh, faces) -> tuple[float, float] | None:
    """Foco que deja todas las caras enteras con margen; si no entran todas, prueba con la más grande.
    None si no hay caras (se queda el foco por defecto del layout)."""
    if not faces:
        return None
    vw, vh = _span(img_wh, box_wh)
    biggest = max(faces, key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))
    best = None
    for group in (faces, [biggest]):
        m = MARGIN * max(f[3] - f[1] for f in group)
        x0, y0 = min(f[0] for f in group) - m, min(f[1] for f in group) - m
        x1, y1 = max(f[2] for f in group) + m, max(f[3] for f in group) + m
        pos = (_fit(x0, x1, vw), _fit(y0, y1, vh))
        best = best or pos
        if not cut_faces(faces, window(img_wh, box_wh, pos)):
            return pos
    return best


def cut_faces(faces, win, circle: bool = False) -> list[tuple[float, float, float, float]]:
    """Pura: caras que el borde visible corta (parte adentro y parte afuera). Las que quedan
    completamente afuera no se ven y no cuentan. `circle`: la ventana es un círculo inscripto."""
    wx0, wy0, wx1, wy1 = win
    out = []
    for f in faces:
        inter = min(f[2], wx1) - max(f[0], wx0) > EPS and min(f[3], wy1) - max(f[1], wy0) > EPS
        if not inter:
            continue
        if circle:  # la cara se aproxima con la elipse inscripta en su caja (las esquinas son pelo/aire)
            # en el círculo se exige la cara (sin el pelo de arriba): un retrato circular recorta pelo siempre
            hh = (f[3] - f[1]) / (1 + HEAD_UP + HEAD_DOWN)
            fy0, fy1 = f[1] + HEAD_UP * hh, f[3] - HEAD_DOWN * hh
            fcx, fcy, frx, fry = (f[0] + f[2]) / 2, (fy0 + fy1) / 2, (f[2] - f[0]) / 2, (fy1 - fy0) / 2
            cx, cy, rx, ry = (wx0 + wx1) / 2, (wy0 + wy1) / 2, (wx1 - wx0) / 2, (wy1 - wy0) / 2
            pts = [(fcx + frx * math.cos(t * math.pi / 8), fcy + fry * math.sin(t * math.pi / 8)) for t in range(16)]
            if any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1 + EPS for x, y in pts):
                out.append(f)
        elif f[0] < wx0 - EPS or f[1] < wy0 - EPS or f[2] > wx1 + EPS or f[3] > wy1 + EPS:
            out.append(f)
    return out


def css_pos(pos: tuple[float, float]) -> str:
    return f"{pos[0]:g}% {pos[1]:g}%"

