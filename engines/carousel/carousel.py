# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Brand-driven carousel renderer: JSON spec + brand.json -> one HTML per slide
(1080x1350) -> optional PNG via Playwright. Offline; never downloads anything.

Usage:
  python carousel.py SPEC.json [--brand brand.json|nombre] [--out DIR] [--project DIR] [--html-only] [--strict]
  python carousel.py --selftest

Optional slide fields (all text): `module` (narrative role, see presets/carousel/modules.json), `image`,
`image_position` (full|top|bottom), `focus` ("30% 20%": which part of the photo stays visible) and, on the
cover, `circle` (a small context photo). Optional spec fields: `goal` ("comments" or "sales").
`--strict` turns every advice into an error and also demands a .source.json per photo and an approved
watermark review (check_watermark.py).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import unicodedata
import sys
import tempfile
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # faces, check_watermark
import brand as brandmod  # noqa: E402
import kit_platform  # noqa: E402

PRESETS = kit_platform.KIT_ROOT / "presets" / "carousel"
W, H = 1080, 1350
TYPES = {"cover", "headline", "body", "quote", "stat", "source", "cta"}
REQUIRED = {"cover": ["title"], "headline": ["title"], "body": ["text"], "quote": ["quote"],
            "stat": ["value", "text"], "source": ["text"], "cta": ["text"]}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_POSITIONS = {"full", "top", "bottom"}  # top/bottom: photo in a band, text on a clean background
MAX_SLIDES = 20
MAX_TEXT = 600
POS = re.compile(r"^(?:left|center|right|\d{1,3}%)(?:\s+(?:top|center|bottom|\d{1,3}%))?$")
BANDS = {"full": (1080, 1350), "top": (1080, 470), "bottom": (1080, 560)}  # visible box of each photo, px
CIRCLE = (250, 250)
MODULES = json.loads((PRESETS / "modules.json").read_text(encoding="utf-8"))
MODULE_IDS = {m["id"] for m in MODULES["modules"]}
QUOTE_OPEN, QUOTE_CLOSE = "«\"“'‘", "»\"”'’"


class SpecError(ValueError):
    pass


def validate_spec(spec) -> list[dict]:
    if not isinstance(spec, dict) or not isinstance(spec.get("slides"), list):
        raise SpecError("spec must be an object with a 'slides' list")
    slides = spec["slides"]
    if not 1 <= len(slides) <= MAX_SLIDES:
        raise SpecError(f"slides must have 1..{MAX_SLIDES} items")
    for i, s in enumerate(slides, 1):
        if not isinstance(s, dict) or s.get("type") not in TYPES:
            raise SpecError(f"slide {i}: type must be one of {sorted(TYPES)}")
        for k in REQUIRED[s["type"]]:
            if not isinstance(s.get(k), str) or not s[k].strip():
                raise SpecError(f"slide {i} ({s['type']}): '{k}' is required text")
        if s.get("module") and s["module"] not in MODULE_IDS:
            raise SpecError(f"slide {i}: módulo desconocido '{s['module']}' (ver presets/carousel/modules.json)")
        if s.get("focus") and not (POS.match(s["focus"]) and all(int(n) <= 100 for n in re.findall(r"(\d{1,3})%", s["focus"]))):
            raise SpecError(f"slide {i}: focus inválido '{s['focus']}' (ej. '30% 20%' o 'center top')")
        if s.get("circle") and s["type"] != "cover":
            raise SpecError(f"slide {i}: 'circle' solo va en la portada")
        pos = s.get("image_position", "full")
        if s["type"] == "cover" and pos != "full":
            raise SpecError(f"slide {i}: la portada lleva la foto a pantalla completa (image_position 'full')")
        if pos not in IMAGE_POSITIONS:
            raise SpecError(f"slide {i}: image_position must be one of {sorted(IMAGE_POSITIONS)}")
        if pos != "full" and not s.get("image"):
            raise SpecError(f"slide {i}: image_position '{pos}' needs an image")
        for k, v in s.items():
            if k != "type" and not isinstance(v, str):
                raise SpecError(f"slide {i}: '{k}' must be text")
            if len(v) > MAX_TEXT:
                raise SpecError(f"slide {i}: '{k}' longer than {MAX_TEXT} chars")
    return slides


TEXT_KEYS = ("title", "text", "subtitle", "quote")
REPEAT_MIN = 20


def structure_warnings(slides: list[dict], goal: str | None = None) -> list[str]:
    """Narrative rules from presets/carousel/ESTRUCTURAS.md. Advice, not errors: a member's
    carousel still renders, the engine just says what to improve. Module rules (polarity, closing,
    photos) only apply when at least one slide declares a `module`."""
    out = []
    if not 4 <= len(slides) <= 8:
        out.append(f"{len(slides)} slides: lo recomendado es de 4 a 8")
    if slides[0]["type"] != "cover":
        out.append("el primer slide debería ser 'cover'")
    if slides[-1]["type"] != "cta":
        out.append("el último slide debería ser 'cta'")
    for i in range(1, len(slides)):
        if slides[i]["type"] == slides[i - 1]["type"] and slides[i]["type"] != "headline":
            out.append(f"slides {i} y {i + 1} son del mismo tipo ('{slides[i]['type']}')")
    seen = {}
    for i, s in enumerate(slides, 1):  # any 20+ character run repeated in two slides reads as filler
        for k in TEXT_KEYS:
            w = _norm(s.get(k, "")).split()
            for a in range(len(w)):
                for b in range(a + 1, len(w) + 1):
                    win = " ".join(w[a:b])
                    if len(win) >= REPEAT_MIN:
                        j = seen.setdefault(win, i)
                        if j != i:
                            out.append(f"slides {j} y {i} repiten el mismo texto: «{win}»")
                        break
    out = list(dict.fromkeys(out))
    h = (slides[0].get("title") or "").strip()
    if len(h) > 1 and h[:1] in QUOTE_OPEN and h[-1:] in QUOTE_CLOSE:
        out.append("la portada es una cita entre comillas: la cita va en el slide 2 y la portada lleva un titular propio")
    mods = [s.get("module") for s in slides]
    if any(mods):
        out += module_warnings(slides, mods, goal)
    elif goal == "comments" and not slides[-1].get("text", "").strip().endswith("?"):
        out.append("el objetivo es comentarios: el último slide debería terminar en una pregunta")
    return out


def module_warnings(slides: list[dict], mods: list, goal: str | None) -> list[str]:
    out = []
    if not set(mods) & set(MODULES["polarity"]):
        out.append("sin tensión: usa al menos un módulo de choque (" + ", ".join(MODULES["polarity"][:5]) + "…)")
    last = mods[-1]
    if goal == "comments":
        if last not in MODULES["closing_comments"]:
            out.append("objetivo comentarios: el cierre debe ser un módulo de " + ", ".join(MODULES["closing_comments"]))
        if not slides[-1].get("text", "").strip().endswith("?"):
            out.append("objetivo comentarios: el último slide debe terminar en pregunta ('?')")
    elif goal == "sales" and last not in MODULES["closing_sales"]:
        out.append("objetivo ventas: el cierre debe ser el módulo 'oferta'")
    bare = [i + 1 for i, s in enumerate(slides) if i and not s.get("image")]
    cap = (len(slides) + 2) // 4  # 4-5 slides: 1 without photo, 6-8: 2
    if bare and len(bare) > cap:
        out.append(f"{len(bare)} slides sin foto {bare}: con {len(slides)} slides el máximo es {cap} (la portada no cuenta)")
    return out


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", str(text).lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in t if not unicodedata.combining(c))).strip()


def safe_image(path: str, project: Path) -> Path:
    """Confine a user image to the project dir; local jpg/png/webp only."""
    if re.match(r"^[a-z][a-z0-9+.-]*://", path, re.I):
        raise SpecError(f"image must be a local file, not a URL: {path}")
    root = project.resolve()
    p = Path(path)
    p = (p if p.is_absolute() else root / p).resolve()
    if p != root and root not in p.parents:
        raise SpecError(f"image outside the project folder: {path}")
    if p.suffix.lower() not in IMAGE_EXT:
        raise SpecError(f"image must be jpg/png/webp: {path}")
    if not p.is_file():
        raise SpecError(f"image not found: {path}")
    return p


def image_files(spec: dict, project: Path) -> list[Path]:
    """Every photo the spec uses (slide photos and cover circles), confined to the project."""
    out = []
    for s in spec["slides"]:
        for k in ("image", "circle"):
            if s.get(k):
                p = safe_image(s[k], project)
                if p not in out:
                    out.append(p)
    return out


SOURCE_ORIGINS = {"own", "ai", "press", "stock", "other"}


def source_problems(files: list[Path]) -> list[str]:
    """Each photo `x.jpg` needs `x.source.json`: {"origin": "own|ai|press|stock|other", "source_url"?, "credit"?}.
    `own` and `ai` need no link; the rest must say where the photo came from."""
    out = []
    for f in files:
        sf = f.with_name(f.stem + ".source.json")
        try:
            d = json.loads(sf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            out.append(f"{f.name}: falta {sf.name} con el origen de la foto")
            continue
        if not isinstance(d, dict) or d.get("origin") not in SOURCE_ORIGINS:
            out.append(f"{sf.name}: 'origin' debe ser uno de {sorted(SOURCE_ORIGINS)}")
        elif d["origin"] not in ("own", "ai") and not str(d.get("source_url", "")).strip():
            out.append(f"{sf.name}: falta 'source_url' (de dónde salió la foto)")
    return out


def face_check(spec: dict, project: Path) -> tuple[dict, list[str], list[str]]:
    """(auto focus by 'slide:field', problems, notes). Finds faces (macOS Vision, optional), picks the
    crop that keeps every head whole, and reports faces the visible edge would cut. Without a
    detector it only leaves a note: it never fails an install or a render."""
    import faces
    auto, bad, notes = {}, [], []
    if not faces.available():
        return auto, bad, ["no hay detector de caras en este equipo (solo macOS con pyobjc): "
                           "revisa a ojo que ninguna cara quede cortada. Para activarlo en Mac: .kit/venv/bin/python -m pip install pyobjc-framework-Vision"]
    for i, s in enumerate(spec["slides"], 1):
        for key, box, circle in ((("image", BANDS[s.get("image_position", "full")], False), ("circle", CIRCLE, True))):
            if not s.get(key):
                continue
            try:
                path = safe_image(s[key], project)
                found, wh = faces.detect_faces(path), faces.image_size(path)
            except (SpecError, faces.DetectorError, OSError, ValueError) as e:
                notes.append(f"slide {i}: no pude revisar las caras de {s[key]} ({str(e)[:60]})")
                continue
            manual = faces.parse_pos(s["focus"]) if s.get("focus") and key == "image" else None
            pos = manual or faces.auto_focal(wh, box, found)
            if pos and not manual:
                auto[f"{i}:{key}"] = faces.css_pos(pos)
            cut = faces.cut_faces(found, faces.window(wh, box, pos or (50, 50)), circle)
            if cut:
                bad.append(f"slide {i} ({key} {s[key]}): {len(cut)} cara(s) cortada(s) por el borde"
                           + (" con el foco manual" if manual else "; cambia la foto o pon 'focus'"))
    return auto, bad, notes


FIT = {"h1": (128, ((40, 1), (70, .82), (100, .69), (999, .56))),
       "h2": (92, ((40, 1), (70, .82), (100, .69), (999, .56))),
       "cta": (110, ((50, 1), (90, .82), (140, .69), (999, .56)))}


def fit(kind: str, text: str) -> str:
    """Inline font-size for long headlines (short ones keep the stylesheet size). The QC still
    blocks whatever does not fit; this only avoids failing on merely long text."""
    base, steps = FIT[kind]
    k = next(f for n, f in steps if len(text) <= n)
    return "" if k == 1 else f' style="font-size:{int(base * k)}px"'


def esc(text: str, highlight: str = "") -> str:
    t = html.escape(text or "")
    if highlight:
        w = html.escape(highlight)
        m = re.search(re.escape(w), t, re.IGNORECASE)
        if m:
            t = f'{t[:m.start()]}<span class="hl">{m.group(0)}</span>{t[m.end():]}'
    return t


FONT_EXT = {".ttf", ".otf", ".woff2", ".woff"}


def kit_font_file(family: str) -> Path | None:
    """Font file for a family inside the kit fonts dir only. Chromium reads woff2, so it counts
    here (kit_platform.find_font_file skips it because ffmpeg/ASS cannot). Kit copy wins over
    the system copy: a member's machine has the kit fonts, not ours."""
    want = "".join(c for c in family.lower() if c.isalnum())
    d = kit_platform.kit_fonts_dir()
    if not want or not d.is_dir():
        return None
    files = sorted((p for p in d.rglob("*") if p.suffix.lower() in FONT_EXT),
                   key=lambda p: (p.suffix.lower() not in (".ttf", ".otf"), len(p.stem)))
    for p in files:
        stem = "".join(c for c in p.stem.lower() if c.isalnum())
        if stem.startswith(want) and not stem[len(want):].startswith(("bold", "italic", "light", "black", "thin")):
            return p.resolve()
    return None


def font_faces(b: dict) -> str:
    """@font-face only for font files that exist inside the kit fonts dir (no web fonts)."""
    out = []
    for fam in dict.fromkeys(b["fonts"].values()):
        f = kit_font_file(fam)
        if f:
            name = re.sub(r"[^\w .-]", "", fam)
            out.append(f'@font-face {{ font-family: "{name}"; src: url("{Path(f).resolve().as_uri()}"); }}')
    return "\n".join(out)


def inner_html(s: dict, b: dict) -> str:
    t, hl = s["type"], s.get("highlight", "")
    g = lambda k: esc(s.get(k, ""))  # noqa: E731
    label = f'<div class="label">{g("label")}</div>' if s.get("label") else ""
    if t == "cover":
        return f'{label}<h1{fit("h1", s["title"])}>{esc(s["title"], hl)}</h1><p class="sub">{g("subtitle")}</p>'
    if t == "headline":
        return f'{label}<h2{fit("h2", s["title"])}>{esc(s["title"], hl)}</h2><p>{g("text")}</p>'
    if t == "body":
        return f'{label}<p>{esc(s["text"], hl)}</p>'
    if t == "quote":
        return f'<blockquote>{esc(s["quote"], hl)}</blockquote><div class="author">{g("author")}</div>'
    if t == "stat":
        return f'{label}<div class="stat">{g("value")}</div><p>{esc(s["text"], hl)}</p>'
    if t == "source":
        return f'<div class="label">{esc(b["source_label"])}</div><p class="source">{g("text")}</p>'
    cta_line = s.get("follow") or b["handle"]
    return f'<div class="cta"{fit("cta", s["text"])}>{esc(s["text"], hl)}</div><p class="follow">{esc(cta_line)}</p>'


def build_html(spec: dict, b: dict, project: Path, auto_focal: dict | None = None) -> list[str]:
    slides = validate_spec(spec)
    tmpl = Template((PRESETS / "slide.html").read_text(encoding="utf-8"))
    css = (PRESETS / "slide.css").read_text(encoding="utf-8")
    faces, vars_ = font_faces(b), brandmod.css_vars(b)
    pages = []
    auto_focal = auto_focal or {}
    for i, s in enumerate(slides, 1):
        if s.get("image"):
            uri = safe_image(s["image"], project).as_uri().replace("'", "%27")
            pos = s.get("image_position", "full")
            shade = '<div class="shade"></div>' if pos == "full" else ""
            f = s.get("focus") or auto_focal.get(f"{i}:image")
            focus = f";background-position:{html.escape(f)}" if f else ""
            media = f'<div class="media band-{pos}" style="background-image:url(\'{uri}\'){focus}"></div>{shade}'
        elif s["type"] in ("cover", "headline", "cta"):
            media = '<div class="media panel"></div>'  # no image: brand-colored panel
        else:
            media = ""
        if s.get("circle"):  # context circle: a real photo of the fact, never the same face as the background
            cu = safe_image(s["circle"], project).as_uri().replace("'", "%27")
            cf = auto_focal.get(f"{i}:circle")
            media += (f'<div class="circle" style="background-image:url(\'{cu}\')'
                      f'{";background-position:" + html.escape(cf) if cf else ""}"></div>')
        pages.append(tmpl.substitute(
            lang=esc(b["language"]), title=esc(spec.get("title", b["name"])), fontfaces=faces,
            vars=vars_, css=css, type=s["type"] + (f" band-{s['image_position']}" if s.get("image_position", "full") != "full" else ""), media=media, logo=esc(b["logo_text"]),
            kicker=esc(s.get("kicker", spec.get("kicker", ""))), inner=inner_html(s, b),
            handle=esc(b["handle"]), page=f"{i}/{len(slides)}"))
    return pages


def write_html(pages: list[str], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, page in enumerate(pages, 1):
        p = out / f"slide-{i:02d}.html"
        p.write_text(page, encoding="utf-8")
        paths.append(p)
    return paths


# QC ported from the vault's carousel@1 render gate: a PNG is only written when every check passes.
QC_JS = """() => {
  const probs = [];
  const slide = document.querySelector('.slide').getBoundingClientRect();
  const els = [...document.querySelectorAll('.body *, .top span, .bottom span')]
    .filter(el => el.innerText.trim() && el.getClientRects().length && !el.querySelector('*'));
  const boxes = [];
  for (const el of els) {
    const name = el.className || el.tagName.toLowerCase();
    if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).display !== 'inline')
      probs.push(`"${name}": una palabra no entra a lo ancho`);
    // element box, not a text Range: a 300px stat's Range includes the font's full ascent and
    // reads as overlapping its neighbours when nothing visibly touches
    const b = el.getBoundingClientRect();
    if (b.top < slide.top - 2 || b.bottom > slide.bottom + 2 || b.left < slide.left - 2 || b.right > slide.right + 2)
      probs.push(`"${name}": el texto se sale del slide (acórtalo)`);
    boxes.push({name, l: b.left, t: b.top, r: b.right, b: b.bottom});
  }
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], c = boxes[j];
    const w = Math.min(a.r, c.r) - Math.max(a.l, c.l), h = Math.min(a.b, c.b) - Math.max(a.t, c.t);
    if (w > 1 && h > 1) probs.push(`"${a.name}" y "${c.name}" quedan encimados (acorta el texto)`);
  }
  // accented capitals on multi-line titles: the accent's top must clear the line above by 6px.
  // Consecutive baselines sit one line-height apart, so the gap is line-height - ascent("Á").
  const ctx = document.createElement('canvas').getContext('2d');
  for (const el of document.querySelectorAll('h1, h2, .cta, blockquote, .stat')) {
    const cs = getComputedStyle(el), lh = parseFloat(cs.lineHeight);
    const t = cs.textTransform === 'uppercase' ? el.innerText.toUpperCase() : el.innerText;
    if (!lh || !/[ÁÉÍÓÚÑÜ]/.test(t) || el.getBoundingClientRect().height < lh * 1.5) continue;
    ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const up = Math.max(...[...'ÁÉÍÓÚÑÜ'].filter(c => t.includes(c)).map(c => ctx.measureText(c).actualBoundingBoxAscent));
    if (lh - up < 6) probs.push(`"${el.tagName.toLowerCase()}": una tilde choca con la línea de arriba (sube line-height)`);
  }
  const circ = document.querySelector('.circle');
  if (circ) {
    const c = circ.getBoundingClientRect();
    for (const bx of boxes) {
      const w = Math.min(bx.r, c.right) - Math.max(bx.l, c.left), h = Math.min(bx.b, c.bottom) - Math.max(bx.t, c.top);
      if (w > 1 && h > 1) probs.push(`"${bx.name}" toca el círculo de contexto (acorta el texto)`);
    }
  }
  const texts = {};
  for (const el of els) {
    const cs = getComputedStyle(el), fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
    const t = cs.textTransform === 'uppercase' ? el.innerText.toUpperCase() : el.innerText;
    texts[fam] = (texts[fam] || '') + t;
  }
  for (const fam of Object.keys(texts)) {  // only families this slide actually uses get loaded
    const face = [...document.fonts].find(f => f.family.replace(/["']/g, '') === fam);
    if (!face || face.status !== 'loaded')
      probs.push(`la fuente "${fam}" no cargó (se vería con otra); instala las fuentes del kit`);
  }
  const items = boxes.map((bx, i) => ({name: bx.name, l: bx.l, t: bx.t, r: bx.r, b: bx.b,
    color: getComputedStyle(els[i]).color}));
  return {probs, texts, items};
}"""

MIN_CONTRAST = 3.0  # WCAG minimum for large text; every carousel text is large on a phone
CLEAN_CSS = "*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}"


# Runs in the page (no Pillow needed): text color vs the median pixel behind each text box.
CONTRAST_JS = """async ({png, items, min}) => {
  // a Blob, not a data: URL: the slide page blocks every non-file request
  const img = await createImageBitmap(new Blob([Uint8Array.from(atob(png), c => c.charCodeAt(0))], {type: 'image/png'}));
  const cv = document.createElement('canvas');
  cv.width = img.width; cv.height = img.height;
  const ctx = cv.getContext('2d', {willReadFrequently: true});
  ctx.drawImage(img, 0, 0);
  const lum = (r, g, b) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
    .reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
  const out = [];
  for (const it of items) {
    const m = it.color.match(/rgba?\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)(?:,\\s*([\\d.]+))?/);
    const x = Math.max(0, Math.floor(it.l)), y = Math.max(0, Math.floor(it.t));
    const w = Math.min(img.width, Math.ceil(it.r)) - x, h = Math.min(img.height, Math.ceil(it.b)) - y;
    if (!m || w < 1 || h < 1 || parseFloat(m[4] ?? 1) < 0.5) continue;
    const d = ctx.getImageData(x, y, w, h).data, ls = [];
    for (let i = 0; i < d.length; i += 4 * 7) ls.push(lum(d[i], d[i + 1], d[i + 2]));
    ls.sort((p, q) => p - q);
    const bg = ls[Math.floor(ls.length / 2)], fg = lum(+m[1], +m[2], +m[3]);
    const ratio = (Math.max(bg, fg) + 0.05) / (Math.min(bg, fg) + 0.05);
    if (ratio < min) out.push({name: it.name, ratio});
  }
  return out;
}"""


def contrast_problems(page, items: list[dict]) -> list[str]:
    """The slide is re-shot with its text hidden, so what is under the letters is exactly what was there."""
    import base64
    page.add_style_tag(content=CLEAN_CSS)
    png = base64.b64encode(page.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})).decode()
    bad = page.evaluate(CONTRAST_JS, {"png": png, "items": items, "min": MIN_CONTRAST})
    return [f'"{b["name"]}": el texto casi no se lee sobre el fondo (contraste {b["ratio"]:.1f}:1, mínimo {MIN_CONTRAST:g}:1)'
            for b in bad]


class QCError(RuntimeError):
    pass


def glyph_problems(texts: dict[str, str]) -> list[str]:
    """Characters the kit font file does not have (they'd render in a fallback font).
    ponytail: optional; skipped when fontTools is not installed."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return []
    try:
        import brotli  # noqa: F401  (fontTools needs it to read woff2)
        woff2 = True
    except ImportError:
        woff2 = False
    out = []
    for fam, text in texts.items():
        f = kit_font_file(fam)
        if not f or (f.suffix.lower() == ".woff2" and not woff2):
            continue
        try:
            cmap = TTFont(str(f), lazy=True).getBestCmap() or {}
        except Exception:  # woff2 without brotli, damaged file: the loaded-font check still runs
            continue
        missing = sorted({ch for ch in text if not ch.isspace() and ord(ch) not in cmap})
        if missing:
            out.append(f'la fuente "{fam}" no tiene: {" ".join(missing)}')
    return out


def render_png(html_paths: list[Path]) -> list[Path]:
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(kit_platform.cache_root() / "ms-playwright"))
    hint = ("install it with: python -m pip install playwright && "
            f"PLAYWRIGHT_BROWSERS_PATH=\"{os.environ['PLAYWRIGHT_BROWSERS_PATH']}\" python -m playwright install chromium "
            "(or use --html-only)")
    try:
        from playwright.sync_api import Error as PwError, sync_playwright
    except ImportError:
        raise SystemExit("carousel: Playwright is not installed; " + hint)
    pngs = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except PwError as e:
            raise SystemExit(f"carousel: Chromium not found ({str(e).splitlines()[0]}); " + hint)
        page = browser.new_page(viewport={"width": W, "height": H})
        # block every non-file request: slides are offline by construction
        page.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
        failed = {}
        for p in html_paths:
            page.goto(p.resolve().as_uri())
            page.wait_for_load_state("load")
            page.evaluate("document.fonts.ready.then(() => true)")
            qc = page.evaluate(QC_JS)
            probs = qc["probs"] + glyph_problems(qc["texts"])
            png = p.with_suffix(".png")
            if probs:
                failed[p.name] = probs
                png.unlink(missing_ok=True)
                continue
            page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": W, "height": H})
            probs = contrast_problems(page, qc["items"])
            if probs:
                failed[p.name] = probs
                png.unlink(missing_ok=True)
                continue
            pngs.append(png)
        browser.close()
    if failed:
        lines = [f"  {name}: {msg}" for name, ps in failed.items() for msg in dict.fromkeys(ps)]
        raise QCError("control de calidad: no se generó la imagen de estos slides\n" + "\n".join(lines))
    return pngs


def selftest() -> int:
    spec = json.loads((PRESETS / "demo-spec.json").read_text(encoding="utf-8"))
    spec["slides"][0]["subtitle"] = "<script>alert(1)</script> & más"
    b = brandmod.load_brand(None)
    with tempfile.TemporaryDirectory() as d:
        pages = build_html(spec, b, Path(d))
        paths = write_html(pages, Path(d) / "out")
        assert len(paths) == len(spec["slides"])
        assert "<script>" not in pages[0] and "&lt;script&gt;" in pages[0]
        assert all(b["colors"]["accent"] in p for p in pages)
        assert {s["type"] for s in spec["slides"]} == TYPES
    print(f"carousel selftest OK ({len(pages)} slides)")
    return 0


def brand_path(arg: str | None, project: Path) -> str | None:
    """--brand as a path, or as a bare name found in .kit-personal/brands/<name>.json (project, then cwd)."""
    if not arg or arg.endswith(".json") or Path(arg).is_file():
        return arg
    for root in (project, Path.cwd()):
        p = root / ".kit-personal" / "brands" / f"{arg}.json"
        if p.is_file():
            return str(p)
    raise SpecError(f"no encuentro la marca '{arg}' (busqué .kit-personal/brands/{arg}.json)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a branded carousel (HTML, optional PNG).")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--brand")
    ap.add_argument("--out")
    ap.add_argument("--project", default=".", help="folder the images must live in (default: cwd)")
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--strict", action="store_true", help="avisos = errores; exige .source.json y revisión de marca de agua")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.spec:
        ap.error("spec is required")
    spec_path, project = Path(a.spec), Path(a.project)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        brand = brandmod.load_brand(brand_path(a.brand, project))
        validate_spec(spec)
        auto, cut, notes = face_check(spec, project)
        pages = build_html(spec, brand, project, auto)
    except (OSError, ValueError) as e:
        print(f"carousel: {e}", file=sys.stderr)
        return 2
    strict = a.strict or spec.get("strict") is True
    advice = structure_warnings(spec["slides"], spec.get("goal"))
    files = image_files(spec, project)
    if strict:
        from check_watermark import problems as wm_problems
        advice += source_problems(files) + (wm_problems(files, spec_path.parent) if files else [])
    for w in advice:
        print(f"carousel: {'ERROR' if strict else 'aviso'}: {w} (ver presets/carousel/ESTRUCTURAS.md)", file=sys.stderr)
    for n in notes:
        print(f"carousel: nota: {n}", file=sys.stderr)
    if cut:
        print("carousel: ERROR: caras cortadas\n  " + "\n  ".join(cut), file=sys.stderr)
        return 2
    if strict and advice:
        return 2
    out = Path(a.out) if a.out else spec_path.parent / (spec_path.stem + "-carousel")
    paths = write_html(pages, out)
    if not a.html_only:
        try:
            paths = render_png(paths)
        except QCError as e:
            print(f"carousel: {e}", file=sys.stderr)
            return 3
    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
