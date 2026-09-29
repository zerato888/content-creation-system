# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Process and token-saving machinery: plain-language hooks, brand gate, no-open, reading budget,
lessons index, statusline, doctor."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engines"))
sys.path.insert(0, str(REPO / "hooks"))
import check_doc_sizes as cds  # noqa: E402
import doctor  # noqa: E402
import lessons_index as li  # noqa: E402
import onboard_write as ow  # noqa: E402
import plan_plain_language as ppl  # noqa: E402

NEW = ["simple_mode", "plan_plain_language", "grounding_track", "brand_gate", "no_open_headless"]


@pytest.fixture
def project(tmp_path):
    shutil.copytree(REPO / "hooks", tmp_path / ".kit/hooks")
    return tmp_path


def hook(root, name, payload, env=None):
    e = {**os.environ, "KIT_HEADLESS": "", "KIT_NO_GATE": "", **(env or {})}
    return subprocess.run([sys.executable, str(root / ".kit/hooks" / f"{name}.py")],
                          input=json.dumps(payload) if not isinstance(payload, str) else payload,
                          capture_output=True, text=True, encoding="utf-8", env=e, timeout=30)


@pytest.mark.parametrize("name", NEW)
def test_new_hooks_fail_open(project, name):
    for junk in ("", "no es json", "[]", "null", '{"tool_input": 5, "prompt": 7}'):
        assert hook(project, name, junk).returncode == 0, (name, junk)


def test_new_hooks_are_registered_for_both_tools():
    for n in NEW:
        assert n in ow.HOOKS and (REPO / "hooks" / f"{n}.py").is_file()
    assert ow.HOOKS["brand_gate"]["codex"] and ow.HOOKS["simple_mode"]["codex"]
    data = {}
    ow._merge_hooks(data, "claude", NEW, ".claude/settings.json", Path("/x"))
    assert "ExitPlanMode" in json.dumps(data) and "PostToolUse" in data["hooks"]
    cx = {}
    ow._merge_hooks(cx, "codex", NEW, ".codex/hooks.json", Path("/x"))
    assert "ExitPlanMode" not in json.dumps(cx) and "PostToolUse" not in cx["hooks"]


# ---- simple_mode
def test_simple_mode_on_off(project):
    p = {"prompt": "hola", "session_id": "abc-1"}
    assert "Modo simple" in hook(project, "simple_mode", p).stdout
    assert hook(project, "simple_mode", {**p, "prompt": "/simple off"}).stdout == ""
    assert hook(project, "simple_mode", p).stdout == ""
    assert "Modo simple" in hook(project, "simple_mode", {**p, "prompt": "/simple on"}).stdout
    assert "Modo simple" in hook(project, "simple_mode", {**p, "session_id": "otra"}).stdout


def test_simple_mode_reads_installed_skill_contract(project):
    d = project / ".claude/skills/simple"
    d.mkdir(parents=True)
    shutil.copy(REPO / "skills/simple/SKILL.md", d / "SKILL.md")
    out = hook(project, "simple_mode", {"prompt": "x", "session_id": "s"}).stdout
    assert "Cómo hablar" in out and "kit:lenguaje-simple" in out


# ---- plan_plain_language
def test_plan_check():
    assert "PLAN_SIN_LENGUAJE_SIMPLE" in ppl.check("# Plan\n## Pasos\n1. algo")
    good = "## En simple\nVamos a ordenar tus carpetas. Si sale mal, vuelve todo como estaba.\n## Detalle\nrun_x()"
    assert ppl.check(good) == ""
    bad = "## En simple\nCorro el wrapper de tools/x.py y hago commit.\n## Detalle"
    assert "PLAN_JERGA" in ppl.check(bad)


def test_plan_hook_never_blocks(project, tmp_path):
    plans = tmp_path / "home/.claude/plans"
    plans.mkdir(parents=True)
    (plans / "p.md").write_text("# sin apertura", encoding="utf-8")
    env = {"HOME": str(tmp_path / "home"), "USERPROFILE": str(tmp_path / "home")}
    r = hook(project, "plan_plain_language", {"tool_name": "ExitPlanMode"}, env)
    assert r.returncode == 0 and "PLAN_SIN_LENGUAJE_SIMPLE" in r.stderr
    assert hook(project, "plan_plain_language", {"tool_name": "Bash"}, env).stderr == ""


# ---- brand_gate + grounding_track
GEN = {"tool_name": "Bash", "tool_input": {"command": 'python .kit/launch.py carousel --brand x'}}


def test_brand_gate(project):
    assert hook(project, "brand_gate", {"tool_input": {"command": "ls"}}).returncode == 0
    assert hook(project, "brand_gate", GEN).returncode == 2  # no brand sheet
    brand = project / ".kit-personal/brands/mia.json"
    brand.parent.mkdir(parents=True)
    brand.write_text("{}", encoding="utf-8")
    assert hook(project, "brand_gate", GEN).returncode == 0  # no read tracking -> existence is enough
    # tracking active but never read -> blocked; after a Read -> allowed
    (project / ".kit-personal/.state").mkdir()
    (project / ".kit-personal/.state/tracking").write_text("on", encoding="utf-8")
    assert hook(project, "brand_gate", GEN).returncode == 2
    hook(project, "grounding_track", {"tool_name": "Read", "tool_input": {"file_path": str(brand)}})
    assert hook(project, "brand_gate", GEN).returncode == 0
    assert hook(project, "brand_gate", GEN, {"KIT_NO_GATE": "1"}).returncode == 0
    (project / ".kit-personal/.state/grounded").write_text(str(time.time() - 3 * 3600), encoding="utf-8")
    assert hook(project, "brand_gate", GEN).returncode == 2


def test_grounding_ignores_other_files(project):
    hook(project, "grounding_track", {"tool_input": {"file_path": str(project / "README.md")}})
    assert not (project / ".kit-personal/.state/grounded").exists()


# ---- no_open_headless
def test_no_open_headless(project):
    opn = {"tool_input": {"command": "echo hi && open out.mp4"}}
    assert hook(project, "no_open_headless", opn).returncode == 0  # attended session: allowed
    assert hook(project, "no_open_headless", opn, {"KIT_HEADLESS": "1"}).returncode == 2
    assert hook(project, "no_open_headless", {"tool_input": {"command": "reopen_x; cat opened.txt"}},
                {"KIT_HEADLESS": "1"}).returncode == 0


# ---- lessons index + router
LESSONS = """# Lecciones
## 2026-05-01 — Nunca subir el video sin revisar el audio
**Regla:** escuchar los primeros diez segundos antes de programar.
Pasó con un reel de recetas.
## Titulo sin fecha sobre miniaturas
texto
"""


def test_lessons_index_and_router(project):
    idx = li.build(LESSONS)["lessons"]
    assert idx[0]["date"] == "2026-05-01" and "diez segundos" in idx[0]["regla"] and idx[1]["date"] == ""
    assert li.build("- una viñeta suelta\n- otra")["lessons"][1]["title"] == "otra"
    (project / ".kit-personal").mkdir()
    (project / ".kit-personal/lessons.md").write_text(LESSONS, encoding="utf-8")
    assert li.main(["--root", str(project)]) == 0
    assert (project / ".kit-personal/lessons-index.json").is_file()
    out = hook(project, "knowledge_router", {"prompt": "voy a programar el video, revisar audio antes"}).stdout
    assert "lección tuya" in out and "diez segundos" in out


def test_lessons_missing_file_is_fine(tmp_path):
    assert li.main(["--root", str(tmp_path)]) == 0


# ---- reading budget
def test_classify_and_report(tmp_path, monkeypatch):
    monkeypatch.setattr(cds, "_ENC", None)
    assert cds.classify(0) == "ok" and cds.classify(cds.WARN_BYTES) == "warn" and cds.classify(cds.FAIL_BYTES) == "fail"
    assert cds.classify(0, tokens=cds.FAIL_TOKENS) == "fail"
    (tmp_path / "big.md").write_text("x" * (cds.FAIL_BYTES + 1), encoding="utf-8")
    (tmp_path / "big-archive.md").write_text("x" * (cds.FAIL_BYTES + 1), encoding="utf-8")
    (tmp_path / "small.md").write_text("hola", encoding="utf-8")
    rows, code = cds.report(tmp_path, ["*.md"])
    assert code == 1 and {r[0]: r[2] for r in rows} == {"big.md": "fail", "small.md": "ok"}
    assert cds.main(["--root", str(tmp_path), "small.md"]) == 0


def test_patterns_from_personal_file_and_no_escape(tmp_path):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/read-budget.txt").write_text("# c\nnotas/*.md\n", encoding="utf-8")
    assert cds.patterns(tmp_path, []) == ["notas/*.md"]
    assert cds.hot_files(tmp_path, ["../*.md", "/etc/*"]) == []


def test_rotate_keeps_newest_and_archives_rest(tmp_path):
    doc = tmp_path / "log.md"
    doc.write_text("# Log\n## 3\nc\n## 2\nb\n## 1\na\n", encoding="utf-8")
    assert cds.main(["--root", str(tmp_path), "--rotate", "log.md", "--keep", "1"]) == 0
    live = doc.read_text(encoding="utf-8")
    arch = (tmp_path / "log-archive.md").read_text(encoding="utf-8")
    assert "## 3" in live and "## 2" not in live and "log-archive.md" in live
    assert "## 2" in arch and "## 1" in arch
    assert cds.main(["--root", str(tmp_path), "--rotate", "../x.md"]) == 2


# ---- statusline
def test_statusline_reads_real_usage(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text("\n".join(json.dumps(x) for x in [
        {"type": "user"}, {"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": 90}}},
        {"type": "assistant", "message": {"usage": {"input_tokens": 50_000, "cache_read_input_tokens": 50_000}}}]) + "\nbasura\n",
        encoding="utf-8")
    r = subprocess.run([sys.executable, str(REPO / "engines/statusline.py")], capture_output=True, text=True, encoding="utf-8",
                       input=json.dumps({"transcript_path": str(t), "model": {"display_name": "M"}}),
                       env={**os.environ, "KIT_CTX_WINDOW": "200000"})
    assert "50%" in r.stdout and "100,000 tokens" in r.stdout and "turno 2" in r.stdout


# ---- doctor
def test_doctor_checks(tmp_path, monkeypatch):
    assert doctor.check_python((3, 12, 1))[0] == "OK"
    assert doctor.check_python((3, 10, 0))[0] == "FALLA" and doctor.check_python((3, 14, 0))[0] == "FALLA"
    assert doctor.check_playwright(tmp_path)[0] == "AVISO"
    (tmp_path / "ms-playwright/chromium-1").mkdir(parents=True)
    assert doctor.check_playwright(tmp_path)[0] == "OK"
    assert doctor.check_whisper(tmp_path)[0] == "AVISO"
    (tmp_path / "whisper/x").mkdir(parents=True)
    (tmp_path / "whisper/x/model.bin").write_bytes(b"1")
    assert doctor.check_whisper(tmp_path)[0] == "OK"
    lock = tmp_path / "f.json"
    lock.write_text(json.dumps({"fonts": [{"file": "A.ttf"}]}), encoding="utf-8")
    assert doctor.check_fonts(tmp_path, lock)[0] == "AVISO"
    (tmp_path / "A.ttf").write_bytes(b"1")
    assert doctor.check_fonts(tmp_path, lock)[0] == "OK"


def test_doctor_keys_never_print_values():
    st, msg, _ = doctor.check_keys({"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"},
                                   lookup=lambda n: ("sk-SECRET" if n.startswith("OPENAI") else None, "env"))
    assert st == "OK" and "openai" in msg and "SECRET" not in msg and "gemini" not in msg


def test_doctor_ffmpeg_needs_libass():
    def fake(out, code=0):
        return lambda *a, **k: subprocess.CompletedProcess(a, code, out, "")
    assert doctor.check_ffmpeg(fake(" T.. subtitles         V->V   Render text\n"))[0] == "OK"
    assert doctor.check_ffmpeg(fake(" T.. scale  V->V\n"))[0] == "FALLA"
    assert doctor.check_ffmpeg(fake("", 1))[0] == "FALLA"


def test_doctor_skills_and_launch_registration(tmp_path):
    assert doctor.check_skills(tmp_path)[0] == "AVISO"
    for n in ("simple", "task"):
        (tmp_path / ".claude/skills" / n).mkdir(parents=True)
        (tmp_path / ".claude/skills" / n / "SKILL.md").write_text("x", encoding="utf-8")
    assert "skills instaladas" in doctor.check_skills(tmp_path)[1]
    src = (REPO / "launch.py").read_text(encoding="utf-8")
    for cmd in ("doctor", "docsizes", "lessons"):
        assert f'"{cmd}"' in src
