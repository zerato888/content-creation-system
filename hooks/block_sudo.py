#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""PreToolUse (shell): refuse commands that ask for administrator rights. Safe default hook.

Blocks with exit code 2 and a reason on stderr (both Claude Code and Codex show it to the model).
Anything unexpected -> exit 0 (fail-open).
"""
import re
import sys

from _common import event, run

ELEVATE = re.compile(r"(^|[\s;&|()`$])(su" r"do|doas|runas)(\s|$)", re.I)
NAMES = {"su" "do", "doas", "runas", "pkexec"}
# wrappers that run the next word as the command (with the options they take before it)
WRAPPERS = {"env", "command", "exec", "nohup", "time", "nice", "builtin", "xargs", "timeout", "stdbuf",
            "setsid", "chronic", "caffeinate"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish", "cmd", "powershell", "pwsh"}
SPLIT = re.compile(r"\|\||&&|[;&|\n()`]|\$\(")
WORD = re.compile(r"(?:'[^']*'|\"(?:\\.|[^\"])*\"|\\.|[^\s'\"\\])+")
UNQUOTE = re.compile(r"'([^']*)'|\"((?:\\.|[^\"])*)\"|\\(.)")


def _words(part: str) -> list[str]:
    """Shell words with quotes removed ('su''do' and "su"do are one word). Stdlib re only."""
    return [UNQUOTE.sub(lambda m: next((g for g in m.groups() if g is not None), ""), w)
            for w in WORD.findall(part.replace("\\", "/"))]  # Windows paths keep their name


def _exe(tok: str) -> str:
    name = tok.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith((".exe", ".cmd", ".bat")) else name


def elevates(cmd: str, depth: int = 0) -> bool:
    """True if any simple command in `cmd` runs an elevation tool, however it is spelled:
    quoted ('su''do'), by absolute path (/usr/bin/...), after VAR=x, or behind env/command/exec/..."""
    if ELEVATE.search(cmd):
        return True
    for part in SPLIT.split(cmd):
        toks = _words(part)
        i = 0
        while i < len(toks):
            t = toks[i]
            name = _exe(t)
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", t) or t.startswith("-") or re.fullmatch(r"[0-9.]+[smhd]?", t):
                i += 1  # VAR=value, a wrapper's option, or a number (nice -n 5, timeout 10)
                continue
            if name in NAMES:
                return True
            if name in SHELLS and depth < 3:
                rest = toks[i + 1:]
                for j, x in enumerate(rest):
                    if x.lower() in ("-c", "/c", "-command", "-lc") and j + 1 < len(rest):
                        return elevates(" ".join(rest[j + 1:]), depth + 1)
                break
            if name in WRAPPERS:
                i += 1
                continue
            break  # the real command of this part is something else
    return False


def main():
    ev = event()
    tool = ev.get("tool_input") or {}
    cmd = tool.get("command") if isinstance(tool, dict) else None
    if isinstance(cmd, list):
        cmd = " ".join(str(x) for x in cmd)
    if isinstance(cmd, str) and elevates(cmd):
        print("Bloqueado por el kit: no se corren comandos con permisos de administrador. "
              "Si de verdad hace falta, pedile a la persona que lo corra ella en su terminal.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    run(main)
