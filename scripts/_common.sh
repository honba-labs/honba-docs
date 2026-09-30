#!/usr/bin/env bash
# Shared helpers for honba-docs scripts. Source this; do not execute.

set -euo pipefail

# Resolve repo root regardless of where the script is invoked from.
DOCS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${DOCS_ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MIN_PY_MINOR=10
MIN_PY_MAJOR=3

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWARN:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

check_python() {
  command -v "$PYTHON_BIN" >/dev/null 2>&1 || \
    die "python3 not found; install Python ${MIN_PY_MAJOR}.${MIN_PY_MINOR}+ first"

  local ver
  ver="$("$PYTHON_BIN" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
  local major="${ver%%.*}" minor="${ver##*.}"

  if (( major < MIN_PY_MAJOR )) || \
     (( major == MIN_PY_MAJOR && minor < MIN_PY_MINOR )); then
    die "Python ${ver} found; need >= ${MIN_PY_MAJOR}.${MIN_PY_MINOR}"
  fi

  log "Python ${ver} at $(command -v "$PYTHON_BIN")"
}

ensure_venv() {
  if [[ ! -d "$VENV_DIR" ]]; then
    log "Creating virtualenv at ${VENV_DIR}"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  else
    log "Reusing virtualenv at ${VENV_DIR}"
  fi

  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"

  python -m pip install --upgrade pip setuptools wheel >/dev/null
}

ensure_mdbook() {
  command -v mdbook >/dev/null 2>&1 && return 0
  warn "mdbook not found on PATH."
  warn "Install with:  cargo install mdbook mdbook-linkcheck mdbook-rustdoc-links"
  return 1
}

has_rust_toolchain() {
  command -v cargo >/dev/null 2>&1
}
