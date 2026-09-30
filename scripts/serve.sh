#!/usr/bin/env bash
# Serve docs locally.
#
#   ./scripts/serve.sh            # mkdocs live-reload on :8000
#   ./scripts/serve.sh --mdbook   # serve built mdBook on :8001
#   ./scripts/serve.sh --port 9000
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_common.sh
source "${SCRIPT_DIR}/_common.sh"

MODE="mkdocs"
PORT=8000
for ((i=1; i<=$#; i++)); do
  arg="${!i}"
  case "$arg" in
    --mdbook) MODE="mdbook" ;;
    --mkdocs) MODE="mkdocs" ;;
    --port)
      j=$((i+1)); PORT="${!j}"; i=$j ;;
    -h|--help)
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown argument: $arg" ;;
  esac
done

cd "$DOCS_ROOT"

if [[ "$MODE" == "mkdocs" ]]; then
  [[ -d "$VENV_DIR" ]] || die "no venv; run ./scripts/bootstrap.sh first"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  log "mkdocs serve on http://127.0.0.1:${PORT}/"
  exec mkdocs serve --dev-addr "127.0.0.1:${PORT}"
fi

ensure_mdbook || die "mdbook not installed"
log "Building mdBook then serving ${DOCS_ROOT}/book/build on :${PORT}"
mdbook build "${DOCS_ROOT}/book"
exec python3 -m http.server "$PORT" --directory "${DOCS_ROOT}/book/build"
