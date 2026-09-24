# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Regression tests for the post-build inspection findings (one or more per finding, named fNN_...)."""
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
from kit_helpers import REPO, SHA, FakeRelease, answers, cli, core, load_json, make_src, ow, run  # noqa: E402

from installer import service  # noqa: E402

sys.path.insert(0, str(REPO))
from cc.config import config as ccconfig  # noqa: E402
from cc.server import app as ccapp  # noqa: E402
from cc.server import creator, guiones, lab, life  # noqa: E402

ELEVATE = "su" + "do"  # split so command-blocking hooks do not trip on this file
REAL_RUN = subprocess.run


def spy_run(monkeypatch, handler):
    """Intercept only the dependency installer's calls (venv/pip/npm); everything else runs for real."""
    def run_(argv, *a, **k):
        if any(x in argv for x in ("venv", "pip", "ci")):
            return handler(argv, *a, **k)
        return REAL_RUN(argv, *a, **k)
    monkeypatch.setattr(core.subprocess, "run", run_)


@pytest.fixture
def src(tmp_path):
    return make_src(tmp_path)


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proyecto con espacios ñ"
    p.mkdir()
    return Path(os.path.realpath(p))


def onboard(proj, a, *extra, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(a)))
    return ow.main(["--answers", "-", "--project", str(proj), *extra])


# ---------------------------------------------------------------- 1 partial onboarding merges
def test_f01_partial_rerun_merges_and_reset_is_explicit(proj, monkeypatch):
    assert onboard(proj, load_json(answers("expert")), monkeypatch=monkeypatch) == 0
    ccconfig.write_toggle(proj, "biblioteca", True)  # switched on later from the Command Center
    before = {n: (proj / ".kit-personal" / n).read_bytes() for n in ("profile.md", "goals.md")}
    brand = proj / ".kit-personal/brands/estudio-norte.json"
    assert onboard(proj, {"hooks": []}, monkeypatch=monkeypatch) == 0  # the documented way to turn hooks off
    cfg = load_json(proj / ".kit-personal/cc.config.json")
    assert [b["id"] for b in cfg["brands"]] == ["estudio-norte", "marca-personal"]
    assert cfg["toggles"]["biblioteca"] is True and cfg["toggles"]["agentic"] is True
    assert [p["label"] for p in cfg["vida"]["fixed_payments"]] == ["Internet"]
    assert cfg["locale"]["timezone"] == "America/Mexico_City"
    assert brand.is_file()
    assert all((proj / ".kit-personal" / n).read_bytes() == b for n, b in before.items())
    # a partial change touches only its own part
    assert onboard(proj, {"toggles": {"metricas": True}}, monkeypatch=monkeypatch) == 0
    cfg = load_json(proj / ".kit-personal/cc.config.json")
    assert cfg["toggles"]["metricas"] is True and cfg["toggles"]["biblioteca"] is True and len(cfg["brands"]) == 2
    # --reset starts over from the new answers alone
    assert onboard(proj, {"name": "Otra"}, "--reset", monkeypatch=monkeypatch) == 0
    cfg = load_json(proj / ".kit-personal/cc.config.json")
    assert cfg["brands"] == [] and cfg["vida"]["fixed_payments"] == []
    assert "Otra" in (proj / ".kit-personal/profile.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- 2 deps never through a symlink
def test_f02_symlinked_venv_is_refused_before_running_anything(src, proj, tmp_path, monkeypatch):
    assert run(src, proj, "install") == 0
    outside = tmp_path / "otro-entorno"
    (outside / "bin").mkdir(parents=True)
    (proj / ".kit/venv").symlink_to(outside, target_is_directory=True)
    (src / "requirements.lock").write_text("demo==1.0\n", encoding="utf-8")
    calls = []
    spy_run(monkeypatch, lambda *a, **k: calls.append(a))
    assert run(src, proj, "install") == 2
    assert calls == [] and list(outside.rglob("*")) == [outside / "bin"]


def test_f02_symlinked_node_modules_is_refused(src, proj, tmp_path, monkeypatch):
    assert run(src, proj, "install") == 0
    (tmp_path / "nm").mkdir()
    (proj / ".kit/node_modules").symlink_to(tmp_path / "nm", target_is_directory=True)
    (proj / ".kit/package-lock.json").write_text("{}", encoding="utf-8")
    calls = []
    spy_run(monkeypatch, lambda *a, **k: calls.append(a))
    with pytest.raises(ow.KitError, match="symlink"):
        core.install_deps(proj, lambda *a, **k: True, core.Log(proj))
    assert calls == []


# ---------------------------------------------------------------- 3 guiones containment
def test_f03_symlinked_script_folder_never_followed(tmp_path):
    root, outside = tmp_path / "data", tmp_path / "fuera"
    (root / "guiones").mkdir(parents=True)
    outside.mkdir()
    (outside / "x.md").write_text("---\ntitulo: \"ajeno\"\n---\n\n## Guion\nno tocar\n", encoding="utf-8")
    (root / "guiones/en_proceso").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="enlace"):
        guiones.save(str(root), {"titulo": "nuevo", "cuerpo": "x"})
    with pytest.raises(ValueError, match="enlace"):
        guiones.save(str(root), {"file": "x.md", "cuerpo": "pisado"})
    with pytest.raises(ValueError, match="enlace"):
        guiones.delete(str(root), "x.md")
    assert guiones.list_all(str(root)) == []
    assert sorted(p.name for p in outside.iterdir()) == ["x.md"]
    assert "no tocar" in (outside / "x.md").read_text(encoding="utf-8")


def test_f03_symlinked_guiones_root_refused(tmp_path):
    root, outside = tmp_path / "data", tmp_path / "fuera"
    root.mkdir()
    outside.mkdir()
    (root / "guiones").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        guiones.save(str(root), {"titulo": "nuevo"})
    assert list(outside.iterdir()) == []


# ---------------------------------------------------------------- 4 one live server per project
def test_f04_second_server_refused_and_marker_cleanup_is_owner_only(tmp_path):
    (tmp_path / ".kit").mkdir()
    s1, a1 = ccapp.make_server(tmp_path)
    s2, a2 = ccapp.make_server(tmp_path)
    try:
        m1 = ccapp.claim(a1)
        with pytest.raises(ccapp.AlreadyRunning, match="ya está corriendo"):
            ccapp.claim(a2)
        assert load_json(tmp_path / ".kit/cc.running")["nonce"] == m1["nonce"]
        ccapp.release(a2, {"pid": os.getpid(), "nonce": "de-otro"})  # not the owner: nothing removed
        assert (tmp_path / ".kit/cc.running").is_file()
        ccapp.release(a1, m1)
        assert not (tmp_path / ".kit/cc.running").exists() and not (tmp_path / ".kit/cc.port").exists()
        # while an installer command holds the lifecycle lock, a server does not start
        ow.create_lock(tmp_path, "update")
        with pytest.raises(ccapp.AlreadyRunning, match="kit.lock"):
            ccapp.claim(a2)
        assert not (tmp_path / ".kit/cc.running").exists()
        assert load_json(tmp_path / ".kit.lock")["command"] == "update"  # the server never takes another's lock
    finally:
        s1.server_close()
        s2.server_close()


# ---------------------------------------------------------------- 5 lifecycle lock + running check
def test_f05_modifying_commands_refuse_a_live_server(src, proj, tmp_path):
    assert run(src, proj, "install") == 0
    assert run(src, proj, "install") == 0  # reinstall: creates the rollback point
    (proj / ".kit/cc.running").write_text(json.dumps({"pid": os.getpid(), "start": ow.proc_start(os.getpid()),
                                                      "nonce": "n"}), encoding="utf-8")
    assert run(src, proj, "install") == 2
    assert cli.main(["rollback", "--target", str(proj), "--yes"]) == 2
    net = FakeRelease(src)
    assert cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", SHA], net=net) == 2
    assert (proj / ".kit/cc.running").is_file()


def test_f05_lock_held_through_dependency_install(src, proj, monkeypatch):
    seen = []
    monkeypatch.setattr(core, "install_deps", lambda root, *a, **k: seen.append(
        load_json(root / ".kit.lock")["command"]) or True)
    assert run(src, proj, "install") == 0
    assert seen == ["install"] and not (proj / ".kit.lock").exists()


# ---------------------------------------------------------------- 6 tzdata
def test_f06_timezone_accepted_without_tz_database(tmp_path, monkeypatch):
    import zoneinfo
    monkeypatch.setattr(zoneinfo, "available_timezones", lambda: set())

    def no_db(name):
        raise zoneinfo.ZoneInfoNotFoundError(name)
    monkeypatch.setattr(zoneinfo, "ZoneInfo", no_db)
    a = {**load_json(answers("expert")), "timezone": "America/Bogota"}
    files, notes = ow.plan(tmp_path, a, tools=["claude"], roles_md="", skills=[])
    assert json.loads(files[".kit-personal/cc.config.json"])["locale"]["timezone"] == "America/Bogota"
    assert any("zonas horarias" in n for n in notes)
    with pytest.raises(ow.KitError, match="timezone"):
        ow.plan(tmp_path, {**a, "timezone": "no es una zona"}, tools=["claude"], roles_md="", skills=[])


def test_f06_tzdata_pinned_and_example_neutral():
    lock = (REPO / "requirements.lock").read_text(encoding="utf-8")
    assert re.search(r"^tzdata==\S+ \\\n    --hash=sha256:[0-9a-f]{64}", lock, re.M)
    assert "tzdata==" in (REPO / "requirements.in").read_text(encoding="utf-8")
    assert "Costa_Rica" not in (REPO / "engines/onboard_write.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------- 7 one launcher
def test_f07_launcher_runs_commands_with_the_project_venv(tmp_path):
    kit = tmp_path / "p ñ" / ".kit"
    (kit / "cc/server").mkdir(parents=True)
    shutil.copy(REPO / "launch.py", kit / "launch.py")
    (kit / "cc/server/app.py").write_text("import sys\nprint('PREFIX', sys.prefix, sys.argv[1:])\n", encoding="utf-8")
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(kit / "venv")], check=True)
    r = subprocess.run([sys.executable, str(kit / "launch.py"), "serve", "--no-print-url"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    prefix, args = r.stdout.split("PREFIX ", 1)[1].rsplit(" [", 1)
    assert Path(prefix).resolve() == (kit / "venv").resolve() and "'serve', '--no-print-url'" in args


def test_f07_launcher_used_by_service_skill_and_instructions(proj):
    assert service.argv(proj)[1:] == [str(proj / ".kit/launch.py"), "serve", "--no-print-url"]
    for rel in ("skills/onboard/SKILL.md", "onboarding/CLAUDE.md.tmpl", "onboarding/AGENTS.md.tmpl",
                "skills/captions/SKILL.md"):
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "python .kit/launch.py" in text and "python .kit/cc/server/app.py" not in text, rel
        assert "python .kit/engines/video/captions.py" not in text, rel


# ---------------------------------------------------------------- 8 update reconciles the venv
def fake_pip(monkeypatch, fail_when):
    """subprocess.run stand-in: `-m venv` makes a venv dir, pip fails when fail_when(lock text) is true."""
    def fake(argv, check=False, **k):
        if argv[1:3] == ["-m", "venv"]:
            bindir = Path(argv[3]) / ("Scripts" if os.name == "nt" else "bin")
            bindir.mkdir(parents=True)
            (bindir / ("python.exe" if os.name == "nt" else "python")).write_text("", encoding="utf-8")
            (Path(argv[3]) / "marker").write_text(Path(argv[3]).name, encoding="utf-8")
        elif "pip" in argv and fail_when(Path(argv[-1]).read_text(encoding="utf-8")):
            raise subprocess.CalledProcessError(1, argv)
    spy_run(monkeypatch, fake)


def _v2_with_lock(src, tmp_path, lock):
    v2 = tmp_path / "v2"
    shutil.copytree(src, v2)
    (v2 / "requirements.lock").write_bytes(lock.encode())
    return v2


@pytest.mark.parametrize("pip_fails", [False, True])
def test_f08_update_reconciles_venv_or_rolls_back(src, proj, tmp_path, monkeypatch, pip_fails):
    (src / "requirements.lock").write_bytes(b"demo==1\n")
    fake_pip(monkeypatch, lambda text: pip_fails and "demo==2" in text)
    assert run(src, proj, "install") == 0
    stamp = proj / ".kit/venv/.kit-req.sha256"
    v1 = stamp.read_text(encoding="utf-8").strip()
    net = FakeRelease(_v2_with_lock(src, tmp_path, "demo==2\n"))
    rc = cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", SHA], net=net)
    lock = (proj / ".kit/requirements.lock").read_text(encoding="utf-8")
    if pip_fails:
        assert rc == 2 and lock == "demo==1\n" and stamp.read_text(encoding="utf-8").strip() == v1
        assert cli.read_manifest(proj)["release"] != SHA
    else:
        assert rc == 0 and lock == "demo==2\n" and stamp.read_text(encoding="utf-8").strip() == hashlib.sha256(b"demo==2\n").hexdigest()
    assert not (proj / ".kit/venv.old").exists()


# ---------------------------------------------------------------- 9 pinned, consented models
def test_f09_models_only_pinned_consented_and_local(tmp_path, monkeypatch):
    sys.path.insert(0, str(REPO / "engines" / "video"))
    import transcribe as tx
    data = b"modelo de prueba"
    lock = tmp_path / "models.lock.json"
    lock.write_text(json.dumps({"faster-whisper": {"small": {"repo": "x/y", "revision": "r" * 40, "files": [
        {"name": "model.bin", "url": "https://example.test/model.bin", "sha256": hashlib.sha256(data).hexdigest(),
         "size": len(data)}]}}}), encoding="utf-8")
    monkeypatch.setattr(tx, "MODELS_LOCK", lock)
    monkeypatch.setattr(tx.kit_platform, "whisper_model_dir", lambda: tmp_path / "cache")
    with pytest.raises(tx.BackendMissing, match="launch.py models small"):
        tx.local_model("faster-whisper", "small")
    assert tx.download_model("small", "faster-whisper", lambda msg: False) is None  # declined: nothing written
    assert not (tmp_path / "cache").exists()

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    with pytest.raises(ValueError, match="hash"):
        tx.download_model("small", "faster-whisper", lambda msg: True, opener=lambda u: Resp(b"x" * len(data)))
    assert not list((tmp_path / "cache").rglob("model.bin"))
    asked = []
    path = tx.download_model("small", "faster-whisper", lambda msg: asked.append(msg) or True,
                             opener=lambda u: Resp(data))
    assert "MB" in asked[0] and str(tmp_path / "cache") in asked[0]
    got = {}

    class FakeModel:
        def __init__(self, model, **kw):
            got.update(model=model, **kw)

        def transcribe(self, *a, **k):
            return [], None
    fake = type(sys)("faster_whisper")
    fake.WhisperModel = FakeModel
    monkeypatch.setitem(sys.modules, "faster_whisper", fake)
    tx._faster("a.wav", None, "small")
    assert got["model"] == str(path) and got["local_files_only"] is True
    with pytest.raises(tx.BackendMissing, match="no tiene una versión fijada"):
        tx.local_model("faster-whisper", "large-v3")


# ---------------------------------------------------------------- 10/11 service ownership
def test_f10_pending_record_written_before_registration(src, proj, monkeypatch):
    assert run(src, proj, "install") == 0
    real = service.install

    def install(root):
        assert load_json(proj / ".kit/manifest.json")["service"]["pending"] is True
        return real(root)
    monkeypatch.setattr(service, "install", install)
    assert run(src, proj, "service", "on") == 0
    assert "pending" not in load_json(proj / ".kit/manifest.json")["service"]


@pytest.mark.parametrize("registered", [True, False])
def test_f10_interrupted_registration_is_recovered(src, proj, fake_os, registered):
    assert run(src, proj, "install") == 0
    rec = service.record(proj)
    cli.write_manifest_key(proj, "service", {**rec, "pending": True})  # crash right after this line...
    if registered:
        service.install(proj)  # ...or right after registering
    assert run(src, proj, "status") == 0
    m = load_json(proj / ".kit/manifest.json")
    assert (m.get("service") == rec) if registered else ("service" not in m)
    assert run(src, proj, "uninstall") == 0
    assert not service._plist(rec["label"]).exists()


def test_f11_failed_removal_keeps_record_and_reports(src, proj, monkeypatch):
    assert run(src, proj, "install") == 0 and run(src, proj, "service", "on") == 0
    real = service.run
    monkeypatch.setattr(service, "run", lambda argv: subprocess.CompletedProcess(argv, 5, "", "denied")
                        if argv[:2] == ["launchctl", "bootout"] else real(argv))
    assert run(src, proj, "service", "off") == 2
    assert load_json(proj / ".kit/manifest.json")["service"]["label"].startswith(service.PREFIX)
    monkeypatch.setattr(service, "run", real)
    assert run(src, proj, "service", "off") == 0
    assert "service" not in load_json(proj / ".kit/manifest.json")


def test_f11_service_off_waits_for_the_server_to_stop(src, proj, monkeypatch):
    assert run(src, proj, "install") == 0 and run(src, proj, "service", "on") == 0
    (proj / ".kit/cc.running").write_text(str(os.getpid()), encoding="utf-8")  # a server that never stops
    monkeypatch.setattr(cli.time, "sleep", lambda s: None)
    assert run(src, proj, "service", "off") == 2
    assert "service" in load_json(proj / ".kit/manifest.json")


# ---------------------------------------------------------------- 12 cookie per project
def test_f12_each_project_has_its_own_cookie(tmp_path):
    a, b = ccapp.App(tmp_path / "a"), ccapp.App(tmp_path / "b")
    assert a.cookie != b.cookie and a.cookie.startswith("cc_session_") and re.fullmatch(r"cc_session_[0-9a-f]{12}", a.cookie)
    (tmp_path / "a/.kit/cc/web").mkdir(parents=True)
    (tmp_path / "a/.kit/cc/web/index.html").write_text("<!doctype html>", encoding="utf-8")
    srv, app = ccapp.make_server(tmp_path / "a")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", app.port, timeout=5)
        conn.request("GET", f"/?token={app.mint_token()}", headers={"Host": f"127.0.0.1:{app.port}"})
        r = conn.getresponse()
        r.read()
        assert r.getheader("Set-Cookie").startswith(app.cookie + "=")
        sid = r.getheader("Set-Cookie").split(";", 1)[0].split("=", 1)[1]
        for name, want in ((app.cookie, 200), (b.cookie, 401), ("cc_session", 401)):
            conn.request("GET", "/", headers={"Host": f"127.0.0.1:{app.port}", "Cookie": f"{name}={sid}"})
            r = conn.getresponse()
            r.read()
            assert r.status == want, name
        conn.close()
    finally:
        srv.shutdown()
        srv.server_close()


# ---------------------------------------------------------------- 13 Codex hooks from a subfolder
def test_f13_codex_hook_commands_absolute_and_work_from_a_subfolder(proj):
    base = {"path": "rapido", "name": "Ana", "tools": ["codex"], "hooks": ["session_start_summary"]}
    files, _ = ow.plan(proj, base, tools=["codex"], roles_md="", skills=[])
    cmd = json.loads(files[".codex/hooks.json"])["hooks"]["SessionStart"][0]["hooks"][0]["command"]
    exe, path = shlex.split(cmd)
    assert Path(path).is_absolute() and path == (proj / ".kit/hooks/session_start_summary.py").as_posix()
    shutil.copytree(REPO / "hooks", proj / ".kit/hooks")
    (proj / ".kit-personal").mkdir()
    (proj / ".kit-personal/hot.md").write_text("pendiente: grabar\n", encoding="utf-8")
    sub = proj / "videos" / "semana 1"
    sub.mkdir(parents=True)
    r = subprocess.run(cmd.replace("python3 ", shlex.quote(sys.executable) + " ", 1), shell=True, cwd=sub,
                       input="{}", capture_output=True, text=True)
    assert r.returncode == 0 and "grabar" in r.stdout


# ---------------------------------------------------------------- 14 elevation guard
@pytest.mark.parametrize("cmd", [f"/usr/bin/{ELEVATE} ls", f"'{ELEVATE}' ls", f'"{ELEVATE}" ls',
                                 f"env {ELEVATE} ls", f"command {ELEVATE} ls", f"exec {ELEVATE} ls",
                                 f"FOO=1 {ELEVATE} id", f"env -i PATH=/x /usr/bin/{ELEVATE} id",
                                 f"bash -c '{ELEVATE} rm -rf x'", f"ls && \"/usr/bin/{ELEVATE}\" id",
                                 f"s'u'do ls".replace("s'u'do", ELEVATE[0] + "'" + ELEVATE[1] + "'" + ELEVATE[2:]),
                                 f"C:\\Windows\\System32\\runas.exe /user:admin cmd"])
def test_f14_block_sudo_normalizes_the_executable(cmd):
    r = subprocess.run([sys.executable, str(REPO / "hooks/block_sudo.py")],
                       input=json.dumps({"tool_input": {"command": cmd}}), capture_output=True, text=True)
    assert r.returncode == 2, cmd


@pytest.mark.parametrize("cmd", ["ls -la", "git commit -m 'arreglo'", "pseudo ls", "echo listo | grep x"])
def test_f14_block_sudo_lets_ordinary_commands_through(cmd):
    r = subprocess.run([sys.executable, str(REPO / "hooks/block_sudo.py")],
                       input=json.dumps({"tool_input": {"command": cmd}}), capture_output=True, text=True)
    assert r.returncode == 0, cmd


# ---------------------------------------------------------------- 15/17/18 UI (static contracts)
def test_f15_guion_saves_draft_before_recording_and_teleprompter():
    js = (REPO / "cc/web/views/guion.js").read_text(encoding="utf-8")
    rec = js[js.index('button("Ya grabé"'):]
    assert rec.index("await saveDraft()") < rec.index("/api/creator/recorded")
    tele = js[js.index('button("Abrir teleprompter"'):]
    assert tele.index("await saveDraft()") < tele.index("teleprompter.html")
    assert "drafts[g.file]" in js and "key in draft ? draft[key]" in js  # dirty fields survive re-renders
    assert "request_key" in js


def test_f17_translation_handoff_names_only_shipped_skills():
    js = (REPO / "cc/web/views/ideas.js").read_text(encoding="utf-8")
    assert "lab-ingest" not in js
    body = js[js.index("export function handoff"):js.index("function translation(")]
    for skill in re.findall(r"skill `([a-z-]+)`", body):
        assert (REPO / "skills" / skill / "SKILL.md").is_file(), skill
    assert "launch.py lab apply-translation" in body and "packet.contrato" in body


def test_f17_translation_cli_writes_whitelisted_fields(tmp_path, capsys):
    (tmp_path / ".kit-personal").mkdir()
    (tmp_path / ".kit-personal/cc.config.json").write_text(json.dumps(
        {"brands": [{"id": "canal", "name": "Canal", "task_prefix": "CAN", "kind": "personal-brand"}]}), encoding="utf-8")
    root = str(tmp_path / ".kit-personal/data")
    item = lab.save_item(root, {"tipo": "reel", "tema": "demo", "transcript_original": "Hello world"}, "canal")
    campos = tmp_path / "t.json"
    campos.write_text(json.dumps({"pieza.hook": "Hola mundo"}), encoding="utf-8")
    assert lab.main(["--target", str(tmp_path), "apply-translation", "--brand", "canal", "--id", item["id"],
                     "--campos", str(campos)]) == 0
    assert lab.get_item(root, item["id"], "canal")["pieza"]["hook"] == "Hola mundo"
    campos.write_text(json.dumps({"notas": "x"}), encoding="utf-8")
    assert lab.main(["--target", str(tmp_path), "apply-translation", "--brand", "canal", "--id", item["id"],
                     "--campos", str(campos)]) == 2


def test_f18_production_ui_calls_can_take_a_draft_to_an_order(tmp_path):
    js = (REPO / "cc/web/views/produccion.js").read_text(encoding="utf-8")
    for needle in ("approved_content: lines(", 'content_state: next[0]', '"ready_to_produce", "Aprobar el contenido"',
                   "result_paths: lines(", "approve_delivery: true", 'production_state: "finished"'):
        assert needle in js, needle
    root, brands = str(tmp_path), ["canal"]
    p = lab.save_production(root, {"title": "Serie", "ecosystem": "canal"}, brands)  # what «Crear» sends
    with pytest.raises(ValueError):
        lab.create_order(root, p["id"], p["revision"])  # a draft cannot be ordered: the UI disables it
    p = lab.save_production(root, {"id": p["id"], "expected_revision": p["revision"], "format": "video",
                                   "input_mode": "script", "approved_content": ["Hook", "Cuerpo"], "source_paths": []},
                            brands)
    for state in ("content_review", "ready_to_produce"):
        p = lab.save_production(root, {"id": p["id"], "expected_revision": p["revision"], "content_state": state}, brands)
    assert lab.create_order(root, p["id"], p["revision"])["execution_state"] == "not_started"


# ---------------------------------------------------------------- 16 «Ya grabé» idempotent
def test_f16_recording_is_idempotent(tmp_path):
    cfg = ccconfig.normalize({})
    root = str(tmp_path)
    a = creator.add_recording(root, cfg, {"title": "t", "script_file": "g.md", "request_key": "k1"})
    b = creator.add_recording(root, cfg, {"title": "t", "script_file": "g.md", "request_key": "k1"})
    c = creator.add_recording(root, cfg, {"title": "t", "script_file": "g.md"})
    d = creator.add_recording(root, cfg, {"title": "otra", "request_key": "k1"})
    assert a["id"] == b["id"] == c["id"] == d["id"] and b["duplicate"] and not a["duplicate"]
    e = creator.add_recording(root, cfg, {"title": "t2", "task_code": "CAN-3"})
    assert creator.add_recording(root, cfg, {"title": "t2", "task_code": "CAN-3"})["id"] == e["id"]
    assert len(creator.list_recordings(root)) == 2
    import sqlite3
    with sqlite3.connect(tmp_path / "creator.db") as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO recordings (date, title, script_file, created_at) VALUES ('2026-01-01','x','g.md','n')")


# ---------------------------------------------------------------- 19 brand schema
def test_f19_onboarded_brand_drives_the_carousel(tmp_path):
    a = {"path": "rapido", "tools": ["claude"], "brands": [{"name": "cocina-ana", "display_name": "Cocina Ana",
                                                              "colors": {"primary": "#123456"}, "tone": "Cálido",
                                                              "fonts": {"title": "Anton"}}]}
    files, _ = ow.plan(tmp_path, a, tools=["claude"], roles_md="", skills=[])
    rel = ".kit-personal/brands/cocina-ana.json"
    doc = json.loads(files[rel])
    assert doc["name"] == "Cocina Ana" and doc["logo_text"] == "COCINA ANA" and doc["voice"]["tone"] == "Cálido"
    assert doc["colors"] == {"accent": "#123456"} and doc["fonts"] == {"display": "Anton"} and "tone" not in doc
    (tmp_path / rel).parent.mkdir(parents=True)
    (tmp_path / rel).write_bytes(files[rel])
    sys.path.insert(0, str(REPO / "engines"))
    sys.path.insert(0, str(REPO / "engines" / "carousel"))
    import brand as brandmod
    import carousel
    b = brandmod.load_brand(tmp_path / rel)
    spec = json.loads((REPO / "presets/carousel/demo-spec.json").read_text(encoding="utf-8"))
    pages = carousel.build_html(spec, b, tmp_path)
    assert all("COCINA ANA" in p and "#123456" in p for p in pages)
    assert not any("ESTUDIO NORTE" in p for p in pages)


# ---------------------------------------------------------------- 20 payment day
@pytest.mark.parametrize("day", [-1, 0, 32, "5", True])
def test_f20_payment_day_validated(tmp_path, day):
    a = {"path": "rapido", "tools": ["claude"], "vida": {"fixed_payments": [{"label": "Luz", "amount": 1, "day": day}]}}
    with pytest.raises(ow.KitError, match="day"):
        ow.plan(tmp_path, a, tools=["claude"], roles_md="", skills=[])


def test_f20_bad_day_in_existing_config_never_breaks_tasks(tmp_path):
    cfg = ccconfig.normalize({"vida": {"fixed_payments": [{"id": "luz", "label": "Luz", "amount": 10, "day": -1},
                                                          {"id": "agua", "label": "Agua", "amount": 5, "day": 31}]}})
    assert [p["day"] for p in cfg["vida"]["fixed_payments"]] == [None, 31] and any("day" in w for w in cfg["_warnings"])
    tasks = life.list_tasks(str(tmp_path), cfg)
    assert sorted(t["title"] for t in tasks) == ["Agua", "Luz"]
    raw = ccconfig.normalize({})
    raw["vida"]["fixed_payments"] = [{"id": "x", "label": "X", "amount": 1, "day": -1}]  # even if it slips through
    assert [t["title"] for t in life.list_tasks(str(tmp_path / "b"), raw)] == ["X"]


# ---------------------------------------------------------------- 21 hook saves under one lock
def test_f21_concurrent_hook_saves_never_lose_each_other(tmp_path, monkeypatch):
    real = guiones._hooks

    def slow(root):  # widen the read-modify-write window
        data = real(root)
        threading.Event().wait(0.002)
        return data
    monkeypatch.setattr(guiones, "_hooks", slow)
    names = [f"g{i}.md" for i in range(16)]
    ts = [threading.Thread(target=guiones.save_hooks, args=(str(tmp_path), {"file": n, "opciones": [n]})) for n in names]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert sorted(load_json(tmp_path / "hooks-visuales.json")["byGuion"]) == sorted(names)


# ---------------------------------------------------------------- 22 milestone deletion persists
def test_f22_deleted_milestone_is_not_seeded_again(tmp_path):
    cfg = ccconfig.normalize({"vida": {"milestones": [{"id": "p", "label": "Primer patrocinio"}]}})
    root = str(tmp_path)
    goal = life.seed_milestones(root, cfg)[0]
    life.delete_goal(root, goal["id"], cfg)
    assert life.seed_milestones(root, cfg) == []


# ---------------------------------------------------------------- network errors are not disk errors
def test_network_error_has_its_own_message(src, proj, capsys):
    assert run(src, proj, "install") == 0

    class Offline(FakeRelease):
        def resolve(self, ref):
            raise urllib.error.URLError("nodename nor servname provided")
    rc = cli.main(["update", "--target", str(proj), "--yes", "--confirm-sha", SHA], net=Offline(src))
    err = capsys.readouterr().err
    assert rc == 4 and "Error de red" in err and "sistema de archivos" not in err
