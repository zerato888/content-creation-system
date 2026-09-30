# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""A fresh Mac's python3 is Apple's 3.9: the launcher and every hook must at least run under it
(the launcher then re-execs into the kit's own venv; hooks stay stdlib and fail open)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
OLD = Path("/usr/bin/python3")


def _old_is_39():
    if not OLD.is_file():
        return False
    r = subprocess.run([str(OLD), "-c", "import sys; print(sys.version_info[:2] < (3, 10))"], capture_output=True, text=True)
    return r.stdout.strip() == "True"


pytestmark = pytest.mark.skipif(sys.platform != "darwin" or not _old_is_39(), reason="no Apple python 3.9 here")


def test_launcher_parses_on_39():
    r = subprocess.run([str(OLD), str(REPO / "launch.py"), "--help"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("hook", sorted(p.name for p in (REPO / "hooks").glob("*.py") if p.name != "_common.py"))
def test_hook_runs_on_39(hook, tmp_path):
    payload = json.dumps({"prompt": "hola", "tool_name": "Bash", "tool_input": {"command": "ls"}})
    r = subprocess.run([str(OLD), str(REPO / "hooks" / hook)], input=payload, capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0 and "Traceback" not in r.stderr, (hook, r.stderr[-300:])
