#!/usr/bin/env bash
# Optional: sets up a local project structure for persistent carousel work.
set -euo pipefail

mkdir -p wiki/entities wiki/concepts outputs
touch wiki/index.md wiki/log.md

if [ ! -f config.json ]; then
  cat > config.json <<'EOF'
{
  "default_route": "generic",
  "default_slide_count": 6,
  "output_dir": "outputs"
}
EOF
fi

if [ ! -f lessons.md ]; then
  cp ../../shared/memory-system/template-lessons.md lessons.md
fi

echo "Project initialized: wiki/, outputs/, config.json, lessons.md"
