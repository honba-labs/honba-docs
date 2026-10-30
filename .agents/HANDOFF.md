Docs drift remediation planned & tracked.

## Phase / Slice Status
- Audited honba-docs drift against implemented code (honba-tamashii honba Python pkg 0.1.0 + sibling Rust crates).
- Wrote honba-docs/plan.md with milestone-based grouping (M1–M5, 19 tracked work items).
- Raised 19 GitHub issues on honba-labs/honba-docs (#1–19), labeled documentation + milestone:M1..M5.
- M1 code-level drift FIXED and merged via PR #21 (main): indicator naming, Honba imports, load_catalog.
- M1 issues #1–5 closed (auto-closed by PR merge or manually); #6 (snippet-vs-code verification) remains open.
- M2 nav inventory FIXED and merged via PR #22 (main): book/src/SUMMARY.md completed, docs/ declared single source of truth.
- M2 issues #7–#9 closed.
- M3 Python-Rust bridge paths FIXED and merged via PR #23 (main): mkdocstrings path → ../honba-tamashii/python/honba; CI checkout → honba-labs/honba-tamashii to honba-tamashii/.
- M3 issues #10–#12 closed. (M3-3 api-reference.md regen requires Rust toolchain via make docs; tracked as build-env prerequisite.)
- M4 conformance matrix + status badges + parity CI FIXED and merged via PR #24 (main).
- M4 issues #13–#16 closed.
- Remaining open: M1-6 (#6), M5 (#17–#19).

## Decisions & Discoveries (probe-verified)
- D1: Indicator classes are Sma/Ema/Rsi/Atr, but ~20 docs still use SMA/RSI/EMA/ATR. FIXED in docs/.
- D2: Honba lives in honba.session (not a top-level export); top-level strategy entry is Strategy. FIXED in docs/.
- D3: load_catalog() does not exist; honba.data.arrow provides load_bars/load_ticks/Lakehouse. FIXED in python_first.md.
- D4: mkdocstrings path ../honba/python/src wrong; actual package is honba-tamashii/python/honba; CI checked out non-existent honba-labs/honba. FIXED via M3 (PR #23).
- D5: Dual doc system (MkDocs docs/ + mdBook book/). RESOLVED M2-3: docs/ is single source of truth; book/ is legacy internals archive.
- D6: No status badges / conformance matrix; no code-to-doc parity CI. RESOLVED M4 (PR #24): conformance_matrix.md published, 18 architecture pages badged, verify_conformance.py wired into CI (strict).
- M2-1: mkdocs.yml nav verified clean — 62/62 entries resolve, 0 missing, 0 orphans.
- M2-2: book/src/SUMMARY.md was missing architecture/index.md, cost-model.md, market-calendar.md, overview.md; pointed NL Verification at stub nl_verification.md instead of full nl-verification.md. FIXED.

## Immediate Next Step
Work M1-6: verify all Python snippets against honba-examples/honba-strategies. Then proceed to M5 (CI strict builds, Pages deploy, pinned requirements).

## Operating Invariants
- .agents/AGENTS.md: no in-file #[test]; tests/ parallel to src; zero floats; zero-I/O domain purity (docs repo is markdown only).
- mkdocs build --strict and mdbook build must pass; code snippets must correspond to tested code in honba-examples/honba-strategies.
