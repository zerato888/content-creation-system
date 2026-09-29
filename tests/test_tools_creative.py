# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Caja de herramientas creativa: imagegen, fetch-image, galería, telegram, apify. Todo sin red ni claves."""
import json
import os
import struct
import sys
import threading
import urllib.request
import zlib
from pathlib import Path

import pytest

ENG = Path(__file__).resolve().parents[1] / "engines"
for sub in ("imagegen", "gallery", "telegram", "apify"):
    sys.path.insert(0, str(ENG / sub))
sys.path.insert(0, str(ENG))
import apify_scrape  # noqa: E402
import fetch_image  # noqa: E402
import gallery  # noqa: E402
import imagegen  # noqa: E402
import tg_send  # noqa: E402


def png(w=8, h=8, gray=128) -> bytes:
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d))
    raw = b"".join(b"\x00" + bytes([gray]) * w for _ in range(h))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


# ---------- imagegen ----------
def test_prompt_has_rules_and_ref_paths(tmp_path):
    ref = tmp_path / "foto.png"
    p = imagegen.build_prompt("un gato", tmp_path, [ref], "codex")
    assert p.startswith("$imagegen ") and str(ref) in p
    assert "REGLA ESTRICTA" in p and "PROHIBIDO dibujar" in p and "No la agrandes" in p
    assert not imagegen.build_prompt("x", tmp_path, [], "agy").startswith("$imagegen")


def test_stage_refs_removes_spaces(tmp_path):
    src = tmp_path / "mi carpeta" / "una foto.png"
    src.parent.mkdir()
    src.write_bytes(png())
    out = imagegen.stage_refs([src], tmp_path / "stage")
    assert " " not in str(out[0]) and out[0].read_bytes() == src.read_bytes()


def test_judge():
    assert imagegen.judge(None, "dark") is None
    assert imagegen.judge((128, 2), "any") == "blank"
    assert imagegen.judge((2, 30), "any") == "extreme"
    assert imagegen.judge((200, 40), "dark") == "dark"
    assert imagegen.judge((40, 40), "light") == "light"
    assert imagegen.judge((100, 40), "any") is None


def test_generate_retries_and_never_resizes(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image
    from PIL.Image import open as pil_open
    calls = []

    def fake(prompt, dest):
        calls.append(prompt)
        f = dest / f"o{len(calls)}.png"
        if len(calls) == 1:
            Image.new("L", (16, 16), 255).save(f)  # blanco plano
        else:
            im = Image.new("L", (64, 40), 40)
            im.paste(200, (0, 0, 20, 20))
            im.save(f)
        return [f]

    out = imagegen.generate("x", tmp_path, provider="fake", providers={"fake": fake}, retries=2)
    assert len(calls) == 2 and "en blanco" in calls[1]
    with out.open("rb") as fh:
        assert pil_open(fh).size == (64, 40)  # tamaño nativo intacto
    assert list(tmp_path.glob("descartada-*"))


def test_generate_auto_skips_missing_provider(tmp_path):
    def ok(prompt, dest):
        f = dest / "a.png"
        f.write_bytes(png())
        return [f]
    out = imagegen.generate("x", tmp_path, providers={"codex": ok, "agy": ok}, ready=lambda n: n == "agy")
    assert out.name == "a.png"
    with pytest.raises(RuntimeError, match="no instalado"):
        imagegen.generate("x", tmp_path / "b", providers={"codex": ok}, ready=lambda n: False)


def test_generate_rejects_missing_ref(tmp_path):
    with pytest.raises(RuntimeError, match="referencia"):
        imagegen.generate("x", tmp_path, refs=[tmp_path / "no.png"], providers={"codex": lambda p, d: []})


@pytest.mark.skipif(os.name == "nt", reason="usa un ejecutable falso de shell")
def test_codex_runner_rescues_and_cleans(tmp_path, monkeypatch):
    home = tmp_path / "home"
    bin_ = tmp_path / "codex"
    # el "codex" falso deja la imagen solo en la carpeta de trabajo, como hace el real a veces
    bin_.write_text(f'#!/bin/sh\nmkdir -p "{home}/generated_images/t1"\nprintf x > "{home}/generated_images/t1/i.png"\n', encoding="utf-8")
    bin_.chmod(0o755)
    monkeypatch.setenv("IMAGEGEN_CODEX_BIN", str(bin_))
    monkeypatch.setenv("CODEX_HOME", str(home))
    dest = tmp_path / "out"
    dest.mkdir()
    files = imagegen.run_codex("p", dest)
    assert [f.name for f in files] == ["i.png"] and not (home / "generated_images" / "t1").exists()


def test_main_named_alternatives(capsys):
    assert imagegen.main(["x", "--provider", "magnific"]) == 3
    assert "conector" in capsys.readouterr().err


def test_no_upscale_code():
    src = (ENG / "imagegen" / "imagegen.py").read_text(encoding="utf-8")
    assert ".save(" not in src and "LANCZOS" not in src  # la única imagen que se reescala es una miniatura de análisis


# ---------- fetch_image ----------
def test_dimensions_png_and_errors(tmp_path):
    assert fetch_image.dimensions(png(30, 20)) == (30, 20)
    assert fetch_image.dimensions(b"<html>") is None
    with pytest.raises(ValueError, match="solo URLs"):
        fetch_image.fetch("file:///etc/passwd", tmp_path / "a")

    class R:
        def __init__(self, b): self.b = b
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self, n=-1): return self.b
    with pytest.raises(ValueError, match="chica"):
        fetch_image.fetch("https://x/a.png", tmp_path / "a.png", 720, opener=lambda r: R(png(30, 20)))
    assert fetch_image.fetch("https://x/a.png", tmp_path / "b.png", 10, opener=lambda r: R(png(30, 20))) == (30, 20)
    assert (tmp_path / "b.png").is_file()


# ---------- galería ----------
def test_gallery_save_and_read(tmp_path):
    (tmp_path / "a.png").write_bytes(png())
    (tmp_path / "nota.txt").write_text("x", encoding="utf-8")
    assert [i["name"] for i in gallery.list_items(tmp_path)] == ["a.png"]
    gallery.save_decision(tmp_path, "a.png", status="aprobado")
    gallery.save_decision(tmp_path, "a.png", comment="más luz")
    assert gallery.read_decisions(tmp_path)["a.png"] == {"status": "aprobado", "comment": "más luz"}
    for bad in (dict(name="../x.png"), dict(name="nota.txt"), dict(name="a.png", status="tal vez")):
        with pytest.raises(ValueError):
            gallery.save_decision(tmp_path, **bad)


def test_gallery_server_security(tmp_path):
    (tmp_path / "a.png").write_bytes(png())
    (tmp_path / "secreto.txt").write_text("no", encoding="utf-8")
    box = {}
    ev = threading.Event()

    def ready(url, srv):
        box["url"], box["srv"] = url, srv
        ev.set()
    t = threading.Thread(target=gallery.serve, args=(tmp_path, "T", 0, False, ready), daemon=True)
    t.start()
    assert ev.wait(5)
    url = box["url"]
    port = url.split(":")[2].split("/")[0]

    def get(u, host=None):
        req = urllib.request.Request(u)
        if host:
            req.add_header("Host", host)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""

    assert get(url)[0] == 200
    assert get(url + "file/a.png")[0] == 200
    assert get(url + "file/secreto.txt")[0] == 404
    assert get(f"http://127.0.0.1:{port}/otro/")[0] == 404  # sin el código, nada
    assert get(url, host="evil.example")[0] == 404  # Host ajeno
    post = lambda origin: urllib.request.Request(url + "decision", data=json.dumps({"name": "a.png", "status": "rechazado"}).encode("utf-8"),
                                                  headers={"Content-Type": "application/json", **({"Origin": origin} if origin else {})})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(post("http://evil.example"))
    assert e.value.code == 403
    assert urllib.request.urlopen(post(f"http://127.0.0.1:{port}")).status == 200
    assert gallery.read_decisions(tmp_path)["a.png"]["status"] == "rechazado"
    box["srv"].shutdown()


# ---------- telegram ----------
def test_kind_of(tmp_path):
    for name, kind in (("a.mp4", "video"), ("a.mp3", "audio"), ("a.png", "photo"), ("a.pdf", "document")):
        (tmp_path / name).write_bytes(b"x")
        assert tg_send.kind_of(tmp_path / name) == kind


def test_kind_of_too_big(tmp_path, monkeypatch):
    monkeypatch.setattr(tg_send, "LIMIT", 3)
    (tmp_path / "a.mp4").write_bytes(b"xxxx")
    with pytest.raises(SystemExit, match="50 MB"):
        tg_send.kind_of(tmp_path / "a.mp4")


def test_send_file_video_and_fallback(tmp_path):
    (tmp_path / "v.mp4").write_bytes(b"vid")
    seen = []

    class R:
        def __init__(self, ok): self.ok = ok
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return json.dumps({"ok": self.ok, "description": "no"}).encode("utf-8")

    def opener(req):
        seen.append(req.full_url.rsplit("/", 1)[1])
        return R(len(seen) > 1)  # sendVideo falla, sendDocument entra
    bot = tg_send.Bot("TOK", "1", opener=opener)
    assert bot.send_file(tmp_path / "v.mp4", "pie") == "document" and seen == ["sendVideo", "sendDocument"]


def test_telegram_error_hides_token():
    class R:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b'{"ok": false, "description": "chat not found"}'
    with pytest.raises(SystemExit) as e:
        tg_send.Bot("SECRETTOKEN", "1", opener=lambda r: R()).call("sendMessage", {"text": "hola"})
    assert "SECRETTOKEN" not in str(e.value) and "chat not found" in str(e.value)


def test_telegram_dry_run(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(tg_send, "Bot", lambda *a, **k: pytest.fail("la prueba tocó el bot"))
    (tmp_path / "v.mp4").write_bytes(b"x")
    assert tg_send.main(["file", str(tmp_path / "v.mp4"), "hola"]) == 0
    assert "no se envió nada" in capsys.readouterr().out


# ---------- apify ----------
def test_apify_plan_and_dry_run(capsys, monkeypatch):
    monkeypatch.setattr(apify_scrape.kit_secrets, "get_secret", lambda n: pytest.fail("la prueba pidió la clave"))
    assert apify_scrape.main(["posts", "@cuenta", "-n", "5"]) == 0
    out = capsys.readouterr().out
    assert "apify~instagram-scraper" in out and "instagram.com/cuenta/" in out and "no se corrió nada" in out
    assert apify_scrape.main(["run", "autor/actor", "{mal"]) == 2


def test_apify_run_sync_uses_bearer_not_url_token():
    seen = {}

    class R:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b'[{"a": 1}]'

    def opener(req):
        seen["url"], seen["auth"] = req.full_url, req.get_header("Authorization")
        return R()
    assert apify_scrape.run_sync("apify~x", {}, "TOK", opener=opener) == [{"a": 1}]
    assert "TOK" not in seen["url"] and seen["auth"] == "Bearer TOK"
