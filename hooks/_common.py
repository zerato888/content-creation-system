# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Shared bits for the kit hooks (Claude Code and Codex). Stdlib only, Windows-safe.

Every hook is fail-open: any error -> exit 0 and no output, so a broken hook never blocks work.
Installed at TARGET/.kit/hooks/, so the project root is two levels up from this file.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP = 4000


def event() -> dict:
    """The JSON the tool sends on stdin ({} if none or unreadable)."""
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def read(rel: str) -> str:
    p = ROOT / rel
    try:
        if p.is_symlink() or not p.is_file():
            return ""
        return p.read_text(encoding="utf-8", errors="replace")[:CAP * 4]
    except OSError:
        return ""


def say(text: str) -> None:
    """Plain stdout: both tools add it to the model's context for SessionStart / UserPromptSubmit."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(text[:CAP])


def run(main) -> None:
    try:
        code = main() or 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 0
    except Exception:
        code = 0  # fail-open
    sys.exit(code)
