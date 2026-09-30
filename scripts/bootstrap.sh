#!/usr/bin/env bash
# Create .venv, install Python docs deps, and (optionally) the mdBook toolchain.
#
#   ./scripts/bootstrap.sh            # python deps only
#   ./scripts/bootstrap.sh --rust     # also cargo install mdbook tooling
#   ./scripts/bootstrap.sh --dev      # install dev extras (requirements-dev.txt)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_common.sh
source "${SCRIPT_DIR}/_common.sh"

WITH_RUST=0
WITH_DEV=0
for arg in "$@"; do
  case "$arg" in
    --rust) WITH_RUST=1 ;;
    --dev)  WITH_DEV=1 ;;
    -h|--help)
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown argument: $arg" ;;
  esac
done

cd "$DOCS_ROOT"

check_python
ensure_venv

REQ="requirements.txt"
[[ "$WITH_DEV" -eq 1 ]] && REQ="requirements-dev.txt"

log "Installing ${REQ}"
python -m pip install -r "$REQ"

if [[ "$WITH_RUST" -eq 1 ]]; then
  has_rust_toolchain || die "cargo not found; install Rust first (https://rustup.rs)"
  log "Installing mdBook toolchain via cargo (this may take a few minutes)"
  cargo install mdbook mdbook-linkcheck mdbook-rustdoc-links --locked
else
  ensure_mdbook || warn "Skipping mdBook toolchain install (use --rust to add)"
fi

log "Bootstrap complete."
log "Activate with:  source .venv/bin/activate"
