# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engines" / "logo"))
import logo_qc  # noqa: E402
import brand  # noqa: E402

B = brand.load_brand(None)
BG, AC = logo_qc.hex_rgb(B["colors"]["background"]), logo_qc.hex_rgb(B["colors"]["accent"])
N = 1024


def disc(radius):
    return lambda x, y: (*AC, 255) if math.hypot(x - N / 2, y - N / 2) < radius else (*BG, 255)


def test_profile_inside_circle_passes(tmp_path):
    logo_qc.write_png(tmp_path / "p.png", N, N, disc(300))
    r = logo_qc.check("perfil", tmp_path / "p.png", B)
    assert r["ok"], r
    assert "accent" in r["colores_de_marca"]


def test_profile_touching_edge_or_not_square_fails(tmp_path):
    logo_qc.write_png(tmp_path / "big.png", N, N, disc(530))
    assert any("borde" in p for p in logo_qc.check("perfil", tmp_path / "big.png", B)["problemas"])
    logo_qc.write_png(tmp_path / "wide.png", N + 200, N, lambda x, y: (*BG, 255))
    assert any("cuadrado" in p for p in logo_qc.check("perfil", tmp_path / "wide.png", B)["problemas"])


def test_logotype_needs_real_transparency(tmp_path):
    mark = lambda fill: lambda x, y: (*AC, 255) if 300 < x < 700 and 400 < y < 600 else fill  # noqa: E731
    logo_qc.write_png(tmp_path / "ok.png", N, N, mark((0, 0, 0, 0)))
    logo_qc.write_png(tmp_path / "white.png", N, N, mark((255, 255, 255, 255)))
    assert logo_qc.check("logotipo", tmp_path / "ok.png", B)["ok"]
    assert any("transparente" in p for p in logo_qc.check("logotipo", tmp_path / "white.png", B)["problemas"])


def test_small_image_is_rejected_not_upscaled(tmp_path):
    logo_qc.write_png(tmp_path / "s.png", 512, 512, disc(100))
    before = (tmp_path / "s.png").read_bytes()
    r = logo_qc.check("perfil", tmp_path / "s.png", B)
    assert any("1024" in p for p in r["problemas"])
    assert (tmp_path / "s.png").read_bytes() == before  # the check never edits the file


def test_not_a_png(tmp_path):
    (tmp_path / "x.jpg").write_bytes(b"\xff\xd8\xff\xe0")
    assert logo_qc.main(["perfil", str(tmp_path / "x.jpg")]) == 2


def test_profile_with_transparent_background_fails(tmp_path):
    logo_qc.write_png(tmp_path / "t.png", N, N, lambda x, y: (*AC, 255) if math.hypot(x - N / 2, y - N / 2) < 300 else (0, 0, 0, 0))
    assert any("transparente" in p for p in logo_qc.check("perfil", tmp_path / "t.png", B)["problemas"])
