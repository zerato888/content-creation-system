# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""onboard_write.py and kit_secrets.py. Secret-shaped strings are assembled at runtime so no file holds one."""
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
from kit_helpers import REPO, answers, core, load_json, ow  # noqa: E402

FAKE_AWS = "AKIA" + "IOSFODNN7" + "EXAMPLE"
FAKE_OPENAI = "sk-" + "proj-" + "Ab3" * 12


def base_answers() -> dict:
    return load_json(answers("beginner"))


@pytest.mark.parametrize("field,value", [
    ("goals", ["mi clave es " + FAKE_AWS]),
    ("audience", "token: " + FAKE_OPENAI),
    ("name", FAKE_AWS),
])
def test_rejects_secret_in_free_text(field, value):
    a = base_answers()
    a[field] = value
    with pytest.raises(ow.KitError) as e:
        ow.validate(a)
    assert FAKE_AWS not in str(e.value) and FAKE_OPENAI not in str(e.value)


@pytest.mark.parametrize("patch", [
    {"services": {"openai": FAKE_OPENAI}},  # a key where yes/no belongs
    {"services": {"unknown-service": True}},
    {"brands": [{"name": "Bad Name", "display_name": "x"}]},
    {"brands": [{"name": "ok", "colors": {"primary": "red"}}]},
    {"audience": "x" * 600},
    {"goals": ["<!-- kit:end --> injected"]},
    {"unexpected": 1},
])
def test_rejects_invalid_answers(patch):
    a = {**base_answers(), **patch}
    with pytest.raises(ow.KitError):
        ow.validate(a)


def test_block_apply_replace_and_remove():
    user = "# mine\r\nkeep\r\n"
    once = ow.apply_block(user, "v1 body", "md")
    assert once.startswith(user) and "\r\nv1 body\r\n" in once
    twice = ow.apply_block(once, "v2 body", "md")
    assert "v2 body" in twice and "v1 body" not in twice and twice.startswith(user)
    assert ow.remove_block(twice) == user
    assert ow.apply_block("", "b", "hash") == "# kit:begin v1\nb\n# kit:end\n"
    for bad in ("<!-- kit:begin v1 -->\n<!-- kit:begin v1 -->\n<!-- kit:end -->",
                "<!-- kit:begin v1 -->\n<!-- kit:end -->\n<!-- kit:end -->"):
        with pytest.raises(ow.MarkerError):
            ow.apply_block(bad, "x", "md")


def test_user_text_fenced_and_capped():
    out = ow.fence("line\n~~~\nkit:begin v9\n" + "y" * 5000, "Perfil")
    assert out.count("~~~") == 2 and "kit:begin" not in out and "[... recortado]" in out


def test_settings_merge_never_clobbers(tmp_path):
    merged = json.loads(ow.merged_settings(json.dumps(
        {"model": "x", "permissions": {"allow": ["Bash(ls)"], "deny": ["Read(./secret.txt)"]}}).encode()))
    assert merged["model"] == "x" and merged["permissions"]["allow"] == ["Bash(ls)"]
    assert merged["permissions"]["deny"] == ["Read(./secret.txt)", "Read(./.kit-personal/.env)"]
    assert ow.merged_settings(json.dumps(merged).encode()) is None  # already present
    with pytest.raises(ow.KitError):
        ow.merged_settings(b"{not json")
    with pytest.raises(ow.KitError):
        ow.merged_settings(b'{"permissions": {"deny": "oops"}}')


def test_cli_stdin_writes_only_allowed_paths(tmp_path, monkeypatch):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "CLAUDE.md").write_text("mine\n", encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(load_json(answers("expert")))))
    assert ow.main(["--answers", "-", "--project", str(proj)]) == 0
    written = {p.relative_to(proj).as_posix() for p in proj.rglob("*") if p.is_file()}
    allowed = ("CLAUDE.md", "AGENTS.md", ".gitignore", ".claude/settings.json", ".kit-personal/", ".kit/backup/")
    assert written and all(w.startswith(allowed) for w in written), written
    assert (proj / ".kit-personal/brands/estudio-norte.json").is_file()
    assert (proj / "CLAUDE.md").read_text(encoding="utf-8").startswith("mine\n")
    assert any(p.name == "CLAUDE.md" for p in (proj / ".kit/backup").rglob("*"))  # backup taken first
    assert not (proj / ".kit.lock").exists()
    env = (proj / ".kit-personal/.env.example").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=\n" in env and "ELEVENLABS_API_KEY=\n" in env and "APIFY" not in env


def test_cli_run_as_script_rejects_secret(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    a = base_answers()
    a["goals"] = [FAKE_AWS]
    r = subprocess.run([sys.executable, str(REPO / "engines/onboard_write.py"), "--answers", "-",
                        "--project", str(proj)], input=json.dumps(a), capture_output=True, text=True)
    assert r.returncode == 2 and FAKE_AWS not in r.stdout + r.stderr
    assert list(proj.iterdir()) == []


def test_secrets_never_logged(tmp_path):
    log = core.Log(tmp_path)
    log("install", "", "error", RuntimeError(f"boom {FAKE_AWS} at {Path.home()}/x"))
    text = (tmp_path / ".kit/install.log").read_text(encoding="utf-8")
    assert FAKE_AWS not in text and "[redacted]" in text and str(Path.home()) not in text


def _secrets_mod():
    spec = importlib.util.spec_from_file_location("kit_secrets", REPO / "engines/kit_secrets.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_secrets_helper_env_fallback_never_prints(monkeypatch, capsys):
    m = _secrets_mod()
    monkeypatch.setattr(m, "_keychain", lambda n: None)  # OS store empty: env fallback only
    monkeypatch.setattr(m, "_wincred", lambda n: None)
    monkeypatch.setenv("KIT_TEST_SECRET", FAKE_OPENAI)
    assert m.get_secret("KIT_TEST_SECRET") == FAKE_OPENAI
    assert m.main(["check", "KIT_TEST_SECRET"]) == 0
    assert m.main(["check", "KIT_MISSING_SECRET"]) == 1
    out = capsys.readouterr()
    assert FAKE_OPENAI not in out.out + out.err and "found (env)" in out.out
    with pytest.raises(ValueError):
        m.get_secret("lower-case")

