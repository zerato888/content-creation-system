# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
import copy
import os
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engines" / "carousel"))
import carousel  # noqa: E402
import brand  # noqa: E402

DEMO = json.loads((ROOT / "presets/carousel/demo-spec.json").read_text(encoding="utf-8"))
PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 16


def build(spec, tmp_path, b=None):
    return carousel.build_html(spec, b or brand.load_brand(None), tmp_path)


@pytest.mark.parametrize("spec", [
    {}, {"slides": []}, {"slides": [{"type": "nope"}]},
    {"slides": [{"type": "cover"}]}, {"slides": [{"type": "body", "text": 3}]},
    {"slides": [{"type": "body", "text": "x" * 601}]},
])
def test_invalid_spec(spec):
    with pytest.raises(carousel.SpecError):
        carousel.validate_spec(spec)


def test_demo_covers_every_type_and_renders(tmp_path):
    pages = build(DEMO, tmp_path)
    assert {s["type"] for s in DEMO["slides"]} == carousel.TYPES
    assert len(pages) == len(DEMO["slides"])
    assert all('class="media panel"' in pages[i] for i, s in enumerate(DEMO["slides"])
               if s["type"] in ("cover", "headline", "cta"))
    paths = carousel.write_html(pages, tmp_path / "out")
    assert all(p.exists() for p in paths)


def test_escaping_inert(tmp_path):
    spec = {"slides": [{"type": "body", "text": "<script>alert(1)</script>", "highlight": "<script>",
                        "label": "\"><img src=x onerror=1>"}]}
    page = build(spec, tmp_path)[0]
    assert "<script>alert" not in page and "<img src=x" not in page
    assert "&lt;script&gt;" in page


def test_brand_tokens_applied(tmp_path):
    b = brand.load_brand(None)
    b["colors"]["accent"] = "#123456"
    page = build(DEMO, tmp_path, b)[0]
    assert "#123456" in page and b["logo_text"] in page


def test_tolerant_brand(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"name": "X", "colors": {"accent": "red"}, "extra": 1}), encoding="utf-8")
    b = brand.load_brand(p)
    assert len(build(DEMO, tmp_path, b)) == len(DEMO["slides"])


def test_image_confinement(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "ok.png").write_bytes(PNG)
    (proj / "bad.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "out.png").write_bytes(PNG)
    assert carousel.safe_image("ok.png", proj) == (proj / "ok.png").resolve()
    for bad in ["../out.png", str(tmp_path / "out.png"), "bad.svg", "missing.jpg", "https://x/y.jpg"]:
        with pytest.raises(carousel.SpecError):
            carousel.safe_image(bad, proj)
    spec = copy.deepcopy(DEMO)
    spec["slides"][0]["image"] = "ok.png"
    page = carousel.build_html(spec, brand.load_brand(None), proj)[0]
    assert (proj / "ok.png").resolve().as_uri() in page


def test_selftest():
    assert carousel.selftest() == 0


def test_png_render(tmp_path):
    pytest.importorskip("playwright")
    paths = carousel.write_html(build(DEMO, tmp_path)[:1], tmp_path)
    try:
        pngs = carousel.render_png(paths)
    except SystemExit as e:
        pytest.skip(str(e))
    assert pngs[0].read_bytes()[:8] == PNG[:8]


# --- punto0: ejemplos, franja de foto, estructura y control de calidad al renderizar ---
EXAMPLES = ["servicios", "marca-personal", "producto"]


@pytest.mark.parametrize("name", EXAMPLES)
def test_examples_are_valid_and_well_structured(name, tmp_path):
    spec = json.loads((ROOT / f"presets/carousel/ejemplo-{name}.json").read_text(encoding="utf-8"))
    b = brand.load_brand(ROOT / f"presets/brands/ejemplo-{name}.json")
    assert b["name"] != brand.DEFAULTS["name"]  # the example brand really loaded
    assert len(build(spec, tmp_path, b)) == len(spec["slides"])
    assert carousel.structure_warnings(spec["slides"]) == []


def test_structure_warnings():
    s = lambda *t: [{"type": x} for x in t]  # noqa: E731
    assert carousel.structure_warnings(s("cover", "body", "stat", "cta")) == []
    w = carousel.structure_warnings(s("body", "stat", "stat"))
    assert any("4 a 8" in x for x in w) and any("cover" in x for x in w)
    assert any("'cta'" in x for x in w) and any("mismo tipo" in x for x in w)


def test_image_position(tmp_path):
    (tmp_path / "foto.png").write_bytes(PNG)
    spec = {"slides": [{"type": "body", "text": "x", "image": "foto.png", "image_position": "top"}]}
    page = build(spec, tmp_path)[0]
    assert 'class="slide s-body band-top"' in page and 'class="media band-top"' in page
    assert 'class="shade"' not in page
    for bad in ({"type": "body", "text": "x", "image_position": "top"},
                {"type": "body", "text": "x", "image": "foto.png", "image_position": "left"}):
        with pytest.raises(carousel.SpecError):
            carousel.validate_spec({"slides": [bad]})


def _render_or_skip(paths):
    pytest.importorskip("playwright")
    try:
        return carousel.render_png(paths)
    except SystemExit as e:
        pytest.skip(str(e))


def test_qc_blocks_overflow_and_missing_font(tmp_path, monkeypatch):
    monkeypatch.setenv("KIT_FONTS_DIR", str(tmp_path / "no-fonts"))  # no kit fonts: nothing loads
    long = {"slides": [{"type": "cover", "title": "Supercalifragilisticoespialidosamente"}]}
    paths = carousel.write_html(build(long, tmp_path), tmp_path / "out")
    with pytest.raises(carousel.QCError) as e:
        _render_or_skip(paths)
    msg = str(e.value)
    assert "no cargó" in msg and "no entra a lo ancho" in msg
    assert not (tmp_path / "out" / "slide-01.png").exists()  # a failing slide never gets a PNG


def test_qc_blocks_accent_collision(tmp_path, monkeypatch):
    fonts = ROOT / ".kit" / "fonts"
    if not (fonts.is_dir() or os.environ.get("KIT_FONTS_DIR")):
        pytest.skip("kit fonts not installed")
    css = (ROOT / "presets/carousel/slide.css").read_text(encoding="utf-8")
    monkeypatch.setattr(carousel, "PRESETS", tmp_path)
    (tmp_path / "slide.html").write_text((ROOT / "presets/carousel/slide.html").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "slide.css").write_text(css + "\nh1 { line-height: .9 !important; }", encoding="utf-8")
    spec = {"slides": [{"type": "cover", "title": "Todos los días y nadie reserva"}]}
    paths = carousel.write_html(build(spec, tmp_path), tmp_path / "out")
    with pytest.raises(carousel.QCError, match="tilde"):
        _render_or_skip(paths)
