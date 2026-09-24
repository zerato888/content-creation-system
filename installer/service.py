# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Always-on Command Center: a per-user LaunchAgent (macOS) or a logon Scheduled Task (Windows).

The only thing the kit writes outside the project, and only with consent. Restart-on-failure
comes from the OS (KeepAlive / task restart settings): no second watchdog process.
All OS calls go through `run` so tests can mock them.
"""
from __future__ import annotations

import hashlib
import os
import plistlib
import subprocess
import sys
from pathlib import Path

from .core import KitError

PREFIX = "com.contentkit.cc."
PLATFORM = "mac" if sys.platform == "darwin" else "windows" if os.name == "nt" else "other"


def run(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=60)


def label(root: Path) -> str:
    return os.environ.get("KIT_SERVICE_LABEL") or PREFIX + hashlib.sha256(str(root).encode()).hexdigest()[:12]


def python_exe(root: Path) -> str:
    venv = root / ".kit" / "venv" / ("Scripts/pythonw.exe" if os.name == "nt" else "bin/python")
    return str(venv) if venv.is_file() else sys.executable


def argv(root: Path) -> list[str]:
    # the kit launcher with the project's own Python: same entry point as `python .kit/launch.py serve`
    return [python_exe(root), str(root / ".kit" / "launch.py"), "serve", "--no-print-url"]


def _plist(lbl: str) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{lbl}.plist"


def _gui() -> str:
    return f"gui/{getattr(os, 'getuid', lambda: 0)()}"


def _ps(script: str) -> list[str]:
    return ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]


def _q(s: str) -> str:  # PowerShell single-quoted literal
    return "'" + s.replace("'", "''") + "'"


def record(root: Path) -> dict:
    """The manifest record `install` will produce, known before anything is registered."""
    lbl = label(root)
    if PLATFORM == "mac":
        return {"kind": "launchagent", "label": lbl, "path": "~/Library/LaunchAgents/" + _plist(lbl).name}
    if PLATFORM == "windows":
        return {"kind": "schtask", "label": lbl}
    raise KitError("el servicio siempre encendido solo existe en macOS y Windows")


def install(root: Path) -> dict:
    """Register and start. Returns the manifest record."""
    lbl, cmd = label(root), argv(root)
    for rel in (("cc", "server", "app.py"), ("launch.py",)):
        if not (root / ".kit").joinpath(*rel).is_file():
            raise KitError(f"no encuentro .kit/{'/'.join(rel)}; instalá el kit primero")
    if PLATFORM == "mac":
        p = _plist(lbl)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(plistlib.dumps({
            "Label": lbl, "ProgramArguments": cmd, "WorkingDirectory": str(root),
            "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False}, "ThrottleInterval": 10,
            "StandardOutPath": str(root / ".kit" / "cc.service.log"),
            "StandardErrorPath": str(root / ".kit" / "cc.service.log")}))
        run(["launchctl", "bootout", f"{_gui()}/{lbl}"])  # idempotent re-install
        r = run(["launchctl", "bootstrap", _gui(), str(p)])
        if r.returncode != 0:
            p.unlink(missing_ok=True)
            raise KitError(f"launchctl no aceptó el servicio: {r.stderr.strip()[:200]}")
        return record(root)
    if PLATFORM == "windows":
        script = (
            f"$a = New-ScheduledTaskAction -Execute {_q(cmd[0])} -Argument {_q(subprocess.list2cmdline(cmd[1:]))} "
            f"-WorkingDirectory {_q(str(root))}; "
            "$t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; "
            "$s = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) "
            "-ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries; "
            f"Register-ScheduledTask -TaskName {_q(lbl)} -Action $a -Trigger $t -Settings $s -Force | Out-Null; "
            f"Start-ScheduledTask -TaskName {_q(lbl)}")
        r = run(_ps(script))
        if r.returncode != 0:
            raise KitError(f"no pude crear la tarea programada: {r.stderr.strip()[:200]}")
        return record(root)
    raise KitError("el servicio siempre encendido solo existe en macOS y Windows")


def remove(rec: dict) -> None:
    """Stop and unregister, then check the OS really forgot it. Missing service = already removed.
    Raises KitError (and leaves the plist) when the service is still registered."""
    lbl = rec["label"]
    if rec["kind"] == "launchagent":
        r = run(["launchctl", "bootout", f"{_gui()}/{lbl}"])
        if status(rec) != "no registrado":
            raise KitError(f"launchctl no quitó el servicio {lbl}: {(r.stderr or '').strip()[:200]}")
        _plist(lbl).unlink(missing_ok=True)
    elif rec["kind"] == "schtask":
        r = run(_ps(f"Stop-ScheduledTask -TaskName {_q(lbl)} -ErrorAction SilentlyContinue; "
                    f"Unregister-ScheduledTask -TaskName {_q(lbl)} -Confirm:$false -ErrorAction SilentlyContinue"))
        if status(rec) != "no registrado":
            raise KitError(f"no pude quitar la tarea programada {lbl}: {(r.stderr or '').strip()[:200]}")
    else:
        raise KitError(f"tipo de servicio desconocido: {rec.get('kind')!r}")


def status(rec: dict) -> str:
    lbl = rec["label"]
    if rec["kind"] == "launchagent":
        r = run(["launchctl", "print", f"{_gui()}/{lbl}"])
        if r.returncode != 0:
            return "no registrado"
        return "corriendo" if "state = running" in r.stdout else "registrado, detenido"
    r = run(_ps(f"(Get-ScheduledTask -TaskName {_q(lbl)} -ErrorAction Stop).State"))
    return (r.stdout.strip() or "no registrado") if r.returncode == 0 else "no registrado"
