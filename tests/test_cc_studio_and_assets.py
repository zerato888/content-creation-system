# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Hooks bank, kit fonts, module toggles from the UI, brand logos, script <-> board card
link, and the Caption Studio module (off by default)."""
import base64
import json
import shutil
import subprocess

import pytest
from test_cc_server import CONFIG, server, set_config  # noqa: F401  (fixture)

REPO_PRESETS = __import__("pathlib").Path(__file__).resolve().parents[1] / "presets"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
WORDS = [{"text": t, "start": round(i * 0.4, 3), "end": round(i * 0.4 + 0.35, 3)}
         for i, t in enumerate("esto es lo que nadie te cuenta sobre grabar videos cortos cada semana".split())]


def _clip(tmp_path, name="clip uno.mp4", words=WORDS):
    d = tmp_path / ".kit-personal/data/captions"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64)
    (d / f"{name}.captions.json").write_text(json.dumps(
        {"schema": "flat_words_v1", "words": words, "video": {"w": 1080, "h": 1920, "fps": 30, "dur": 6.0}}))
    return name


def _studio_on(tmp_path):
    set_config(tmp_path, {**CONFIG, "toggles": {"subtitulos": True}})


# ---------------------------------------------------------------- A
def test_hooks_bank_served_from_installed_kit(server):
    client, tmp_path = server
    client.login()
    assert client.get("/api/hooks-bank")[2]["bank"] is None  # not installed yet: clear, not an error
    (tmp_path / ".kit/presets/hooks").mkdir(parents=True)
    shutil.copy(REPO_PRESETS / "hooks/hooks-bank.json", tmp_path / ".kit/presets/hooks/hooks-bank.json")
    bank = client.get("/api/hooks-bank")[2]["bank"]
    assert bank["schema_version"] == 1 and bank["categories"]


def test_fonts_are_served_confined_and_woff2_only(server):
    client, tmp_path = server
    client.login()
    fonts = tmp_path / ".kit/fonts"
    fonts.mkdir(parents=True)
    (fonts / "Sora-Variable.woff2").write_bytes(b"wOF2fake")
    (fonts / "Inter-Variable.ttf").write_bytes(b"ttf")
    status, headers, body = client.get("/fonts/Sora-Variable.woff2")
    assert status == 200 and headers["Content-Type"] == "font/woff2" and body == b"wOF2fake"
    for bad in ("/fonts/Inter-Variable.ttf", "/fonts/../cc/web/index.html", "/fonts/%2e%2e/manifest.json",
                "/fonts/sub/x.woff2", "/fonts/Nope.woff2"):
        assert client.get(bad)[0] == 404, bad


def test_toggle_from_ui_writes_config_and_applies_without_restart(server):
    client, tmp_path = server
    client.login()
    assert client.get("/api/library")[0] == 404
    status, _, body = client.post("/api/config/toggle", {"module": "biblioteca", "on": True})
    assert status == 200 and body["config"]["toggles"]["biblioteca"] is True
    assert client.get("/api/library")[0] == 200
    raw = json.loads((tmp_path / ".kit-personal/cc.config.json").read_text())
    assert raw["toggles"] == {"biblioteca": True} and raw["brands"] == CONFIG["brands"]  # rest kept
    assert client.post("/api/config/toggle", {"module": "biblioteca", "on": False})[0] == 200
    assert client.get("/api/library")[0] == 404
    for bad in ({"module": "rm -rf", "on": True}, {"module": "vida", "on": "yes"}, {"module": "core", "on": True}):
        assert client.post("/api/config/toggle", bad)[0] == 400, bad
    (tmp_path / ".kit-personal/cc.config.json").write_text("{broken")
    assert client.post("/api/config/toggle", {"module": "vida", "on": True})[0] == 400  # never clobbers


def test_brand_logo_upload_checked_by_magic_bytes_and_served(server):
    client, tmp_path = server
    client.login()
    assert client.get("/api/brand/logo?brand=canal")[0] == 404
    b64 = base64.b64encode(PNG).decode()
    assert client.post("/api/brand/logo", {"brand": "canal", "data": b64})[2]["type"] == "png"
    status, headers, body = client.get("/api/brand/logo?brand=canal")
    assert status == 200 and headers["Content-Type"] == "image/png" and body == PNG
    assert client.get("/api/config")[2]["logos"] == ["canal"]
    svg = base64.b64encode(b"<svg onload=alert(1)></svg>").decode()
    assert client.post("/api/brand/logo", {"brand": "canal", "data": svg})[0] == 400
    big = base64.b64encode(PNG + b"\x00" * (1024 * 1024)).decode()
    assert client.post("/api/brand/logo", {"brand": "canal", "data": big})[0] in (400, 413)
    assert client.post("/api/brand/logo", {"brand": "tienda", "data": b64})[0] == 404  # brand not active
    assert client.post("/api/brand/logo", {"brand": "../x", "data": b64})[0] == 404
    assert [p.name for p in (tmp_path / ".kit-personal/data/logos").iterdir()] == ["canal.png"]


def test_script_links_board_card_by_task_code(server):
    client, _ = server
    client.login()
    task = client.post("/api/tasks", {"ecosystem": "canal", "title": "Idea A", "source_id": "t1", "stage": "idea"})[2]["task"]
    saved = client.post("/api/guion", {"titulo": "Otro título", "cuerpo": "", "task_code": task["code"]})[2]
    g = client.get("/api/guiones")[2]["guiones"][0]
    assert g["task_code"] == task["code"]
    assert client.post("/api/guion", {"titulo": "x", "task_code": "not a code"})[0] == 400
    # titles differ: the link is the id, not the title
    assert client.post("/api/creator/recorded", {"file": saved["file"], "brand": "canal"})[0] == 200
    assert client.get(f"/api/tasks?code={task['code']}")[2]["tasks"][0]["stage"] == "grabado"


def test_old_script_without_task_code_still_records(server):
    client, tmp_path = server
    client.login()
    d = tmp_path / ".kit-personal/data/guiones/en_proceso"
    d.mkdir(parents=True)
    (d / "2026-01-01-viejo.md").write_text('---\ntitulo: "Viejo"\nestado: "en_proceso"\ntask_code: "CAN-99"\n---\n\n## Guion\nhola\n')
    assert client.get("/api/guiones")[2]["guiones"][0]["task_code"] == "CAN-99"
    assert client.post("/api/creator/recorded", {"file": "2026-01-01-viejo.md", "brand": "canal"})[0] == 200


# ---------------------------------------------------------------- B: caption studio
STUDIO_GETS = ["/api/captions/presets", "/api/captions/videos", "/api/captions/transcript?file=clip%20uno.mp4",
               "/api/captions/video?file=clip%20uno.mp4"]


def test_studio_is_off_by_default_and_on_with_its_toggle(server):
    client, tmp_path = server
    client.login()
    _clip(tmp_path)
    for path in STUDIO_GETS:
        assert client.get(path)[0] == 404, path
    assert client.post("/api/captions/render", {"file": "clip uno.mp4", "format": "srt"})[0] == 404
    _studio_on(tmp_path)
    for path in STUDIO_GETS:
        assert client.get(path)[0] == 200, path
    presets = client.get("/api/captions/presets")[2]
    assert {p["id"] for p in presets["presets"]} >= {"hook-serif-escalation", "base-uniform-clean"}
    assert set(presets["font_slots"].values()) <= {"Inter", "Montserrat", "Bebas Neue", "Instrument Serif", "Anton",
                                                   "GFS Didot", "JetBrains Mono"}
    assert client.get("/api/captions/videos")[2]["videos"] == [{"file": "clip uno.mp4", "bytes": 76, "has_transcript": True}]


def test_studio_paths_are_confined(server):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    _clip(tmp_path)
    for bad in ("../cc.config.json", "..%2Fcc.config.json", ".hidden.mp4", "clip.m3u8", "x.json", "nope.mp4"):
        assert client.get(f"/api/captions/video?file={bad}")[0] in (400, 404), bad
    assert client.get("/api/captions/output?file=../../cc.config.json")[0] in (400, 404)
    link = tmp_path / ".kit-personal/data/captions/link.mp4"
    link.symlink_to(tmp_path / ".kit-personal/cc.config.json")
    assert client.get("/api/captions/video?file=link.mp4")[0] == 400


def test_preview_forces_a_three_line_balanced_hook(server):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    _clip(tmp_path)
    hook = json.loads((REPO_PRESETS / "captions/presets/hook-serif-escalation.json").read_text())
    assert hook["layout"]["line_count"] == 3
    body = {"file": "clip uno.mp4", "format": "preview", "base_preset": "base-uniform-clean", "hook_preset": hook,
            "annotated_text": "[hook]esto es lo que nadie te cuenta[/hook] sobre grabar videos cortos cada semana",
            "margin_v_frac": 0.3}
    status, _, r = client.post("/api/captions/render", body)
    assert status == 200, r
    first = r["blocks"][0]
    assert first["kind"] == "hook" and len(first["lines"]) == 3
    lens = [sum(len(w["t"]) for w in ln["words"]) for ln in first["lines"]]
    assert max(lens) - min(lens) <= 8, lens  # balanced by characters
    sizes = [ln["words"][0]["size_frac"] for ln in first["lines"]]
    assert sizes[1] > sizes[0] and sizes[1] > sizes[2]  # line_size_mult [0.44, 1, 0.66]
    assert all(b["kind"] == "base" for b in r["blocks"][1:])
    hook2 = {**hook, "layout": {**hook["layout"], "line_count": 2}}
    r2 = client.post("/api/captions/render", {**body, "hook_preset": hook2})[2]
    assert len(r2["blocks"][0]["lines"]) == 2
    assert client.post("/api/captions/render", {**body, "hook_preset": {**hook, "layout": {**hook["layout"], "line_count": 7}}})[0] == 400
    assert client.post("/api/captions/render", {**body, "margin_v_frac": 2})[0] == 400
    bad_font = json.loads(json.dumps(hook))
    bad_font["typography_tokens"]["normal"]["font_slot"] = "some-commercial-font"
    assert client.post("/api/captions/render", {**body, "hook_preset": bad_font})[0] == 400


def test_srt_export_and_saved_presets(server):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    _clip(tmp_path)
    status, _, r = client.post("/api/captions/render", {"file": "clip uno.mp4", "format": "srt",
                                                        "base_preset": "base-uniform-clean", "margin_v_frac": 0.2})
    assert status == 200 and r["file"] == "clip uno.captions.srt"
    status, _, srt = client.get("/api/captions/output?file=clip%20uno.captions.srt")
    assert status == 200 and srt.startswith(b"1\n00:00:00,000 --> ") and b"nadie" in srt
    preset = client.get("/api/captions/presets")[2]["presets"]
    hook = next(p["data"] for p in preset if p["id"] == "hook-serif-escalation")
    assert client.post("/api/captions/save-preset", {"name": "hook-serif-escalation", "preset": hook})[0] == 400
    assert client.post("/api/captions/save-preset", {"name": "../evil", "preset": hook})[0] == 400
    assert client.post("/api/captions/save-preset", {"name": "mi-hook", "preset": hook})[2]["id"] == "mi-hook"
    mine = [p for p in client.get("/api/captions/presets")[2]["presets"] if p["source"] == "mine"]
    assert [p["id"] for p in mine] == ["mi-hook"] and mine[0]["data"]["name"] == "mi-hook"
    assert (tmp_path / ".kit-personal/data/captions/presets/mi-hook.json").is_file()


def test_word_edits_are_validated_and_kept(server):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    _clip(tmp_path)
    words = [dict(w) for w in WORDS]
    words[0]["text"] = "Esto"
    tr = client.post("/api/captions/transcript", {"file": "clip uno.mp4", "words": words})[2]["transcript"]
    assert tr["words"][0]["text"] == "Esto" and tr["video"]["w"] == 1080
    assert client.post("/api/captions/transcript", {"file": "clip uno.mp4", "words": [{"text": "x", "start": 2, "end": 1}]})[0] == 400


def _libass():
    ff = shutil.which("ffmpeg")
    if not ff:
        return False
    out = subprocess.run([ff, "-hide_banner", "-h", "filter=subtitles"], capture_output=True, text=True).stdout
    return "Unknown filter" not in out and "subtitles" in out


def test_video_export_needs_libass_and_says_so(server):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    _clip(tmp_path)
    body = {"file": "clip uno.mp4", "base_preset": "base-uniform-clean", "margin_v_frac": 0.2}
    if not _libass():
        for fmt in ("video", "alpha"):
            status, _, r = client.post("/api/captions/render", {**body, "format": fmt})
            assert status == 400 and ("libass" in r["error"] or "fuente" in r["error"]), r
        return
    ff = shutil.which("ffmpeg")
    _clip(tmp_path, "real.mp4")  # transcript + placeholder, then a real 6 s clip over the placeholder
    subprocess.run([ff, "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=540x960:r=30:d=6",
                    str(tmp_path / ".kit-personal/data/captions/real.mp4")], check=True)
    for fmt, ext in (("video", ".mp4"), ("alpha", ".mov")):
        status, _, r = client.post("/api/captions/render", {**body, "file": "real.mp4", "format": fmt})
        assert status == 200, r
        assert r["file"].endswith(ext)


@pytest.mark.parametrize("ext", ["m3u8", "ffconcat"])
def test_playlists_are_never_media(server, ext):
    client, tmp_path = server
    client.login()
    _studio_on(tmp_path)
    (tmp_path / ".kit-personal/data/captions").mkdir(parents=True, exist_ok=True)
    (tmp_path / f".kit-personal/data/captions/list.{ext}").write_text("#EXTM3U\nfile:///etc/passwd\n")
    assert client.get("/api/captions/videos")[2]["videos"] == []
    assert client.post("/api/captions/transcript", {"file": f"list.{ext}"})[0] == 400
