#!/bin/sh
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
# Content kit installer (macOS / Linux). Source: https://github.com/zerato888/content-creation-system
# Usage: ./install.sh install [--target DIR] [--yes] [--answers FILE] [--dry-run] [--module X]
#        ./install.sh update [--to TAG] | uninstall | status | rollback | service on|off|status | cache-clean | migrate-brands
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
py=""
# 3.11-3.13 only: some pinned wheels (onnxruntime for subtitles) do not exist yet for newer Pythons.
for c in python3.12 python3.13 python3.11 /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(not ((3, 11) <= sys.version_info[:2] <= (3, 13)))' 2>/dev/null; then
    py=$c; break
  fi
done
if [ -z "$py" ]; then
  echo "Error: hace falta Python 3.11, 3.12 o 3.13 y no lo encontré." >&2
  echo "En Mac: brew install python@3.12  (https://brew.sh) y volvé a correr este comando." >&2
  exit 127
fi
PYTHONPATH="$here${PYTHONPATH:+:$PYTHONPATH}" PYTHONUTF8=1 exec "$py" -m installer "$@"
