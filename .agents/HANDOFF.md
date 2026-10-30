Docs drift remediation planned & tracked.

## Phase / Slice Status
- Audited honba-docs drift against implemented code (honba-tamashii honba Python pkg 0.1.0 + sibling Rust crates).
- Wrote honba-docs/plan.md with milestone-based grouping (M1–M5, 19 tracked work items).
- Raised 19 GitHub issues on honba-labs/honba-docs (#1–19), labeled documentation + milestone:M1..M5.
- M1 code-level drift FIXED and merged via PR #21 (main): indicator naming, Honba imports, load_catalog.
- M1 issues #1–5 closed (auto-closed by PR merge or manually); #6 (snippet-vs-code verification) remains open.

## Decisions & Discoveries (probe-verified)
- D1: Indicator classes are Sma/Ema/Rsi/Atr, but ~20 docs still use SMA/RSI/EMA/ATR. FIXED in docs/.
- D2: Honba lives in honba.session (not a top-level export); top-level strategy entry is Strategy. FIXED in docs/.
- D3: load_catalog() does not exist; honba.data.arrow provides load_bars/load_ticks/Lakehouse. FIXED in python_first.md.
- D4: mkdocstrings path ../honba/python/src wrong; actual package is honba-tamashii/python/honba; CI checks out honba-labs/honba. (M3)
- D5: Dual doc system (MkDocs docs/ + mdBook book/) has duplicate/stale content; no declared source of truth. (M2)
- D6: No status badges / conformance matrix; no code-to-doc parity CI. (M4)

## Immediate Next Step
Work M1-6: verify all Python snippets against honba-examples/honba-strategies. Then proceed to M2 (navigation/page inventory).

## Operating Invariants
- .agents/AGENTS.md: no in-file #[test]; tests/ parallel to src; zero floats; zero-I/O domain purity (docs repo is markdown only).
- mkdocs build --strict and mdbook build must pass; code snippets must correspond to tested code in honba-examples/honba-strategies.
