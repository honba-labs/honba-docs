# Backtesting

Honba does not have "a backtester." It has three, each appropriate
for a different stage of research, plus a validation suite that
determines whether a result means anything.

## The Documents

- **[Three-Tier Pipeline](three_tier_pipeline.md)** — the vectorized
  pre-filter, the event-driven simulator, and the concurrent
  parameter sweep.
- **[Cost Modeling](cost_modeling.md)** — how the Indian cost model
  integrates with the engine, and how to measure a strategy's
  sensitivity to it.
- **[Latency Modeling](latency_modeling.md)** — why realistic latency
  matters for intraday strategies and how to configure it.
- **[Statistical Validation](statistical_validation.md)** — the six
  tests a strategy must pass before it is considered validated.

## The Recommended Workflow

1. **Write the strategy.** Use the `Strategy` base class.
2. **Run Tier 1** across a parameter grid. Eliminate the obvious
   non-starters.
3. **Run Tier 2** on the survivors. Get realistic numbers after costs
   and latency.
4. **Run Tier 3** on the top candidates. Full parameter sweep, Monte
   Carlo, walk-forward.
5. **Validate.** Run the statistical validation suite. Reject
   anything that fails.
6. **Paper trade.** Deploy to the paper adapter for at least a month
   before considering live trading.

Steps 5 and 6 are not optional. The number of strategies that pass
Tier 2 but fail validation is high — typically 80% or more.

## The Number That Matters

The number to compare between strategies is the **out-of-sample
deflated Sharpe** from the validation report, not the in-sample Sharpe
from a Tier 2 backtest. The in-sample number is an upper bound that
will not hold.

If you remember nothing else from this section, remember that.

## A Note on Speed

A Tier 1 run on 100 strategies over 5 years takes seconds. A Tier 2
run on one strategy takes minutes. A Tier 3 sweep of 10,000
parameter combinations takes 20 minutes on a 16-core machine.

The pipeline is designed so that the expensive tier runs on the
smallest possible set of candidates. Running Tier 2 on all 100
candidates is 100x more expensive than running Tier 2 on the 5 that
survived Tier 1.
