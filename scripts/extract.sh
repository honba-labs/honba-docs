#!/usr/bin/env bash
# Extract runnable Python from docs/tutorials/*.md into examples/tutorials/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_common.sh
source "${SCRIPT_DIR}/_common.sh"

cd "$DOCS_ROOT"

if [[ -d "$VENV_DIR" ]]; then
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
fi

log "extracting tutorials -> examples/tutorials/"
exec python3 "${SCRIPT_DIR}/extract_tutorials.py" "$@"
