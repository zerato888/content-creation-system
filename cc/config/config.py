# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Load `.kit-personal/cc.config.json` tolerantly: never crash, never trust.

Missing fields take defaults.json. An invalid field falls back to its default,
an invalid list item (a brand, a habit, a payment) is dropped, and every
fallback is recorded in cfg["_warnings"] so the UI can say what it ignored.
All personal lists default to empty: nothing about any real person ships here.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "cc.config.schema.json").read_text(encoding="utf-8"))
DEFAULTS = json.loads((HERE / "defaults.json").read_text(encoding="utf-8"))
CONFIG_REL = Path(".kit-personal") / "cc.config.json"
MODULES = tuple(DEFAULTS["toggles"])            # vida, agentic, produccion_avanzada, ...
VIDA_ECOSYSTEM, VIDA_PREFIX = "vida", "VIDA"    # built-in task ecosystem for Vida Personal
BRAND_DEFAULTS = {"accent": "#7C5CFF", "logo": None, "kind": "brand",
                  "metrics": {"provider": "none", "account": {}}}
LIST_ITEMS = {"habits", "fixed_payments", "recurring_income", "milestones"}
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
          "integer": int, "number": (int, float)}


def validate(inst, schema: dict, path: str = "$") -> list[str]:
    """Same JSON Schema subset as tools/guard.py (which is not installed with the kit)."""
    if "$ref" in schema:
        return validate(inst, SCHEMA["$defs"][schema["$ref"].rsplit("/", 1)[-1]], path)
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(isinstance(inst, _TYPES[t]) and (t == "boolean" or not isinstance(inst, bool))
                   for t in ts):
            return [f"{path}: expected {'/'.join(ts)}"]
    errs = []
    if "enum" in schema and not any(inst == e and type(inst) is type(e) for e in schema["enum"]):
        errs.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errs.append(f"{path}: invalid format")
        if len(inst) < schema.get("minLength", 0):
            errs.append(f"{path}: too short")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            errs.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and inst > schema["maximum"]:
            errs.append(f"{path}: above {schema['maximum']}")
    if isinstance(inst, list):
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in inst}) != len(inst):
            errs.append(f"{path}: items must be unique")
        for i, x in enumerate(inst):
            errs += validate(x, schema.get("items", {}), f"{path}[{i}]")
    if isinstance(inst, dict):
        errs += [f"{path}: missing '{k}'" for k in schema.get("required", []) if k not in inst]
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unknown field '{k}'")
    return errs


def _items(raw, schema: dict, path: str, warnings: list[str]) -> list[dict]:
    """Keep the valid items of a list, drop the rest (with a warning), unique by id."""
    if not isinstance(raw, list):
        warnings.append(f"{path}: expected a list; using default")
        return []
    out, seen = [], set()
    for i, item in enumerate(raw):
        errs = validate(item, schema, f"{path}[{i}]")
        if not errs and item["id"] in seen:
            errs = [f"{path}[{i}]: duplicate id '{item['id']}'"]
        if errs:
            warnings.extend(errs)
            continue
        seen.add(item["id"])
        out.append(copy.deepcopy(item))
    return out


def _brands(raw, warnings: list[str]) -> list[dict]:
    out, prefixes = [], {VIDA_PREFIX}
    for i, b in enumerate(_items(raw, SCHEMA["$defs"]["brand"], "$.brands", warnings)):
        if b["id"] == VIDA_ECOSYSTEM or b["task_prefix"] in prefixes:
            warnings.append(f"$.brands[{i}]: id or task_prefix already in use; brand ignored")
            continue
        prefixes.add(b["task_prefix"])
        metrics = {**BRAND_DEFAULTS["metrics"], **b.get("metrics", {})}
        out.append({**copy.deepcopy(BRAND_DEFAULTS), **b, "metrics": metrics})
    return out


def _clamp(section: dict, key: str, low, high, warnings: list[str], nullable=False):
    value = section[key]
    if value is None and nullable:
        return
    if not (low <= value <= high):
        warnings.append(f"$.{_section_of(key)}.{key}: out of range; using default")
        section[key] = copy.deepcopy(DEFAULTS[_section_of(key)][key])


def _section_of(key: str) -> str:
    return next(s for s, v in DEFAULTS.items() if isinstance(v, dict) and key in v)


def _payment_days(raw, path: str, warnings: list[str]):
    """A bad `day` (-1, 40, "5") never drops the payment nor breaks the task list: it becomes null."""
    if not isinstance(raw, list):
        return raw
    out = []
    for i, item in enumerate(raw):
        if isinstance(item, dict) and item.get("day") is not None:
            d = item["day"]
            if isinstance(d, bool) or not isinstance(d, int) or not 1 <= d <= 31:
                warnings.append(f"{path}[{i}].day: not a day of the month (1-31); ignored")
                item = {**item, "day": None}
        out.append(item)
    return out


def normalize(raw) -> dict:
    """Defaults + every valid field of `raw`. Pure: no I/O."""
    warnings: list[str] = []
    cfg = copy.deepcopy(DEFAULTS)
    if not isinstance(raw, dict):
        warnings.append("$: config is not a JSON object; using defaults")
        raw = {}
    props = SCHEMA["properties"]
    for key, value in raw.items():
        if key == "schema_version":
            continue
        if key not in props:
            warnings.append(f"$: unknown field '{key}' ignored")
        elif key == "brands":
            cfg["brands"] = _brands(value, warnings)
        elif not isinstance(value, dict):
            warnings.append(f"$.{key}: expected an object; using default")
        else:
            sub = props[key]["properties"]
            for k, v in value.items():
                path = f"$.{key}.{k}"
                if k not in sub:
                    warnings.append(f"{path}: unknown field ignored")
                elif k in LIST_ITEMS:
                    if k == "fixed_payments":
                        v = _payment_days(v, path, warnings)
                    cfg[key][k] = _items(v, sub[k]["items"], path, warnings)
                elif errs := validate(v, sub[k], path):
                    warnings.extend(errs)
                else:
                    cfg[key][k] = copy.deepcopy(v)
    for habit in cfg["vida"]["habits"]:
        habit.setdefault("weekdays", list(range(7)))
    for p in cfg["vida"]["fixed_payments"]:
        p.setdefault("day", None)
    _clamp(cfg["creator"], "weekly_goal", 1, 21, warnings)
    _clamp(cfg["creator"], "grace_days", 0, 6, warnings)
    _clamp(cfg["vida"], "fx_rate", 1e-9, 1e12, warnings, nullable=True)
    _clamp(cfg["vida"], "income_goal", 0, 1e15, warnings, nullable=True)
    if _tz(cfg["locale"]["timezone"]) is None:
        warnings.append("$.locale.timezone: unknown on this machine; using UTC")
        cfg["locale"]["timezone"] = "UTC"
    cfg["_warnings"] = warnings
    return cfg


def load(target) -> dict:
    """Read TARGET/.kit-personal/cc.config.json. Missing or unreadable file = defaults."""
    path = Path(target) / CONFIG_REL
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raw = {}
    except (OSError, ValueError, UnicodeDecodeError):
        cfg = normalize({})
        cfg["_warnings"].insert(0, "cc.config.json is not valid JSON; using defaults")
        return cfg
    return normalize(raw)


def _tz(name: str):
    if name == "UTC":
        return dt.timezone.utc
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:  # unknown name, or no tz database (Windows without tzdata)
        return None


def now(cfg: dict) -> dt.datetime:
    return dt.datetime.now(_tz(cfg["locale"]["timezone"]) or dt.timezone.utc)


def today(cfg: dict) -> dt.date:
    return now(cfg).date()


def enabled(cfg: dict, module: str) -> bool:
    """`core` is always on; every other module follows its toggle."""
    return module == "core" or bool(cfg["toggles"].get(module))


def active_brands(cfg: dict) -> list[dict]:
    """Personal brands always; other brands only with `marcas_extra` (the first brand
    stays visible when there is no personal brand, so nobody opens an empty app)."""
    brands = cfg["brands"]
    if cfg["toggles"]["marcas_extra"]:
        return brands
    return [b for b in brands if b["kind"] == "personal-brand"] or brands[:1]


def task_prefixes(cfg: dict) -> dict[str, str]:
    """Every configured brand plus Vida Personal. A brand added later is just a new row."""
    return {**{b["id"]: b["task_prefix"] for b in cfg["brands"]}, VIDA_ECOSYSTEM: VIDA_PREFIX}



def write_toggle(target, module: str, on: bool) -> None:
    """The one writer the UI has: flip one toggle in cc.config.json, keep everything else as is.
    Fixed schema (a known module, a real bool); refuses symlinks and a file that is not JSON."""
    import os
    import secrets
    if module not in MODULES or not isinstance(on, bool):
        raise ValueError("módulo o valor inválido")
    path = Path(target) / CONFIG_REL
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("cc.config.json es un enlace simbólico; no lo toco")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raw = {"schema_version": DEFAULTS["schema_version"]}
    except (OSError, ValueError, UnicodeDecodeError):
        raise ValueError("cc.config.json no es JSON válido; arreglalo a mano antes de cambiar módulos")
    if not isinstance(raw, dict):
        raise ValueError("cc.config.json no es un objeto JSON; arreglalo a mano")
    toggles = raw.get("toggles") if isinstance(raw.get("toggles"), dict) else {}
    raw["toggles"] = {**toggles, module: on}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{secrets.token_hex(4)}.tmp")
    tmp.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
