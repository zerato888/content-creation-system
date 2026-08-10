#!/usr/bin/env bash
set -euo pipefail

mkdir -p wiki/entities wiki/concepts outputs
touch wiki/index.md wiki/log.md

if [ ! -f config.json ]; then
  cat > config.json <<'EOF'
{
  "default_route": "short-form-reel",
  "default_duration_seconds": 45,
  "output_dir": "outputs"
}
EOF
fi

if [ ! -f lessons.md ]; then
  cp ../../shared/memory-system/template-lessons.md lessons.md
fi

echo "Project initialized: wiki/, outputs/, config.json, lessons.md"
