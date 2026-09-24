# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Word-by-word (karaoke) captions: hook + base preset engine -> ASS -> alpha .mov.

Flow:
  1. transcribe VIDEO                -> VIDEO.captions.json (editable: fix `text`,
                                        delete words; start/end survive edits)
  2. edit the JSON by hand (and optionally write an annotated text with
     [hook]...[/hook], [strong]...[/strong], *emphasis*)
  3. render VIDEO.captions.json --base-preset NAME [--hook-preset NAME]
            [--annotated-text FILE] --margin-v-frac F
                                     -> VIDEO.captions.mov (ProRes 4444, alpha)

Presets: presets/captions/presets/*.json (OFL fonts only, via font-map.default.json).
Fonts: libass gets the font dir explicitly (`fontsdir=`) and FONTCONFIG_FILE points
at a generated fonts.conf, so no system font install is needed.
`--selftest` runs offline (no ffmpeg, no whisper, no fonts).
"""
from __future__ import annotations

import argparse
import difflib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand as brand_mod  # noqa: E402
import kit_platform  # noqa: E402
from transcribe import (PROTOCOL_WHITELIST, check_media_input, group_blocks,  # noqa: E402
                        norm_word, probe, transcribe)

PRESETS_DIR = kit_platform.KIT_ROOT / "presets" / "captions"
ALPHA_PIX_FMT = "yuva444p10le"
MULETILLAS = {"eh", "ehh", "eeh", "em", "emm", "mm", "mmm", "ah", "uh", "um", "este", "osea", "o sea"}
PUNCT_RE = re.compile(r"[.:!?¿¡…\"“”«»()\[\]\-—_/;]")
ACCENT_MAP = str.maketrans("áéíóúÁÉÍÓÚüÜñÑ", "aeiouAEIOUuUnN")
PRESET_REQUIRED_KEYS = {"name", "version", "kind", "typography_tokens", "layout", "reveal"}
BRACKET_TAG_RE = re.compile(r"\[(/?)(\w+)\]")
EMPHASIS_WORD_RE = re.compile(r"^(\W*)\*(.+?)\*(\W*)$")
SEGMENT_TYPE_TAGS = {"hook", "base"}


class ContractViolation(RuntimeError):
    """The request would violate the caption layer contract."""


# --- text ------------------------------------------------------------------------

def ass_time(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def esc(txt):
    """No ASS override blocks from user text."""
    return txt.replace("{", "(").replace("}", ")").replace("\\", "/").strip()


def sanitize_text(text):
    """Lowercase, strip accents/ñ, drop punctuation except commas."""
    text = PUNCT_RE.sub("", text.translate(ACCENT_MAP))
    return re.sub(r"[^\w\s,]", "", text).strip().lower()


def drop_muletillas(words):
    """flat words -> [{t,s,e}] without fillers (checked on the raw text)."""
    out = []
    for w in words:
        text = str(w["text"]).strip()
        if not text or PUNCT_RE.sub("", text).lower().strip(" ,") in MULETILLAS:
            continue
        out.append({"t": text, "s": round(float(w["start"]), 3), "e": round(float(w["end"]), 3)})
    return out


def _emit_plain_words(text, context, tokens):
    for raw in text.split():
        m = EMPHASIS_WORD_RE.match(raw)
        if m:
            prefix, core, suffix = m.groups()
            tokens.append({"text": prefix + core + suffix, "segment_type": context["segment_type"],
                           "role": "emphasized"})
        else:
            tokens.append({"text": raw, **context})


def parse_annotated_text(text):
    """[hook]/[base] spans set segment_type; any other [name] span sets role;
    *word* = role 'emphasized'. An unmatched closing tag pops the innermost span."""
    tokens, stack, pos = [], [{"segment_type": "base", "role": "normal"}], 0
    for m in BRACKET_TAG_RE.finditer(text):
        _emit_plain_words(text[pos:m.start()], stack[-1], tokens)
        closing, tag = m.group(1), m.group(2)
        if closing:
            if len(stack) > 1:
                stack.pop()
        else:
            ctx = dict(stack[-1])
            ctx["segment_type" if tag in SEGMENT_TYPE_TAGS else "role"] = tag
            stack.append(ctx)
        pos = m.end()
    _emit_plain_words(text[pos:], stack[-1], tokens)
    return tokens


def align_annotated_text(annotated_text, words):
    """Tag timed words with the annotated intent by CONTENT (SequenceMatcher on
    normalized words), never by index. A timed word missing from the text is
    dropped; any other disagreement fails closed (no guessed timing).
    `words` are [{t,s,e}]."""
    tokens = parse_annotated_text(annotated_text)
    matcher = difflib.SequenceMatcher(None, [norm_word(t["text"]) for t in tokens],
                                      [norm_word(w["t"]) for w in words], autojunk=False)
    tagged, failures = {}, []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                tok, w = tokens[i1 + k], words[j1 + k]
                tagged[j1 + k] = {"t": tok["text"], "s": w["s"], "e": w["e"],
                                  "segment_type": tok["segment_type"], "role": tok["role"]}
        elif tag != "insert":
            near = words[j1]["s"] if j1 < len(words) else (words[-1]["e"] if words else None)
            failures.append({"type": tag, "annotated": [t["text"] for t in tokens[i1:i2]],
                             "timed": [w["t"] for w in words[j1:j2]], "near_second": near})
    if failures:
        raise ContractViolation(f"el texto anotado no coincide con el JSON de palabras: {failures[:3]}")
    return [tagged[i] for i in sorted(tagged)]


def tag_plain(words):
    return [{**w, "segment_type": "base", "role": "normal"} for w in words]


# --- presets and fonts --------------------------------------------------------------

def preset_path(name_or_path) -> Path:
    p = Path(name_or_path)
    if p.suffix == ".json" and p.is_file():
        return p
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(name_or_path)):
        raise ContractViolation(f"nombre de preset inválido: {name_or_path!r}")
    return PRESETS_DIR / "presets" / f"{name_or_path}.json"


def load_preset(name_or_path):
    path = preset_path(name_or_path)
    try:
        preset = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractViolation(f"no se pudo leer el preset {path.name}: {exc}") from None
    missing = PRESET_REQUIRED_KEYS - preset.keys()
    if missing:
        raise ContractViolation(f"preset {path.name} incompleto, faltan: {sorted(missing)}")
    if preset["kind"] not in ("hook", "base"):
        raise ContractViolation(f"preset {path.name} kind inválido: {preset['kind']!r}")
    return preset


def list_presets():
    return sorted(p.stem for p in (PRESETS_DIR / "presets").glob("*.json"))


def load_font_map(path=None):
    return json.loads(Path(path or PRESETS_DIR / "font-map.default.json").read_text(encoding="utf-8"))


def resolve_fonts(families, font_map, finder=None):
    """family -> (ass_family_name, font_file). Kit font first, then the map's
    system fallbacks. Fails closed if nothing is found."""
    finder = finder or kit_platform.find_font_file
    out = {}
    for fam in sorted(families):
        candidates = [fam] + font_map.get("families", {}).get(fam, {}).get("system_fallback", [])
        for cand in candidates:
            f = finder(cand)
            if f:
                if cand != fam:
                    print(f"captions: '{fam}' no está en .kit/fonts; uso '{cand}' del sistema", file=sys.stderr)
                out[fam] = (cand, f)
                break
        else:
            raise ContractViolation(f"la fuente {fam!r} no se encontró en .kit/fonts ni en el "
                                    "sistema; corré el instalador de fuentes del kit")
    return out


def resolve_word_style(word, preset, font_map, line_font_role=None):
    """Token for the word's role; `line_font_role` borrows font_slot+case from
    another token (used for a forced hook's outer lines)."""
    tokens = preset["typography_tokens"]
    role = word.get("role", "normal")
    if role not in tokens:
        raise ContractViolation(f"preset {preset['name']!r} no define el token {role!r}")
    token = tokens[role]
    if line_font_role:
        if line_font_role not in tokens:
            raise ContractViolation(f"preset {preset['name']!r} no define el token {line_font_role!r}")
        o = tokens[line_font_role]
        token = {**token, "font_slot": o.get("font_slot"), "case": o.get("case", token.get("case"))}
    slots = font_map.get("slots", {})
    if token.get("font_slot") not in slots:
        raise ContractViolation(f"el font-map no define el casillero {token.get('font_slot')!r} "
                                f"pedido por {preset['name']!r}")
    return {**token, "font": slots[token["font_slot"]]}


def ass_color(value, brand=None):
    """'&HBBGGRR&' passes through; '#RRGGBB' or 'brand.<key>' become ASS colors."""
    if isinstance(value, str) and value.startswith("brand."):
        if brand is None:
            brand = brand_mod.load_brand()
        value = brand["colors"].get(value.split(".", 1)[1], "#FFFFFF")
    if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        r, g, b = value[1:3], value[3:5], value[5:7]
        return f"&H{b}{g}{r}&".upper()
    if isinstance(value, str) and re.fullmatch(r"&H[0-9A-Fa-f]{6,8}&?", value):
        return value
    raise ContractViolation(f"color inválido en preset: {value!r}")


# --- grouping ------------------------------------------------------------------------

def regroup_blocks_by_max_lines(blocks, max_lines):
    lines = [ln for b in blocks for ln in b["lines"]]
    if not lines:
        return []
    if max_lines is None:
        return [{"lines": lines}]
    return [{"lines": lines[i:i + max_lines]} for i in range(0, len(lines), max_lines)]


def isolate_roles_in_lines(blocks, isolate_roles):
    if not isolate_roles:
        return blocks
    iso = set(isolate_roles)
    return [{"lines": [list(g) for ln in b["lines"]
                       for _, g in itertools.groupby(ln, key=lambda w: w.get("role", "normal") in iso)]}
            for b in blocks]


def split_into_n_lines(words, n):
    """Exactly n contiguous lines, as even as possible by visible length (letters + spaces).
    Optimal, not greedy: minimizes the squared gap from an even share over every split.
    Fails closed if there are fewer words than lines. ponytail: O(n * words^2) DP, fine for hooks."""
    if len(words) < n:
        raise ContractViolation(f"no se pueden forzar {n} líneas con solo {len(words)} palabra(s)")
    lens = [len(w["t"]) for w in words]
    pre = [0]
    for x in lens:
        pre.append(pre[-1] + x)
    width = lambda i, j: pre[j] - pre[i] + (j - i - 1)  # words i..j-1 on one line
    target = width(0, len(words)) / n
    inf = float("inf")
    cost = [[inf] * (len(words) + 1) for _ in range(n + 1)]
    back = [[0] * (len(words) + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for k in range(1, n + 1):
        for j in range(k, len(words) - (n - k) + 1):
            for i in range(k - 1, j):
                c = cost[k - 1][i] + (width(i, j) - target) ** 2
                if c < cost[k][j]:
                    cost[k][j], back[k][j] = c, i
    cuts, j = [], len(words)
    for k in range(n, 0, -1):
        cuts.append((back[k][j], j))
        j = back[k][j]
    return [{"lines": [words[i:j] for i, j in reversed(cuts)]}]


def group_for_render(tagged, presets_by_kind):
    blocks = []
    for seg, run in itertools.groupby(tagged, key=lambda w: w["segment_type"]):
        run = list(run)
        layout = presets_by_kind[seg]["layout"]
        if layout.get("line_count"):
            blocks.extend(split_into_n_lines(run, layout["line_count"]))
            continue
        raw = group_blocks(run, layout.get("max_words_per_line", 4), layout.get("pause_break", 0.6))
        raw = isolate_roles_in_lines(raw, layout.get("isolate_roles"))
        blocks.extend(regroup_blocks_by_max_lines(raw, layout.get("max_lines")))
    return blocks


# --- ASS -------------------------------------------------------------------------------

def _measure_pil(font_file, size, text):
    try:
        from PIL import ImageFont
        return ImageFont.truetype(font_file, size).getlength(text)
    except Exception:  # ponytail: PIL/font missing -> no auto-shrink, never a crash
        return None


measure_text = _measure_pil  # (font_file, size, text) -> width px or None; tests replace it


def _line_fit_scale(resolved, available_width, font_files):
    """Shrink a line just enough to fit (0.97 margin for faux bold). 1.0 if it
    fits or if it can't be measured."""
    total = 0.0
    for idx, (style, size, surface) in enumerate(resolved):
        f = font_files.get(style["font"])
        wlen = measure_text(f, size, surface) if f else None
        if wlen is None:
            return 1.0
        total += wlen + ((measure_text(f, size, " ") or 0) if idx else 0)
    return 1.0 if total <= available_width else (available_width / total) * 0.97


def _ass_style_line(name, preset, brand):
    box = preset.get("background_box")
    if box:
        bs, outline = 3, box.get("padding", 14)
        back = ass_color(box.get("color", "&H00000000"), brand)
        primary = ass_color(box.get("text_color", "&H00FFFFFF"), brand)
    else:
        bs, outline, back, primary = 1, 0, "&H00000000", "&H00FFFFFF"
    return (f"Style: {name},Arial,60,{primary},{primary},&H00000000,{back},"
            f"0,0,0,0,100,100,0,0,{bs},{outline},0,1,80,60,200,1")


def build_ass_from_preset(cfg, presets_by_kind, font_map, margin_v_frac=None, brand=None,
                          font_names=None, font_files=None):
    """Every event renders the whole block; the current word fades in, future
    words are invisible but keep their space (no horizontal jitter).
    `margin_v_frac` (baseline height as a fraction from the bottom) overrides every
    preset's own value. `font_names` maps family -> name libass should use
    (system fallback); `font_files` maps that name -> file (auto-shrink)."""
    w, h = int(cfg["video"]["w"]), int(cfg["video"]["h"])
    font_names, font_files = font_names or {}, font_files or {}
    names, style_lines = {}, []
    for p in presets_by_kind.values():
        if p["name"] not in names:
            names[p["name"]] = f"S{len(names)}"
            style_lines.append(_ass_style_line(names[p["name"]], p, brand))
    header = ("[Script Info]\nScriptType: v4.00+\n"
              f"PlayResX: {w}\nPlayResY: {h}\nScaledBorderAndShadow: yes\n\n"
              "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
              "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
              "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
              + "\n".join(style_lines) +
              "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev, blocks = [], cfg["blocks"]
    for bi, block in enumerate(blocks):
        lines = block["lines"]
        flat = [wd for ln in lines for wd in ln]
        if not flat:
            continue
        preset = presets_by_kind[flat[0]["segment_type"]]
        sname, layout = names[preset["name"]], preset["layout"]
        fade_ms = preset["reveal"].get("fade_ms", 150)
        glow = preset.get("glow")
        glow_tag = ("" if preset.get("background_box") else
                    f"\\3c{ass_color(glow['color'], brand)}\\bord{glow['radius']}\\blur{glow['blur']}\\shad0"
                    if glow else "\\bord0\\shad0")
        block_end = flat[-1]["e"] + 0.25
        if bi + 1 < len(blocks) and blocks[bi + 1]["lines"]:
            block_end = min(block_end, blocks[bi + 1]["lines"][0][0]["s"])
        margin_l = round(w * layout.get("margin_l_frac", 0.08))
        mv = margin_v_frac if margin_v_frac is not None else layout.get("margin_v_frac", 0.28)
        margin_v = round(h * (1 - mv))
        anchor, pos_x = {"left": (1, margin_l), "center": (2, round(w / 2)),
                         "right": (3, w - margin_l)}[layout.get("alignment", "left")]
        size_mults = layout.get("line_size_mult")
        forced_hook = (preset["kind"] == "hook" and layout.get("line_count")
                       and "emphasized" in preset["typography_tokens"])
        line_data = []
        for li, ln in enumerate(lines):
            mult = (size_mults[min(li, len(size_mults) - 1)] if size_mults else
                    layout.get("first_line_size_mult", 1.0) if li == 0 else 1.0)
            role_override = "emphasized" if forced_hook and li in (0, len(lines) - 1) else None
            resolved = []
            for wd in ln:
                style = resolve_word_style(wd, preset, font_map, line_font_role=role_override)
                style["font"] = font_names.get(style["font"], style["font"])
                surface = PUNCT_RE.sub("", esc(wd["t"])).strip()
                if style.get("strip_diacritics"):
                    surface = surface.translate(ACCENT_MAP)
                if style.get("strip_commas"):
                    surface = surface.replace(",", "")
                if style.get("case") == "lower":
                    surface = surface.lower()
                elif style.get("case") == "upper":
                    surface = surface.upper()
                resolved.append((style, round(h * style["size_frac"] * mult), surface))
            line_data.append((resolved, _line_fit_scale(resolved, w - 2 * margin_l, font_files)))
        rot = layout.get("rotation_deg", 0)
        rot_tag = f"\\frz{rot}" if rot else ""
        raw_sp = layout.get("line_spacing_mult")
        spacing = raw_sp if isinstance(raw_sp, list) else ([raw_sp] if raw_sp else [])
        for i, wd in enumerate(flat):
            start = wd["s"]
            end = flat[i + 1]["s"] if i + 1 < len(flat) else block_end
            if end <= start:
                continue
            fade = min(fade_ms, round((end - start) * 1000))
            rendered, k = [], 0
            for resolved, fit in line_data:
                parts = []
                for style, base_size, surface in resolved:
                    tag = ("{\\fn" + style["font"] + "\\fs" + str(round(base_size * fit))
                           + ("\\b1" if style.get("weight") == "bold" else "\\b0")
                           + ("\\i1" if style.get("italic") else "\\i0")
                           + ("\\c" + ass_color(style["color"], brand) if style.get("color") else "")
                           + glow_tag + "}")
                    alpha = ("{\\alpha&HFF&\\t(0," + str(fade) + ",\\alpha&H00&)}" if k == i else
                             "{\\alpha&HFF&\\t(0,0,\\alpha&HFF&)}" if k > i else "{\\alpha&H00&}")
                    parts.append(tag + alpha + surface)
                    k += 1
                rendered.append(" ".join(parts))
            t0, t1 = ass_time(start), ass_time(end)
            if spacing and len(rendered) > 1:
                heights = [round(max((round(bs * fit) for _, bs, _ in res), default=0)
                                 * spacing[min(li, len(spacing) - 1)])
                           for li, (res, fit) in enumerate(line_data)]
                ys, acc = [0] * len(rendered), 0
                for li in range(len(rendered) - 1, -1, -1):
                    ys[li] = margin_v - acc
                    acc += heights[li]
                for li, text in enumerate(rendered):
                    ev.append(f"Dialogue: 0,{t0},{t1},{sname},,0,0,0,,"
                              f"{{\\an{anchor}\\pos({pos_x},{ys[li]}){rot_tag}}}{text}")
            else:
                ev.append(f"Dialogue: 0,{t0},{t1},{sname},,0,0,0,,"
                          f"{{\\an{anchor}\\pos({pos_x},{margin_v}){rot_tag}}}" + "\\N".join(rendered))
    return header + "\n".join(ev) + "\n"


def used_families(presets_by_kind, font_map):
    slots = font_map.get("slots", {})
    return {slots[t["font_slot"]] for p in presets_by_kind.values()
            for t in p["typography_tokens"].values() if t.get("font_slot") in slots}


# --- ffmpeg ----------------------------------------------------------------------------

def _escape(s, chars):
    return "".join("\\" + c if c in chars else c for c in s)


def filter_path(path) -> str:
    """Path for a filter option value: forward slashes (Windows drive paths
    survive), escaped for the option parser (\\ ' :) then the graph parser
    (\\ ' [ ] , ;)."""
    p = path if isinstance(path, PurePath) else Path(path)
    return _escape(_escape(p.as_posix(), "\\':"), "\\'[],;")


def subtitles_filter(ass_path, fonts_dir) -> str:
    return f"subtitles=filename={filter_path(ass_path)}:fontsdir={filter_path(fonts_dir)}:alpha=1"


def render_argv(ffmpeg, ass_path, fonts_dir, out, *, width, height, fps, duration):
    width, height, fps, duration = int(width), int(height), float(fps), float(duration)
    if Path(out).suffix.lower() != ".mov":
        raise ContractViolation("la capa de subtítulos debe ser .mov")
    return [ffmpeg, "-nostdin", "-y", "-v", "error", *PROTOCOL_WHITELIST,
            "-f", "lavfi", "-i", f"color=c=black@0.0:s={width}x{height}:r={fps:g},format=rgba",
            "-vf", subtitles_filter(ass_path, fonts_dir), "-t", f"{duration:.3f}",
            "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", ALPHA_PIX_FMT, str(out)]


def render_env(tmpdir, fonts_dir) -> dict:
    env = dict(os.environ)
    env["FONTCONFIG_FILE"] = str(kit_platform.write_fontconfig(Path(tmpdir), fonts_dir))
    return env


def ffmpeg_with_libass():
    ff = kit_platform.ffmpeg()
    try:
        out = subprocess.run([ff, "-hide_banner", "-h", "filter=subtitles"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    except OSError:
        out = ""
    if "subtitles" not in out or "Unknown filter" in out:
        raise ContractViolation("ffmpeg sin libass (falta el filtro subtitles); instalá un ffmpeg "
                                "con libass o apuntá KIT_FFMPEG a uno")
    return ff


def prepare_fonts_dir(resolved, tmpdir) -> Path:
    """Kit fonts dir if every resolved file lives there; else a temp dir with
    copies of the resolved files (system fallbacks), deleted after render."""
    kit = kit_platform.kit_fonts_dir().resolve()
    files = [Path(f).resolve() for _, f in resolved.values()]
    if all(kit in f.parents for f in files):
        return kit
    d = Path(tmpdir) / "fonts"
    d.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, d / f.name)
    return d


# --- commands -----------------------------------------------------------------------

def cmd_transcribe(args):
    video = check_media_input(args.video)
    art = transcribe(video, args.lang, args.model, args.allow_large_model)
    art["video"] = probe(video)
    out = Path(args.out) if args.out else video.with_name(video.name + ".captions.json")
    out.write_text(json.dumps(art, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
    for b in group_blocks(drop_muletillas(art["words"])):
        print("  " + " / ".join(" ".join(w["t"] for w in ln) for ln in b["lines"]))
    print("Revisá y corregí el JSON (campo text), después: render", out.name)


def build_from_files(words_json, base, hook=None, annotated=None, brand_path=None):
    art = json.loads(Path(words_json).read_text(encoding="utf-8"))
    if art.get("schema") != "flat_words_v1":
        raise ContractViolation(f"esperaba flat_words_v1, encontré {art.get('schema')!r}")
    words = drop_muletillas(art["words"])
    tagged = (align_annotated_text(Path(annotated).read_text(encoding="utf-8"), words)
              if annotated else tag_plain(words))
    presets = {"base": load_preset(base), "hook": load_preset(hook or base)}
    if presets["base"]["kind"] != "base" or (hook and presets["hook"]["kind"] != "hook"):
        raise ContractViolation("--base-preset debe ser kind=base y --hook-preset kind=hook")
    return art, tagged, presets, (brand_mod.load_brand(brand_path) if brand_path else None)


def cmd_render(args):
    art, tagged, presets, brand = build_from_files(args.words, args.base_preset, args.hook_preset,
                                                   args.annotated_text, args.brand)
    video = {**art.get("video", {}), **{k: v for k, v in
             {"w": args.width, "h": args.height, "fps": args.fps, "dur": args.duration}.items() if v}}
    if not all(k in video for k in ("w", "h", "fps", "dur")):
        raise ContractViolation("faltan w/h/fps/dur: transcribí con este motor o pasá --width/--height/--fps/--duration")
    font_map = load_font_map(args.font_map)
    resolved = resolve_fonts(used_families(presets, font_map), font_map)
    cfg = {"video": video, "blocks": group_for_render(tagged, presets)}
    last = max((wd["e"] for b in cfg["blocks"] for ln in b["lines"] for wd in ln), default=0.0)
    if float(video["dur"]) < last:
        raise ContractViolation(f"la duración ({video['dur']}s) termina antes de la última palabra ({last}s)")
    ass = build_ass_from_preset(cfg, presets, font_map, args.margin_v_frac, brand,
                                font_names={fam: n for fam, (n, _) in resolved.items()},
                                font_files={n: f for n, f in resolved.values()})
    out = Path(args.out) if args.out else Path(str(args.words).replace(".captions.json", "") + ".captions.mov")
    ass_path = out.with_suffix(".ass")
    ass_path.write_text(ass, encoding="utf-8")
    ff = ffmpeg_with_libass()
    with tempfile.TemporaryDirectory() as td:
        fonts_dir = prepare_fonts_dir(resolved, td)
        subprocess.run(render_argv(ff, ass_path, fonts_dir, out, width=video["w"], height=video["h"],
                                   fps=video["fps"], duration=video["dur"]),
                       check=True, env=render_env(td, fonts_dir))
    print(out)


def selftest():
    """Offline: synthetic words -> ASS for every shipped preset; checks the
    ffmpeg argv/env builders. No ffmpeg, whisper or fonts needed."""
    words = drop_muletillas([{"text": t, "start": i * 0.4, "end": i * 0.4 + 0.35}
                             for i, t in enumerate("Hola eh esto es una prueba, con énfasis final.".split())])
    assert [w["t"] for w in words][:2] == ["Hola", "esto"], words
    font_map = load_font_map()
    brand = {"colors": {"accent": "#F2B134"}}
    names = list_presets()
    assert names, "no hay presets"
    hook = load_preset("hook-serif-escalation")
    for name in names:
        p = load_preset(name)
        presets = {"base": p if p["kind"] == "base" else load_preset("base-uniform-clean"),
                   "hook": p if p["kind"] == "hook" else hook}
        tagged = align_annotated_text("[hook]Hola esto es[/hook] una *prueba*, con énfasis final.", words)
        cfg = {"video": {"w": 1080, "h": 1920}, "blocks": group_for_render(tagged, presets)}
        ass = build_ass_from_preset(cfg, presets, font_map, margin_v_frac=0.7, brand=brand)
        assert ass.startswith("[Script Info]") and "Dialogue:" in ass, name
        assert used_families(presets, font_map) <= set(font_map["families"]), name
    assert ass_color("brand.accent", brand) == "&H34B1F2&"
    argv = render_argv("ffmpeg", Path("t", "a.ass"), Path("fonts"), "o.mov", width=1080, height=1920,
                       fps=30, duration=2)
    assert "-protocol_whitelist" in argv and "fontsdir=" in argv[argv.index("-vf") + 1]
    with tempfile.TemporaryDirectory() as td:
        assert Path(render_env(td, Path(td))["FONTCONFIG_FILE"]).is_file()
    return len(names)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("transcribe", help="video -> <video>.captions.json editable")
    t.add_argument("video")
    t.add_argument("--lang", default=None)
    t.add_argument("--model", default=None)
    t.add_argument("--allow-large-model", action="store_true")
    t.add_argument("--out")
    r = sub.add_parser("render", help="captions.json + presets -> overlay .mov con alpha")
    r.add_argument("words")
    r.add_argument("--base-preset", required=True)
    r.add_argument("--hook-preset")
    r.add_argument("--annotated-text")
    r.add_argument("--margin-v-frac", type=float, required=True,
                   help="altura de la línea base medida desde abajo (0.12 abajo, 0.5 centro, 0.7 arriba); se pregunta siempre")
    r.add_argument("--font-map")
    r.add_argument("--brand", help="brand.json para colores brand.*")
    r.add_argument("--out")
    for k in ("width", "height"):
        r.add_argument(f"--{k}", type=int)
    for k in ("fps", "duration"):
        r.add_argument(f"--{k}", type=float)
    sub.add_parser("list", help="lista los presets")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            print(f"selftest OK ({selftest()} presets)")
        elif args.cmd == "transcribe":
            cmd_transcribe(args)
        elif args.cmd == "render":
            if not 0.0 < args.margin_v_frac < 1.0:
                raise ContractViolation("--margin-v-frac va entre 0 y 1")
            cmd_render(args)
        elif args.cmd == "list":
            print("\n".join(list_presets()))
        else:
            ap.error("usar --selftest, transcribe, render o list")
    except (ContractViolation, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
