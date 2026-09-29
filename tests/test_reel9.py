# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""reel9: control de datos, reglas de la plantilla, armado con la ficha de marca, mezcla, maqueta y render.

Imágenes de relleno (color sólido) y audio en silencio; nada creativo ni de red. Lo que necesita ffmpeg,
las tipografías del kit, GSAP en la caché o un navegador se salta solo si falta.
"""
import json
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

ENGINES = Path(__file__).resolve().parents[1] / "engines"
sys.path.insert(0, str(ENGINES / "video"))
sys.path.insert(0, str(ENGINES))
import kit_platform  # noqa: E402
import reel9  # noqa: E402
import reel9_gate as gate  # noqa: E402
import reel9_layout  # noqa: E402

BRANDS = Path(__file__).resolve().parents[1] / "presets" / "reel" / "brands"
FFMPEG = shutil.which(kit_platform.ffmpeg())
FFPROBE = shutil.which(kit_platform.ffprobe())
needs_ffprobe = pytest.mark.skipif(FFPROBE is None, reason="sin ffprobe")
needs_ffmpeg = pytest.mark.skipif(FFMPEG is None, reason="sin ffmpeg")
HAS_FONTS = all(kit_platform.find_font_file(f) for f in ("Montserrat", "Inter", "JetBrains Mono"))
needs_fonts = pytest.mark.skipif(not HAS_FONTS, reason="sin las tipografías del kit (KIT_FONTS_DIR)")


def _real_gsap():
    try:
        return reel9.gsap_path()
    except reel9.ReelBuildError:
        return None


REAL_GSAP = _real_gsap()
try:
    import playwright  # noqa: F401
    HAS_PW = True
except ImportError:
    HAS_PW = False
needs_browser = pytest.mark.skipif(not (HAS_PW and REAL_GSAP), reason="sin Playwright o sin GSAP en la caché (reel9 fetch-gsap --yes)")


# ---------- fixture ----------

def _png(path: Path, seed: int, side: int = 800) -> None:
    color = bytes([(seed * 53) % 256, (seed * 97) % 256, (seed * 29 + 60) % 256])
    raw = b"".join(b"\x00" + color * side for _ in range(side))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", side, side, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _wav(path: Path, seconds: float) -> None:
    """WAV mono 16 bit a 8 kHz en silencio, escrito a mano (sin ffmpeg)."""
    data = b"\x00\x00" * int(8000 * seconds)
    head = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 8000, 16000, 2, 16)
            + b"data" + struct.pack("<I", len(data)))
    path.write_bytes(head + data)


def make_reel(reel: Path, duration: float = 45.0, step: float = 2.5) -> Path:
    """Reel que cumple las reglas: hook de 3 tramos, cortes cortos, una tarjeta por idea, un retrato."""
    (reel / "assets").mkdir(parents=True)
    times = [(0.0, 2.5, "hook_image"), (2.5, 3.7, "image"), (3.7, 5.0, "image")]
    t = 5.0
    while t < duration - 1e-9:
        times.append((t, min(t + step, duration), "image"))
        t += step
    slots = []
    for i, (s, e, role) in enumerate(times):
        asset = "hook-image.png" if role == "hook_image" else f"assets/shot-{i:02d}.png"
        _png(reel / asset, 4000 + i)
        slots.append({"id": i + 1, "start": s, "end": e, "asset": asset, "role": role,
                      "origin": "50% 40%", "scale_start": 1.0, "scale_end": 1.05})
    outro_start = duration - 2
    n_blocks = int((outro_start - 5.0) // 5) if duration > 20 else 1
    edge = (outro_start - 5.0) / n_blocks
    blocks = [{"start": 5.0 + edge * i, "end": 5.0 + edge * (i + 1)} for i in range(n_blocks)]
    _png(reel / "assets/retrato.png", 99, 900)
    cards = [{"type": "intro", "start": 0.0, "end": 5.0}]
    for i, b in enumerate(blocks):
        if i == 1:
            cards.append({"type": "stat", "start": b["start"], "end": b["end"],
                          "val": "22<span class=\"stat-sep\">/</span>5", "label": "IDEA DE PRUEBA", "tag": "FUENTE DE PRUEBA"})
        elif i == 2:
            cards.append({"type": "dossier", "start": b["start"], "end": b["end"], "asset": "assets/retrato.png",
                          "caption": "Persona de prueba", "subject": "person"})
            cards.append({"type": "lower-third", "start": b["start"], "end": b["end"], "html": "IDEA<br>DE PRUEBA"})
        else:
            cards.append({"type": "lower-third", "start": b["start"], "end": b["end"],
                          "html": f"IDEA {i + 1}<br><span class=\"b\">DE PRUEBA</span>"})
    cards.append({"type": "outro", "start": outro_start, "end": duration})
    _wav(reel / "audio_mix.wav", duration)
    (reel / "vo.txt").write_text(" ".join(["palabra"] * int(duration * 2.7)), encoding="utf-8")
    (reel / "data.json").write_text(json.dumps({
        "kicker": "TEMA · PRUEBA",
        "title": "TÍTULO DE <span class=\"hl\">PRUEBA</span> PARA EL HOOK",
        "subtitle": "Un subtítulo distinto que promete el final.",
        "audio": {"src": "audio_mix.wav", "duration": duration},
        "visual_slots": slots, "cards": cards, "script_blocks": blocks,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return reel


def _edit(reel: Path, fn) -> None:
    p = reel / "data.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def _mini_standard(tmp_path: Path) -> Path:
    std = gate.load_standard()
    std["duration_s"] = [8, 60]
    p = tmp_path / "std.json"
    p.write_text(json.dumps(std), encoding="utf-8")
    return p


def _stub_gsap(tmp_path: Path) -> Path:
    p = tmp_path / "gsap.min.js"
    p.write_text("/* stub */", encoding="utf-8")
    return p


# ---------- control de datos ----------

@needs_ffprobe
def test_passing_reel_writes_ok_result(tmp_path):
    reel = make_reel(tmp_path / "reel")
    assert gate.check(reel) == []
    res = json.loads((reel / ".reel-gate.json").read_text(encoding="utf-8"))
    assert res["ok"] is True and res["errors"] == []


@needs_ffprobe
def test_hook_of_ten_seconds_is_rejected(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["visual_slots"][1].update(end=10.0))
    assert any("hook" in e for e in gate.check(reel))


@needs_ffprobe
def test_hook_without_cover_image_is_rejected(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["visual_slots"][0].update(role="image"))
    assert any("hook_image" in e for e in gate.check(reel))


@needs_ffprobe
def test_title_must_cover_the_hook(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["cards"][0].update(end=3.0))
    assert any("no cubre todo el hook" in e for e in gate.check(reel))


@needs_ffprobe
def test_repeated_image_is_rejected_in_reel_and_in_batch(tmp_path):
    a = make_reel(tmp_path / "a")
    shutil.copyfile(a / "assets/shot-04.png", a / "assets/shot-05.png")
    assert any("imagen repetida en el reel" in e for e in gate.check(a))
    fresh = make_reel(tmp_path / "d")
    shutil.copyfile(a / "assets/shot-06.png", fresh / "assets/shot-06.png")
    assert not any("lote" in e for e in gate.check(fresh))
    assert any("imagen repetida en el lote" in e for e in gate.check(fresh, [a]))


@needs_ffprobe
def test_small_image_and_outside_image_are_rejected(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _png(reel / "assets/shot-04.png", 4004, 300)
    assert any("300×300" in e for e in gate.check(reel))
    outside = tmp_path / "fuera.png"
    _png(outside, 7)
    _edit(reel, lambda d: d["visual_slots"][5].update(asset=str(outside)))
    assert any("fuera de la carpeta del reel" in e for e in gate.check(reel))


@needs_ffprobe
def test_static_image_too_long_is_rejected(tmp_path):
    reel = make_reel(tmp_path / "reel", step=5.0)
    assert any("queda quieta" in e for e in gate.check(reel))


@needs_ffprobe
def test_gap_and_missing_card_are_rejected(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["cards"].remove(d["cards"][1]))
    errs = gate.check(reel)
    assert any("no tiene tarjeta" in e for e in errs)
    assert any("hueco sin tarjeta" in e for e in errs)


@needs_ffprobe
def test_portrait_needs_a_card_of_its_idea(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d.update(cards=[c for c in d["cards"] if c.get("html") != "IDEA<br>DE PRUEBA"]))
    assert any("nunca sale solo" in e for e in gate.check(reel))


@needs_ffprobe
def test_dossier_rules(tmp_path):
    reel = make_reel(tmp_path / "reel")

    def worse(d):
        c = next(c for c in d["cards"] if c["type"] == "dossier")
        c.update(caption="", subject="otra")
        c["asset"] = "assets/no-existe.png"
    _edit(reel, worse)
    errs = gate.check(reel)
    assert any("falta caption" in e for e in errs)
    assert any("subject tiene que ser" in e for e in errs)
    assert any("falta el archivo" in e for e in errs)
    std = gate.load_standard()
    std["cards"]["min_dossier"] = 2
    assert any("1 tarjeta(s) dossier (mínimo 2)" in e for e in gate.check(make_reel(tmp_path / "r2"), standard=std))


def _std():
    return gate.load_standard()


def test_overlapping_short_and_gapped_cards_are_rejected():
    std = _std()
    two = [{"type": "lower-third", "start": 5, "end": 8, "html": "uno dos tres"},
           {"type": "lower-third", "start": 5.2, "end": 8, "html": "cuatro cinco seis"}]
    sched = gate.card_schedule(two, std)
    assert sched[1]["in"] >= sched[0]["out_end"]  # la segunda espera a que salga la primera
    short = gate.card_schedule([{"type": "lower-third", "start": 5, "end": 5.6, "html": "una frase larga que no se lee"}], std)
    assert short[0]["hold"] >= short[0]["read"]  # el horario alarga la permanencia hasta la lectura
    forced = [dict(short[0], hold=0.2)]
    assert any("su lectura pide" in e for e in gate.sequence_errors(forced, std))
    gap = gate.card_schedule([{"type": "lower-third", "start": 5, "end": 7, "html": "a b"},
                              {"type": "lower-third", "start": 9, "end": 11, "html": "c d"}], std)
    assert any("hueco" in e for e in gate.sequence_errors(gap, std))
    over = gate.card_schedule([{"type": "lower-third", "start": 5, "end": 8, "html": "uno dos tres cuatro cinco seis siete ocho nueve"}], std)
    assert any("no entran antes del cierre" in e for e in gate.sequence_errors(over, std, outro_start=6.0))


def test_overlap_error_when_schedule_is_forced():
    std = _std()
    sched = [{"index": 0, "type": "lower-third", "words": 2, "read": 1.0, "in": 5, "in_end": 5.4, "out": 7, "out_end": 7.4, "hold": 1.6},
             {"index": 1, "type": "lower-third", "words": 2, "read": 1.0, "in": 6.9, "in_end": 7.3, "out": 9, "out_end": 9.4, "hold": 1.7}]
    assert any("dos tarjetas a la vez" in e for e in gate.sequence_errors(sched, std))


@needs_ffprobe
def test_audio_and_voice_rules(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["audio"].update(duration=30.0))
    errs = gate.check(reel)
    assert any("debe durar entre 40 y 55" in e for e in errs)
    assert any("dura 45.0 s" in e for e in errs)
    reel = make_reel(tmp_path / "r2")
    (reel / "vo.txt").write_text("muy pocas palabras", encoding="utf-8")
    assert any("por segundo" in e for e in gate.check(reel))
    (reel / "vo.txt").unlink()
    assert any("falta vo.txt" in e for e in gate.check(reel))
    (reel / "audio_mix.wav").unlink()
    assert any("falta el archivo de audio" in e for e in gate.check(reel))


@needs_ffprobe
def test_missing_data_fails_with_reason(tmp_path):
    reel = tmp_path / "vacio"
    reel.mkdir()
    errs = gate.check(reel)
    assert errs and "falta data.json" in errs[0]


@needs_ffprobe
def test_declared_music_must_exist(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d["audio"].update(music="musica.mp3"))
    assert any("falta el archivo de música" in e for e in gate.check(reel))


# ---------- reglas de la plantilla ----------

def _data(**over):
    d = {"kicker": "TEMA", "title": "Un título con <span class=\"hl\">fuerza</span>",
         "subtitle": "Lo que nadie te cuenta del final", "cards": []}
    d.update(over)
    return d


def test_template_rules():
    assert reel9.reel_rules(_data()) == []
    assert any("kicker" in e for e in reel9.reel_rules(_data(kicker=" ")))
    assert any("sello de abajo" in e for e in reel9.reel_rules(_data(cards=[{"type": "ticker"}])))
    assert any("mezcla marcador y color" in e for e in reel9.reel_rules(_data(title='a <span class="mk">b</span> <span class="hl">c</span>')))
    assert any("solo para carruseles" in e for e in reel9.reel_rules(_data(hook_circle={"x": 1})))
    assert any("muy corto" in e for e in reel9.reel_rules(_data(subtitle="corto")))
    assert any("repite el título" in e for e in reel9.reel_rules(_data(title="La verdad sobre el ahorro mensual", subtitle="La verdad sobre el ahorro mensual siempre")))
    assert reel9.highlight_used('<span class="hl-box"><span class="hl-text">x</span></span>') == {"hl"}


def test_mark_ink_picks_the_readable_letter():
    assert reel9.mark_ink("#F2A93B", "#10202B") == "#10202B"
    assert reel9.mark_ink("#B4472A", "#F3E9DC") == "#ffffff"


def test_template_has_every_marker_once_and_no_private_names():
    html = reel9.TEMPLATE.read_text(encoding="utf-8")
    for m in reel9.MARKERS[:-1]:
        assert html.count(m) >= 1, m
    assert html.count("/*__REEL_DATA__*/") == 1 and "__REEL_DURATION__" in html and "__REEL_AUDIO_SRC__" in html
    assert "https://" not in html and "http://" not in html


def test_example_brands_are_neutral_and_use_kit_fonts():
    families = reel9.kit_families()
    for f in sorted(BRANDS.glob("*.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        b = reel9.kit_brand.load_brand(f)
        assert {b["fonts"]["display"], b["fonts"]["body"], b["fonts"]["mono"]} <= families, f.name
        assert raw["reel"]["display_case"] in reel9.CASES


def test_stack_and_font_rules(tmp_path):
    b = reel9.kit_brand.load_brand(BRANDS / "servicios.json")
    b["fonts"]["display"] = "Fuente Comercial"
    with pytest.raises(reel9.ReelBuildError, match="no es una de las libres"):
        reel9.resolve_fonts(b)
    b["fonts"]["display"] = 'Inter"; } body { display:none'
    with pytest.raises(reel9.ReelBuildError, match="no es un nombre de fuente seguro"):
        reel9.resolve_fonts(b)


# ---------- armado ----------

@needs_ffprobe
@needs_fonts
@pytest.mark.parametrize("brand", ["servicios", "marca-personal", "producto"])
def test_builds_with_each_example_brand(tmp_path, brand):
    reel = make_reel(tmp_path / "reel")
    out = reel9.build(BRANDS / f"{brand}.json", reel, gsap=_stub_gsap(tmp_path), skip_layout=True)
    html = out.read_text(encoding="utf-8")
    raw = json.loads((BRANDS / f"{brand}.json").read_text(encoding="utf-8"))
    assert raw["colors"]["accent"] in html and raw["name"].split()[0].upper() in html.upper()
    assert "/*__" not in html and "__REEL_" not in html
    data = json.loads(__import__("re").search(r"var DATA = (\{.*?\});\n", html, __import__("re").S).group(1))
    assert data["card_schedule"] and all("anim" in c for c in data["cards"] if c["type"] in ("lower-third", "stat", "dossier"))
    fonts = {p.name for p in (reel / "fonts").iterdir()}
    assert 1 <= len(fonts) <= 3
    stamp = json.loads((reel / ".reel-build.json").read_text(encoding="utf-8"))
    assert stamp["layout_checked"] is False and stamp["format"] == "reel@9"


@needs_ffprobe
@needs_fonts
def test_gate_failure_blocks_the_build_and_leaves_no_index(tmp_path):
    reel = make_reel(tmp_path / "reel")
    (reel / "index.html").write_text("viejo", encoding="utf-8")
    _edit(reel, lambda d: d["visual_slots"][1].update(end=10.0))
    with pytest.raises(reel9.ReelBuildError, match="control de datos"):
        reel9.build(BRANDS / "servicios.json", reel, gsap=_stub_gsap(tmp_path), skip_layout=True)
    assert not (reel / "index.html").exists()


@needs_ffprobe
@needs_fonts
def test_template_rule_failure_blocks_the_build(tmp_path):
    reel = make_reel(tmp_path / "reel")
    _edit(reel, lambda d: d.update(subtitle="corto"))
    with pytest.raises(reel9.ReelBuildError, match="la plantilla rechazó"):
        reel9.build(BRANDS / "servicios.json", reel, gsap=_stub_gsap(tmp_path), skip_layout=True)
    assert not (reel / "index.html").exists()


@needs_ffprobe
@needs_fonts
def test_image_outside_the_reel_is_copied_in(tmp_path):
    reel = make_reel(tmp_path / "reel")
    outside = tmp_path / "banco" / "foto.png"
    outside.parent.mkdir()
    _png(outside, 12)
    _edit(reel, lambda d: d["visual_slots"][6].update(asset=str(outside)))
    reel9.build(BRANDS / "servicios.json", reel, gsap=_stub_gsap(tmp_path), skip_layout=True)
    data = json.loads((reel / "data.json").read_text(encoding="utf-8"))
    assert data["visual_slots"][6]["asset"] == "assets/_ext/foto.png"
    assert (reel / "assets/_ext/foto.png").is_file()


@needs_ffprobe
@needs_fonts
def test_missing_gsap_says_how_to_get_it(tmp_path, monkeypatch):
    monkeypatch.setenv("KIT_CACHE", str(tmp_path / "cache"))
    monkeypatch.delenv("KIT_GSAP", raising=False)
    reel = make_reel(tmp_path / "reel")
    with pytest.raises(reel9.ReelBuildError, match="fetch-gsap"):
        reel9.build(BRANDS / "servicios.json", reel, skip_layout=True)


def test_gsap_lock_is_pinned_https():
    lock = json.loads(reel9.GSAP_LOCK.read_text(encoding="utf-8"))
    assert lock["url"].startswith("https://") and len(lock["sha256"]) == 64 and lock["size"] > 10000


def test_fetch_gsap_asks_first(capsys):
    assert reel9.main(["fetch-gsap"]) == 2
    assert "--yes" in capsys.readouterr().out


# ---------- audio ----------

def test_mix_args_keep_music_flat_and_below_the_voice(tmp_path):
    args = reel9.mix_args(tmp_path / "v.mp3", tmp_path / "m.mp3", tmp_path / "o.m4a", 45.0, -17.0)
    graph = args[args.index("-filter_complex") + 1]
    assert "volume=-17.0dB" in graph and "normalize=0" in graph
    assert "sidechain" not in graph and "afade=t=out:st=44.000" in graph
    assert args[args.index("-stream_loop") + 1] == "-1"
    with pytest.raises(reel9.ReelBuildError):
        reel9.mix(tmp_path, tmp_path / "v.wav", music_db=-3)


@needs_ffmpeg
def test_mix_produces_audio_of_the_voice_length(tmp_path):
    reel = tmp_path / "reel"
    reel.mkdir()
    ff = kit_platform.ffmpeg()
    voice, music = tmp_path / "voz.wav", tmp_path / "musica.wav"
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=4", str(voice)], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=660:d=1.5", str(music)], check=True)
    out = reel9.mix(reel, voice, music, -17.0)
    assert out.name == "audio_mix.m4a" and abs(gate.audio_duration(out) - 4.0) < 0.3
    solo = reel9.mix(reel, voice)
    assert abs(gate.audio_duration(solo) - 4.0) < 0.3


# ---------- maqueta y render (navegador real) ----------

def _mini_reel(tmp_path):
    reel = make_reel(tmp_path / "mini", duration=10.0, step=2.5)
    _edit(reel, lambda d: d.update(cards=[
        {"type": "intro", "start": 0.0, "end": 5.0},
        {"type": "lower-third", "start": 5.0, "end": 8.5, "html": "DOS PALABRAS"},
        {"type": "outro", "start": 8.5, "end": 10.0}], script_blocks=[{"start": 5.0, "end": 8.5}]))
    (reel / "vo.txt").write_text(" ".join(["palabra"] * 27), encoding="utf-8")
    return reel


@needs_ffprobe
@needs_fonts
@needs_browser
def test_layout_passes_and_long_title_is_caught(tmp_path):
    reel = _mini_reel(tmp_path)
    std = _mini_standard(tmp_path)
    reel9.build(BRANDS / "servicios.json", reel, standard=std)
    assert reel9_layout.check(reel) == []
    assert json.loads((reel / ".reel-build.json").read_text(encoding="utf-8"))["layout_checked"] is True
    _edit(reel, lambda d: d.update(title="PALABRA " * 60))
    with pytest.raises(reel9.ReelBuildError, match="TITULO_LARGO"):
        reel9.build(BRANDS / "servicios.json", reel, standard=std)
    assert not (reel / "index.html").exists()


@needs_ffprobe
@needs_ffmpeg
@needs_fonts
@needs_browser
def test_render_makes_a_vertical_mp4_with_audio(tmp_path):
    reel = _mini_reel(tmp_path)
    reel9.build(BRANDS / "servicios.json", reel, standard=_mini_standard(tmp_path), skip_layout=True)
    out = reel9.render(reel, fps=6)
    assert out.is_file()
    probe = subprocess.run([kit_platform.ffprobe(), "-v", "error", "-show_entries", "stream=codec_type,width,height",
                            "-of", "json", str(out)], capture_output=True, text=True, check=True).stdout
    streams = json.loads(probe)["streams"]
    video = next(s for s in streams if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == (1080, 1920)
    assert any(s["codec_type"] == "audio" for s in streams)
    assert abs(gate.audio_duration(out) - 10.0) < 0.6


def test_launch_knows_reel9():
    import importlib.util
    spec = importlib.util.spec_from_file_location("kit_launch", Path(__file__).resolve().parents[1] / "launch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.COMMANDS["reel9"] == ("engines/video/reel9.py", [])
    assert (Path(mod.KIT) / mod.COMMANDS["reel9"][0]).is_file()
