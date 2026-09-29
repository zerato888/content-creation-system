# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Carousel modules, cover circle, photo checks (faces, sources, watermark) and brand lookup. Offline."""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engines" / "carousel"))
import carousel  # noqa: E402  (puts engines/ on the path)
import brand  # noqa: E402
import check_watermark  # noqa: E402
import faces  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 16
VAULT_MODULES = """problema contexto friccion contradiccion polarizacion plot_twist referencia_relatable critica
antes_despues comparacion_pais mito_realidad que_significa_para_vos villano_victima lo_que_nadie_dice doble_estandar
abogado_del_diablo encuesta_ab dato_que_no_cuadra letra_chica ya_paso_antes ironia traducido_a_tu_bolsillo la_escena
meme_frase_viral voz_experta documento linea_de_tiempo que_viene_ahora tu_turno""".split()


def sl(t, mod=None, **kw):
    base = {"cover": {"title": "Titular propio del tema"}, "body": {"text": "texto"}, "stat": {"value": "3", "text": "x"},
            "cta": {"text": "¿A o B?"}, "headline": {"title": "t"}}[t]
    return {"type": t, **({"module": mod} if mod else {}), **base, **kw}


def test_catalog_has_all_29_modules_and_valid_groups():
    ids = [m["id"] for m in carousel.MODULES["modules"]]
    assert len(ids) == len(set(ids)) and set(VAULT_MODULES) <= set(ids) and len(VAULT_MODULES) == 29
    for k in ("polarity", "closing_comments", "closing_sales"):
        assert carousel.MODULES[k] and set(carousel.MODULES[k]) <= set(ids)
    table = (ROOT / "presets/carousel/ESTRUCTURAS.md").read_text(encoding="utf-8")
    assert all(f"| {i} |" in table for i in ids)  # the guide documents every module


def test_spec_field_validation():
    bad = [{"type": "body", "text": "x", "module": "inventado"}, {"type": "body", "text": "x", "focus": "101% 0%"},
           {"type": "body", "text": "x", "circle": "c.png"},
           {"type": "cover", "title": "x", "image": "a.png", "image_position": "top"}]
    for s in bad:
        with pytest.raises(carousel.SpecError):
            carousel.validate_spec({"slides": [s]})
    carousel.validate_spec({"slides": [{"type": "body", "text": "x", "focus": "30% top", "module": "friccion"}]})


def test_module_rules():
    ok = [sl("cover", "problema", image="a"), sl("body", "friccion", image="a"), sl("stat", "dato_que_no_cuadra", image="a"),
          sl("cta", "tu_turno", image="a")]
    assert carousel.structure_warnings(ok, "comments") == []
    no_tension = copy.deepcopy(ok)
    no_tension[1]["module"] = "contexto"
    assert any("sin tensión" in w for w in carousel.structure_warnings(no_tension))
    bad_close = copy.deepcopy(ok)
    bad_close[-1].update(module="oferta", text="Compra ya")
    w = carousel.structure_warnings(bad_close, "comments")
    assert any("cierre" in x for x in w) and any("pregunta" in x for x in w)
    assert carousel.structure_warnings(bad_close, "sales") == []
    assert any("ventas" in x for x in carousel.structure_warnings(ok, "sales"))
    bare = copy.deepcopy(ok)
    del bare[1]["image"], bare[2]["image"]
    assert any("sin foto" in x for x in carousel.structure_warnings(bare))


def test_no_modules_means_no_module_rules_and_comment_goal_asks_a_question():
    plain = [{"type": "cover", "title": "Tema"}, {"type": "body", "text": "a"}, {"type": "stat", "value": "1", "text": "b"},
             {"type": "cta", "text": "Compra"}]
    assert carousel.structure_warnings(plain) == []
    assert any("pregunta" in x for x in carousel.structure_warnings(plain, "comments"))


def test_quoted_cover_and_repeated_run_warn():
    s = [{"type": "cover", "title": "«El precio sigue al problema»"}, {"type": "body", "text": "El precio sigue al problema de todos"},
         {"type": "stat", "value": "1", "text": "Nada"}, {"type": "cta", "text": "?"}]
    w = carousel.structure_warnings(s)
    assert any("cita entre comillas" in x for x in w) and any("repiten" in x for x in w)


def test_source_files(tmp_path):
    a, b, c = (tmp_path / n for n in ("a.jpg", "b.jpg", "c.jpg"))
    for f in (a, b, c):
        f.write_bytes(PNG)
    (tmp_path / "a.source.json").write_text(json.dumps({"origin": "own"}), encoding="utf-8")
    (tmp_path / "b.source.json").write_text(json.dumps({"origin": "press"}), encoding="utf-8")
    probs = carousel.source_problems([a, b, c])
    assert len(probs) == 2 and "source_url" in probs[0] and "c.source.json" in probs[1]
    (tmp_path / "b.source.json").write_text(json.dumps({"origin": "press", "source_url": "https://x.org/n"}), encoding="utf-8")
    assert carousel.source_problems([a, b]) == []


def test_watermark_review_roundtrip(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image
    Image.new("RGB", (40, 40), "red").save(tmp_path / "a.png")
    files = [tmp_path / "a.png"]
    check_watermark.prepare(files, tmp_path)
    assert (tmp_path / "a.watermark-check.png").is_file()
    assert any("veredicto" in p for p in check_watermark.problems(files, tmp_path))
    rev = tmp_path / "watermark.json"
    d = json.loads(rev.read_text(encoding="utf-8"))
    d.update(verdict="OK", reviewer="Ana")
    rev.write_text(json.dumps(d), encoding="utf-8")
    assert check_watermark.problems(files, tmp_path) == []
    Image.new("RGB", (40, 40), "blue").save(tmp_path / "a.png")  # changed after the review
    assert any("cambiaron" in p for p in check_watermark.problems(files, tmp_path))


def test_face_math():
    head = (0.4, 0.1, 0.6, 0.4)
    assert faces.cut_faces([head], (0.0, 0.0, 1.0, 1.0)) == []
    assert faces.cut_faces([head], (0.0, 0.25, 1.0, 1.0)) == [head]  # forehead above the visible edge
    pos = faces.auto_focal((1000, 1000), (1080, 470), [head])  # wide band over a square photo
    assert pos and not faces.cut_faces([head], faces.window((1000, 1000), (1080, 470), pos))
    assert faces.auto_focal((1000, 1000), (1080, 470), []) is None
    assert faces.parse_pos("30% top") == (30.0, 0.0)


def test_face_check_without_detector_only_notes(tmp_path, monkeypatch):
    monkeypatch.setattr(faces, "available", lambda: False)
    (tmp_path / "a.png").write_bytes(PNG)
    spec = {"slides": [{"type": "cover", "title": "T", "image": "a.png"}]}
    auto, bad, notes = carousel.face_check(spec, tmp_path)
    assert auto == {} and bad == [] and "detector de caras" in notes[0]


def test_face_check_flags_cut_face_and_sets_auto_focus(tmp_path, monkeypatch):
    monkeypatch.setattr(faces, "available", lambda: True)
    monkeypatch.setattr(faces, "image_size", lambda p: (1000, 1000))
    (tmp_path / "a.png").write_bytes(PNG)
    spec = {"slides": [{"type": "body", "text": "x", "image": "a.png", "image_position": "top"}]}
    monkeypatch.setattr(faces, "detect_faces", lambda p: [(0.4, 0.1, 0.6, 0.4)])
    auto, bad, _ = carousel.face_check(spec, tmp_path)
    assert bad == [] and auto["1:image"].endswith("%")
    tall = [(0.3, 0.0, 0.7, 0.9)]  # taller than the 470 px band shows: cannot fit
    monkeypatch.setattr(faces, "detect_faces", lambda p: tall)
    _, bad, _ = carousel.face_check(spec, tmp_path)
    assert bad and "cortada" in bad[0]
    spec["slides"][0]["focus"] = "50% 50%"  # manual focus wins and is reported as such
    _, bad, _ = carousel.face_check(spec, tmp_path)
    assert "foco manual" in bad[0]


def test_cover_circle_and_focus_in_html(tmp_path):
    (tmp_path / "bg.png").write_bytes(PNG)
    (tmp_path / "ctx.png").write_bytes(PNG)
    spec = {"slides": [{"type": "cover", "title": "T", "image": "bg.png", "circle": "ctx.png", "focus": "30% 20%"}]}
    page = carousel.build_html(spec, brand.load_brand(None), tmp_path, {"1:circle": "40% 10%"})[0]
    assert 'class="circle"' in page and "background-position:40% 10%" in page and "background-position:30% 20%" in page
    css = (ROOT / "presets/carousel/slide.css").read_text(encoding="utf-8")
    assert ".s-cover .shade" in css and "border-radius: 50%" in css


def test_long_titles_shrink_short_ones_do_not():
    assert carousel.fit("h1", "Corto") == ""
    assert "font-size:" in carousel.fit("h1", "x" * 90)
    assert carousel.fit("cta", "y" * 200) != ""


def test_brand_by_name(tmp_path, monkeypatch):
    d = tmp_path / ".kit-personal" / "brands"
    d.mkdir(parents=True)
    (d / "mia.json").write_text(json.dumps({"name": "Mia"}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert carousel.brand_path("mia", tmp_path).endswith("mia.json")
    assert carousel.brand_path("x.json", tmp_path) == "x.json" and carousel.brand_path(None, tmp_path) is None
    with pytest.raises(carousel.SpecError):
        carousel.brand_path("nadie", tmp_path)


def test_cli_strict_demands_sources_and_review(tmp_path, capsys):
    (tmp_path / "a.png").write_bytes(PNG)
    spec = {"slides": [{"type": "cover", "title": "Tema", "image": "a.png"}, {"type": "body", "text": "a"},
                       {"type": "stat", "value": "1", "text": "b"}, {"type": "cta", "text": "Sigue"}]}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(spec), encoding="utf-8")
    base = [str(p), "--project", str(tmp_path), "--html-only", "--out", str(tmp_path / "o")]
    assert carousel.main(base) == 0  # advice only
    assert carousel.main(base + ["--strict"]) == 2
    err = capsys.readouterr().err
    assert "a.source.json" in err and "watermark.json" in err


def test_cli_lenient_run_notes_missing_face_detector(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(faces, "available", lambda: False)
    (tmp_path / "a.png").write_bytes(PNG)
    spec = {"slides": [{"type": "cover", "title": "Tema", "image": "a.png"}, {"type": "body", "text": "a"},
                       {"type": "stat", "value": "1", "text": "b"}, {"type": "cta", "text": "Sigue"}]}
    (tmp_path / "s.json").write_text(json.dumps(spec), encoding="utf-8")
    assert carousel.main([str(tmp_path / "s.json"), "--project", str(tmp_path), "--html-only", "--out", str(tmp_path / "o")]) == 0
    assert "detector de caras" in capsys.readouterr().err


def test_cover_with_circle_renders_png(tmp_path):
    pytest.importorskip("playwright")
    pytest.importorskip("PIL")
    if not (ROOT / ".kit" / "fonts").is_dir() and not os.environ.get("KIT_FONTS_DIR"):
        pytest.skip("kit fonts not installed")
    from PIL import Image
    Image.new("RGB", (1080, 1350), (40, 60, 90)).save(tmp_path / "bg.jpg")
    Image.new("RGB", (400, 400), (200, 90, 40)).save(tmp_path / "ctx.jpg")
    spec = {"slides": [{"type": "cover", "title": "Publicas todos los días y nadie reserva", "highlight": "nadie reserva",
                        "subtitle": "El problema no es cuánto publicas", "image": "bg.jpg", "circle": "ctx.jpg"}]}
    paths = carousel.write_html(carousel.build_html(spec, brand.load_brand(None), tmp_path), tmp_path / "out")
    try:
        pngs = carousel.render_png(paths)
    except SystemExit as e:
        pytest.skip(str(e))
    assert pngs[0].read_bytes()[:8] == PNG[:8]
