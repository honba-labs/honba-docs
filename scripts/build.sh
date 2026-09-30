#!/usr/bin/env bash
# Build the documentation.
#
#   ./scripts/build.sh            # build both MkDocs and mdBook
#   ./scripts/build.sh --mkdocs   # only MkDocs
#   ./scripts/build.sh --mdbook   # only mdBook
#   ./scripts/build.sh --no-strict
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_common.sh
source "${SCRIPT_DIR}/_common.sh"

DO_MKDOCS=1
DO_MDBOOK=1
STRICT=1
for arg in "$@"; do
  case "$arg" in
    --mkdocs)    DO_MDBOOK=0 ;;
    --mdbook)    DO_MKDOCS=0 ;;
    --no-strict) STRICT=0 ;;
    -h|--help)
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown argument: $arg" ;;
  esac
done

cd "$DOCS_ROOT"

if [[ "$DO_MKDOCS" -eq 1 ]]; then
  [[ -d "$VENV_DIR" ]] || die "no venv; run ./scripts/bootstrap.sh first"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"

  args=(build)
  [[ "$STRICT" -eq 1 ]] && args+=(--strict)

  log "mkdocs ${args[*]}"
  mkdocs "${args[@]}"
  log "MkDocs output: ${DOCS_ROOT}/site/"
fi

if [[ "$DO_MDBOOK" -eq 1 ]]; then
  if ! ensure_mdbook; then
    warn "skipping mdBook build"
  else
    log "mdbook build book/"
    mdbook build "${DOCS_ROOT}/book"
    log "mdBook output: ${DOCS_ROOT}/book/build/"
  fi
fi

log "Build complete."
