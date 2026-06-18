#!/usr/bin/env bash
# Agent Memory — install into an existing or new project directory.
# Version: see VERSION in repo root
# Local (from cloned template repo):
#   ./install.sh --target /path/to/project
#
# Remote one-liner (after publishing standalone repo — set YOUR_ORG):
#   curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/agent-memory/main/install.sh | bash -s -- --target .
#
# Non-interactive:
#   ./install.sh --target . --yes --project-name "My App" --stack "Next.js" \
#     --primary-config .env --src-root src/ --test-command "npm test"
#
# Environment:
#   AGENT_MEMORY_INSTALL_REPO   git URL (default from config/install.defaults.env)
#   AGENT_MEMORY_INSTALL_REF    branch/tag (default: main)
#   AGENT_MEMORY_SCAFFOLD_ROOT  use existing checkout (skip clone)

set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

# shellcheck disable=SC1091
[[ -f "$SCRIPT_DIR/config/install.defaults.env" ]] && source "$SCRIPT_DIR/config/install.defaults.env"

AGENT_MEMORY_INSTALL_REPO="${AGENT_MEMORY_INSTALL_REPO:-https://github.com/YOUR_ORG/agent-memory.git}"
AGENT_MEMORY_INSTALL_REF="${AGENT_MEMORY_INSTALL_REF:-main}"

TARGET=""
CONFIG=""
LOCAL=""
FORCE=""
NO_VERIFY=""
NO_PROMPT=""
YES=""
CLONE_TMP=""
PRESET=""

PROJECT_NAME=""
STACK=""
PRIMARY_CONFIG=""
SRC_ROOT=""
TEST_COMMAND=""

usage() {
  cat <<'EOF'
Usage: install.sh --target PATH [options]

Required:
  --target PATH          Project directory to bootstrap (created if missing)

Options:
  --local                Use this repo checkout (do not git clone)
  --repo URL             Template git URL for remote install
  --ref REF              Git ref (branch/tag), default: main
  --config FILE          agent_memory.project.yaml passed to apply.py
  --yes                  Non-interactive (requires --project-name or --config)
  --force                Overwrite existing scaffold files
  --no-verify            Skip post-install docs_integrity + pytest
  --preset NAME          Stack preset: python|node|go|rust (sets defaults)
  --project-name NAME
  --stack TEXT           One-line stack summary
  --primary-config PATH  e.g. config/settings.yaml or .env
  --src-root PATH        e.g. src/ or apps/api/
  --test-command CMD     e.g. pytest -q, npm test, go test ./...
  -h, --help

Examples:
  ./install.sh --target ../my-app
  curl -fsSL .../install.sh | bash -s -- --target . --yes --preset node --project-name "My App"
EOF
}

cleanup() {
  if [[ -n "$CLONE_TMP" && -d "$CLONE_TMP" ]]; then
    rm -rf "$CLONE_TMP"
  fi
}
trap cleanup EXIT

log() { printf 'agent-memory: %s\n' "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

apply_preset() {
  case "$PRESET" in
    python)
      STACK="${STACK:-Python 3.12+ application}"
      PRIMARY_CONFIG="${PRIMARY_CONFIG:-config/settings.yaml}"
      SRC_ROOT="${SRC_ROOT:-src/}"
      TEST_COMMAND="${TEST_COMMAND:-pytest -q}"
      ;;
    node)
      STACK="${STACK:-Node.js / TypeScript application}"
      PRIMARY_CONFIG="${PRIMARY_CONFIG:-.env}"
      SRC_ROOT="${SRC_ROOT:-src/}"
      TEST_COMMAND="${TEST_COMMAND:-npm test}"
      ;;
    go)
      STACK="${STACK:-Go application}"
      PRIMARY_CONFIG="${PRIMARY_CONFIG:-config.yaml}"
      SRC_ROOT="${SRC_ROOT:-./}"
      TEST_COMMAND="${TEST_COMMAND:-go test ./...}"
      ;;
    rust)
      STACK="${STACK:-Rust application}"
      PRIMARY_CONFIG="${PRIMARY_CONFIG:-.env}"
      SRC_ROOT="${SRC_ROOT:-src/}"
      TEST_COMMAND="${TEST_COMMAND:-cargo test}"
      ;;
    "" ) ;;
    * ) die "unknown preset: $PRESET (python|node|go|rust)" ;;
  esac
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target) TARGET="$2"; shift 2 ;;
      --local) LOCAL=1; shift ;;
      --repo) AGENT_MEMORY_INSTALL_REPO="$2"; shift 2 ;;
      --ref) AGENT_MEMORY_INSTALL_REF="$2"; shift 2 ;;
      --config) CONFIG="$2"; shift 2 ;;
      --yes) YES=1; NO_PROMPT=1; shift ;;
      --force) FORCE=1; shift ;;
      --no-verify) NO_VERIFY=1; shift ;;
      --no-prompt) NO_PROMPT=1; shift ;;
      --preset) PRESET="$2"; shift 2 ;;
      --project-name) PROJECT_NAME="$2"; shift 2 ;;
      --stack) STACK="$2"; shift 2 ;;
      --primary-config) PRIMARY_CONFIG="$2"; shift 2 ;;
      --src-root) SRC_ROOT="$2"; shift 2 ;;
      --test-command) TEST_COMMAND="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument: $1 (try --help)" ;;
    esac
  done
  [[ -n "$TARGET" ]] || die "--target is required"
}

resolve_scaffold_root() {
  if [[ -n "${AGENT_MEMORY_SCAFFOLD_ROOT:-}" ]]; then
    echo "$AGENT_MEMORY_SCAFFOLD_ROOT"
    return
  fi
  if [[ -n "$LOCAL" ]] || [[ -f "$SCRIPT_DIR/apply.py" ]]; then
    echo "$SCRIPT_DIR"
    return
  fi
  need_cmd git
  CLONE_TMP="$(mktemp -d 2>/dev/null || mktemp -d -t agent-memory)"
  log "cloning $AGENT_MEMORY_INSTALL_REPO ($AGENT_MEMORY_INSTALL_REF) ..."
  git clone --depth 1 --branch "$AGENT_MEMORY_INSTALL_REF" "$AGENT_MEMORY_INSTALL_REPO" "$CLONE_TMP" \
    || die "git clone failed — set AGENT_MEMORY_INSTALL_REPO or use --local"
  echo "$CLONE_TMP"
}

ensure_python_tooling() {
  need_cmd python3
  if ! python3 -c "import yaml" 2>/dev/null; then
    log "installing PyYAML (user) ..."
    python3 -m pip install --user -q pyyaml || die "pip install pyyaml failed"
  fi
  if [[ -z "$NO_VERIFY" ]]; then
    if ! python3 -c "import pytest" 2>/dev/null; then
      log "installing pytest (user) for verification ..."
      python3 -m pip install --user -q pytest || die "pip install pytest failed"
    fi
  fi
}

run_apply() {
  local root="$1"
  local apply_py="$root/apply.py"
  [[ -f "$apply_py" ]] || die "apply.py not found in scaffold root: $root"

  local -a cmd=(python3 "$apply_py" --target "$TARGET")
  [[ -n "$CONFIG" ]] && cmd+=(--config "$CONFIG")
  [[ -n "$NO_PROMPT" ]] && cmd+=(--no-prompt)
  [[ -n "$FORCE" ]] && cmd+=(--force)
  [[ -n "$PROJECT_NAME" ]] && cmd+=(--project-name "$PROJECT_NAME")
  [[ -n "$STACK" ]] && cmd+=(--stack "$STACK")
  [[ -n "$PRIMARY_CONFIG" ]] && cmd+=(--primary-config "$PRIMARY_CONFIG")
  [[ -n "$SRC_ROOT" ]] && cmd+=(--src-root "$SRC_ROOT")
  [[ -n "$TEST_COMMAND" ]] && cmd+=(--test-command "$TEST_COMMAND")

  log "running apply.py → $TARGET"
  "${cmd[@]}"
}

run_verify() {
  [[ -z "$NO_VERIFY" ]] || return 0
  log "verifying docs integrity ..."
  (cd "$TARGET" && python3 scripts/docs_integrity.py)
  log "running docs regression tests ..."
  (cd "$TARGET" && python3 -m pytest tests/test_docs_integrity.py -q)
  log "verification passed"
}

main() {
  parse_args "$@"
  apply_preset

  if [[ -n "$YES" && -z "$CONFIG" && -z "$PROJECT_NAME" ]]; then
    PROJECT_NAME="$(basename "$(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")")"
    log "non-interactive: inferred project name '$PROJECT_NAME'"
  fi

  mkdir -p "$TARGET"
  TARGET="$(cd "$TARGET" && pwd)"

  ensure_python_tooling
  SCAFFOLD_ROOT="$(resolve_scaffold_root)"
  run_apply "$SCAFFOLD_ROOT"
  run_verify

  log "done — next: edit docs/ARCHITECTURE.md and docs/CORE.md"
  log "commit suggestion: chore: bootstrap agent memory doc system"
}

main "$@"
