# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Command Center wiring: cc/ copied into .kit, cc.config.json from onboarding, tool detection,
the running marker, and the always-on service (OS calls mocked in conftest.py)."""
import json
import os
import plistlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
from kit_helpers import REPO, answers, cli, load_json, make_src, ow, run  # noqa: E402

from installer import service  # noqa: E402

sys.path.insert(0, str(REPO))
from cc.config import config as ccconfig  # noqa: E402


@pytest.fixture
def src(tmp_path):
    s = make_src(tmp_path)
    (s / "cc" / "tests").mkdir()
    (s / "cc" / "tests" / "test_x.py").write_text("x = 1\n", encoding="utf-8")
    return s


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proyecto con espacios ñ"
    p.mkdir()
    return Path(os.path.realpath(p))


def test_cc_tree_copied_without_tests(src, proj):
    assert run(src, proj, "install") == 0
    assert (proj / ".kit/cc/server/app.py").is_file() and (proj / ".kit/cc/config/defaults.json").is_file()
    assert not (proj / ".kit/cc/tests").exists()
    assert not (proj / ".kit/content-lab").exists()


def test_cc_config_from_expert_answers(src, proj):
    assert run(src, proj, "install", "--answers", str(answers("expert"))) == 0
    raw = load_json(proj / ".kit-personal/cc.config.json")
    assert [(b["id"], b["task_prefix"], b["kind"]) for b in raw["brands"]] == [
        ("estudio-norte", "NOR", "brand"), ("marca-personal", "MAR", "personal-brand")]
    assert raw["brands"][0]["accent"] == "#F2A541"
    assert [h["id"] for h in raw["vida"]["habits"]] == ["grabar", "leer"]
    assert raw["locale"] == {"timezone": "America/Mexico_City", "language": "es", "date_format": "DD/MM/YYYY"}
    assert raw["toggles"]["agentic"] is True and raw["toggles"]["vida"] is True
    cfg = ccconfig.load(proj)
    assert cfg["_warnings"] == [] and cfg["creator"]["weekly_goal"] == 4
    assert not load_json(proj / ".kit/manifest.json").get("service")  # expert said no


@pytest.mark.parametrize("patch, msg", [
    ({"timezone": "Marte/Base_Uno"}, "timezone"),
    ({"toggles": {"cohetes": True}}, "cohetes"),
    ({"vida": {"habits": [{"label": "token = ghp_" + "a" * 36}]}}, "clave"),
    ({"creator": {"weekly_goal": "tres"}}, "weekly_goal"),
    ({"service": "si"}, "service"),
])
def test_cc_answers_rejected(tmp_path, patch, msg):
    a = {**load_json(answers("expert")), **patch}
    with pytest.raises(ow.KitError, match=msg):
        ow.plan(tmp_path, a, tools=["claude"], roles_md="", skills=[])


@pytest.mark.parametrize("found, want", [(["claude"], {"CLAUDE.md"}), (["codex"], {"AGENTS.md"}),
                                          (["claude", "codex"], {"CLAUDE.md", "AGENTS.md"})])
def test_only_detected_tools_rendered(src, proj, tmp_path, monkeypatch, found, want):
    monkeypatch.setattr(ow, "detect_tools", lambda: found)
    a = load_json(answers("beginner"))
    del a["tools"]
    a["service"] = False
    f = tmp_path / "a.json"
    f.write_text(json.dumps(a), encoding="utf-8")
    assert run(src, proj, "install", "--answers", str(f)) == 0
    assert {n for n in ("CLAUDE.md", "AGENTS.md") if (proj / n).exists()} == want
    assert (proj / ".claude/skills").exists() == ("claude" in found)
    assert (proj / ".agents/skills").exists() == ("codex" in found)
    assert load_json(proj / ".kit/manifest.json")["tools"] == found


def test_detect_tools_uses_path(monkeypatch):
    monkeypatch.undo()
    monkeypatch.setattr(ow.shutil, "which", lambda t: "/bin/x" if t == "codex" else None)
    assert ow.detect_tools() == ["codex"]
    monkeypatch.setattr(ow.shutil, "which", lambda t: None)
    assert ow.detect_tools() == ["claude", "codex"]


def test_service_mac_lifecycle(src, proj, fake_os, tmp_path):
    assert run(src, proj, "install", "--answers", str(answers("beginner"))) == 0
    rec = load_json(proj / ".kit/manifest.json")["service"]
    assert rec["kind"] == "launchagent" and rec["label"].startswith("com.contentkit.cc.")
    pl = plistlib.loads(service._plist(rec["label"]).read_bytes())
    assert pl["ProgramArguments"][1:] == [str(proj / ".kit/launch.py"), "serve", "--no-print-url"]
    assert pl["KeepAlive"] == {"SuccessfulExit": False} and pl["RunAtLoad"] is True
    assert any(c[:2] == ["launchctl", "bootstrap"] for c in fake_os)
    assert run(src, proj, "service", "status") == 0
    assert run(src, proj, "install") == 0  # reinstall keeps the record
    assert load_json(proj / ".kit/manifest.json")["service"] == rec
    assert run(src, proj, "uninstall") == 0
    assert not service._plist(rec["label"]).exists()
    assert any(c[:2] == ["launchctl", "bootout"] for c in fake_os)
    assert (proj / ".kit-personal/cc.config.json").is_file()


def test_service_on_off_command(src, proj, fake_os):
    assert run(src, proj, "install") == 0
    assert run(src, proj, "service", "on") == 0
    lbl = load_json(proj / ".kit/manifest.json")["service"]["label"]
    assert run(src, proj, "service", "on") == 0  # idempotent
    assert run(src, proj, "service", "off") == 0
    assert "service" not in load_json(proj / ".kit/manifest.json")
    assert not service._plist(lbl).exists()


def test_service_needs_consent(src, proj):
    assert run(src, proj, "install") == 0
    assert run(src, proj, "service", "on", confirm=lambda *a, **k: False) == 0
    assert "service" not in load_json(proj / ".kit/manifest.json")


def test_service_windows_task(src, proj, fake_os, monkeypatch):
    monkeypatch.setattr(service, "PLATFORM", "windows")
    assert run(src, proj, "install") == 0
    assert run(src, proj, "service", "on") == 0
    rec = load_json(proj / ".kit/manifest.json")["service"]
    ps = fake_os[-1][-1]
    assert rec["kind"] == "schtask" and "-AtLogOn" in ps and "-RestartCount" in ps and rec["label"] in ps
    assert "serve --no-print-url" in ps
    assert run(src, proj, "uninstall") == 0
    assert any("Unregister-ScheduledTask" in c[-1] for c in fake_os)


def test_running_marker_blocks_and_stale_is_cleared(src, proj):
    assert run(src, proj, "install") == 0
    marker = proj / ".kit/cc.running"
    marker.write_text(f"{os.getpid()}\n", encoding="utf-8")  # alive: this test process
    assert run(src, proj, "uninstall") == 2
    assert (proj / ".kit/manifest.json").is_file()
    marker.write_text("999999\n", encoding="utf-8")  # dead pid: stale
    assert run(src, proj, "uninstall") == 0
    assert not marker.exists()


def test_label_is_per_project(tmp_path):
    a, b = service.label(tmp_path / "a"), service.label(tmp_path / "b")
    assert a != b and a.startswith(service.PREFIX)


def test_install_fonts_reads_the_preset_lock_verifies_hashes_and_skips_todo(tmp_path):
    import hashlib
    from installer import core
    lock = tmp_path / ".kit/presets/captions/fonts.lock.json"
    lock.parent.mkdir(parents=True)
    good = b"wOF2-good"
    lock.write_text(json.dumps({"fonts": [
        {"file": "Sora-Variable.woff2", "url": "https://example.invalid/a", "sha256": hashlib.sha256(good).hexdigest()},
        {"file": "Later.ttf", "url": "TODO", "sha256": "TODO-pin"}]}))
    got = []
    core.install_fonts(tmp_path, lambda url, limit: got.append(url) or good, lambda msg: True, core.Log(tmp_path))
    assert got == ["https://example.invalid/a"]  # the TODO entry is never fetched
    assert (tmp_path / ".kit/fonts/Sora-Variable.woff2").read_bytes() == good
    assert (tmp_path / ".kit/fonts/fonts.conf").is_file()
    (tmp_path / ".kit/fonts/Sora-Variable.woff2").unlink()
    with pytest.raises(core.KitError):
        core.install_fonts(tmp_path, lambda url, limit: b"tampered", lambda msg: True, core.Log(tmp_path))
    assert not (tmp_path / ".kit/fonts/Sora-Variable.woff2").exists()


def test_repo_font_lock_is_installed_where_install_fonts_reads_it():
    from installer import cli as kcli, core
    assert "presets" in kcli.KIT_DIRS and core.FONTS_LOCK == ".kit/presets/captions/fonts.lock.json"
    assert (REPO / "presets/captions/fonts.lock.json").is_file()
