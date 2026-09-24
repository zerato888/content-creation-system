# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Tests never touch the real OS service manager and see both tools unless a test says otherwise."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from installer import ow, service  # noqa: E402


@pytest.fixture(autouse=True)
def fake_os(monkeypatch, tmp_path):
    calls = []
    registered = set()  # a tiny fake service manager: status follows register/unregister

    def run(argv):
        calls.append(argv)
        text = " ".join(argv)
        if argv[:2] == ["launchctl", "bootstrap"]:
            registered.add(Path(argv[-1]).stem)
        elif argv[:2] == ["launchctl", "bootout"]:
            registered.discard(argv[-1].rsplit("/", 1)[-1])
        elif argv[:2] == ["launchctl", "print"]:
            ok = argv[-1].rsplit("/", 1)[-1] in registered
            return subprocess.CompletedProcess(argv, 0 if ok else 113, "state = running\n" if ok else "", "")
        elif "Register-ScheduledTask -TaskName" in text and "Unregister" not in text:
            registered.add(text.split("Register-ScheduledTask -TaskName '", 1)[1].split("'", 1)[0])
        elif "Unregister-ScheduledTask" in text:
            registered.discard(text.split("Unregister-ScheduledTask -TaskName '", 1)[1].split("'", 1)[0])
        elif "Get-ScheduledTask" in text:
            ok = text.split("-TaskName '", 1)[1].split("'", 1)[0] in registered
            return subprocess.CompletedProcess(argv, 0 if ok else 1, "Ready\n" if ok else "", "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(service, "run", run)
    monkeypatch.setattr(service, "_plist", lambda lbl: tmp_path / "LaunchAgents" / f"{lbl}.plist")
    monkeypatch.setattr(service, "PLATFORM", "mac")
    monkeypatch.setattr(ow, "detect_tools", lambda: ["claude", "codex"])
    return calls
