#!/usr/bin/env bash
# Remove build artifacts.
#
#   ./scripts/clean.sh         # remove site/ and book/build/
#   ./scripts/clean.sh --venv  # also remove .venv
#   ./scripts/clean.sh --all   # everything including __pycache__
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_common.sh
source "${SCRIPT_DIR}/_common.sh"

RM_VENV=0
ALL=0
for arg in "$@"; do
  case "$arg" in
    --venv) RM_VENV=1 ;;
    --all)  RM_VENV=1; ALL=1 ;;
    -h|--help)
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown argument: $arg" ;;
  esac
done

cd "$DOCS_ROOT"

for d in site book/build; do
  if [[ -d "$d" ]]; then
    log "removing $d"
    rm -rf "$d"
  fi
done

if [[ "$ALL" -eq 1 ]]; then
  log "removing __pycache__ and .pyc"
  find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  find . -type f -name '*.pyc' -delete 2>/dev/null || true
fi

if [[ "$RM_VENV" -eq 1 && -d "$VENV_DIR" ]]; then
  log "removing $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

log "Clean complete."
