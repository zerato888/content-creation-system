# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Content Lab store, faithful translation contract, productions, library, and scripts."""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.server import guiones, lab  # noqa: E402

BRAND = "canal"


def test_items_roundtrip_archive_delete(tmp_path):
    root = str(tmp_path)
    item = lab.save_item(root, {"tipo": "reel", "tema": "Cómo ordenar ideas", "transcript_original": "Hello"}, BRAND)
    assert item["id"].endswith("c-mo-ordenar-ideas") and item["pieza"]["hook"] == ""
    again = lab.save_item(root, {"tipo": "reel", "tema": "Cómo ordenar ideas"}, BRAND)
    assert again["id"] == item["id"] + "-2"
    lab.save_item(root, {"id": item["id"], "pieza": {"hook": "Nuevo"}, "final_video": {"media_local": "../x"}}, BRAND)
    got = lab.get_item(root, item["id"], BRAND)
    assert got["pieza"]["hook"] == "Nuevo" and got["pieza"]["full_script"] == "" and "final_video" not in got
    lab.archive_item(root, item["id"], True, BRAND)
    assert [i["archivada"] for i in lab.list_items(root, BRAND) if i["id"] == item["id"]] == [True]
    lab.delete_item(root, item["id"], BRAND)
    with pytest.raises(FileNotFoundError):
        lab.get_item(root, item["id"], BRAND)
    assert lab.list_items(root, "otra-marca") == []
    with pytest.raises(ValueError):
        lab.save_item(root, {"tipo": "podcast"}, BRAND)


@pytest.mark.parametrize("bad", ["../x", "a/b", "..", ".hidden", "x\\y", "", None, "a" * 300])
def test_ids_and_brands_never_become_paths(tmp_path, bad):
    root = str(tmp_path)
    for call in (lambda: lab.get_item(root, bad, BRAND), lambda: lab.archive_item(root, bad, True, BRAND),
                 lambda: lab.delete_item(root, bad, BRAND), lambda: lab.list_items(root, bad),
                 lambda: lab.save_item(root, {"id": bad}, BRAND)):
        with pytest.raises((ValueError, FileNotFoundError)):
            call()
    assert not any(p.name == "x" for p in tmp_path.rglob("*"))


def test_media_is_confined(tmp_path):
    root = str(tmp_path)
    item = lab.save_item(root, {"tipo": "reel", "tema": "m"}, BRAND)
    media = tmp_path / "lab" / BRAND / "media" / item["id"]
    media.mkdir(parents=True)
    (media / "cover.jpg").write_bytes(b"jpg")
    assert lab.media_path(root, BRAND, item["id"], "cover.jpg").endswith("cover.jpg")
    for name in ("../../tasks.db", "cover.exe", "x/cover.jpg"):
        with pytest.raises(ValueError):
            lab.media_path(root, BRAND, item["id"], name)
    lab.save_item(root, {"id": item["id"]}, BRAND)
    path = tmp_path / "lab" / BRAND / "activos" / f"{item['id']}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["final_video"] = {"media_local": "../../../tasks.db"}
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        lab.final_media_path(root, item["id"], BRAND)
    assert lab.list_items(root, BRAND)[0]["final_video"]["available"] is False


def test_faithful_translation_contract_is_pure_and_generic(tmp_path):
    root = str(tmp_path)
    item = lab.save_item(root, {"tipo": "carrusel", "tema": "t", "transcript_original": "Original text.",
                                "pieza": {"headline": "", "slides": ["a", "b"]}}, BRAND)
    packet = lab.translation_packet(root, item["id"], BRAND)
    contract = packet["contrato"]
    assert "FIEL PURA" in contract and "Sin giro" in contract and "No generar" in contract
    assert packet["transcript_original"] == "Original text."
    assert "pieza.talking_points" not in packet["writable_fields"]
    with pytest.raises(ValueError):
        lab.apply_translation(root, item["id"], BRAND, {"pieza.headline": "T", "pieza.talking_points": "x"})
    assert lab.get_item(root, item["id"], BRAND)["pieza"]["headline"] == ""  # all or nothing
    with pytest.raises(ValueError):
        lab.apply_translation(root, item["id"], BRAND, {"pieza.slides[5]": "x"})
    with pytest.raises(ValueError):
        lab.apply_translation(root, item["id"], BRAND, {"transcript_original": "x"})
    out = lab.apply_translation(root, item["id"], BRAND, {"pieza.headline": "Titular", "pieza.slides[1]": "B"})
    assert out["pieza"]["slides"] == ["a", "B"] and out["redaccion"]["modo"] == "traduccion_fiel"
    assert out["transcript_original"] == "Original text."
    empty = lab.save_item(root, {"tipo": "reel", "tema": "sin"}, BRAND)
    with pytest.raises(ValueError):
        lab.translation_packet(root, empty["id"], BRAND)


def test_productions_revisions_and_guards(tmp_path):
    root = str(tmp_path)
    brands = {BRAND}
    with pytest.raises(ValueError):
        lab.save_production(root, {"title": "x", "ecosystem": "ajena"}, brands)
    prod = lab.save_production(root, {"title": "Serie", "ecosystem": BRAND, "approved_content": ["texto"]}, brands)
    assert prod["revision"] == 1
    with pytest.raises(lab.RevisionConflict):
        lab.save_production(root, {"id": prod["id"], "title": "Otra", "expected_revision": 9}, brands)
    ready = lab.save_production(root, {"id": prod["id"], "content_state": "ready_to_produce",
                                       "expected_revision": 1}, brands)
    assert ready["revision"] == 2 and len(lab.list_production_revisions(root, prod["id"])) == 2
    order = lab.create_order(root, prod["id"], 2)
    assert lab.create_order(root, prod["id"], 2)["id"] == order["id"]  # idempotent
    with pytest.raises(ValueError):
        lab.save_production(root, {"id": prod["id"], "production_state": "finished", "expected_revision": 2}, brands)
    with pytest.raises(ValueError):
        lab.save_production(root, {"id": prod["id"], "delivery_approved_at": "now", "expected_revision": 2}, brands)
    with pytest.raises(ValueError):
        lab.save_template(root, {"name": "t", "ecosystem": BRAND})
    assert lab.save_template(root, {"name": "t", "config": {"format": "video"}})["revision"] == 1


def test_carousel_promise_must_match_slides(tmp_path):
    root = str(tmp_path)
    content = [{"role": "cover", "text": "3 errores comunes"}, "uno", "dos"]
    prod = lab.save_production(root, {"title": "c", "ecosystem": BRAND, "format": "carousel", "family": "editorial",
                                      "approved_content": content, "content_state": "ready_to_produce"}, {BRAND})
    with pytest.raises(ValueError, match="promesa"):
        lab.create_order(root, prod["id"])


def test_final_files_confined_and_no_playlists(tmp_path):
    (tmp_path / "ok.mp4").write_bytes(b"x")
    (tmp_path / "list.m3u8").write_text("x", encoding="utf-8")
    assert lab.confined_file(str(tmp_path), "ok.mp4").name == "ok.mp4"
    for raw in ("list.m3u8", "../outside.mp4", "/etc/hosts"):
        with pytest.raises(ValueError):
            lab.confined_file(str(tmp_path), raw)


def test_library_reads_the_installed_kit(tmp_path):
    assert lab.component_catalog(tmp_path) == {"captions": [], "broll_modes": [], "carousel": [],
                                               "hooks_bank": False, "voices": [], "components": []}
    catalog = lab.component_catalog(REPO)  # the repo tree has the same layout as .kit/
    assert catalog["captions"] and catalog["broll_modes"] and catalog["hooks_bank"] is True


def test_guiones_roundtrip_states_and_escaping(tmp_path):
    root = str(tmp_path)
    saved = guiones.save(root, {"titulo": "Mi primer video", "hook": "Hook", "cuerpo": "Linea\n## Parte 2\nmás",
                                "caption": "cap"})
    assert saved["estado"] == "en_proceso"
    listed = guiones.list_all(root)[0]
    assert listed["cuerpo"] == "Linea\n## Parte 2\nmás" and listed["caption"] == "cap"
    guiones.save(root, {"file": saved["file"], "estado": "grabado"})
    assert (tmp_path / "guiones" / "grabados" / saved["file"]).is_file()
    assert not (tmp_path / "guiones" / "en_proceso" / saved["file"]).exists()
    assert guiones.list_all(root)[0]["hook"] == "Hook"  # partial save keeps sections
    assert guiones.toggle_favorite(root, saved["file"])["favorito"] is True
    second = guiones.save(root, {"titulo": "Mi primer video"})
    assert second["file"] != saved["file"]
    hooks = guiones.save_hooks(root, {"file": saved["file"], "opciones": ["A", "B", "C"], "elegida": 1})
    assert hooks["elegida"] == 1
    with pytest.raises(ValueError):
        guiones.save_hooks(root, {"file": saved["file"], "elegida": 7})
    for bad in ("../../tasks.db", "x.txt", "/etc/passwd.md"):
        with pytest.raises((ValueError, FileNotFoundError)):
            guiones.delete(root, bad)
    guiones.delete(root, saved["file"])
    assert [g["file"] for g in guiones.list_all(root)] == [second["file"]]
