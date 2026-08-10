#!/usr/bin/env bash
# INTERNAL TOOL — not for public use. Run by the repo maintainer only,
# from their private content vault, to push generic improvements to
# templates and agents into this public repo.
#
# This script assumes a private source directory with brand-specific
# templates/agents that must be manually genericized before syncing —
# it does NOT auto-strip brand references. Review every diff before
# committing.
set -euo pipefail

VAULT_TEMPLATES_DIR="${VAULT_TEMPLATES_DIR:?Set VAULT_TEMPLATES_DIR to your private vault's templates path}"
VAULT_AGENTS_DIR="${VAULT_AGENTS_DIR:?Set VAULT_AGENTS_DIR to your private vault's agents path}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "This script copies files for MANUAL review — it does not auto-commit."
echo "Review every diff for brand/personal references before committing."
echo ""
echo "Suggested manual steps:"
echo "1. diff -r $VAULT_TEMPLATES_DIR $REPO_DIR/meta-skills/*/templates/"
echo "2. diff -r $VAULT_AGENTS_DIR $REPO_DIR/shared/agents/"
echo "3. Manually copy + genericize only what's safe to publish."
echo "4. Run the brand-leak grep check before committing:"
echo "   grep -riE 'gto|abstracto|sivanna|breaking.?facts|moody|nitelightz|zerato' $REPO_DIR --include='*.md' --include='*.py' --include='*.sh' --include='*.json'"
echo "5. git add -A && git commit -m 'sync: reviewed vault update' && git push"
