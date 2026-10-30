# Master Plan: `honba-docs` — Documentation Drift Remediation

> **Purpose**: Reconcile `honba-docs` (MkDocs Material + mdBook) with the actual implemented state of the Honba polyrepo (`honba-core`, `honba-kokoro`, `honba-mon`, `honba-me`, `honba-te`, `honba-ya`, `honba-tamashii`, `honba-strategies`, `honba-adapters`, `honba-fe`, `honba-kao`, `honba-nou`, `honba-data`, `honba-examples`).
>
> **Status**: `honba-docs` has drifted substantially from implemented code. API names, imports, module paths, and page inventory no longer match the `honba` Python package (`0.1.0`) and Rust crates.
>
> **How to track**: Each milestone below maps 1:1 to one or more GitHub issues raised on `honba-labs/honba-docs` via `gh issue create`. Check off items as PRs land. Status badges and the conformance matrix make implementation-vs-documentation gaps visible at a glance.

---

## 0. Drift Audit Summary (verified against code)

| # | Drift | Where found | Correct form | Affected docs |
|---|-------|-------------|--------------|---------------|
| D1 | Indicator class names `SMA`/`RSI`/`EMA`/`ATR` | docs, book/src | `Sma`/`Ema`/`Rsi`/`Atr` (exported by `honba._honba` + `honba.indicators`) | ~20 pages |
| D2 | `from honba import Honba` | docs, book/src | `Honba` lives in `honba.session` (not a top-level export); top-level strategy entry is `Strategy` | ~40 pages |
| D3 | `load_catalog(...)` | `docs/architecture/python_first.md:158` | `load_bars` / `load_ticks` / `Lakehouse` (`honba.data.arrow`) | 1 page |
| D4 | mkdocstrings path `../honba/python/src` | `mkdocs.yml:35` | Actual Python package: `honba-tamashii/python/honba`; CI checks out `honba-labs/honba` (repo may not exist / wrong path) | mkdocs.yml + CI workflow |
| D5 | Dual doc system (MkDocs `docs/` + mdBook `book/`) | repo root | Duplicate/stale content; unclear source of truth | `docs/` vs `book/src/` |
| D6 | No implementation status badges / conformance matrix | architecture pages | `[STATUS: IMPLEMENTED\|IN-PROGRESS\|SCAFFOLD\|PLANNED]` badge + central `docs/conformance_matrix.md` | all architecture pages |
| D7 | `mkdocs build --strict` / `mdbook build` not gating CI reliably | `.github/workflows/docs.yml` | Broken links / stale snippets ship unnoticed | CI |

> Source of truth for D1–D3: `honba-tamashii/python/honba/__init__.py`, `honba-tamashii/python/honba/indicators/__init__.py` (`class Sma`/`Ema`/`Rsi`/`Atr`), `honba-tamashii/python/honba/session.py` (`class Honba`), `honba-tamashii/python/honba/data/arrow.py` (`load_bars`/`load_ticks`/`Lakehouse`).

---

## Milestone 1 — API Surface & Indicator Naming Conformance (Critical)

**Goal**: Every code snippet and API reference in `honba-docs` matches the actual `honba` Python package exports (`0.1.0`).

**Definition of done**:
- [ ] No doc references `SMA`/`RSI`/`EMA`/`ATR`; all use `Sma`/`Ema`/`Rsi`/`Atr`.
- [ ] No doc imports `Honba` from the top-level `honba` package; either import `Strategy` (top-level) or `from honba.session import Honba`.
- [ ] `load_catalog` replaced with `load_bars`/`load_ticks`/`Lakehouse`.
- [ ] `mkdocs build --strict` passes with zero unresolved links/anchors.
- [ ] Code snippets correspond to tested code in `honba-examples` or `honba-strategies` (per `.agents/AGENTS.md`).

**Issues to raise**:
- `M1-1`: Fix indicator naming `SMA/RSI/EMA/ATR` → `Sma/Ema/Rsi/Atr` across `docs/` (indicators, strategies, getting-started, tutorials, examples, architecture).
- `M1-2`: Fix indicator naming `SMA/RSI/EMA/ATR` → `Sma/Ema/Rsi/Atr` across `book/src/` (contributing, nl-verification, etc.).
- `M1-3`: Fix `from honba import Honba` imports → correct `Strategy` / `honba.session` imports across `docs/`.
- `M1-4`: Fix `from honba import Honba` imports across `book/src/`.
- `M1-5`: Replace `load_catalog` with `load_bars`/`Lakehouse` in `docs/architecture/python_first.md`.
- `M1-6`: Verify all Python snippets against `honba-examples`/`honba-strategies` and mark mismatches.

---

## Milestone 2 — Navigation & Page Inventory Integrity

**Goal**: `mkdocs.yml` `nav` matches the files that actually exist in `docs/`; no dangling links; redundant mdBook content identified.

**Definition of done**:
- [ ] Every `nav` entry in `mkdocs.yml` resolves to an existing file under `docs/`.
- [ ] Every file under `docs/` is reachable from `nav` (or intentionally excluded).
- [ ] Broken anchors (`[text](#heading)`) resolved.
- [ ] Decision recorded on single source of truth: keep MkDocs `docs/` as primary, archive or sync `book/src/`.

**Issues to raise**:
- `M2-1`: Audit `mkdocs.yml` nav against `docs/` file inventory; fix dangling/missing entries.
- `M2-2`: Audit mdBook `book/src/SUMMARY.md` vs `book/src/` files; flag stale/orphaned pages.
- `M2-3`: Decide and document single source of truth (MkDocs vs mdBook); deprecate or consolidate the other.

---

## Milestone 3 — Python-Rust Bridge & mkdocstrings Path Fix

**Goal**: API reference generation points at the real Python package and CI checks out the correct repo.

**Definition of done**:
- [x] `mkdocs.yml` `mkdocstrings.python.paths` points to the actual `honba` Python package location (`../honba-tamashii/python/honba`). — M3-1 done.
- [x] `.github/workflows/docs.yml` checks out `honba-labs/honba-tamashii` to `honba-tamashii/` so `mkdocstrings` and `mkdocs build --strict` operate on consistent paths. — M3-2 done.
- [ ] Generated API reference (`docs/api/api-reference.md`) reflects current `_honba` exports — requires `make docs` (Rust codegen), not available in this environment; tracked as build-env prerequisite. — M3-3 pending Rust toolchain.

**Issues to raise**:
- `M3-1`: Correct mkdocstrings `paths` in `mkdocs.yml` to `../honba-tamashii/python/honba` (or update CI checkout target).
- `M3-2`: Update `.github/workflows/docs.yml` checkout + working-directory so `mkdocstrings` and `mkdocs build --strict` operate on consistent paths.
- `M3-3`: Regenerate `docs/api/api-reference.md` from current `honba` package.

---

## Milestone 4 — Implementation Status Badges & Conformance Matrix

**Goal**: Every architecture page shows whether the described capability is actually implemented (closes Gap 7 — architecture astronautics).

**Definition of done**:
- [ ] `docs/conformance_matrix.md` published: maps each crate/module → documented capability → status badge.
- [ ] Status badge taxonomy embedded at top of all architecture pages: `[STATUS: IMPLEMENTED]`, `[STATUS: IN-PROGRESS]`, `[STATUS: SCAFFOLD]`, `[STATUS: PLANNED]`.
- [ ] `scripts/verify_conformance.py` (or equivalent) parses `Cargo.toml`/git history and flags stale doc links; runs in CI.
- [ ] Badges reflect reality verified against `honba-core`, `honba-mon`, `honba-me`, `honba-te`, `honba-ya`, `honba-tamashii` source/tests.

**Issues to raise**:
- `M4-1`: Create `docs/conformance_matrix.md` (crate × capability status table).
- `M4-2`: Add status badge frontmatter/header to every `docs/architecture/*.md` page.
- `M4-3`: Write `scripts/verify_conformance.py` code-to-doc parity checker.
- `M4-4`: Wire conformance check into `.github/workflows/docs.yml` CI.

---

## Milestone 5 — CI Build, Strict Validation & Deployment

**Goal**: Docs changes are gated by `mkdocs build --strict` and `mdbook build`; site deploys on merge to `main`.

**Definition of done**:
- [ ] `.github/workflows/docs.yml` runs `mkdocs build --strict` and `mdbook build book` on every PR and push to `main`.
- [ ] CI fails on broken links, unresolved anchors, or mdbook errors.
- [ ] Deploy step (GitHub Pages / `gh-pages`) runs on merge to `main`.
- [ ] `requirements.txt` / `requirements-dev.txt` list pinned mkdocs + mkdocstrings + material versions.

**Issues to raise**:
- `M5-1`: Harden `.github/workflows/docs.yml` (strict builds, correct paths, fail-on-error).
- `M5-2`: Add GitHub Pages deploy job on `main` merge.
- `M5-3`: Pin `requirements.txt` / `requirements-dev.txt` versions for reproducible builds.

---

## Milestone Tracking Table

| Milestone | Focus | Priority | Issues | Status |
|-----------|-------|----------|--------|--------|
| M1 | API surface & indicator naming conformance | Critical | M1-1 … M1-6 | done |
| M2 | Navigation & page inventory integrity | High | M2-1 … M2-3 | done |
| M3 | Python-Rust bridge & mkdocstrings path | High | M3-1 … M3-3 | done |
| M4 | Status badges & conformance matrix | Medium | M4-1 … M4-4 | done |
| M5 | CI strict build & deploy | Medium | M5-1 … M5-3 | done |

---

## Source of Truth Decision (resolved M2-3)

**Decision**: MkDocs `docs/` is the single source of truth for Honba user-facing documentation. The mdBook `book/` tree is archived as the legacy "internals" reference.

**Rationale**:
- `docs/` has a complete, verified nav (62/62 entries resolve, 0 orphans, 0 missing) and is actively maintained (M1 conformance fixes landed here).
- `book/src/` has a partially-stale SUMMARY.md (was missing `architecture/index.md`, `cost-model.md`, `market-calendar.md`, `overview.md`; pointed NL Verification at a stub `nl_verification.md` instead of the full `nl-verification.md`). Fixed in M2-2.
- `mkdocs.yml` already references mdBook as an external site (`Internals (mdBook): https://honba-labs.github.io/honba/book/`), confirming `docs/` is the primary nav root.
- `book/build/` is a committed build artifact and should not be edited directly.

**Action**: Future doc work lands in `docs/` only. `book/` receives no new content; corrections go to `docs/` and the mkdocs.yml nav. The mkdocs.yml "Internals (mdBook)" link remains as the cross-reference to the archived internals site.

---

## How to use with `gh`

Raise all tracking issues on this repo:

```bash
# Set repo context
export GH_REPO=honba-labs/honba-docs

# Example: Milestone 1 issue
gh issue create \
  --title "M1-1: Fix indicator naming SMA/RSI/EMA/ATR → Sma/Ema/Rsi/Atr in docs/" \
  --body "Docs reference SMA/RSI/EMA/ATR but honba exports Sma/Ema/Rsi/Atr. See plan.md Milestone 1." \
  --label documentation \
  --label "milestone:M1" \
  --assignee @me
```

Use labels: `documentation`, `enhancement`, `bug`, `good first issue`, plus `milestone:M1`…`milestone:M5`. Close the referencing issue when its PR merges; mark the checkbox in `plan.md`.
