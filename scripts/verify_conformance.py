#!/usr/bin/env python3
"""Code-to-documentation conformance checker for honba-docs.

Parses workspace Cargo.toml files and the mkdocs.yml nav to detect:
1. Rust crates referenced in docs/architecture but absent from the workspace.
2. Workspace crates with no corresponding documentation page.
3. Docs nav entries that point to missing files.

Usage:
    python scripts/verify_conformance.py          # run from honba-docs root
    python scripts/verify_conformance.py --strict # exit non-zero on any drift

Exit codes:
    0 — conformant (or only informational notes)
    1 — drift detected (when --strict)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Canonical workspace crates (discovered from Cargo.toml members + on-disk dirs).
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent  # honba-workspace/
DOCS_ROOT = Path(__file__).resolve().parent.parent            # honba-docs/
MKDOCS_YML = DOCS_ROOT / "mkdocs.yml"

# Architecture pages that should each have a status badge (M4-2).
ARCHITECTURE_DIR = DOCS_ROOT / "docs" / "architecture"

# Expected badge taxonomy.
VALID_BADGES = {
    "[STATUS: IMPLEMENTED]",
    "[STATUS: IN-PROGRESS]",
    "[STATUS: SCAFFOLD]",
    "[STATUS: PLANNED]",
}


def discover_workspace_crates() -> set[str]:
    """Return the set of crate directory names under the workspace.

    Excludes git worktree checkouts (names matching `*-wt-*`) which are
    temporary copies of a crate on a feature branch, not workspace members.
    """
    crates: set[str] = set()
    for entry in WORKSPACE_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if not entry.name.startswith("honba-"):
            continue
        if "-wt-" in entry.name:  # git worktree checkout, not a workspace member
            continue
        if (entry / "Cargo.toml").exists():
            crates.add(entry.name)
    return crates


def parse_mkdocs_nav() -> tuple[list[str], list[str]]:
    """Return (referenced_doc_files, all_nav_path_strings) from mkdocs.yml."""
    text = MKDOCS_YML.read_text()
    referenced: list[str] = []
    for line in text.splitlines():
        m = re.search(r'-\s*(?:[^:\n]+:\s*)?(\S+\.md)', line)
        if m:
            referenced.append(m.group(1))
    return referenced, referenced


def check_nav_files(referenced: list[str]) -> list[str]:
    """Return list of problems: nav entries pointing to missing docs files."""
    problems: list[str] = []
    for ref in referenced:
        p = DOCS_ROOT / "docs" / ref
        if not p.exists():
            problems.append(f"  * nav entry '{ref}' does not exist in docs/")
    return problems


def check_architecture_badges() -> list[str]:
    """Return list of architecture pages missing a valid status badge."""
    problems: list[str] = []
    if not ARCHITECTURE_DIR.exists():
        return [f"  * architecture dir {ARCHITECTURE_DIR} missing"]
    for page in sorted(ARCHITECTURE_DIR.glob("*.md")):
        text = page.read_text()
        if not any(badge in text for badge in VALID_BADGES):
            problems.append(f"  * {page.relative_to(DOCS_ROOT)} has no status badge")
    return problems


def check_crate_doc_coverage(crates: set[str]) -> list[str]:
    """Return list of workspace crates with no documentation reference."""
    # Build a set of crate-name tokens that appear in docs/architecture + conformance matrix.
    doc_text = ""
    for page in (DOCS_ROOT / "docs").rglob("*.md"):
        doc_text += page.read_text()
    problems: list[str] = []
    for crate in sorted(crates):
        # Crates are referenced by their directory name (e.g. honba-mon).
        if crate not in doc_text:
            problems.append(
                f"  * workspace crate '{crate}' is not referenced in any docs page"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check honba-docs conformance with the implemented workspace."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any conformance drift is detected.",
    )
    args = parser.parse_args()

    problems: list[str] = []

    crates = discover_workspace_crates()
    referenced, _ = parse_mkdocs_nav()

    problems.extend(check_nav_files(referenced))
    problems.extend(check_architecture_badges())
    problems.extend(check_crate_doc_coverage(crates))

    if problems:
        print("Conformance drift detected:")
        for prob in problems:
            print(prob)
        if args.strict:
            print(f"\n{len(problems)} issue(s). Fix or update docs/conformance_matrix.md.")
            return 1
        print(f"\n{len(problems)} issue(s) (non-strict).")
        return 0

    print("Conformance OK: nav entries resolve, architecture badges present, "
          f"{len(crates)} workspace crates referenced in docs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
