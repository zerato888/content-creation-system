#!/usr/bin/env bash
# Validates that required keys are present in a .env file.
# Usage: ./setup-env.sh <path-to-.env> KEY_ONE KEY_TWO ...
set -euo pipefail

ENV_FILE="${1:?Usage: setup-env.sh <path-to-.env> KEY_ONE KEY_TWO ...}"
shift
REQUIRED_KEYS=("$@")

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE not found. Copy .env.example to .env first:"
  echo "   cp $(dirname "$ENV_FILE")/.env.example $ENV_FILE"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MISSING=0

for KEY in "${REQUIRED_KEYS[@]}"; do
  VALUE=$(grep -E "^${KEY}=" "$ENV_FILE" | tail -n1 | cut -d'=' -f2- || true)
  if [ -z "$VALUE" ]; then
    echo "❌ $KEY is missing or empty in $ENV_FILE"
    MISSING=1
  else
    echo "✅ $KEY is set"
  fi
done

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "Add the missing key(s) above to $ENV_FILE, then re-run this script."
  exit 1
fi

echo ""
echo "All required keys present. You're ready to run this skill."
