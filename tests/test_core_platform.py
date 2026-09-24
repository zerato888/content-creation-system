# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Shared engine helpers: tolerant brand loading, platform paths, skill smoke, dep lock."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engines"))
import brand  # noqa: E402
import kit_platform  # noqa: E402
import skill_check  # noqa: E402

ROLES = skill_check.ROLES


def test_demo_brand_complete():
    b = brand.load_brand(REPO / "presets/brands/estudio-norte.json")
    assert b["name"] == "Estudio Norte" and b["schema_version"] == 1
    assert set(b["colors"]) >= {"background", "text", "accent"}


def test_brand_tolerant(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"schema_version": 7, "name": "X", "colors": {"accent": "red", "text": "#000000"},
                             "fonts": "nope", "unknown": {"a": 1}}), encoding="utf-8")
    b = brand.load_brand(p)
    assert b["name"] == "X"
    assert b["colors"]["accent"] == brand.DEFAULTS["colors"]["accent"]  # bad hex -> default
    assert b["colors"]["text"] == "#000000"
    assert b["fonts"] == brand.DEFAULTS["fonts"]
    assert "unknown" not in b
    assert brand.load_brand(tmp_path / "missing.json")["name"] == brand.DEFAULTS["name"]
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    assert brand.load_brand(tmp_path / "bad.json")["schema_version"] == 1


def test_css_vars_sanitizes_font_names():
    b = brand.load_brand()
    b["fonts"]["body"] = 'Inter"; } body{x:y'
    css = brand.css_vars(b)
    assert '"; }' not in css and "--brand-accent:" in css


def test_demo_brand_uses_ofl_fonts_only():
    ofl = {"Inter", "Montserrat", "Bebas Neue", "Instrument Serif", "Anton", "GFS Didot", "JetBrains Mono"}
    b = json.loads((REPO / "presets/brands/estudio-norte.json").read_text(encoding="utf-8"))
    assert set(b["fonts"].values()) <= ofl


def test_cache_root_env(monkeypatch, tmp_path):
    monkeypatch.setenv("KIT_CACHE", str(tmp_path))
    assert kit_platform.cache_root() == tmp_path
    assert kit_platform.whisper_model_dir() == tmp_path / "whisper"


def test_fontconfig_points_at_kit_fonts(tmp_path):
    fonts = tmp_path / "fonts dir & co"
    fonts.mkdir()
    conf = kit_platform.write_fontconfig(tmp_path / "fc", fonts).read_text(encoding="utf-8")
    assert "fonts dir &amp; co" in conf and "<cachedir>" in conf


def test_skill_check(tmp_path):
    d = tmp_path / "demo"
    (d / "references").mkdir(parents=True)
    (d / "references" / "a.md").write_text("x", encoding="utf-8")
    (d / "SKILL.md").write_text("---\nname: demo\ndescription: d\nrole: copywriter\nfiles: [references/a.md]\n---\nbody\n",
                                encoding="utf-8")
    assert skill_check.check(d) == []
    (d / "SKILL.md").write_text("---\nname: other\ndescription: d\nrole: boss\nfiles:\n  - ../x.md\n---\n", encoding="utf-8")
    errs = " ".join(skill_check.check(d))
    assert "folder" in errs and "unknown role" in errs and "outside" in errs


def test_catalog_roles_are_kit_roles():
    cat = json.loads((REPO / "catalog.json").read_text(encoding="utf-8"))
    for s in cat["skills"]:
        assert s["role"] in ROLES
        if s["tier"] == "core":
            assert s["paid_services"] == []


def test_requirements_lock_fresh():
    r = subprocess.run([sys.executable, str(REPO / "tools/lock_deps.py"), "--check"], capture_output=True)
    assert r.returncode == 0, r.stdout
