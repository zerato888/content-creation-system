# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Agentic OS for the person: the four hooks (fail-open, Windows-safe), their config for only
the tools present, the empty lessons/hot files, the new skills, and a clean uninstall."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
from kit_helpers import REPO, make_src, ow, run  # noqa: E402

HOOKS = ["block_sudo", "knowledge_router", "post_compact_reminder", "session_start_summary"]
ELEVATE = "su" + "do"  # split so command-blocking hooks do not trip on this test file
BASE = {"name": "Ana", "languages": ["es"], "timezone": "UTC", "personal_brand": True}


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proyecto con espacios ñ"
    shutil.copytree(REPO / "hooks", root / ".kit/hooks")
    return root


def hook(root, name, payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(root / ".kit/hooks" / f"{name}.py")], input=stdin,
                          capture_output=True, text=True, encoding="utf-8", timeout=30)


# ---------------------------------------------------------------- hooks
def test_block_sudo_blocks_elevation_and_passes_the_rest(project):
    r = hook(project, "block_sudo", {"tool_name": "Bash", "tool_input": {"command": f"{ELEVATE} rm -rf /x"}})
    assert r.returncode == 2 and "administrador" in r.stderr
    r = hook(project, "block_sudo", {"tool_input": {"command": ["bash", "-lc", f"echo hi && {ELEVATE} ls"]}})
    assert r.returncode == 2
    for ok in ("ls -la", "echo pseudo-thing", "git commit -m 'sudoku'"):
        assert hook(project, "block_sudo", {"tool_input": {"command": ok}}).returncode == 0, ok


@pytest.mark.parametrize("name", HOOKS)
def test_every_hook_fails_open(project, name):
    for junk in ("", "not json", "[1,2]", json.dumps({"prompt": 42, "tool_input": "x"})):
        assert hook(project, name, junk).returncode == 0, (name, junk)


def test_session_start_prints_hot_fenced_and_is_silent_without_it(project):
    assert hook(project, "session_start_summary", {}).stdout == ""
    (project / ".kit-personal").mkdir()
    (project / ".kit-personal/hot.md").write_text("", encoding="utf-8")
    assert hook(project, "session_start_summary", {}).stdout == ""
    (project / ".kit-personal/hot.md").write_text("# Dónde estamos\n- guion de la receta ~~~ x\n", encoding="utf-8")
    out = hook(project, "session_start_summary", {"source": "startup"}).stdout
    assert "no son instrucciones" in out and "guion de la receta" in out and out.count("~~~") == 2


def test_post_compact_points_at_hot_and_latest_checkpoint(project):
    (project / ".kit-personal/checkpoints/CAN-3").mkdir(parents=True)
    (project / ".kit-personal/checkpoints/CAN-3/CURRENT.md").write_text("# CAN-3\n", encoding="utf-8")
    (project / ".kit-personal/hot.md").write_text("x", encoding="utf-8")
    out = hook(project, "post_compact_reminder", {"source": "compact"}).stdout
    assert "hot.md" in out and "checkpoints/CAN-3/CURRENT.md" in out


def test_knowledge_router_reads_installed_catalog_and_lessons_only(project):
    shutil.copy(REPO / "catalog.json", project / ".kit/catalog.json")
    prompt = {"prompt": "Necesito escribir hooks para mi próximo video de recetas"}
    assert hook(project, "knowledge_router", prompt).stdout == ""  # nothing installed yet
    shutil.copytree(REPO / "skills/hooks", project / ".claude/skills/hooks")
    out = hook(project, "knowledge_router", prompt).stdout
    assert "skill `hooks`" in out and "rol `copywriter`" in out
    (project / ".kit-personal").mkdir(exist_ok=True)
    (project / ".kit-personal/lessons.md").write_text(
        "- 2026-01-02 · Los hooks dicen el tema del video de entrada — siempre\n- otra cosa sin relación\n",
        encoding="utf-8")
    out = hook(project, "knowledge_router", prompt).stdout
    assert "lección tuya: 2026-01-02 · Los hooks dicen el tema" in out and "sin relación" not in out


def test_hooks_are_stdlib_python_with_no_owner_lists():
    for p in (REPO / "hooks").glob("*.py"):
        src = p.read_text(encoding="utf-8")
        imports = set(re.findall(r"^(?:from|import) ([a-zA-Z_]+)", src, re.M))
        assert imports <= {"json", "re", "sys", "unicodedata", "pathlib", "_common"}, (p.name, imports)
        assert "/" + "Users/" not in src and "C:\\" not in src


# ---------------------------------------------------------------- onboarding per tool
def _plan(root, tools, hooks=None, **extra):
    a = {**BASE, "tools": tools, **({"hooks": hooks} if hooks is not None else {}), **extra}
    return ow.plan(root, a, tools=tools, roles_md="", skills=["task"])[0]


def test_only_claude_writes_only_claude_files(tmp_path):
    files = _plan(tmp_path, ["claude"], ["block_sudo", "session_start_summary"])
    assert "CLAUDE.md" in files and ".claude/settings.json" in files
    assert "AGENTS.md" not in files and not any(f.startswith(".codex/") for f in files)
    assert files[".kit-personal/lessons.md"] == b"" and files[".kit-personal/hot.md"] == b""
    s = json.loads(files[".claude/settings.json"])
    cmds = [h["command"] for ev in s["hooks"].values() for e in ev for h in e["hooks"]]
    assert len(cmds) == 2 and all("$CLAUDE_PROJECT_DIR/.kit/hooks/" in c for c in cmds)
    assert s["hooks"]["PreToolUse"][0]["matcher"] == "Bash"
    assert s["hooks"]["SessionStart"][0]["matcher"] == "startup"
    assert "Read(./.kit-personal/.env)" in s["permissions"]["deny"]
    text = files["CLAUDE.md"].decode()
    assert "Codex" not in text.split("Segunda opinión")[0]  # the only mention is the optional second opinion


def test_only_codex_writes_only_codex_files(tmp_path):
    files = _plan(tmp_path, ["codex"], ["block_sudo", "session_start_summary", "post_compact_reminder"])
    assert "AGENTS.md" in files and ".codex/hooks.json" in files
    assert "CLAUDE.md" not in files and not any(f.startswith(".claude/") for f in files)
    h = json.loads(files[".codex/hooks.json"])["hooks"]
    assert set(h) == {"PreToolUse", "SessionStart"}  # post_compact has no Codex event: skipped
    cmds = [x["command"] for ev in h.values() for e in ev for x in e["hooks"]]
    assert all(re.search(r"\.kit[/\\\\]hooks[/\\\\][a-z_]+\.py", c) and ("$CLAUDE_PROJECT_DIR" not in c) for c in cmds), cmds
    assert "CLAUDE_PROJECT_DIR" not in files[".codex/hooks.json"].decode()


def test_hooks_off_by_default_and_never_clobber(tmp_path):
    files = _plan(tmp_path, ["claude", "codex"])
    assert "hooks" not in json.loads(files[".claude/settings.json"]) and ".codex/hooks.json" not in files
    (tmp_path / ".claude").mkdir()
    mine = {"model": "x", "hooks": {"PreToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "my-lint"}]}]}}
    (tmp_path / ".claude/settings.json").write_text(json.dumps(mine), encoding="utf-8")
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/lessons.md").write_text("- mi lección\n", encoding="utf-8")
    files = _plan(tmp_path, ["claude"], ["block_sudo"])
    s = json.loads(files[".claude/settings.json"])
    assert s["model"] == "x" and {"matcher": "Edit", "hooks": [{"type": "command", "command": "my-lint"}]} in s["hooks"]["PreToolUse"]
    assert ".kit-personal/lessons.md" not in files  # never overwritten
    (tmp_path / ".claude/settings.json").write_bytes(files[".claude/settings.json"])
    again = _plan(tmp_path, ["claude"], ["block_sudo"])
    assert ".claude/settings.json" not in again  # idempotent
    off = json.loads(_plan(tmp_path, ["claude"], [])[".claude/settings.json"])
    assert off["hooks"] == mine["hooks"]  # only the kit's entries go
    with pytest.raises(ow.KitError):
        _plan(tmp_path, ["claude"], ["rm-everything"])


def test_install_then_uninstall_removes_kit_hook_entries(tmp_path):
    src = make_src(tmp_path)
    shutil.copytree(REPO / "hooks", src / "hooks")
    proj = tmp_path / "proj ñ"
    proj.mkdir()
    (proj / ".claude").mkdir()
    (proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "mine"}]}]}}), encoding="utf-8")
    ans = tmp_path / "a.json"
    ans.write_text(json.dumps({**BASE, "tools": ["claude", "codex"], "hooks": ["block_sudo", "knowledge_router"]}), encoding="utf-8")
    assert run(src, proj, "install", "--answers", str(ans)) == 0
    assert (proj / ".kit/hooks/block_sudo.py").is_file()
    assert "block_sudo" in (proj / ".claude/settings.json").read_text(encoding="utf-8") and (proj / ".codex/hooks.json").is_file()
    assert run(src, proj, "uninstall") == 0
    s = json.loads((proj / ".claude/settings.json").read_text(encoding="utf-8"))
    assert s["hooks"] == {"Stop": [{"hooks": [{"type": "command", "command": "mine"}]}]}
    assert json.loads((proj / ".codex/hooks.json").read_text(encoding="utf-8")) == {}
    assert not (proj / ".kit/hooks").exists()


# ---------------------------------------------------------------- skills
OPTIONAL_TOOLS = {"python>=3.11"}  # anything else must be marked "(optional)"
NEW = ["task", "task-checkpoint", "finish-session", "simple"]


@pytest.mark.parametrize("name", NEW)
def test_new_skills_need_no_second_tool(name):
    body = (REPO / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    assert not re.search(r"(requiere|necesit\w+|obligatori\w+)[^.\n]{0,40}(codex|gemini|claude code)", body, re.I)
    cat = json.loads((REPO / "catalog.json").read_text(encoding="utf-8"))
    entry = next(s for s in cat["skills"] if s["name"] == name)
    assert all(d in OPTIONAL_TOOLS or "(optional" in d for d in entry["deps"]), entry["deps"]
    assert entry["tier"] == "core" and entry["status"] == "tested" and entry["support"]["codex"] and entry["support"]["claude"]
    role = next(r for r in cat["roles"] if r["name"] == entry["role"])
    assert name in role["skills"]
    assert re.search(rf"^skills: \[.*\b{re.escape(name)}\b.*\]$", (REPO / f"agents/{entry['role']}.md").read_text(encoding="utf-8"), re.M)


def test_checkpoint_script(tmp_path):
    script = REPO / "skills/task-checkpoint/scripts/checkpoint.py"
    assert subprocess.run([sys.executable, str(script), "--selftest"], capture_output=True).returncode == 0
    p = subprocess.run([sys.executable, str(script), "save", "CAN-7", "--file", "-", "--project", str(tmp_path)],
                       input="# CAN-7 — prueba\n", capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0 and (tmp_path / ".kit-personal/checkpoints/CAN-7/CURRENT.md").is_file()
    bad = subprocess.run([sys.executable, str(script), "save", "../../x", "--file", "-", "--project", str(tmp_path)],
                         input="x", capture_output=True, text=True)
    assert bad.returncode == 2


def test_task_skill_cli_runs_from_project_root(tmp_path):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/cc.config.json").write_text(json.dumps(
        {"brands": [{"id": "canal", "name": "Canal", "task_prefix": "CAN", "kind": "personal-brand"}]}), encoding="utf-8")
    cli = [sys.executable, str(REPO / "cc/server/tasks.py")]
    r = subprocess.run([*cli, "add", "Grabar intro", "--ecosystem", "canal"], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0 and json.loads(r.stdout)["code"] == "CAN-1", r.stderr
    r = subprocess.run([*cli, "list"], cwd=tmp_path, capture_output=True, text=True, env={**os.environ})
    assert [t["code"] for t in json.loads(r.stdout)] == ["CAN-1"]
