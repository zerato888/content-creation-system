#!/bin/sh
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
# Content kit installer (macOS / Linux). Source: https://github.com/zerato888/content-creation-system
# Usage: ./install.sh install [--target DIR] [--yes] [--answers FILE] [--dry-run] [--module X]
#        ./install.sh update [--to TAG] | uninstall | status | rollback | service on|off|status | cache-clean | migrate-brands
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
py=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
    py=$c; break
  fi
done
if [ -z "$py" ]; then
  echo "Error: hace falta Python 3.11 o más nuevo y no lo encontré." >&2
  echo "Instalalo desde https://www.python.org/downloads/ y volvé a correr este comando." >&2
  exit 127
fi
PYTHONPATH="$here${PYTHONPATH:+:$PYTHONPATH}" PYTHONUTF8=1 exec "$py" -m installer "$@"
