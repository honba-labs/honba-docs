Docs drift remediation planned & tracked.

## Phase / Slice Status
- Audited honba-docs drift against implemented code (honba-tamashii honba Python pkg 0.1.0 + sibling Rust crates).
- Wrote honba-docs/plan.md with milestone-based grouping (M1–M5, 19 tracked work items).
- Raised 19 GitHub issues on honba-labs/honba-docs (#1–19), all open, labeled documentation + milestone:M1..M5.

## Decisions & Discoveries (probe-verified)
- D1: Indicator classes are Sma/Ema/Rsi/Atr, but ~20 docs still use SMA/RSI/EMA/ATR.
- D2: Honba lives in honba.session (not a top-level export); top-level strategy entry is Strategy. ~40 docs import `from honba import Honba`.
- D3: load_catalog() does not exist; honba.data.arrow provides load_bars/load_ticks/Lakehouse (used in python_first.md).
- D4: mkdocstrings path ../honba/python/src wrong; actual package is honba-tamashii/python/honba; CI checks out honba-labs/honba.
- D5: Dual doc system (MkDocs docs/ + mdBook book/) has duplicate/stale content; no declared source of truth.
- D6: No status badges / conformance matrix; no code-to-doc parity CI.
- No pre-existing open issues on the repo.

## Immediate Next Step
Work M1 issues (#1–6): fix indicator naming, Honba imports, load_catalog, and snippet-vs-code verification in docs/ and book/src/.

## Operating Invariants
- .agents/AGENTS.md: no in-file #[test]; tests/ parallel to src; zero floats; zero-I/O domain purity (docs repo is markdown only).
- mkdocs build --strict and mdbook build must pass; code snippets must correspond to tested code in honba-examples/honba-strategies.
