# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Control de marca de agua para las fotos de un carrusel (una persona lo revisa a ojo).

  python check_watermark.py SPEC.json [--project DIR]      prepara: crea <foto>.watermark-check.png
  python check_watermark.py SPEC.json --check              dice si la revisión está aprobada

Las copias en gris y con contraste alto hacen visible la marca de agua casi invisible. Quien revisa las
mira una por una; si alguna tiene texto, logo o marca, se descarta esa foto. Después escribe en
`watermark.json` (junto al spec) "verdict": "OK" y su nombre en "reviewer". Si una foto cambia después
de la revisión, el control vuelve a fallar (se compara el sha256). Necesita Pillow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REVIEW = "watermark.json"


def digest(files: list[Path]) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def boost(path: Path) -> Path:
    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        raise SystemExit("check_watermark: falta Pillow (python -m pip install pillow)")
    with getattr(Image, "open")(path) as im:  # getattr: an image, not a text file
        g = ImageEnhance.Contrast(im.convert("L")).enhance(3.0)
    out = path.with_name(path.stem + ".watermark-check.png")
    ImageEnhance.Brightness(g).enhance(1.6).save(out)
    return out


def prepare(files: list[Path], review_dir: Path) -> Path:
    for p in files:
        print(f"  REVISAR {boost(p)}: si tiene texto, logo o marca, descarta {p.name}")
    out = review_dir / REVIEW
    out.write_text(json.dumps({"status": "pending", "verdict": None, "reviewer": None,
                               "images": digest(files)}, indent=2) + "\n", encoding="utf-8")
    return out


def problems(files: list[Path], review_dir: Path) -> list[str]:
    f = review_dir / REVIEW
    if not f.is_file():
        return [f"falta {REVIEW}: corre check_watermark.py y revisa las fotos"]
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except ValueError:
        return [f"{REVIEW} está dañado: vuelve a prepararlo"]
    out = []
    if data.get("verdict") != "OK" or not data.get("reviewer"):
        out.append(f"{REVIEW}: falta el veredicto OK con el nombre de quien revisó")
    if data.get("images") != digest(files):
        out.append(f"{REVIEW}: las fotos cambiaron después de la revisión")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--project", default=".")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import carousel
    spec_path = Path(a.spec)
    try:
        files = carousel.image_files(json.loads(spec_path.read_text(encoding="utf-8")), Path(a.project))
    except (OSError, ValueError) as e:
        print(f"check_watermark: {e}", file=sys.stderr)
        return 2
    if not files:
        print("check_watermark: el spec no usa fotos, nada que revisar")
        return 0
    if a.check:
        probs = problems(files, spec_path.parent)
        for p in probs:
            print(f"check_watermark: {p}", file=sys.stderr)
        return 3 if probs else 0
    print(prepare(files, spec_path.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
