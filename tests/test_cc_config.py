# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""cc.config.json: defaults, tolerant validation, toggles, brand scope."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402

sys.path.insert(0, str(REPO / "tools"))
import guard  # noqa: E402

BRANDS = [
    {"id": "yo", "name": "Canal Uno", "task_prefix": "YO", "kind": "personal-brand", "accent": "#112233"},
    {"id": "tienda", "name": "Tienda Ficticia", "task_prefix": "TDA"},
]


def write(tmp_path, payload):
    (tmp_path / ".kit-personal").mkdir(exist_ok=True)
    (tmp_path / ".kit-personal" / "cc.config.json").write_text(
        payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_schema_uses_only_the_guard_subset_and_defaults_validate():
    assert guard.validate(config.DEFAULTS, config.SCHEMA, config.SCHEMA) == []
    assert config.validate(config.DEFAULTS, config.SCHEMA) == []


def test_missing_file_gives_defaults_with_empty_personal_lists(tmp_path):
    cfg = config.load(tmp_path)
    assert cfg["brands"] == [] and cfg["_warnings"] == []
    assert all(cfg["vida"][k] == [] for k in ("habits", "fixed_payments", "recurring_income", "milestones"))
    assert cfg["vida"]["income_goal"] is None and cfg["vida"]["fx_rate"] is None
    assert cfg["toggles"] == {"vida": True, "agentic": False, "produccion_avanzada": False,
                              "biblioteca": False, "metricas": False, "marcas_extra": False,
                              "subtitulos": False}
    assert cfg["creator"] == {"weekly_goal": 3, "grace_days": 1}
    assert cfg["locale"]["timezone"] == "UTC"


def test_broken_json_and_wrong_types_never_crash(tmp_path):
    write(tmp_path, "{nope")
    cfg = config.load(tmp_path)
    assert cfg["brands"] == [] and "not valid JSON" in cfg["_warnings"][0]
    write(tmp_path, [1, 2])
    assert config.load(tmp_path)["toggles"]["vida"] is True
    write(tmp_path, {"brands": "x", "toggles": [], "vida": {"habits": {"a": 1}, "currency": 5},
                     "creator": {"weekly_goal": 0, "grace_days": 9}, "surprise": 1,
                     "locale": {"timezone": "Mars/Base"}})
    cfg = config.load(tmp_path)
    assert cfg["brands"] == [] and cfg["vida"]["habits"] == [] and cfg["vida"]["currency"] == "USD"
    assert cfg["creator"] == {"weekly_goal": 3, "grace_days": 1}
    assert cfg["locale"]["timezone"] == "UTC"
    assert len(cfg["_warnings"]) >= 6


def test_partial_config_merges_and_bad_items_are_dropped(tmp_path):
    write(tmp_path, {
        "brands": BRANDS + [{"id": "Bad Id", "name": "x", "task_prefix": "BAD"},
                            {"id": "dup", "name": "Dup", "task_prefix": "YO"},
                            {"id": "vida", "name": "Reserved", "task_prefix": "VV"}],
        "toggles": {"marcas_extra": True},
        "vida": {"currency": "EUR", "habits": [{"id": "leer", "label": "Leer"},
                                               {"id": "correr", "label": "Correr", "weekdays": [0, 2]},
                                               {"id": "leer", "label": "otra vez"},
                                               {"id": "x", "label": "x", "weekdays": [True]}]},
    })
    cfg = config.load(tmp_path)
    assert [b["id"] for b in cfg["brands"]] == ["yo", "tienda"]
    assert cfg["brands"][1]["kind"] == "brand" and cfg["brands"][1]["metrics"]["provider"] == "none"
    assert cfg["toggles"]["marcas_extra"] is True and cfg["toggles"]["vida"] is True
    assert [h["id"] for h in cfg["vida"]["habits"]] == ["leer", "correr"]
    assert cfg["vida"]["habits"][0]["weekdays"] == list(range(7))
    assert cfg["vida"]["currency"] == "EUR"
    assert config.task_prefixes(cfg) == {"yo": "YO", "tienda": "TDA", "vida": "VIDA"}


def test_active_brands_follow_marcas_extra():
    cfg = config.normalize({"brands": BRANDS})
    assert [b["id"] for b in config.active_brands(cfg)] == ["yo"]
    cfg = config.normalize({"brands": BRANDS, "toggles": {"marcas_extra": True}})
    assert [b["id"] for b in config.active_brands(cfg)] == ["yo", "tienda"]
    only_brand = config.normalize({"brands": BRANDS[1:]})
    assert [b["id"] for b in config.active_brands(only_brand)] == ["tienda"]
    assert config.active_brands(config.normalize({})) == []


def test_enabled_core_always_and_toggles_otherwise():
    cfg = config.normalize({"toggles": {"vida": False, "agentic": True}})
    assert config.enabled(cfg, "core") and config.enabled(cfg, "agentic")
    assert not config.enabled(cfg, "vida") and not config.enabled(cfg, "metricas")
