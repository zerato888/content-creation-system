# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Offline tests for engines/video/captions.py and presets/captions (no ffmpeg,
whisper or font files needed)."""
import json
import re
import subprocess
import sys
from pathlib import Path, PureWindowsPath

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engines" / "video"))
import captions as cap  # noqa: E402

PRESETS = sorted((REPO / "presets" / "captions" / "presets").glob("*.json"))
OFL = {"Inter", "Montserrat", "Bebas Neue", "Instrument Serif", "Anton", "GFS Didot", "JetBrains Mono"}
FONT_MAP = cap.load_font_map()
BRAND = {"colors": {"accent": "#F2B134"}}


def words(text, step=0.4):
    return [{"t": t, "s": round(i * step, 3), "e": round(i * step + step * 0.8, 3)}
            for i, t in enumerate(text.split())]


def base_preset(**layout):
    return {"name": "t", "version": 1, "kind": "base",
            "typography_tokens": {"normal": {"font_slot": "sans", "size_frac": 0.05, "case": "keep"},
                                  "emphasized": {"font_slot": "display", "size_frac": 0.07, "case": "upper",
                                                 "weight": "bold"}},
            "layout": {"max_lines": 2, "alignment": "left", "margin_l_frac": 0.08, **layout},
            "reveal": {"type": "word_by_word_fade", "fade_ms": 150}}


# --- text cleanup -------------------------------------------------------------------

def test_ass_time_and_esc():
    assert cap.ass_time(61.25) == "0:01:01.25"
    assert cap.ass_time(-1) == "0:00:00.00"
    assert cap.esc(" {\\an8}hola ") == "(/an8)hola"


def test_sanitize_text():
    assert cap.sanitize_text(" Ñandú, ¿qué?") == "nandu, que"


def test_drop_muletillas_keeps_raw_text():
    out = cap.drop_muletillas([{"text": "eh", "start": 0, "end": .2}, {"text": "Este,", "start": .2, "end": .3},
                               {"text": "Hola.", "start": .3, "end": .5}])
    assert out == [{"t": "Hola.", "s": 0.3, "e": 0.5}]


# --- annotated text --------------------------------------------------------------------

def test_parse_annotated_text():
    toks = cap.parse_annotated_text("[hook]Un *golpe* [strong]fuerte[/strong][/hook] normal")
    assert [t["segment_type"] for t in toks] == ["hook", "hook", "hook", "base"]
    assert [t["role"] for t in toks] == ["normal", "emphasized", "strong", "normal"]
    assert cap.parse_annotated_text("a[/hook] b")[1]["segment_type"] == "base"


def test_align_by_content_drops_unannotated_and_fails_closed_on_substitution():
    w = words("un golpe eh normal")
    tagged = cap.align_annotated_text("[hook]Un *golpe*[/hook] normal", w)
    assert [x["t"] for x in tagged] == ["Un", "golpe", "normal"]
    assert tagged[1]["role"] == "emphasized" and tagged[2]["s"] == w[3]["s"]
    with pytest.raises(cap.ContractViolation):
        cap.align_annotated_text("un golpe distinto", words("un golpe normal"))


# --- presets & fonts -----------------------------------------------------------------

@pytest.mark.parametrize("path", PRESETS, ids=lambda p: p.stem)
def test_every_preset_loads_and_uses_only_ofl_fonts(path):
    p = cap.load_preset(path)
    assert p["name"] == path.stem
    for tok in p["typography_tokens"].values():
        assert FONT_MAP["slots"][tok["font_slot"]] in OFL


@pytest.mark.parametrize("path", PRESETS, ids=lambda p: p.stem)
def test_every_preset_builds_an_ass(path):
    p = cap.load_preset(path)
    presets = {"base": p if p["kind"] == "base" else cap.load_preset("base-uniform-clean"),
               "hook": p if p["kind"] == "hook" else cap.load_preset("hook-serif-escalation")}
    tagged = cap.align_annotated_text("[hook]esto es un[/hook] ejemplo de *prueba* larga",
                                      words("esto es un ejemplo de prueba larga"))
    ass = cap.build_ass_from_preset({"video": {"w": 1080, "h": 1920}, "blocks": cap.group_for_render(tagged, presets)},
                                    presets, FONT_MAP, margin_v_frac=0.3, brand=BRAND)
    assert ass.count("Dialogue:") >= 7
    assert "brand." not in ass


def _font_refs(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("font", "family", "font_family", "font_slot") and isinstance(v, str):
                yield k, v
            yield from _font_refs(v)
    elif isinstance(node, list):
        for x in node:
            yield from _font_refs(x)


def test_presets_only_reference_locked_fonts():
    lock = json.loads((REPO / "presets/captions/fonts.lock.json").read_text())
    allowed = {f["family"] for f in lock["fonts"] if f["use"] == "captions"}
    assert set(FONT_MAP["slots"].values()) <= allowed and set(FONT_MAP["families"]) <= allowed
    for f in list(PRESETS) + [REPO / "presets/captions/LIBRARY.json"]:
        for k, v in _font_refs(json.loads(f.read_text())):
            ok = v in FONT_MAP["slots"] if k == "font_slot" else v in allowed
            assert ok, f"{f.name}: {k}={v}"


def test_library_lists_every_preset_and_fonts_lock_is_pinned():
    lib = json.loads((REPO / "presets/captions/LIBRARY.json").read_text())
    assert sorted(e["id"] for e in lib["presets"]) == sorted(p.stem for p in PRESETS)
    lock = json.loads((REPO / "presets/captions/fonts.lock.json").read_text())
    caps = [f for f in lock["fonts"] if f["use"] == "captions"]
    ui = [f for f in lock["fonts"] if f["use"] == "ui"]
    assert {f["family"] for f in caps} == OFL
    assert {f["file"] for f in ui} == {"Sora-Variable.woff2", "JetBrainsMono-Variable.woff2"}
    css = (REPO / "cc/web/styles.css").read_text()
    for f in lock["fonts"]:
        assert f["license"] == "OFL-1.1" and re.fullmatch(r"[0-9a-f]{64}", f["sha256"]), f["file"]
        # immutable: a 40-hex commit in the URL, never a branch name
        assert re.match(r"https://raw\.githubusercontent\.com/[\w.-]+/[\w.-]+/[0-9a-f]{40}/", f["url"]), f["url"]
        assert re.fullmatch(r"[A-Za-z0-9_-]+\.(woff2|ttf)", f["file"])
        assert (f["file"].endswith(".woff2")) == (f["use"] == "ui")
    for f in ui:
        assert f"fonts/{f['file']}" in css
    fonts = [p for p in REPO.rglob("*") if p.suffix.lower() in (".ttf", ".otf", ".woff", ".woff2", ".ttc")]
    assert fonts == []


def test_load_preset_rejects_bad_input(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"name": "x", "kind": "base"}))
    with pytest.raises(cap.ContractViolation, match="faltan"):
        cap.load_preset(bad)
    bad.write_text(json.dumps({**base_preset(), "kind": "otro"}))
    with pytest.raises(cap.ContractViolation, match="kind"):
        cap.load_preset(bad)
    with pytest.raises(cap.ContractViolation):
        cap.load_preset("../../etc/passwd")


def test_resolve_word_style_errors_and_case():
    p = base_preset()
    assert cap.resolve_word_style({"role": "emphasized"}, p, FONT_MAP)["font"] == "Bebas Neue"
    with pytest.raises(cap.ContractViolation):
        cap.resolve_word_style({"role": "nope"}, p, FONT_MAP)
    with pytest.raises(cap.ContractViolation):
        cap.resolve_word_style({"role": "normal"}, p, {"slots": {}})


def test_resolve_fonts_kit_first_then_fallback_then_fail():
    fm = {"families": {"Inter": {"system_fallback": ["Arial"]}}}
    assert cap.resolve_fonts({"Inter"}, fm, finder=lambda n: f"/k/{n}.ttf")["Inter"] == ("Inter", "/k/Inter.ttf")
    assert cap.resolve_fonts({"Inter"}, fm, finder=lambda n: "/s/Arial.ttf" if n == "Arial" else None
                             )["Inter"] == ("Arial", "/s/Arial.ttf")
    with pytest.raises(cap.ContractViolation):
        cap.resolve_fonts({"Inter"}, fm, finder=lambda n: None)


def test_brand_accent_color():
    assert cap.ass_color("brand.accent", BRAND) == "&H34B1F2&"
    assert cap.ass_color("#FF0000") == "&H0000FF&"
    assert cap.ass_color("&H00FFFFFF") == "&H00FFFFFF"
    with pytest.raises(cap.ContractViolation):
        cap.ass_color("red")
    p = cap.load_preset("base-serif-accent")
    presets = {"base": p, "hook": p}
    ass = cap.build_ass_from_preset({"video": {"w": 1080, "h": 1920},
                                     "blocks": cap.group_for_render(cap.tag_plain(words("hola")), presets)},
                                    presets, FONT_MAP, brand=BRAND)
    assert "\\c&H34B1F2&" in ass


# --- grouping & ASS --------------------------------------------------------------------

def test_hook_stays_one_block_and_forced_line_count():
    hook = cap.load_preset("hook-serif-escalation")
    tagged = [{**w, "segment_type": "hook", "role": "normal"} for w in words("el viaje empieza hoy mismo aca")]
    blocks = cap.group_for_render(tagged, {"hook": hook, "base": base_preset()})
    assert len(blocks) == 1 and len(blocks[0]["lines"]) == 3
    with pytest.raises(cap.ContractViolation):
        cap.split_into_n_lines(tagged[:2], 3)


def test_isolate_roles_and_max_lines():
    p = base_preset(max_lines=1, isolate_roles=["emphasized"])
    tagged = cap.align_annotated_text("una *palabra* sola", words("una palabra sola"))
    blocks = cap.group_for_render(tagged, {"base": p, "hook": p})
    assert [[w["t"] for w in b["lines"][0]] for b in blocks] == [["una"], ["palabra"], ["sola"]]


def test_word_reveal_margin_override_and_alignment():
    p = base_preset(alignment="center", margin_v_frac=0.12)
    cfg = {"video": {"w": 1000, "h": 2000}, "blocks": [{"lines": [cap.tag_plain(words("uno dos"))]}]}
    ass = cap.build_ass_from_preset(cfg, {"base": p, "hook": p}, FONT_MAP, margin_v_frac=0.5)
    assert "\\an2\\pos(500,1000)" in ass
    assert ass.count("Dialogue:") == 2 and "\\t(0,150,\\alpha&H00&)" in ass
    own = cap.build_ass_from_preset(cfg, {"base": p, "hook": p}, FONT_MAP)
    assert "\\pos(500,1760)" in own


def test_fade_clamped_to_word_window_and_punctuation_removed():
    p = base_preset()
    fast = [{"t": "hola.", "s": 0.0, "e": 0.05}, {"t": "chau", "s": 0.05, "e": 0.3}]
    ass = cap.build_ass_from_preset({"video": {"w": 1080, "h": 1920}, "blocks": [{"lines": [cap.tag_plain(fast)]}]},
                                    {"base": p, "hook": p}, FONT_MAP)
    assert "\\t(0,50," in ass and "hola." not in ass


def test_auto_shrink_uses_measurement(monkeypatch):
    p = base_preset()
    cfg = {"video": {"w": 1000, "h": 1000}, "blocks": [{"lines": [cap.tag_plain(words("ancha"))]}]}
    monkeypatch.setattr(cap, "measure_text", lambda f, size, text: 5000.0 if text.strip() else 0.0)
    ass = cap.build_ass_from_preset(cfg, {"base": p, "hook": p}, FONT_MAP, font_files={"Inter": "x.ttf"})
    size = int(re.search(r"\\fs(\d+)", ass).group(1))
    assert size < 50


def test_background_box_uses_borderstyle_3():
    p = cap.load_preset("base-mono-box")
    ass = cap.build_ass_from_preset({"video": {"w": 1080, "h": 1920},
                                     "blocks": [{"lines": [cap.tag_plain(words("caja"))]}]},
                                    {"base": p, "hook": p}, FONT_MAP)
    style = [ln for ln in ass.splitlines() if ln.startswith("Style: S0")][0]
    assert style.split(",")[15] == "3"


# --- ffmpeg argv / env ---------------------------------------------------------------------

def _av_get_token(s, i, term):
    """Minimal emulation of ffmpeg's av_get_token (quotes + backslash escapes)."""
    out = []
    while i < len(s) and s[i] not in term:
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(s[i + 1])
            i += 2
        elif c == "'":
            j = s.index("'", i + 1)
            out.append(s[i + 1:j])
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out), i


def _parse_filter(spec):
    name, rest = spec.split("=", 1)
    args, _ = _av_get_token(rest, 0, "[],;")
    opts, i = {}, 0
    while i < len(args):
        key, i = _av_get_token(args, i, "=:")
        val, i = _av_get_token(args, i + 1, ":")
        opts[key] = val
        i += 1
    return name, opts


@pytest.mark.parametrize("path", [Path("/tmp/it's, [odd]; dir/x.ass"), PureWindowsPath(r"C:\clips\a b\x.ass")])
def test_filter_path_escaping_round_trips(path):
    fonts = PureWindowsPath(r"D:\kit\fonts") if isinstance(path, PureWindowsPath) else Path("/k/fo:nts")
    name, opts = _parse_filter(cap.subtitles_filter(path, fonts))
    assert name == "subtitles"
    assert opts["filename"] == path.as_posix() and opts["fontsdir"] == fonts.as_posix()
    assert opts["alpha"] == "1"


def test_render_argv_has_whitelist_fontsdir_and_alpha_codec(tmp_path):
    argv = cap.render_argv("ffmpeg", tmp_path / "a.ass", tmp_path / "fonts", tmp_path / "o.mov",
                           width=1080, height=1920, fps=29.97, duration=3)
    assert argv[argv.index("-protocol_whitelist") + 1] == "file,pipe"
    vf = argv[argv.index("-vf") + 1]
    assert vf.startswith("subtitles=") and "fontsdir=" in vf
    assert argv[argv.index("-pix_fmt") + 1] == "yuva444p10le" and "prores_ks" in argv
    assert all(isinstance(a, str) for a in argv)
    with pytest.raises(cap.ContractViolation):
        cap.render_argv("ffmpeg", "a.ass", "f", "o.mp4", width=1, height=1, fps=1, duration=1)
    with pytest.raises(ValueError):
        cap.render_argv("ffmpeg", "a.ass", "f", "o.mov", width="1;x", height=1, fps=1, duration=1)


def test_render_env_sets_fontconfig_file_pointing_at_fonts_dir(tmp_path):
    fonts = tmp_path / "fonts"
    fonts.mkdir()
    env = cap.render_env(tmp_path / "t", fonts)
    conf = Path(env["FONTCONFIG_FILE"]).read_text()
    assert str(fonts.resolve()) in conf


def test_prepare_fonts_dir_kit_or_temp_copy(tmp_path, monkeypatch):
    kit = tmp_path / "kit"
    kit.mkdir()
    (kit / "Inter.ttf").write_bytes(b"x")
    sysf = tmp_path / "Arial.ttf"
    sysf.write_bytes(b"y")
    monkeypatch.setattr(cap.kit_platform, "kit_fonts_dir", lambda: kit)
    assert cap.prepare_fonts_dir({"Inter": ("Inter", str(kit / "Inter.ttf"))}, tmp_path) == kit.resolve()
    d = cap.prepare_fonts_dir({"Inter": ("Arial", str(sysf))}, tmp_path / "t")
    assert (d / "Arial.ttf").is_file()


def test_cmd_render_wires_env_and_argv(tmp_path, monkeypatch):
    wj = tmp_path / "v.captions.json"
    wj.write_text(json.dumps({"schema": "flat_words_v1", "video": {"w": 540, "h": 960, "fps": 30, "dur": 3},
                              "words": [{"text": "hola", "start": 0, "end": .4}, {"text": "mundo", "start": .5, "end": .9}]}))
    monkeypatch.setattr(cap, "ffmpeg_with_libass", lambda: "ffmpeg")
    monkeypatch.setattr(cap.kit_platform, "find_font_file", lambda n: str(tmp_path / "F.ttf"))
    (tmp_path / "F.ttf").write_bytes(b"x")
    seen = {}
    monkeypatch.setattr(cap.subprocess, "run", lambda argv, **k: seen.update(argv=argv, env=k["env"]))
    assert cap.main(["render", str(wj), "--base-preset", "base-bold-left", "--margin-v-frac", "0.2"]) == 0
    assert "FONTCONFIG_FILE" in seen["env"] and "-protocol_whitelist" in seen["argv"]
    assert (tmp_path / "v.captions.ass").read_text().count("Dialogue:") == 2
    assert cap.main(["render", str(wj), "--base-preset", "base-bold-left", "--margin-v-frac", "1.5"]) == 2


def test_selftest_cli_offline():
    r = subprocess.run([sys.executable, str(REPO / "engines/video/captions.py"), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stderr


def test_no_absolute_paths_in_my_files():
    files = [REPO / "engines/video/captions.py", REPO / "engines/video/transcribe.py",
             *REPO.glob("presets/captions/**/*.json"), *REPO.glob("presets/luts/*"),
             REPO / "skills/captions/SKILL.md"]
    # patterns assembled at runtime so this file does not trip the guard itself
    parts = ["/" + "Users/", "/" + "home/", r"[A-Z]:\\\\", "Library/" + "Application Support",
             "/opt/" + "homebrew", "My " + "Drive"]
    pat = re.compile("|".join(parts))
    for f in files:
        if f.is_file():
            assert not pat.search(f.read_text(encoding="utf-8")), f


def test_forced_lines_are_optimally_balanced():
    ws = [{"t": t, "s": i, "e": i + 0.5} for i, t in enumerate("esto es lo que nadie te".split())]
    lines = cap.split_into_n_lines(ws, 3)[0]["lines"]
    assert [" ".join(w["t"] for w in ln) for ln in lines] == ["esto es", "lo que", "nadie te"]
    two = cap.split_into_n_lines(ws, 2)[0]["lines"]
    assert [" ".join(w["t"] for w in ln) for ln in two] == ["esto es lo", "que nadie te"]
    assert [len(ln) for ln in cap.split_into_n_lines(ws[:3], 3)[0]["lines"]] == [1, 1, 1]
    assert sum(len(ln) for ln in cap.split_into_n_lines(ws, 3)[0]["lines"]) == len(ws)  # nothing dropped
