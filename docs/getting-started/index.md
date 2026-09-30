# Getting Started

This section walks through installing Honba and running your first
backtest. It assumes no prior experience with the codebase.

## What You Will Need

- A machine with Rust 1.75+ and Python 3.10+ (see
  [Installation](installation.md) for the toolchain setup).
- Roughly 30 minutes for the install and first backtest.
- No broker credentials. Backtesting runs entirely offline against a
  local Parquet catalog.

## The Path

1. **[Installation](installation.md)** — install Rust, Python, and the
   Honba workspace. Verify the build with the dependency hierarchy
   check and a minimal test run.
2. **[Your First Backtest](first-backtest.md)** — run a moving-average
   crossover on the NIFTY 50 universe, inspect the cost breakdown, and
   read the tearsheet.

## After the First Backtest

Once the first backtest runs, the natural next reads are:

- **[Architecture → Overview](../architecture/overview.md)** — why
  the codebase is organized the way it is.
- **[India → Cost Model](../india/cost_model.md)** — the cost
  assumptions that determine whether a strategy is viable.
- **[Backtesting → Three-Tier Pipeline](../backtesting/three_tier_pipeline.md)**
  — how to validate a strategy properly.

## A Note on Data

Backtests need historical data. The tutorials use a small synthetic
dataset that ships with the repository, so no downloads are required
for the first run. For real backtests, the
[Installation](installation.md) guide covers how to populate the
catalog from NSE bhavcopy or a broker API.
