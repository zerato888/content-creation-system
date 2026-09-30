# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Genera UNA imagen con la herramienta de imágenes que la persona ya tenga. Reemplaza los .sh de la bóveda.

    python3 .kit/launch.py imagegen "prompt" --dest out [--ref foto.png ...] [--provider auto|codex|agy]
                                   [--bg any|dark|light] [--retries 2]

Proveedores (auto = el primero que esté instalado):
  codex  ChatGPT/Codex CLI (paquete npm @openai/codex + `codex login`, cuenta ChatGPT). Ver la skill `imagen`.
  agy    Gemini por línea de comandos (headless): programa aparte que instala la persona; si no está, se salta.
  magnific / higgsfield: no tienen comando local; se usan desde sus conectores (ver la skill `imagen`).

Reglas que el motor impone siempre:
  - Las imágenes de referencia van escritas por ruta dentro del prompt; el agente las abre solo.
  - Nunca se agranda ni se reescala la imagen: el archivo que entrega el proveedor se mueve tal cual.
  - El prompt prohíbe dibujar con código (PIL, SVG, canvas...): solo la herramienta nativa de imágenes.
  - Si la imagen sale en blanco, casi negra/blanca o con un fondo distinto al pedido, se reintenta.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
STRICT = ("REGLA ESTRICTA: usá ÚNICAMENTE la herramienta nativa de generación de imágenes. "
          "PROHIBIDO dibujar o componer la imagen con código (PIL, matplotlib, SVG, canvas, HTML, ImageMagick) "
          "ni copiar una imagen existente como resultado. Si la herramienta nativa no está disponible, avisá y no generes nada.")
NO_UPSCALE = "No la agrandes ni la reescales después: entregá la resolución nativa tal cual sale."
RETRY_HINT = {"blank": "La versión anterior salió en blanco o plana: generá una imagen con contenido y detalle reales.",
              "dark": "La versión anterior tenía un fondo demasiado claro: el fondo tiene que ser oscuro.",
              "light": "La versión anterior tenía un fondo demasiado oscuro: el fondo tiene que ser claro.",
              "extreme": "La versión anterior salió casi toda negra o toda blanca: cuidá la exposición, con rango de tonos completo."}


def build_prompt(prompt: str, dest: Path, refs: list[Path], provider: str, extra: str = "") -> str:
    parts = [prompt.strip()]
    if refs:
        parts.append("Imágenes de referencia (abrí cada archivo, mirala y respetá su identidad/estilo):\n"
                     + "\n".join(f"- {r}" for r in refs))
    if extra:
        parts.append(extra)
    parts += [STRICT, NO_UPSCALE, f"Guardá el resultado como UN archivo PNG o JPG real en este directorio: {dest}"]
    body = "\n\n".join(parts)
    return "$imagegen " + body if provider == "codex" else body


def analyze(path: Path):
    """(media, desvío) de luminancia 0-255 sobre una miniatura; solo para juzgar, la imagen no se toca. None sin Pillow."""
    try:
        from PIL.Image import open as pil_open  # binario: el test de codificación no aplica
    except ImportError:
        return None
    with path.open("rb") as fh, pil_open(fh) as im:
        px = list(im.convert("L").resize((32, 32)).tobytes())
    m = sum(px) / len(px)
    return m, (sum((p - m) ** 2 for p in px) / len(px)) ** 0.5


def judge(stats, bg: str) -> str | None:
    if stats is None:
        return None
    mean, std = stats
    if std < 6:
        return "blank"
    if mean < 6 or mean > 249:
        return "extreme"
    if bg == "dark" and mean > 140:
        return "dark"
    if bg == "light" and mean < 115:
        return "light"
    return None


def stage_refs(refs: list[Path], stage: Path) -> list[Path]:
    """Copia las referencias a una carpeta sin espacios (algunos agentes no abren rutas con espacios)."""
    stage.mkdir(parents=True, exist_ok=True)
    out = []
    for i, r in enumerate(refs):
        t = stage / f"ref{i}_{''.join(c if c.isalnum() or c in '._-' else '_' for c in r.name)}"
        shutil.copy2(r, t)
        out.append(t)
    return out


def _images(d: Path) -> dict[Path, float]:
    return {p: p.stat().st_mtime for p in d.glob("*") if p.suffix.lower() in IMG_EXT} if d.is_dir() else {}


def run_codex(prompt: str, dest: Path, timeout: int = 900) -> list[Path]:
    exe = os.environ.get("IMAGEGEN_CODEX_BIN") or shutil.which("codex")
    if not exe:
        raise RuntimeError("no encuentro `codex`. Instalá el paquete npm @openai/codex y corré `codex login` (pasos en la skill `imagen`).")
    gen = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "generated_images"
    gen.mkdir(parents=True, exist_ok=True)
    before_dest, before_gen = set(_images(dest)), {p for p in gen.iterdir() if p.is_dir()}
    cmd = [exe, "exec", "--skip-git-repo-check", "--sandbox", "workspace-write"]
    if os.environ.get("IMAGEGEN_CODEX_MODEL"):
        cmd += ["-m", os.environ["IMAGEGEN_CODEX_MODEL"]]
    r = subprocess.run(cmd + [prompt], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    new = [p for p in _images(dest) if p not in before_dest]
    mine = [p for p in gen.iterdir() if p.is_dir() and p not in before_gen]
    if not new:  # el agente generó pero no copió: rescatar de su carpeta de trabajo
        for d in mine:
            for f in d.rglob("*"):
                if f.suffix.lower() in IMG_EXT:
                    t = dest / f.name
                    if not t.exists():
                        shutil.move(str(f), str(t))
                        new.append(t)
    if new:  # limpiar solo lo que esta corrida creó
        for d in mine:
            shutil.rmtree(d, ignore_errors=True)
    if not new:
        raise RuntimeError(f"codex terminó sin dejar imagen (código {r.returncode}). {(r.stderr or r.stdout)[-300:]}")
    return new


def run_agy(prompt: str, dest: Path, timeout: int = 900) -> list[Path]:
    exe = os.environ.get("IMAGEGEN_AGY_BIN") or shutil.which("agy")
    if not exe:
        raise RuntimeError("no encuentro `agy` (Gemini por línea de comandos). Es un programa aparte que instala la persona.")
    scratch = Path.home() / ".gemini" / "antigravity-cli" / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    before_dest, before_sc = set(_images(dest)), set(_images(scratch))
    cmd = [exe, "--print", prompt, "--output-format", "json", "--dangerously-skip-permissions"]
    if os.environ.get("IMAGEGEN_AGY_MODEL"):
        cmd += ["--model", os.environ["IMAGEGEN_AGY_MODEL"]]
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    new = [p for p in _images(dest) if p not in before_dest]
    if not new:
        for p in [p for p in _images(scratch) if p not in before_sc]:
            t = dest / p.name
            shutil.move(str(p), str(t))
            new.append(t)
    if not new:  # "SUCCESS" vacío = permiso denegado en silencio
        raise RuntimeError(f"agy no dejó ninguna imagen (código {r.returncode}); suele ser un permiso de escritura denegado.")
    return new


PROVIDERS = {"codex": run_codex, "agy": run_agy}
_BIN_ENV = {"codex": "IMAGEGEN_CODEX_BIN", "agy": "IMAGEGEN_AGY_BIN"}


def available(name: str) -> bool:
    return bool(os.environ.get(_BIN_ENV[name]) or shutil.which(name))


def generate(prompt, dest: Path, refs=(), provider="auto", bg="any", retries=2, providers=None, ready=None):
    """Devuelve la ruta de la imagen. Lanza RuntimeError si ningún proveedor lo logra."""
    providers = providers or PROVIDERS
    ready = ready or available
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    refs = [Path(r).expanduser().resolve() for r in refs]
    for r in refs:
        if not r.is_file():
            raise RuntimeError(f"la referencia no existe: {r}")
    order = list(providers) if provider == "auto" else [provider]
    errors = []
    for name in order:
        if name not in providers:
            raise RuntimeError(f"proveedor desconocido: {name} (usá codex, agy o auto)")
        if provider == "auto" and not ready(name):
            errors.append(f"{name}: no instalado")
            continue
        with tempfile.TemporaryDirectory(prefix="imagegen-") as tmp:
            use = stage_refs(refs, Path(tmp)) if name == "agy" else refs
            extra = ""
            for attempt in range(retries + 1):
                try:
                    files = providers[name](build_prompt(prompt, dest, use, name, extra), dest)
                except (RuntimeError, subprocess.TimeoutExpired) as e:
                    errors.append(f"{name}: {e}")
                    break
                out = max(files, key=lambda p: p.stat().st_mtime)
                bad = judge(analyze(out), bg)
                if not bad:
                    return out
                errors.append(f"{name} intento {attempt + 1}: {bad}")
                if attempt == retries:
                    return out  # último intento: se entrega igual y se avisa
                out.rename(out.with_name(f"descartada-{int(time.time() * 1000)}-{out.name}"))
                extra = RETRY_HINT[bad]
    raise RuntimeError("no se pudo generar la imagen. " + " | ".join(errors))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("prompt")
    ap.add_argument("--dest", default="imagen-out")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--provider", default="auto", choices=["auto", "codex", "agy", "magnific", "higgsfield"])
    ap.add_argument("--bg", default="any", choices=["any", "dark", "light"])
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args(argv)
    if a.provider in ("magnific", "higgsfield"):
        print(f"{a.provider} no tiene comando local: usalo desde su conector (mirá la skill `imagen`).", file=sys.stderr)
        return 3
    try:
        out = generate(a.prompt, Path(a.dest), a.ref, a.provider, a.bg, a.retries)
    except RuntimeError as e:
        print(f"imagegen: {e}", file=sys.stderr)
        return 1
    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
