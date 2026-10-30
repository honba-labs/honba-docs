# Platform Conformance Matrix

> **Single source of truth** mapping every Honba crate/module to its documented
> capability and implementation status. This is the authoritative reference for
> closing the documentation↔implementation lag (Gap 7). Status badges on each
> architecture page mirror this matrix.

## Status taxonomy

| Badge | Meaning |
|:------|:--------|
| `[STATUS: IMPLEMENTED]` | Code is compiled, unit-tested, and passing CI conformance. |
| `[STATUS: IN-PROGRESS]` | Core contracts and basic engines active; edge features under development. |
| `[STATUS: SCAFFOLD]` | Uniform API skeleton and interfaces defined; execution logic stubbed. |
| `[STATUS: PLANNED]` | Architectural blueprint formulated; implementation not yet started. |

## Matrix

| Crate / module | Documented capability | Status | Doc reference | Test coverage |
|:---------------|:----------------------|:-------|:--------------|:--------------|
| `honba-core` | Value objects (`Price`, `Quantity`, `Money`), `InstrumentId`, `Decision`, `Order`, `Portfolio`, `Signal`, `Sizing`, `Market`, `Calendar`, `Events`, `Wire`, `Types` | `[STATUS: IMPLEMENTED]` | [DDD](../architecture/domain_driven_design.md), [Money](../architecture/money.md), [Contracts](../architecture/contracts_from_rust.md) | `tests/core_tests.rs`, `tests/proptest_invariants.rs`, `tests/golden_test.rs`, `tests/schema_compatibility_test.rs` |
| `honba-kokoro` | Double-entry FIFO ledger, OMS state machine, tax-lot matching, portfolio accounting | `[STATUS: IMPLEMENTED]` | [Money](../architecture/money.md), [Order Reject & Cancel](../architecture/order_reject_cancel.md), [Tradebook](../architecture/tradebook.md) | `crates/honba-kokoro-ledger/tests/ledger_proptest_invariants.rs`, `crates/honba-kokoro-portfolio/tests/apply_fill_tests.rs`, `crates/honba-kokoro/tests/repository_and_sizing_tests.rs` |
| `honba-mon` | SEBI algo_id registry, OTR circuit breakers, price bands, freeze limits, pre-trade risk gate | `[STATUS: IMPLEMENTED]` | [Order Reject & Cancel](../architecture/order_reject_cancel.md), [Risk Migration Plan](../architecture/migration_plan_kokoro_risk_to_mon.md) | `tests/proptest_tests.rs`, `tests/risk_tests.rs`, `tests/phase7_tests.rs` |
| `honba-me` | Multi-broker binary WebSocket feeds, tick coalescing, L2/L3 depth, 100+ StockSharp indicators, Parquet Lakehouse, Bhavcopy loaders | `[STATUS: IMPLEMENTED]` | [Adapter Interface](../architecture/adapter_interface.md), [WASM Indicators](../architecture/wasm_indicators.md) | `crates/honba-me-indicators/tests/*`, `crates/honba-me-feed/tests/*`, `crates/honba-me-market/tests/*`, `crates/honba-me-loaders/tests/*` |
| `honba-te` | Token-bucket rate limiter, freeze slicer, headless TOTP auth, Smart Order Router (SOR), SQLite WAL audit journal, broker execution adapters | `[STATUS: IMPLEMENTED]` | [Adapter Interface](../architecture/adapter_interface.md), [Order Reject & Cancel](../architecture/order_reject_cancel.md) | `crates/honba-te-core/tests/*`, `crates/honba-te-router/tests/*`, `crates/honba-te-slicer/tests/*`, `crates/honba-te-audit/tests/*`, `crates/honba-te-auth/tests/*` |
| `honba-ya` | Tokio actor pipeline, backtest engine, REST API server, persistence, strategy tester/runner, GA/Bayesian/WFO/DSR enhancer, CLI | `[STATUS: IMPLEMENTED]` | [Actor Runtime & Event Loop](../architecture/event_loop.md), [Strategy Tester & Enhancer](../architecture/strategy_tester_and_enhancer.md), [Using the Simulator](../architecture/simulator_usage.md) | `crates/honba-ya-backtest/tests/*`, `crates/honba-ya-api-rest/tests/*`, `crates/honba-ya-actors/tests/*`, `crates/honba-ya-enhancer/tests/*`, `crates/honba-ya-persistence/tests/*` |
| `honba-tamashii` | PyO3 FFI bridge, zero-copy Arrow/PyCapsule memory, `honba` Python wheel, GIL management (`py.allow_threads`), codegen | `[STATUS: IMPLEMENTED]` | [Python-First Architecture](../architecture/python_first.md), [Contracts from Rust](../architecture/contracts_from_rust.md) | `crates/honba-tamashii-py/tests/*`, `crates/honba-tamashii-codegen/tests/*`, `tests/*.py` |
| `honba-nou` | Autonomous research loop, MCP server, prompt replayer, LLM integration, genetic strategy synthesis, DSR/PBO/walk-forward analytics | `[STATUS: IMPLEMENTED]` | [AI Engine & Quant Researcher](../architecture/ai_engine.md) | `crates/honba-nou-analytics/tests/*`, `crates/honba-nou-mcp/tests/mcp_tests.rs`, `crates/honba-nou-agent/tests/*` |
| `honba-kao` | Leptos CSW frontend, Strategy Studio visual canvas, Simulator port, openalgo-charts bridge, WASM charting | `[STATUS: IMPLEMENTED]` | [honba-kao Simulator Port](../architecture/kao_simulator_port.md), [honba-kao Strategy Studio](../architecture/strategy_studio.md), [WASM Indicators](../architecture/wasm_indicators.md) | `crates/openalgo-charts-rs/tests/*`, `crates/honba-kao-app/tests/*`, `crates/honba-kao-api-wasm/tests/*` |
| `honba-strategies` | Production strategy catalog (quoting, arbitrage, TWAP/VWAP slicers, Turtle breakout, risk parity), `step.toml` manifests, `registry.json` | `[STATUS: IMPLEMENTED]` | [Strategies index](../strategies/index.md), [Step Manifests & Chaining](../strategies/step_manifests_and_chaining.md) | `test_readme_sections.py`, `test_step_manifests.py`, per-strategy `tests/` |
| `honba-adapters` | Community broker connectors (Dhan, Zerodha implemented; Angel One, Fyers, Upstox, Kotak, IIFL scaffolded) | `[STATUS: IN-PROGRESS]` | [Brokers](../india/brokers.md), [Adapter Configuration](../india/adapter_configuration.md) | `crates/honba-te-zerodha/tests/*`, `crates/honba-te-upstox/tests/*`, `crates/honba-te-angelone/tests/*` |
| `honba-data` | Point-in-time corporate actions, splits, dividends, coverage ledgers, Parquet catalog, DuckDB queries | `[STATUS: IMPLEMENTED]` | [Universes](../india/universes.md), [Cost Model](../india/cost_model.md) | Python test suite (`pytest`) |
| `honba-examples` | Runnable Python reference scripts (backtesting, screening, SIP, options, AI research, production) | `[STATUS: IMPLEMENTED]` | [Examples](../examples/index.md), [Known Issues](../examples/known_issues.md) | `pytest` per numbered script `Pitfalls::` sections |
| `honba-fe` | TypeScript web desktop UI: dockview workspace, trading terminal, real-time depth, screener, portfolio management | `[STATUS: IMPLEMENTED]` | [honba-kao Strategy Studio](../architecture/strategy_studio.md) | `vitest`, `tsc --noEmit` |
| `honba-kokoro-journal` | `TradeRecord`, `JournalSession`, `ChartSnapshotRef`, replay-to-simulator pipeline | `[STATUS: PLANNED]` | [Tradebook (Journal & Replay)](../architecture/tradebook.md) | Not yet implemented (design doc only) |
| `honba-ya-enhancer` | GA, Bayesian optimization, walk-forward analysis, DSR gate (sub-crate of honba-ya) | `[STATUS: IMPLEMENTED]` | [Strategy Tester & Enhancer](../architecture/strategy_tester_and_enhancer.md) | `crates/honba-ya-enhancer/tests/ga_optimizer_tests.rs`, `bayesian_optimizer_tests.rs`, `walk_forward_tests.rs` |

## Status summary

| Status | Count | Crates/modules |
|:-------|:------|:---------------|
| IMPLEMENTED | 13 | honba-core, honba-kokoro, honba-mon, honba-me, honba-te, honba-ya, honba-tamashii, honba-nou, honba-kao, honba-strategies, honba-data, honba-examples, honba-fe |
| IN-PROGRESS | 1 | honba-adapters |
| SCAFFOLD | 0 | — |
| PLANNED | 1 | honba-kokoro-journal |

## How this matrix is verified

- Rust crates: `cargo test --workspace` must be green; clippy with `-D warnings`.
- Python packages (`honba-tamashii`, `honba-strategies`, `honba-adapters`, `honba-data`, `honba-examples`): `pytest -q` must be green.
- `scripts/verify_conformance.py` parses `Cargo.toml`/`pyproject.toml` members and git history to flag crates referenced in docs but absent from the workspace (and vice versa). Run in CI.

## Change log

- 2026-10-30: Initial matrix published (M4-1). All statuses verified against crate source and test files in the workspace.
