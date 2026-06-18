#!/usr/bin/env bash
# Create GitHub template repo from exported standalone folder.
#
# Prerequisites: gh auth login, exported folder (see export-standalone.sh)
#
# Usage:
#   ./scripts/publish-github.sh YOUR_ORG/agent-memory ../agent-memory
#   ./scripts/publish-github.sh YOUR_ORG/agent-memory   # exports to ../agent-memory first

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REPO="${1:?Usage: publish-github.sh ORG/REPO [EXPORT_DIR]}"
EXPORT_DIR="${2:-$(dirname "$ROOT")/agent-memory}"

if [[ ! -f "$EXPORT_DIR/apply.py" ]]; then
  echo "Export dir missing apply.py — running export-standalone.sh ..."
  "$ROOT/scripts/export-standalone.sh" "$EXPORT_DIR"
fi

ORG="${REPO%%/*}"
NAME="${REPO##*/}"

echo "Replacing YOUR_ORG with $ORG in exported tree ..."
if command -v rg >/dev/null 2>&1; then
  rg -l 'YOUR_ORG' "$EXPORT_DIR" | while read -r f; do
    sed -i.bak "s/YOUR_ORG/$ORG/g" "$f" && rm -f "$f.bak"
  done
else
  grep -rl 'YOUR_ORG' "$EXPORT_DIR" | while read -r f; do
    sed -i.bak "s/YOUR_ORG/$ORG/g" "$f" && rm -f "$f.bak"
  done
fi

cd "$EXPORT_DIR"
if [[ ! -d .git ]]; then
  git init
  git branch -M main
fi

git add .
git commit -m "Initial agent-memory template v$(cat VERSION 2>/dev/null || echo 0.1.0)" --allow-empty

if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "Repo exists — pushing ..."
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$REPO.git"
  git push -u origin main
else
  echo "Creating $REPO ..."
  gh repo create "$REPO" --public --source=. --remote=origin --push
fi

echo ""
echo "Done. Enable template repo: GitHub → $REPO → Settings → Template repository"
echo "Install: curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | bash -s -- --target ."
