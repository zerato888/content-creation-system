# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Installer end to end against the fixture catalog (tests/fixtures/kit-src), not the real one."""
import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
from kit_helpers import (FIX, REPO, SHA, FakeRelease, answers, cli, core, load_json, make_src,  # noqa: E402
                         ow, run, tree)


@pytest.fixture
def src(tmp_path):
    return make_src(tmp_path)


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "mi proyecto ñandú"
    p.mkdir()
    return Path(os.path.realpath(p))


def norm(text: str) -> str:
    return text.replace("\r\n", "\n")


@pytest.mark.parametrize("who", ["beginner", "expert"])
def test_fresh_install_golden(src, proj, who):
    assert run(src, proj, "install", "--answers", str(answers(who))) == 0
    for tool_dir in (".claude/skills", ".agents/skills"):
        assert (proj / tool_dir / "demo-hooks/SKILL.md").is_file()
        assert (proj / tool_dir / "demo-hooks/scripts/run.py").is_file()
        assert (proj / tool_dir / "onboard/SKILL.md").is_file()
        assert not (proj / tool_dir / "demo-future").exists()  # untested: never installable
        assert (proj / tool_dir / "demo-extra").exists() == (who == "expert")
    writer = (proj / ".claude/agents/writer.md").read_text(encoding="utf-8")
    assert ".kit/knowledge/guide.md" in writer and "\n1. Read knowledge/" not in writer
    assert (proj / ".kit/knowledge/guide.md").is_file()
    assert (proj / ".claude/agents/planner.md").read_text(encoding="utf-8").startswith("---\nname: planner")
    m = cli.read_manifest(proj)
    assert m["skills"] == sorted(m["skills"]) and "demo-future" not in m["skills"]
    assert all(core.sha256_file(proj / r) == h for r, h in m["files"].items())
    gi = (proj / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".kit-personal/" in gi and ".env" in gi
    s = load_json(proj / ".claude/settings.json")
    assert "Read(./.kit-personal/.env)" in s["permissions"]["deny"]
    assert (proj / ".kit-personal/profile.md").is_file()
    env = (proj / ".kit-personal/.env.example").read_text(encoding="utf-8")
    assert all("=" not in ln or ln.endswith("=") for ln in env.splitlines() if not ln.startswith("#"))
    agents = norm((proj / "AGENTS.md").read_text(encoding="utf-8"))
    assert "## Roles" in agents and "### writer" in agents and ".kit/knowledge/guide.md" in agents
    for f in ("CLAUDE.md", "AGENTS.md"):
        got = norm((proj / f).read_text(encoding="utf-8"))
        golden = FIX / "golden" / f"{who}-{f}"
        if os.environ.get("UPDATE_GOLDEN"):
            golden.write_text(got, encoding="utf-8", newline="\n")
        assert got == norm(golden.read_text(encoding="utf-8")), f"{f} differs from {golden.name}"
    r = subprocess.run([sys.executable, str(REPO / "tools/guard.py"), "--project", str(proj)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_dry_run_changes_nothing(src, proj):
    assert run(src, proj, "install", "--dry-run") == 0
    assert list(proj.iterdir()) == []


def test_idempotent_reinstall(src, proj, capsys):
    assert run(src, proj, "install", "--answers", str(answers("beginner"))) == 0
    before = tree(proj)
    capsys.readouterr()
    assert run(src, proj, "install", "--answers", str(answers("beginner"))) == 0
    assert "Todo al día" in capsys.readouterr().out
    assert run(src, proj, "install") == 0  # no answers: profile-derived block must stay identical
    assert tree(proj) == before


def test_existing_claude_md_preserved(src, proj):
    mine = "# Mis notas\n\nNo tocar esto.\n"
    (proj / "CLAUDE.md").write_text(mine, encoding="utf-8")
    assert run(src, proj, "install") == 0
    text = (proj / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith(mine) and "kit:begin v1" in text
    assert run(src, proj, "uninstall") == 0
    assert (proj / "CLAUDE.md").read_text(encoding="utf-8") == mine


@pytest.mark.parametrize("bad", ["<!-- kit:begin v1 -->\nx\n<!-- kit:begin v1 -->\n<!-- kit:end -->\n",
                                 "<!-- kit:end -->\n<!-- kit:begin v1 -->\n",
                                 "a\n<!-- kit:begin v1 -->\nno end\n"])
def test_malformed_markers_abort(src, proj, bad, capsys):
    (proj / "AGENTS.md").write_text(bad, encoding="utf-8")
    assert run(src, proj, "install") == 2
    assert "marcadores" in capsys.readouterr().err
    assert (proj / "AGENTS.md").read_text(encoding="utf-8") == bad
    assert not (proj / ".kit/manifest.json").exists() and not (proj / ".claude").exists()


def test_collision_skip_and_report(src, proj, capsys):
    p = proj / ".claude/skills/demo-hooks/SKILL.md"
    p.parent.mkdir(parents=True)
    p.write_text("mine\n", encoding="utf-8")
    assert run(src, proj, "install") == 0
    assert p.read_text(encoding="utf-8") == "mine\n"
    assert not (proj / ".claude/skills/demo-hooks/scripts").exists()  # whole group unavailable
    assert (proj / ".agents/skills/demo-hooks/SKILL.md").is_file()
    m = cli.read_manifest(proj)
    assert "demo-hooks" in m["unavailable"] and ".claude/skills/demo-hooks/SKILL.md" not in m["files"]
    assert "no es del kit" in capsys.readouterr().out
    assert run(src, proj, "uninstall") == 0
    assert p.read_text(encoding="utf-8") == "mine\n"


def test_symlink_destination_refused(src, proj, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (proj / ".claude").mkdir()
    try:
        os.symlink(outside, proj / ".claude/skills", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    assert run(src, proj, "install") == 2
    assert list(outside.iterdir()) == []


def test_source_symlink_refused(src, proj):
    try:
        os.symlink(src / "presets/demo.json", src / "presets/link.json")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    assert run(src, proj, "install") == 2
    assert not (proj / ".kit/manifest.json").exists()


def test_path_escape_refused(proj):
    for bad in ("../x", "/etc/x", "C:/x", "a/../../x", "a\\..\\..\\x", ""):
        with pytest.raises(ow.KitError):
            ow.safe_path(proj, bad)


def test_lock_contention_and_stale(src, proj, capsys):
    info = ow.create_lock(proj, "other")  # a live holder: this very process
    assert run(src, proj, "install") == 2
    assert "candado" in capsys.readouterr().err
    (proj / ".kit.lock").unlink()
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    info.update(pid=dead.pid, start="gone", nonce="old")
    (proj / ".kit.lock").write_text(json.dumps(info), encoding="utf-8")
    assert run(src, proj, "install") == 2  # stale, but clearing needs confirmation
    assert (proj / ".kit.lock").exists()
    assert cli.main(["install", "--target", str(proj), "--source", str(src), "--yes", "--clear-stale-lock"]) == 0
    assert not (proj / ".kit.lock").exists()
    log = (proj / ".kit/install.log").read_text(encoding="utf-8")
    assert '"lock-clear-stale"' in log and '\\"nonce\\": \\"old\\"' in log


def test_lock_nonce_recheck(proj):
    lk = core.Lock(proj, "install", lambda *a, **k: False, core.Log(proj))
    lk.acquire()
    lk.check()
    data = json.loads((proj / ".kit.lock").read_text())
    data["nonce"] = "someone-else"
    (proj / ".kit.lock").write_text(json.dumps(data))
    with pytest.raises(core.LockLost):
        lk.check()


@pytest.mark.parametrize("k", [0, 3, 9])
def test_crash_mid_transaction_recovers(src, proj, k):
    (proj / "CLAUDE.md").write_text("mine\n", encoding="utf-8")
    before = tree(proj)
    with pytest.raises(core.SimulatedCrash):
        run(src, proj, "install", fail_at=k)
    assert (proj / ".kit-journal.json").exists()
    assert cli.main(["status", "--target", str(proj)]) == 0  # any command recovers first
    assert not (proj / ".kit-journal.json").exists()
    assert tree(proj, skip=(".kit/install.log",)) == before


def test_crash_recovery_never_clobbers_user_edit(src, proj, capsys):
    with pytest.raises(core.SimulatedCrash):
        run(src, proj, "install", fail_at=4)
    j = load_json(proj / ".kit-journal.json")
    edited = proj / j["steps"][1]["rel"]
    edited.write_text("edited after the crash\n", encoding="utf-8")
    assert cli.main(["status", "--target", str(proj)]) == 3  # reports the conflict, fixes nothing
    assert run(src, proj, "install") == 3
    assert j["steps"][1]["rel"] in capsys.readouterr().err
    assert edited.read_text(encoding="utf-8") == "edited after the crash\n"
    assert (proj / ".kit-journal.json").exists()
    edited.unlink()  # the user resolves it
    assert run(src, proj, "install") == 0


def _v2(src: Path, tmp: Path) -> Path:
    import shutil
    v2 = tmp / "v2"
    shutil.copytree(src, v2)
    (v2 / "skills/demo-hooks/SKILL.md").write_text("---\nname: demo-hooks\ndescription: v2.\n---\n\n# v2\n",
                                                    encoding="utf-8")
    cat = load_json(v2 / "catalog.json")
    cat["skills"] = [s for s in cat["skills"] if s["name"] != "demo-plan"]
    for r in cat["roles"]:
        r["skills"] = [x for x in r["skills"] if x != "demo-plan"]
    (v2 / "catalog.json").write_text(json.dumps(cat), encoding="utf-8")
    shutil.rmtree(v2 / "skills/demo-plan")
    return v2


@pytest.mark.parametrize("choice", ["--keep-mine", "--take-new"])
def test_update_modified_file_and_orphans(src, proj, tmp_path, choice):
    assert run(src, proj, "install", "--answers", str(answers("beginner"))) == 0
    mod = proj / ".claude/skills/demo-hooks/SKILL.md"
    mod.write_text("my edit\n", encoding="utf-8")
    personal = tree(proj / ".kit-personal")
    net = FakeRelease(_v2(src, tmp_path))
    assert cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", SHA, choice], net=net) == 0
    m = cli.read_manifest(proj)
    assert m["release"] == SHA
    assert not (proj / ".claude/skills/demo-plan").exists()  # orphan removed
    assert (proj / ".agents/skills/demo-hooks/SKILL.md").read_text(encoding="utf-8").endswith("# v2\n")
    backups = list((proj / ".kit/backup").rglob("*"))
    assert any(p.as_posix().endswith(".claude/skills/demo-plan/SKILL.md") for p in backups)
    rel = ".claude/skills/demo-hooks/SKILL.md"
    if choice == "--keep-mine":
        assert mod.read_text(encoding="utf-8") == "my edit\n"
        assert rel not in m["files"] and rel in m["user_owned"]
    else:
        assert mod.read_text(encoding="utf-8").endswith("# v2\n") and rel in m["files"]
        assert any(p.as_posix().endswith(rel) and p.read_text(encoding="utf-8") == "my edit\n"
                   for p in backups if p.is_file())
    assert tree(proj / ".kit-personal") == personal
    # rollback restores the pre-update state of kit files
    assert cli.main(["rollback", "--target", str(proj), "--yes"]) == 0
    assert (proj / ".claude/skills/demo-plan/SKILL.md").is_file()


def test_update_needs_explicit_sha(src, proj, tmp_path):
    assert run(src, proj, "install") == 0
    before = tree(proj)
    net = FakeRelease(_v2(src, tmp_path))
    assert cli.main(["update", "--target", str(proj), "--yes"], net=net) == 1  # --yes never approves a SHA
    assert cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", "b" * 40], net=net) == 2
    assert tree(proj) == before


def test_update_sha_mismatch_aborts(src, proj, tmp_path):
    assert run(src, proj, "install") == 0
    before = tree(proj)
    v2 = _v2(src, tmp_path)
    man = cli.build_release_manifest(v2)
    man["files"]["skills/demo-hooks/SKILL.md"] = "0" * 64
    net = FakeRelease(v2, manifest=man)
    assert cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", SHA], net=net) == 2
    assert tree(proj) == before


def _tar(members) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for ti, data in members:
            tf.addfile(ti, io.BytesIO(data) if data is not None else None)
    return buf.getvalue()


def _ti(name, data=b"x", type_=tarfile.REGTYPE, link=""):
    ti = tarfile.TarInfo(name)
    ti.type, ti.linkname = type_, link
    ti.size = len(data) if type_ == tarfile.REGTYPE else 0
    return ti, (data if type_ == tarfile.REGTYPE else None)


@pytest.mark.parametrize("members", [
    [_ti("top/../../evil.txt")],
    [_ti("/abs.txt")],
    [_ti("top/C:/x.txt")],
    [_ti("top/a.txt"), _ti("top/b.txt", type_=tarfile.LNKTYPE, link="top/a.txt")],
    [_ti("top/s", type_=tarfile.SYMTYPE, link="/etc/passwd")],
    [_ti("top/dev", type_=tarfile.CHRTYPE)],
    [_ti("top/zeros.bin", b"\0" * 5_000_000)],  # compression ratio bomb
], ids=["zip-slip", "absolute", "drive", "hardlink", "symlink", "device", "bomb"])
def test_safe_extract_rejects(tmp_path, members):
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(ow.KitError):
        core.safe_extract(_tar(members), out)
    assert not (tmp_path / "evil.txt").exists()


def test_safe_extract_ok_and_file_limit(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    core.safe_extract(_tar([_ti("top/a/b.txt", b"hello")]), out)
    assert (out / "a/b.txt").read_bytes() == b"hello"
    with pytest.raises(ow.KitError):
        core.safe_extract(_tar([_ti(f"top/{i}.txt") for i in range(5)]), tmp_path / "o2",
                          limits={"files": 3, "total": 10**9, "ratio": 100})


def test_uninstall_leaves_personal_and_user_content(src, proj):
    (proj / "notes.md").write_text("user file\n", encoding="utf-8")
    (proj / ".gitignore").write_text("dist/\n", encoding="utf-8")
    assert run(src, proj, "install", "--answers", str(answers("expert")), "--module", "demo-extra") == 0
    personal = tree(proj / ".kit-personal")
    changed = proj / ".agents/skills/demo-extra/SKILL.md"
    changed.write_text("changed by me\n", encoding="utf-8")
    assert run(src, proj, "uninstall") == 0
    assert tree(proj / ".kit-personal") == personal
    assert (proj / "notes.md").read_text(encoding="utf-8") == "user file\n"
    assert (proj / ".gitignore").read_text(encoding="utf-8") == "dist/\n"
    assert changed.read_text(encoding="utf-8") == "changed by me\n"  # modified kit file is kept
    assert not (proj / ".claude/skills").exists() and not (proj / ".kit/manifest.json").exists()
    assert not (proj / "CLAUDE.md").exists() and not (proj / "AGENTS.md").exists()
    assert not (proj / ".kit-prev").exists() and not (proj / ".kit.lock").exists()


def test_install_log_contract(src, proj):
    assert run(src, proj, "install") == 0
    recs = [json.loads(x) for x in (proj / ".kit/install.log").read_text(encoding="utf-8").splitlines()]
    assert recs and all({"ts", "action", "path", "status"} <= set(r) for r in recs)
    assert not any(str(proj) in json.dumps(r) for r in recs)
