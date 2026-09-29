# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Reel de contenido armado desde un guion: voz + imágenes + tu marca (plantilla reel@9).

    python .kit/launch.py reel9 check  <reel> [--batch <otro-reel> ...]      # control de datos, no arma nada
    python .kit/launch.py reel9 build  <reel> --brand <ficha.json> [--batch ...] [--skip-layout]
    python .kit/launch.py reel9 layout <reel>                                # control de maqueta, cuadro por cuadro
    python .kit/launch.py reel9 mix    <reel> --voice voz.mp3 [--music musica.mp3] [--music-db -17]
    python .kit/launch.py reel9 render <reel> [--out reel.mp4] [--fps 30]
    python .kit/launch.py reel9 fetch-gsap --yes                             # baja la librería de animación (con permiso)

<reel> es una carpeta con data.json (contrato: skills/reel-contenido/SKILL.md), vo.txt (el texto de la voz),
el audio (audio.src) y las imágenes DENTRO de la carpeta. La voz la trae la persona: su grabación o la que
generó con la herramienta que use; el kit no genera voces.

build falla cerrado, en este orden: control de datos (reel9_gate), reglas propias de la plantilla (subtítulo,
línea de tema, un solo resaltado, tarjetas de a una) y control de maqueta sobre la página armada. Si algo
falla, no deja index.html. Sale <reel>/index.html + gsap.min.js + fonts/ (solo las de la marca) y
.reel-build.json con los hashes. Las tipografías se resuelven con kit_platform (solo las libres del kit).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand as kit_brand  # noqa: E402
import kit_platform  # noqa: E402
import reel9_gate  # noqa: E402

KIT = kit_platform.KIT_ROOT
PRESETS = KIT / "presets" / "reel"
TEMPLATE = PRESETS / "template.html"
GSAP_LOCK = PRESETS / "gsap.lock.json"
FONTS_LOCK = KIT / "presets" / "captions" / "fonts.lock.json"
STAMP = ".reel-build.json"
CASES = {"uppercase", "none"}
MARKERS = ("/*__BRAND_TOKENS__*/", "/*__BRAND__*/", "/*__HOOK__*/", "/*__TEXT_FIT__*/",
           "/*__BRAND_ID__*/", "/*__FORMAT_STAMP__*/", "/*__CARDS_BOTTOM__*/", "/*__REEL_DATA__*/")
FAMILY = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ]{0,40}")
LOGO_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

TEXT_FIT = """function fitTextBlocks(configs) {
  (configs || []).forEach(function (cfg) {
    var minFont = cfg.minFontPx || 24, step = cfg.stepPx || 2, maxH = cfg.maxHeight;
    document.querySelectorAll(cfg.selector).forEach(function (el) {
      var guard = 200;
      while (el.scrollHeight > maxH && guard-- > 0) {
        var current = parseFloat(window.getComputedStyle(el).fontSize);
        if (!(current > minFont)) break;
        el.style.fontSize = (current - step) + "px";
      }
    });
  });
}"""


class ReelBuildError(ValueError):
    pass


def _need(ok, msg):
    if not ok:
        raise ReelBuildError(msg)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _js(value) -> str:
    """JSON seguro dentro de <script>: un '</script>' en un texto no corta el bloque."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


# ---------- ficha de marca ----------

def kit_families() -> set[str]:
    """Familias libres (OFL) que el kit sabe instalar para video."""
    lock = json.loads(FONTS_LOCK.read_text(encoding="utf-8"))
    return {f["family"] for f in lock["fonts"] if f.get("use") == "captions"}


def load_brand(path) -> tuple[dict, dict, Path]:
    """(ficha completa del kit, bloque opcional 'reel', carpeta de la ficha)."""
    path = Path(path)
    _need(path.is_file(), f"no encuentro la ficha de marca {path}")
    b = kit_brand.load_brand(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    extra = raw.get("reel") if isinstance(raw, dict) and isinstance(raw.get("reel"), dict) else {}
    return b, extra, path.parent


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def mark_ink(accent: str, dark: str) -> str:
    """Letra del marcador: blanca u oscura, la de mayor contraste sobre el acento (WCAG)."""
    a = _lum(accent)
    white = 1.05 / (a + 0.05)
    black = (max(a, _lum(dark)) + 0.05) / (min(a, _lum(dark)) + 0.05)
    return "#ffffff" if white >= black else dark


def resolve_fonts(brand: dict, dest: Path | None = None) -> dict[str, tuple[str, Path]]:
    """{rol: (familia, archivo)} para display, body y mono, con kit_platform. Solo tipografías libres del kit."""
    allowed = kit_families()
    out = {}
    for role in ("display", "body", "mono"):
        fam = brand["fonts"].get(role) or brand["fonts"]["display"]
        _need(FAMILY.fullmatch(fam) is not None, f"fonts.{role} no es un nombre de fuente seguro: {fam!r}")
        _need(fam in allowed, f"la tipografía {fam!r} (fonts.{role}) no es una de las libres del kit "
                              f"({', '.join(sorted(allowed))}): elegí una de esas")
        found = kit_platform.find_font_file(fam)
        _need(found, f"no encuentro el archivo de {fam!r}: instalá las tipografías del kit "
                     "(installer con --fonts) o poné KIT_FONTS_DIR")
        out[role] = (fam, Path(found))
    return out


def brand_css(brand: dict, extra: dict, fonts: dict) -> tuple[str, list[Path]]:
    """(@font-face + variables de marca, archivos de fuente usados)."""
    p = brand["colors"]
    faces, files = [], []
    for fam, file in fonts.values():
        if file in files:
            continue
        files.append(file)
        # rango 100-900: el navegador usa la cara del archivo tal cual, sin inventar negritas
        faces.append(f'@font-face {{ font-family: "{fam}"; src: url("fonts/{file.name}"); '
                     f'font-weight: 100 900; font-display: block; }}')
    weight, case = extra.get("display_weight", 700), extra.get("display_case", "none")
    _need(type(weight) is int and 100 <= weight <= 900 and weight % 100 == 0, f"reel.display_weight debe ser 100-900: {weight!r}")
    _need(case in CASES, f"reel.display_case debe ser {sorted(CASES)}: {case!r}")
    leading, em = extra.get("display_leading"), extra.get("emphasis_weight")
    _need(leading is None or (type(leading) is int and 100 <= leading <= 160), f"reel.display_leading debe ser 100-160: {leading!r}")
    _need(em is None or (type(em) is int and 100 <= em <= 900 and em % 100 == 0), f"reel.emphasis_weight debe ser 100-900: {em!r}")
    title_lh = leading / 100 if leading else 1.1
    card_lh = max(1.24, leading / 100) if leading else 1.24
    title_em, card_em = (em, em) if em else (weight, 400)
    stack = lambda fam: f'"{fam}", system-ui, sans-serif'  # noqa: E731
    css = "\n    ".join(faces) + f"""
    [data-composition-id="reel"] {{
      --bg: {p["background"]}; --accent: {p["accent"]}; --text: {p["text"]}; --muted: {p["muted"]};
      --font-display: {stack(fonts["display"][0])}; --font-body: {stack(fonts["body"][0])}; --font-mono: {stack(fonts["mono"][0])};
      --display-weight: {weight}; --display-case: {case}; --mark-ink: {mark_ink(p["accent"], p["background"])};
      --title-lh: {title_lh}; --card-lh: {card_lh}; --title-em-weight: {title_em}; --card-em-weight: {card_em};
    }}"""
    return css, files


def brand_tokens(brand: dict, extra: dict, logo: str | None) -> dict:
    name = extra.get("name") or brand.get("logo_text") or brand["name"]
    return {"name": name, "tag": extra.get("tag") or name,
            "cta": brand.get("cta") or extra.get("cta") or brand["name"],
            "cta_sub": brand.get("handle", ""), "stat_kicker": extra.get("stat_kicker") or "DATO",
            "logo": logo, "logo_has_name": bool(logo) and extra.get("logo_has_name") is True}


# ---------- reglas propias de la plantilla ----------

def _words_of(html: str) -> list[str]:
    return re.findall(r"[a-záéíóúñü0-9$]+", re.sub(r"<[^>]+>", " ", str(html or "")).lower())


def subtitle_errors(title: str, subtitle: str) -> list[str]:
    """El subtítulo acompaña al hook con contexto o promesa; no puede faltar ni repetir el título.
    La tensión y la emoción no se miden acá: las juzga quien escribe y quien revisa el guion."""
    sub = _words_of(subtitle)
    if len(sub) < 4:
        return ["el subtítulo falta o es muy corto (mínimo 4 palabras): tiene que prometer el cierre o sumar contexto"]
    tit = {w for w in _words_of(title) if len(w) > 2}
    long_sub = [w for w in sub if len(w) > 2]
    if long_sub and sum(w in tit for w in long_sub) / len(long_sub) > 0.5:
        return ["el subtítulo repite el título; tiene que sumar algo nuevo (promesa o contexto)"]
    return []


def highlight_used(title: str) -> set[str]:
    """Tipos de resaltado del título: 'mk' (marcador) y 'hl' (color; el hl-box viejo cuenta como color)."""
    classes = set(re.findall(r'class="([^"]+)"', title or ""))
    got = set()
    if "mk" in classes:
        got.add("mk")
    if classes & {"hl", "hl-box", "hl-text"}:
        got.add("hl")
    return got


def reel_rules(data: dict) -> list[str]:
    errs = []
    if any(c.get("type") == "ticker" for c in data.get("cards", [])):
        errs.append("esta plantilla no tiene sello de abajo: sacá las tarjetas 'ticker' del data.json")
    errs += subtitle_errors(data.get("title", ""), data.get("subtitle", ""))
    if not str(data.get("kicker") or "").strip():
        errs.append("falta 'kicker' en el data.json (línea de tema arriba del título, ej. 'FINANZAS · AHORRO')")
    if len(highlight_used(data.get("title", ""))) > 1:
        errs.append("el título mezcla marcador y color: cada video usa un solo resaltado")
    if data.get("hook_circle") is not None:
        errs.append("el círculo de contexto es solo para carruseles; quitá hook_circle de data.json")
    return errs


def localize_assets(reel: Path) -> int:
    """Copia a assets/_ext/ toda imagen que el data.json apunte fuera del reel y reescribe la ruta.
    El render solo sirve archivos de la carpeta del reel: una ruta '../..' se dibuja en negro."""
    data_path = reel / "data.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    moved = 0
    items = data.get("visual_slots", []) + [c for c in data.get("cards", []) if c.get("type") == "dossier" and c.get("asset")]
    for slot in items:
        if not slot.get("asset"):
            continue
        src = (reel / slot["asset"]).resolve()
        if reel in src.parents or not src.is_file():
            continue
        dest = reel / "assets" / "_ext" / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        slot["asset"] = dest.relative_to(reel).as_posix()
        moved += 1
    if moved:
        data_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return moved


# ---------- gsap (con permiso) ----------

def gsap_path(explicit=None) -> Path:
    """gsap.min.js: --gsap, $KIT_GSAP o la copia verificada en la caché del kit."""
    for cand in (explicit, __import__("os").environ.get("KIT_GSAP")):
        if cand:
            p = Path(cand)
            _need(p.is_file(), f"no encuentro gsap en {p}")
            return p
    lock = json.loads(GSAP_LOCK.read_text(encoding="utf-8"))
    p = kit_platform.cache_root() / "gsap" / lock["file"]
    _need(p.is_file() and _sha(p.read_bytes()) == lock["sha256"],
          "falta la librería de animación (GSAP). Bajala con permiso: python .kit/launch.py reel9 fetch-gsap --yes")
    return p


def fetch_gsap() -> Path:
    lock = json.loads(GSAP_LOCK.read_text(encoding="utf-8"))
    dest = kit_platform.cache_root() / "gsap" / lock["file"]
    return kit_platform.fetch_verified(lock["url"], lock["sha256"], lock["size"], dest)


# ---------- armado ----------

def build(brand_path, reel_dir, batch_dirs=(), standard=None, gsap=None, skip_layout=False) -> Path:
    reel = reel9_gate.resolve_reel_dir(Path(reel_dir)).resolve()
    out = reel / "index.html"
    out.unlink(missing_ok=True)  # sin index.html viejo no queda nada renderizable si algo falla
    std = reel9_gate.load_standard(standard)
    brand, extra, base = load_brand(brand_path)
    fonts = resolve_fonts(brand)
    gsap_file = gsap_path(gsap)
    _need((reel / "data.json").is_file(), f"falta data.json en {reel}")
    localize_assets(reel)
    errors = reel9_gate.check(reel, batch_dirs, std)
    if errors:
        raise ReelBuildError("el control de datos rechazó el reel:\n  - " + "\n  - ".join(errors))

    data_bytes = (reel / "data.json").read_bytes()
    data = json.loads(data_bytes)
    errors = reel_rules(data)
    if errors:
        raise ReelBuildError("la plantilla rechazó el reel:\n  - " + "\n  - ".join(errors))
    segs = std["hook"]["segments"]
    hook = {"segments": segs, "end": segs[-1]["end"], "tolerance_s": std["hook"]["tolerance_s"]}

    css, font_files = brand_css(brand, extra, fonts)
    logo = None
    if extra.get("logo"):
        src = (base / extra["logo"]).resolve()
        _need(src.is_file() and src.suffix.lower() in LOGO_EXT, f"reel.logo no es una imagen ({sorted(LOGO_EXT)}): {extra['logo']!r}")
        logo = f"brand-logo{src.suffix.lower()}"
        shutil.copyfile(src, reel / logo)
    intro = next(c for c in data["cards"] if c.get("type") == "intro")
    hook_js = {"segments": hook["segments"], "end": hook["end"], "title_end": intro["end"]}
    template = TEMPLATE.read_bytes()
    html = template.decode("utf-8")
    bottom = std["cards"]["bottom_px"]
    _need(type(bottom) is int and 0 < bottom <= 1920, f"cards.bottom_px inválido: {bottom!r}")
    for marker, value in (("/*__BRAND_TOKENS__*/", css), ("/*__BRAND__*/", _js(brand_tokens(brand, extra, logo))),
                          ("/*__HOOK__*/", _js(hook_js)), ("/*__TEXT_FIT__*/", TEXT_FIT),
                          ("/*__BRAND_ID__*/", re.sub(r"[^a-z0-9]+", "-", brand["name"].lower()).strip("-") or "marca"),
                          ("/*__FORMAT_STAMP__*/", f"reel@9 {_sha(template)[:12]}")):
        _need(html.count(marker) == 1, f"la plantilla no tiene el marcador {marker} una sola vez")
        html = html.replace(marker, value)
    html = html.replace("/*__CARDS_BOTTOM__*/", str(bottom))

    cards, pairs, errors = reel9_gate.pair_dossiers(data["cards"], data.get("script_blocks"))
    _need(not errors, "el retrato necesita tarjeta:\n  - " + "\n  - ".join(errors))
    data["cards"] = cards
    schedule = reel9_gate.card_schedule(cards, std, paired_dossiers=True)
    outro = next((c["start"] for c in cards if c["type"] == "outro"), None)
    errors = reel9_gate.sequence_errors(schedule, std, outro)
    _need(not errors, "las tarjetas de a una no entran:\n  - " + "\n  - ".join(errors))
    for s in schedule:
        card = cards[s["index"]]
        card["anim"] = {k: s[k] for k in ("in", "in_end", "out", "out_end")}
    by_index = {s["index"]: s for s in schedule}
    for d, k in pairs:
        cards[d]["anim"] = {x: by_index[k][x] for x in ("in", "in_end", "out", "out_end")}
        cards[d]["start"], cards[d]["end"] = by_index[k]["in"], round(by_index[k]["out_end"] - 0.06, 3)
        cards[d]["paired_with"] = k
    data["card_schedule"] = schedule

    audio = data["audio"]
    _need(MARKERS[-1] in html and "__REEL_DURATION__" in html and "__REEL_AUDIO_SRC__" in html, "la plantilla perdió sus marcadores de datos")
    html = html.replace(MARKERS[-1], _js(data)).replace("__REEL_DURATION__", str(audio["duration"]))
    html = html.replace("__REEL_AUDIO_SRC__", str(audio["src"]).replace('"', "&quot;"))

    shutil.copyfile(gsap_file, reel / "gsap.min.js")
    (reel / "fonts").mkdir(exist_ok=True)
    for f in font_files:
        shutil.copyfile(f, reel / "fonts" / f.name)
    out.write_text(html, encoding="utf-8")
    if not skip_layout:  # control de maqueta sobre la página armada, antes de cualquier exportación
        import reel9_layout
        try:
            errors = reel9_layout.check(reel, std)
        except reel9_layout.BrowserMissing as exc:
            out.unlink(missing_ok=True)
            raise ReelBuildError(f"no se pudo correr el control de maqueta: {exc}. "
                                 "Con --skip-layout se arma igual, pero sin ese control.") from exc
        if errors:
            out.unlink(missing_ok=True)
            raise ReelBuildError("el control de maqueta rechazó el reel:\n  - " + "\n  - ".join(errors))
    (reel / STAMP).write_text(json.dumps({
        "format": "reel@9", "card_schedule": schedule, "layout_checked": not skip_layout,
        "sha256": {"template": _sha(template), "brand": _sha(Path(brand_path).read_bytes()),
                   "data": _sha(data_bytes), "index_html": _sha(html.encode("utf-8"))},
    }, indent=2) + "\n", encoding="utf-8")
    return out


# ---------- mezcla de audio ----------

def mix_args(voice: Path, music: Path | None, out: Path, duration: float, music_db: float) -> list[str]:
    """Voz a -16 LUFS; música a nivel FIJO (relativo a la voz), en bucle si es corta, sin subidas ni bajadas."""
    ff = kit_platform.ffmpeg()
    if music is None:
        return [ff, "-v", "error", "-y", "-i", str(voice), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-t", f"{duration:.3f}", "-c:a", "aac", "-b:a", "192k", str(out)]
    fade = max(0.0, duration - 1.0)
    graph = (f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[v];"
             f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,"
             f"volume={music_db}dB,afade=t=out:st={fade:.3f}:d=1[m];"
             f"[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]")
    return [ff, "-v", "error", "-y", "-i", str(voice), "-stream_loop", "-1", "-i", str(music),
            "-filter_complex", graph, "-map", "[a]", "-t", f"{duration:.3f}", "-c:a", "aac", "-b:a", "192k", str(out)]


def mix(reel_dir, voice, music=None, music_db=-17.0) -> Path:
    """Escribe <reel>/audio_mix.m4a y deja audio.src/duration/music listos para copiar en el data.json."""
    _need(music_db <= -6, "music_db tiene que ser -6 o menos: la música nunca tapa la voz")
    reel = reel9_gate.resolve_reel_dir(Path(reel_dir)).resolve()
    dur = reel9_gate.audio_duration(Path(voice))
    _need(dur, "no se pudo medir la voz (¿está ffprobe instalado?)")
    out = reel / "audio_mix.m4a"
    subprocess.run(mix_args(Path(voice), Path(music) if music else None, out, dur, music_db), check=True)
    return out


# ---------- render ----------

def render(reel_dir, out=None, fps=30) -> Path:
    """Mp4 1080x1920: fotograma a fotograma desde la página armada (misma línea de tiempo que revisó el
    control de maqueta) + el audio del reel. Tarda unos minutos: es un fotograma por captura."""
    import reel9_layout
    reel = reel9_gate.resolve_reel_dir(Path(reel_dir)).resolve()
    data = json.loads((reel / "data.json").read_text(encoding="utf-8"))
    audio = reel / data["audio"]["src"]
    _need((reel / "index.html").is_file(), "falta index.html: armá el reel primero (reel9 build)")
    _need(audio.is_file(), f"falta el audio {audio.name}")
    out = Path(out) if out else reel / "reel.mp4"
    dur = float(data["audio"]["duration"])
    frames = round(dur * fps)
    cmd = [kit_platform.ffmpeg(), "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        with reel9_layout.open_reel(reel) as page:
            page.evaluate("() => { window.__timelines.reel.pause(); }")  # sin devolver la línea de tiempo: no se puede serializar
            for f in range(frames):
                page.evaluate("t => { window.__timelines.reel.seek(t, false); }", f / fps)
                proc.stdin.write(page.screenshot(type="jpeg", quality=95))
        proc.stdin.close()
    except BaseException:
        proc.kill()
        raise
    _need(proc.wait() == 0, "ffmpeg no pudo armar el mp4")
    return out


# ---------- CLI ----------

def selftest() -> int:
    """Chequeo sin conexión ni medios: reglas de subtítulo y resaltado, tarjetas de a una, mezcla."""
    std = reel9_gate.load_standard()
    assert subtitle_errors("Título del hook", "corto") and not subtitle_errors("Título del hook", "Lo que nadie te cuenta del final")
    assert highlight_used('<span class="mk">a</span><span class="hl">b</span>') == {"mk", "hl"}
    assert mark_ink("#F2A93B", "#10202B") == "#10202B"
    sched = reel9_gate.card_schedule([{"type": "lower-third", "start": 5, "end": 8, "html": "dos palabras"}], std)
    assert sched and sched[0]["hold"] >= sched[0]["read"] and not reel9_gate.sequence_errors(sched, std, 8.5)
    graph = mix_args(Path("v.wav"), Path("m.wav"), Path("o.m4a"), 45.0, -17.0)
    assert "volume=-17.0dB" in graph[graph.index("-filter_complex") + 1]
    assert TEMPLATE.is_file() and STANDARD_OK(std)
    return 5


def STANDARD_OK(std) -> bool:  # noqa: N802
    return std["hook"]["segments"][0]["role"] == "hook_image" and std["cards"]["bottom_px"] <= 1920


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--selftest"]:
        print(f"reel9 selftest OK ({selftest()} casos)")
        return 0
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "build", "layout", "mix", "render"):
        p = sub.add_parser(name)
        p.add_argument("reel_dir", type=Path)
        if name in ("check", "build", "layout"):
            p.add_argument("--standard", type=Path)
        if name in ("check", "build"):
            p.add_argument("--batch", type=Path, nargs="*", default=[])
        if name == "build":
            p.add_argument("--brand", type=Path, required=True)
            p.add_argument("--gsap", type=Path)
            p.add_argument("--skip-layout", action="store_true")
        if name == "mix":
            p.add_argument("--voice", type=Path, required=True)
            p.add_argument("--music", type=Path)
            p.add_argument("--music-db", type=float, default=-17.0)
        if name == "render":
            p.add_argument("--out", type=Path)
            p.add_argument("--fps", type=int, default=30)
    g = sub.add_parser("fetch-gsap")
    g.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "fetch-gsap":
            lock = json.loads(GSAP_LOCK.read_text(encoding="utf-8"))
            if not a.yes:
                print(f"Voy a bajar GSAP ({lock['size'] // 1024} KB) de {lock['url']}\n"
                      f"a {kit_platform.cache_root() / 'gsap'} (licencia: {lock['license']}). Repetí con --yes para aceptar.")
                return 2
            print(f"GSAP listo: {fetch_gsap()}")
        elif a.cmd == "check":
            errors = reel9_gate.check(a.reel_dir, a.batch, a.standard)
            reel9_gate.report(errors, a.reel_dir)
            return 1 if errors else 0
        elif a.cmd == "layout":
            import reel9_layout
            return reel9_layout.main([str(a.reel_dir)])
        elif a.cmd == "build":
            out = build(a.brand, a.reel_dir, a.batch, a.standard, a.gsap, a.skip_layout)
            print(f"REEL BUILD OK: {out}")
        elif a.cmd == "mix":
            print(f"MEZCLA OK: {mix(a.reel_dir, a.voice, a.music, a.music_db)}")
        elif a.cmd == "render":
            print(f"RENDER OK: {render(a.reel_dir, a.out, a.fps)}")
    except (ReelBuildError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"REEL9 — {a.cmd} no terminó:\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
