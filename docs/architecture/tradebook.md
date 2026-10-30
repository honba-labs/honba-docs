# Honba Tradebook — Trading Journal & Post-Mortem Replay — Architecture

> **[STATUS: PLANNED]** — `honba-kokoro-journal`. See [Platform Conformance Matrix](conformance_matrix.md).

**Document ID:** HBD-2026-DES-005
**Status:** Draft — proposed architecture, not yet implemented
**Version:** 1.0
**Last updated:** 2026-10-28
**Target Systems:** `honba-kokoro`, `honba-ya`, `honba-me`, `honba-kao`, `honba-fe`, `honba-data`, `honba-docs`

**Companion documents**

- `honba-docs/docs/architecture/strategy_tester_and_enhancer.md` — the backtest engine this document replays trades *into*.
- `honba-docs/docs/architecture/money.md` — `Price`/`Quantity`/`Money` invariants this document reuses, not re-specifies.
- `honba-docs/docs/architecture/algo_designer_and_simulator.md` — journal/run-event ADRs (0020/0021) this document's journal schema should stay consistent with.

---

## 1. Purpose and baseline

The user wants a **Tradebook**: a journaling page that gives multi-horizon performance views (daily/weekly/quarterly/yearly), stores charts with the user's own drawings against each trade, and — critically — stores enough structured state to re-run a past trade through the Simulator for a post-mortem ("what went wrong").

This is a design document only — no code in this change. It exists to fix the data model and cross-repo contracts *before* any crate is touched, per the workspace's interface-first and TDD rules.

### What already exists (do not re-invent)

A frontend-only prototype already exists and anchors naming/UX, but it is disconnected from any backend of record:

| Piece | File | Status |
| :--- | :--- | :--- |
| Tradebook UI | `honba-fe/apps/web/src/features/tradebook/TradebookView.tsx` | Renders `TradebookSessionRecord[]` from `accountStore.ts` — **hardcoded mock array** (`INITIAL_TRADEBOOK_RECORDS`), no API call. |
| Session record shape | `honba-fe/apps/web/src/core/store/accountStore.ts:74` (`TradebookSessionRecord`) | Flat `number`/`string` fields (no `Price`/`Money`), one record per *session* with an embedded `trades[]` array — not wire-compatible with `honba_core` types. |
| Backtest fill→round-trip pairing | `honba-fe/apps/web/src/core/simulator/trade-pairing.ts` | Already implements FIFO fill pairing into round trips **client-side**, from `GET /backtests/{id}/journal`. This logic is the right algorithm but belongs server-side (§4) and duplicates work `honba-kokoro`'s lot matcher already does for live/paper accounts (§3.1). |
| Journal fetch | `honba-fe/apps/web/src/core/simulator/journal.ts` | Thin fetch wrapper around the generated client; good pattern to replicate for the new endpoints (§6). |

Backend-side, the real primitives the Tradebook must be built *on*, not duplicate:

- `honba-core::{Price, Quantity, Money, InstrumentId, FillReport, OrderSide}` — `honba-core/src/types.rs`, `honba-core/src/order.rs`.
- `honba-kokoro::{TaxLot, MatchedLot, FillReport, PositionRecord}` — `honba-kokoro/crates/honba-kokoro/src/repository.rs:272-330`. **`MatchedLot` is already a closed round-trip** (entry price, exit price, matched quantity, realized PnL, holding period, LTCG/STCG flag) produced by FIFO lot matching. The Tradebook's "trade" is a thin wrapper around one or more `MatchedLot`s plus their originating `FillReport`s — it must not re-implement FIFO pairing in TypeScript.
- `honba-ya-backtest::{BacktestEngine, CatalogLoader, MarketEvent, FillEvent}` — `honba-ya/crates/honba-ya-backtest/src/{engine,events,catalog}.rs`. Replay already exists as a primitive: `BacktestEngine::run_catalog(loader, instruments, timeframe, from, to)` loads historical bars for an instrument/time-range and runs the deterministic event loop. This is the exact mechanism §5 reuses for "replay this trade."
- `honba-me-feed::lakehouse` — Parquet, Hive-partitioned, `Decimal128(18,4)` ticks and bars (`honba-me/crates/honba-me-feed/src/lakehouse.rs:1-45`). This is where the chart data for any historical trade already lives; the Tradebook never stores its own copy of OHLCV.
- `openalgo-charts-rs::drawing::{DrawingItem, DrawingTool}` — `honba-kao/crates/openalgo-charts-rs/src/drawing.rs`. A drawing primitive already exists (trend line, horizontal line, ray, Fibonacci retracement, rectangle) but it is **in-memory only, never persisted, and stores price as `f64`** — a zero-floats violation the moment it's wired to persistence (§4.3 fixes this).

**Conclusion:** nothing here starts from zero, but nothing existing is wire-ready. The design below is mostly *connecting and persisting* real engine output, plus one new aggregate (`TradeRecord`) and one new crate (`honba-kokoro-journal`).

---

## 2. Scope boundaries

In scope:
- A `TradeRecord` aggregate (one closed or open round trip) and a `JournalSession` rollup (one trading day/session), persisted durably.
- Chart-with-drawings storage, as a **replayable recipe**, not a raster image.
- Daily/weekly/quarterly/yearly aggregation views over `TradeRecord`.
- A documented replay contract from `TradeRecord` → `BacktestEngine::run_catalog`.
- REST endpoints and the `honba-fe` wiring to replace the mock data.

Out of scope (explicitly deferred, call out if asked):
- Automated "what went wrong" diagnosis (AI-generated post-mortem text) — this document only guarantees the *data* exists to do it; `honba-nou` can consume it later.
- Broker-side trade import reconciliation — assumed to already land in `honba-kokoro`'s `FillReport`/`TaxLot` tables via existing OMS fills; the Tradebook reads from there, it does not ingest broker CSVs itself.

---

## 3. Domain model

### 3.1 `TradeRecord` — one round trip

A `TradeRecord` is **derived**, not primary data: it is a projection over `FillReport`s and `MatchedLot`s that already exist in `honba-kokoro`. Storing it as its own row is a materialized view for query speed and for attaching journal-only fields (notes, tags, ratings) that have no other home.

```rust
// honba-kokoro-journal/src/model.rs (new crate)
pub struct TradeRecord {
    pub trade_id: TradeId,                 // new, stable id — not a lot_id (one TradeRecord can span several lots)
    pub account_id: AccountId,              // honba_kokoro::AccountId
    pub instrument: InstrumentId,           // honba_core::InstrumentId
    pub direction: PositionSide,            // honba_kokoro::PositionSide (Long/Short)
    pub status: TradeStatus,                // Open | Closed | Flipped
    pub entry_fills: Vec<FillReport>,       // honba_kokoro::FillReport, as recorded — never re-derived
    pub exit_fills: Vec<FillReport>,
    pub matched_lots: Vec<MatchedLot>,      // honba_kokoro::MatchedLot — realized PnL, holding period, LTCG/STCG
    pub avg_entry_price: Price,
    pub avg_exit_price: Option<Price>,
    pub quantity: Quantity,
    pub realized_pnl: Money,
    pub fees: Money,
    pub opened_at: DateTime<Utc>,
    pub closed_at: Option<DateTime<Utc>>,
    pub algo_id: Option<AlgoId>,             // SEBI algo id, if algo-originated — ties to Decision::PlaceOrder.algo_id
    pub session_id: SessionId,               // which JournalSession this belongs to (§3.2)
    pub chart: Option<ChartSnapshotRef>,     // §4
    pub journal: TradeJournalEntry,          // §3.3 — the only genuinely new, non-derived state
}

pub enum TradeStatus { Open, Closed, Flipped }
```

Why not store `TradeRecord` as the source of truth: `honba-kokoro`'s ledger is already the audited, double-entry source for fills and realized PnL (SEBI/tax-audit surface). A second mutable copy of PnL numbers in a journal table is a reconciliation hazard. `TradeRecord` therefore **always recomputes `realized_pnl`, `fees`, `matched_lots` from the ledger on read**, and only the `journal` sub-struct and `chart` ref are independently stored and mutable. This mirrors the existing split between `PortfolioState` (input) and `PortfolioSnapshot` (serializable report projection) in `honba-kokoro-portfolio`.

### 3.2 `JournalSession` — one trading day (or manually grouped session)

Equivalent to today's mock `TradebookSessionRecord`, but as a query result, not a stored blob:

```rust
pub struct JournalSession {
    pub session_id: SessionId,
    pub account_id: AccountId,
    pub trading_day: NaiveDate,           // IST trading day, per honba_ya_backtest::calendar::NseTradingCalendar
    pub trades: Vec<TradeId>,             // references, not embedded copies
    pub gross_pnl: Money,
    pub net_pnl: Money,
    pub fees: TaxBreakdown,               // honba_kokoro_ledger::TaxBreakdown — reused verbatim, not re-summed ad hoc
    pub win_rate_pct: Decimal,
    pub notes: SessionJournalEntry,       // session-level reflection, separate from per-trade notes
}
```

### 3.3 Journal-only state (the genuinely new data)

This is the only state with no existing home — everything else above is a view.

```rust
pub struct TradeJournalEntry {
    pub setup_tag: Option<String>,        // free-text or enum from a user-defined playbook
    pub psychology_rating: Option<u8>,    // 1-5
    pub setup_rating: Option<u8>,         // 1-5
    pub lessons: String,
    pub tags: Vec<String>,
    pub review_status: ReviewStatus,      // Pending | Reviewed
}
pub struct SessionJournalEntry {
    pub narrative: String,
    pub tags: Vec<String>,
}
```

---

## 4. Chart + drawing storage — a recipe, not a picture

**Decision:** never store a rasterized chart image. A screenshot cannot be replayed, cannot be re-themed, and cannot be queried. Store the *recipe* needed to deterministically regenerate the same chart from the lakehouse, plus the overlay drawings on top of it.

```rust
pub struct ChartSnapshotRef {
    pub instrument: InstrumentId,
    pub timeframe: Timeframe,             // honba_core::Timeframe — same type the lakehouse partitions on
    pub window: TimeRange,                // { from: DateTime<Utc>, to: DateTime<Utc> } — padded around the trade (§5)
    pub indicator_overlays: Vec<IndicatorSpec>,  // e.g. Sma(20), already defined in honba-me's 100+ indicator catalog
    pub drawings: Vec<ChartDrawing>,
}

// Fixes the f64 violation in openalgo-charts-rs::drawing::DrawingItem before it is persisted.
pub struct ChartDrawing {
    pub id: String,
    pub tool: DrawingTool,                // reuse honba_kao's enum (TrendLine, HorizontalLine, Ray, Fib, Rectangle)
    pub color: String,
    pub points: Vec<(DateTime<Utc>, Price)>,  // was Vec<(i64, f64)> — must become (timestamp, Price) to hold the zero-floats line
}
```

Required follow-up change flagged by this design (not done here): `honba-kao/crates/openalgo-charts-rs/src/drawing.rs`'s `DrawingItem.points: Vec<(i64, f64)>` must be changed to carry `Price`/`Decimal`, or a serialization-boundary adapter must convert `f64` display coordinates to `Decimal` prices before anything persists — the in-canvas pixel math can stay `f64` (WASM canvas rendering is not a financial-math path), but the **stored** value crossing into `honba-kokoro-journal` must not be.

Because the lakehouse (`honba-me-feed::lakehouse`) is the system of record for OHLCV and is immutable once written, a `ChartSnapshotRef` is cheap (a few hundred bytes) and never goes stale: re-rendering the same `instrument` + `window` + `timeframe` against the lakehouse always reproduces the same candles, byte for byte, satisfying the workspace's temporal-determinism invariant.

Storage location for `ChartSnapshotRef` + `Vec<ChartDrawing>`: alongside `TradeRecord` in `honba-kokoro-journal`'s repository (§6), not in `honba-me` — drawings are journal annotations, not market data, and must not pollute the lakehouse's zero-I/O, broker-agnostic domain purity.

---

## 5. Replay-to-simulator pipeline (the "what went wrong" mechanism)

This is the design's central requirement: a `TradeRecord` must carry enough to reconstruct a `BacktestEngine` run that reproduces the market conditions around the trade.

A `TradeRecord` already carries `instrument`, `opened_at`, `closed_at`, and (via `ChartSnapshotRef`) `timeframe`. Replay is:

```rust
pub struct ReplaySeed {
    pub instrument: InstrumentId,
    pub timeframe: Timeframe,
    pub from: DateTime<Utc>,   // opened_at minus a configurable lookback (default: 50 bars, for indicator warm-up)
    pub to: DateTime<Utc>,     // closed_at plus a configurable lookahead (default: 20 bars, to see what price did after exit)
    pub starting_cash: Decimal,       // from the account's actual pre-trade equity, for a realistic sizing counterfactual
    pub product_type: ProductType,
    pub recorded_fills: Vec<FillReport>,  // the ACTUAL fills — rendered as an overlay, never fed back into the engine as input
}

impl ReplaySeed {
    pub fn from_trade(trade: &TradeRecord, lookback_bars: u32, lookahead_bars: u32) -> Self { /* ... */ }

    /// Runs the real engine, unmodified, over the real lakehouse data for this window.
    pub fn run(&self, loader: &CatalogLoader, engine: &mut BacktestEngine<impl Strategy>) -> BacktestResult {
        engine.run_catalog(loader, &[self.instrument.clone()], self.timeframe.as_str(),
                            Some(self.from), Some(self.to)).expect("lakehouse must have this range")
    }
}
```

Two replay modes, both built on the same `ReplaySeed`:

1. **Pure chart replay** (no strategy): `honba-kao` renders the lakehouse candles for `[from, to]` with the trade's actual entry/exit fills and the user's saved drawings overlaid — this is what the Tradebook page shows by default. No `BacktestEngine` run needed, just a lakehouse read.
2. **Counterfactual strategy replay** (the post-mortem): if the trade was algo-originated (`algo_id` is `Some`), the *same* `StrategyIr`/config that generated it (looked up by `algo_id` from the Strategy Studio's run catalog — see `algo_designer_and_simulator.md`) is replayed through `BacktestEngine::run_catalog` over the identical window. The diff between the engine's `FillEvent`s and the `TradeRecord.entry_fills`/`exit_fills` recorded live is the "what went wrong" signal: slippage vs. the sim, a risk-gate refusal that didn't fire the same way live, a different fill price under the L2 simulator, etc. This reuses `honba-mon`'s risk gate and `honba-ya-backtest`'s L2/slippage models exactly as they already exist — no new simulation logic, only a new *entry point* into the existing engine, keyed off a past `TradeRecord` instead of a fresh strategy run.

For a discretionary (non-algo) trade, mode 2 has no strategy to replay — the Tradebook instead offers "run my own annotated levels as a manual strategy" by letting the user mark their stated stop/target as a static `Decision` sequence; this is a thin UI feature on top of the same `ReplaySeed`, not a new backend capability.

---

## 6. Storage and cross-repo responsibility

| Repo | Responsibility | New code |
| :--- | :--- | :--- |
| `honba-kokoro` | Source of truth for `FillReport`, `TaxLot`, `MatchedLot`. Unchanged. | None. |
| `honba-kokoro-journal` (**new crate**, sibling to `honba-kokoro-ledger`/`honba-kokoro-portfolio`) | Defines `TradeRecord`, `JournalSession`, `TradeJournalEntry`, `ChartSnapshotRef`, `ChartDrawing`. Defines `JournalRepository` trait (interface-first, per AGENTS §4.2) before any storage impl: `fn get_session(&self, date) -> JournalSession`, `fn upsert_journal_entry(&mut self, trade_id, entry)`, `fn save_drawings(&mut self, trade_id, Vec<ChartDrawing>)`. Derives `TradeRecord` on read by scanning `honba-kokoro`'s fill/lot repository for the account + date range — never duplicates PnL math. | New crate, `trait`-first. |
| `honba-data` | Cold storage for `TradeRecord`/`JournalSession` beyond the hot window (e.g. >90 days), as Parquet under a `journal/` tree parallel to the existing `BAR_SCHEMA` convention in `honba-data/src/honba_data/store/parquet.py`. DuckDB queries power the quarterly/yearly rollups cheaply over Parquet without a running service. | `journal/` schema + loader, Python side. |
| `honba-ya-api-rest` (or a new `honba-kokoro-journal-api`, consistent with the existing Axum headless server pattern) | New endpoints: `GET /journal/sessions?from=&to=` (daily/weekly/quarterly/yearly rollups — same range, different `group_by`, computed server-side, not duplicated client logic), `GET /journal/trades/{id}`, `PATCH /journal/trades/{id}/notes`, `GET /journal/trades/{id}/chart`, `PUT /journal/trades/{id}/drawings`, `POST /journal/trades/{id}/replay`. | REST handlers only; no new domain logic. |
| `honba-kao` | Fix `DrawingItem` to carry `Price`/`Decimal` at the persistence boundary (§4). Chart rendering reused as-is (`canvas/candles.rs`, `canvas/bars.rs`). | One type fix. |
| `honba-fe` | Replace `INITIAL_TRADEBOOK_RECORDS` mock in `accountStore.ts` with real fetches via the generated client, following the exact pattern `core/simulator/journal.ts` already established (narrow client seam, graceful degradation if the route is missing). Delete the client-side FIFO pairing in `trade-pairing.ts` for *live/paper* trades (keep it only for raw backtest fills, where `honba-kokoro` has no lot ledger to query) — the Tradebook calls the server for already-paired `TradeRecord`s. | Wiring only; delete duplicated pairing logic for the live path. |

---

## 7. Multi-horizon analysis (daily / weekly / quarterly / yearly)

These are **query parameters, not separate storage**. `GET /journal/sessions?group_by=day|week|quarter|year&from=&to=` buckets `JournalSession`s (themselves one-per-trading-day) by the IST trading calendar already implemented in `honba-ya-backtest::calendar::NseTradingCalendar` — reused so that a "week" or "quarter" boundary matches the same calendar the backtest engine uses, keeping live-journal stats and backtest stats comparable (a stated goal of the broader `research-live parity` principle in `AGENTS.md` §5.3).

Rollup math (win rate, profit factor, max drawdown, Sharpe/Sortino/Calmar per the Jesse-inspired metrics already named in `AGENTS.md` §5.1) is computed once, server-side, over `Money`/`Decimal` — never re-derived in the frontend from floats, closing the one place the current mock UI (`TradebookView.tsx`'s `bookkeepingSummary` `useMemo`) does arithmetic on plain `number`s.

---

## 8. Compliance with workspace invariants

- **Zero-I/O domain purity**: `TradeRecord` derivation reads from repositories via trait objects (`JournalRepository`, existing `AccountRepository`/ledger repos) — `honba-kokoro-journal`'s domain logic itself performs no direct filesystem/network I/O; repository implementations do.
- **Zero floats**: every monetary/price field above is `Price`/`Quantity`/`Money`/`Decimal`. The one existing float (`DrawingItem.points: Vec<(i64, f64)>`) is called out explicitly in §4 as a required fix before persistence, not silently inherited.
- **Parallel `tests/` directory, TDD**: a new `honba-kokoro-journal` crate starts with `tests/journal_repository_tests.rs` defining the `JournalRepository` contract against a fake, red-green-refactor, before any real Parquet/SQLite-backed implementation — per AGENTS §3.2. Golden vectors: a fixed `FillReport` sequence replayed through `ReplaySeed::run` must produce byte-identical `BacktestResult` across runs (determinism regression test), stored under `tests/golden/`.
- **Interface-first**: `JournalRepository` (trait) is specified before any storage backend, per AGENTS §4.2, so the hot-path backend (SQLite WAL, matching `honba-te-audit`'s existing journal pattern) and the cold-path backend (`honba-data` Parquet) can share one contract and be swapped without touching `honba-kokoro-journal`'s domain logic.

---

## 9. Open questions

1. **Hot-store technology for `honba-kokoro-journal`**: SQLite WAL (reusing the `honba-te-audit` pattern already in the workspace) vs. an in-process `BTreeMap` repository backed by periodic Parquet flush to `honba-data`. Recommend SQLite WAL for the hot window (mutable notes, fast point lookups) with async flush to `honba-data` Parquet for anything past 90 days, mirroring the "hot/cold" split already implicit in `honba-data`'s point-in-time coverage ledger design.
2. **Where counterfactual replay runs**: inline in the REST handler (synchronous, bounded by lookback/lookahead window size) vs. queued as an async job like existing backtest runs (`honba-ya-api::cache.rs` already has a run-cache concept to reuse). Recommend the async-job path for consistency with how every other backtest run in the system is already surfaced, rather than inventing a second "replay" execution path.
3. **Discretionary-trade replay UX** (§5, mode 2 fallback) is sketched but not specified in detail — needs its own short follow-up note once the algo-path replay is validated end-to-end.
