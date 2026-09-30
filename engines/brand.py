# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Tolerant brand.json loader. Missing fields take defaults, unknown fields are
ignored, bad values fall back to defaults (with a warning), so an old or
hand-edited brand file never crashes an engine. Stdlib only.

Lookup order for load_brand(None): $KIT_BRAND (path) -> presets/brands/estudio-norte.json.
"""
from __future__ import annotations

import copy
import json
import os
import re
import sys
from pathlib import Path

KIT_ROOT = Path(os.environ.get("KIT_ROOT") or Path(__file__).resolve().parent.parent)
DEFAULT_BRAND = KIT_ROOT / "presets" / "brands" / "estudio-norte.json"
SCHEMA_VERSION = 1
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

DEFAULTS = {
    "schema_version": SCHEMA_VERSION,
    "name": "Estudio Norte",
    "handle": "",
    "language": "es",
    "voice": {"tone": "claro y directo", "person": "second", "avoid": []},
    "colors": {"background": "#0F1B2D", "surface": "#172A45", "text": "#F2EFE9",
               "muted": "#9AA8BC", "accent": "#F2B134", "accent_2": "#4FB3A9"},
    "fonts": {"display": "Bebas Neue", "body": "Inter", "serif": "Instrument Serif",
              "mono": "JetBrains Mono", "condensed": "Anton"},
    "logo_text": "ESTUDIO NORTE",
    "cta": "",
    "source_label": "Fuente:",
}


def _warn(msg: str) -> None:
    print(f"brand: {msg}", file=sys.stderr)


def _merge(defaults: dict, data: dict, where: str) -> dict:
    out = copy.deepcopy(defaults)
    for key, dv in defaults.items():
        if key not in data:
            continue
        v = data[key]
        if isinstance(dv, dict):
            if isinstance(v, dict):
                out[key] = _merge(dv, v, f"{where}{key}.")
            else:
                _warn(f"{where}{key} is not an object; using defaults")
        elif isinstance(dv, list):
            if isinstance(v, list) and all(isinstance(x, str) for x in v):
                out[key] = list(v)
            else:
                _warn(f"{where}{key} is not a list of strings; using default")
        elif isinstance(v, type(dv)):
            if where == "colors." and not _HEX.match(v):
                _warn(f"colors.{key}={v!r} is not #RRGGBB; using default")
            else:
                out[key] = v
        else:
            _warn(f"{where}{key} has the wrong type; using default")
    return out


def load_brand(path: str | os.PathLike | None = None) -> dict:
    """Return a complete brand dict. Never raises on content problems."""
    p = Path(path or os.environ.get("KIT_BRAND") or DEFAULT_BRAND)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        _warn(f"cannot read {p.name} ({e.__class__.__name__}); using defaults")
        data = {}
    if not isinstance(data, dict):
        data = {}
    if data.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        _warn(f"schema_version {data.get('schema_version')!r} unknown; reading tolerantly")
    brand = _merge(DEFAULTS, data, "")
    brand["schema_version"] = SCHEMA_VERSION
    return brand


def css_vars(brand: dict) -> str:
    """Brand tokens as CSS custom properties (for HTML engines)."""
    c, f = brand["colors"], brand["fonts"]
    lines = [f"  --brand-{k.replace('_', '-')}: {v};" for k, v in c.items()]
    safe = {k: re.sub(r"[^\w .-]", "", v) for k, v in f.items()}  # user text inside CSS
    lines += [f'  --font-{k}: "{v}", system-ui, sans-serif;' for k, v in safe.items()]
    return ":root {\n" + "\n".join(lines) + "\n}\n"


def save_brand(name: str, data: dict, replace: bool = False, project: Path | None = None) -> Path:
    """Validate strictly and write .kit-personal/brands/<name>.json. Raises ValueError with what to fix."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", name):
        raise ValueError("el nombre corto va en minúsculas, números y guiones (ej. mi-marca)")
    errs = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"schema_version tiene que ser {SCHEMA_VERSION}")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errs.append("falta name")
    for k, v in (data.get("colors") or {}).items():
        if k not in DEFAULTS["colors"] or not isinstance(v, str) or not _HEX.match(v):
            errs.append(f"colors.{k}: usá #RRGGBB y uno de {', '.join(DEFAULTS['colors'])}")
    if "person" in (data.get("voice") or {}) and data["voice"]["person"] not in ("first", "second", "third"):
        errs.append("voice.person: first, second o third")
    if errs:
        raise ValueError("; ".join(errs))
    out = (project or KIT_ROOT.parent) / ".kit-personal" / "brands" / f"{name}.json"
    if out.exists() and not replace:
        raise ValueError(f"{out.name} ya existe; confirmá con la persona y repetí con --replace")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["save"]:
        if len(a) < 3:
            sys.exit("uso: brand save <nombre-corto> <archivo.json | -> [--replace]")
        try:
            raw = sys.stdin.read() if a[2] == "-" else Path(a[2]).read_text(encoding="utf-8")
            print("Guardada en", save_brand(a[1], json.loads(raw), "--replace" in a))
        except (ValueError, OSError) as e:
            sys.exit(f"brand save: {e}")
    else:
        print(json.dumps(load_brand(a[0] if a else None), ensure_ascii=False, indent=2))
