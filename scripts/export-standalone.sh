#!/usr/bin/env bash
# Export scaffold/agent-memory as a standalone git repository folder.
#
# Usage (from Stock Scanner repo):
#   ./scaffold/agent-memory/scripts/export-standalone.sh ../agent-memory
#   cd ../agent-memory && git init && git add . && git commit -m "Initial template"
#
# Or from inside agent-memory template repo:
#   ./scripts/export-standalone.sh /tmp/agent-memory-export

set -euo pipefail

DEST="${1:-export/agent-memory-standalone}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$SOURCE/apply.py" ]]; then
  echo "export-standalone: apply.py not found in $SOURCE" >&2
  exit 1
fi

mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude '.git/' \
    --exclude 'export/' \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '*.pyc' \
    "$SOURCE/" "$DEST/"
else
  rm -rf "$DEST"/*
  (cd "$SOURCE" && tar cf - .) | (cd "$DEST" && tar xf -)
fi

chmod +x "$DEST/install.sh" "$DEST/apply.py" "$DEST/register_subsystem.py" \
  "$DEST/bin/agent-memory" 2>/dev/null || true

VERSION="$(cat "$SOURCE/VERSION" 2>/dev/null || echo dev)"
cat > "$DEST/EXPORTED_FROM.txt" <<EOF
Exported: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Source: $SOURCE
Version: $VERSION

Next steps:
  1. Edit config/install.defaults.env — set v3gaS/agent-memory.git
  2. git init && git add . && git commit -m "Initial agent-memory template v$VERSION"
  3. Create GitHub repo and push
  4. Settings → check "Template repository"
  5. Update README curl one-liners with real org/repo
EOF

echo "export-standalone: wrote $DEST"
echo "  see $DEST/EXPORTED_FROM.txt"
