# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
import copy
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
