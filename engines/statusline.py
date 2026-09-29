#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Barra de estado de Claude Code con el uso REAL de contexto (lee el último uso de la API del
historial de la sesión, no una estimación). Python estándar: anda en Mac, Linux y Windows.

Activar (una vez), en `.claude/settings.json` del proyecto o en el global:
  "statusLine": {"type": "command", "command": "python .kit/engines/statusline.py"}
Ventana por defecto 200000 tokens; para otra, variable KIT_CTX_WINDOW (ej. 1000000).
Solo Claude Code (Codex no tiene barra de estado configurable).
"""
import json
import os
import sys


def last_usage(transcript: str):
    """(tokens del último turno del asistente, cantidad de turnos)."""
    tokens = turns = 0
    with open(transcript, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            u = (o.get("message") or {}).get("usage") if o.get("type") == "assistant" else None
            if isinstance(u, dict):
                turns += 1
                tokens = sum(int(u.get(k) or 0) for k in
                             ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return tokens, turns


def render(data: dict, window: int) -> str:
    tokens = turns = 0
    tp = data.get("transcript_path")
    if isinstance(tp, str) and os.path.isfile(tp):
        try:
            tokens, turns = last_usage(tp)
        except OSError:
            pass
    pct = min(100, tokens * 100 // window) if window > 0 else 0
    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
    m = data.get("model") or {}
    model = m.get("display_name") or m.get("id") or "Claude"
    return f"CTX {bar} {pct}% ({tokens:,} tokens) · turno {turns} · {model}"


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if not isinstance(data, dict):
            data = {}
    except ValueError:
        data = {}
    try:
        window = int(os.environ.get("KIT_CTX_WINDOW", "200000"))
    except ValueError:
        window = 200000
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(render(data, window))
    return 0


if __name__ == "__main__":
    sys.exit(main())
