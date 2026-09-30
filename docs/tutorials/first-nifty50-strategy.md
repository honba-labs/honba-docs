# Tutorial: Your First NIFTY 50 Strategy

Build, backtest, and validate a moving-average crossover on the NIFTY
50 universe. This tutorial requires no broker credentials and runs
entirely against the small synthetic dataset that ships with the
repository.

**Time:** 20 minutes.
**Prerequisites:** [Installation](../getting-started/installation.md).

## What You Will Build

A strategy that:

1. Subscribes to daily bars for all 50 NIFTY 50 constituents.
2. Buys when a 20-day SMA crosses above a 50-day SMA.
3. Sells when it crosses back below.
4. Sizes positions at 2% of equity per name.

## Step 1: Create the Strategy File

Create `first_strategy.py` in the workspace root:

    from honba.strategies.base import Strategy
    from honba.strategies.indicators import SMA
    from honba.india.universes import nifty50


    class SmaCrossover(Strategy):
        fast_period: int = 20
        slow_period: int = 50
        position_pct: float = 0.02

        def on_start(self):
            self.subscribe_bars(self.universe, timeframe="1d")
            self.fast = {i: SMA(self.fast_period) for i in self.universe}
            self.slow = {i: SMA(self.slow_period) for i in self.universe}

        def on_bar(self, bar):
            instr = bar.instrument
            f = self.fast[instr].update(bar.close)
            s = self.slow[instr].update(bar.close)
            if f is None or s is None:
                return

            pos = self.position(instr)
            size = int((self.equity * self.position_pct) / bar.close)

            if f > s and not pos.is_long and size > 0:
                self.buy(instr, size=size)
            elif f < s and pos.is_long:
                self.close(instr)

The `universe` attribute is populated by the backtest configuration,
not by the strategy. This lets the same strategy run on different
universes without modification.

## Step 2: Configure the Backtest

Append to `first_strategy.py`:

    from honba.backtest import BacktestNode, BacktestConfig

    config = BacktestConfig(
        universe=nifty50(as_of="2023-01-01"),
        start="2023-01-01",
        end="2024-12-31",
        initial_capital=1_000_000,
        cost_model="india_equity_delivery",
        latency_ms=50,
        calendar="NSE",
    )

    if __name__ == "__main__":
        node = BacktestNode(config)
        result = node.run(SmaCrossover)

        print(result.summary())
        result.tearsheet().save("sma_crossover.html")

Note `as_of="2023-01-01"`. The universe is fetched as it existed on
that date, not as it exists today. This avoids look-ahead bias from
constituent changes since 2023.

## Step 3: Run It

    python3 first_strategy.py

Expected output (numbers will differ slightly on synthetic data):

    Backtest: SmaCrossover
    Universe: NIFTY 50 (50 instruments, as of 2023-01-01)
    Period:   2023-01-01 to 2024-12-31 (496 trading days)

    Initial capital:  ₹1,000,000
    Final equity:     ₹1,187,340

    Trades:           412
    Win rate:         51.4%
    CAGR:             14.2%
    Sharpe:           0.94
    Sortino:          1.28
    Max drawdown:     -13.7%

    Cost breakdown:
      STT:              ₹32,140   (78.4%)
      Brokerage:        ₹5,240    (12.8%)
      Exchange + SEBI:  ₹2,180    (5.3%)
      GST:              ₹1,020    (2.5%)
      Stamp duty:       ₹420      (1.0%)
      ─────────────────────────────
      Total costs:      ₹41,000   (4.1% of initial capital)

    Tearsheet saved: sma_crossover.html

## Step 4: Read the Cost Breakdown

4.1% of initial capital over two years. That is a substantial drag.
Notice where it comes from:

- **STT dominates.** 78% of total costs. This is delivery equity at
  0.1% per side.
- **Brokerage is minor.** ₹20 per order across 412 trades is ₹5,240.
  The signal-to-cost ratio is not what kills strategies here; the STT
  is.

If the strategy traded weekly instead of on crossovers, STT would be
3–4x higher. Before optimizing the signal, check the turnover.

## Step 5: Validate

A Sharpe of 0.94 after costs is not evidence the strategy works. Run
the validation suite:

    from honba.algo_analytics import walk_forward, monte_carlo

    wf = walk_forward(
        node=node, strategy=SmaCrossover,
        train_months=12, test_months=6, n_folds=4,
    )
    print(wf.summary())

    mc = monte_carlo(
        node=node, strategy=SmaCrossover,
        iterations=1000, method="bootstrap",
    )
    print(mc.summary())

Typical output for a crossover strategy on NIFTY 50:

    Walk-forward: 4 folds
      Fold 1 (test 2023-H2): Sharpe 1.12
      Fold 2 (test 2024-H1): Sharpe 0.68
      Fold 3 (test 2024-H2): Sharpe 0.31
      Fold 4 (test 2025-H1): Sharpe 0.87
      Mean OOS Sharpe: 0.74   Std: 0.29

    Monte Carlo: 1000 iterations
      Sharpe 5th–95th: [0.42, 1.28]   Median: 0.88
      Max DD 5th:      -19.4%
      P(negative Sharpe): 8.2%

## Step 6: Interpret Honestly

The walk-forward mean OOS Sharpe (0.74) is well below the in-sample
Sharpe (0.94). The Monte Carlo 5th percentile Sharpe is positive
(0.42), which is good, but the 8.2% probability of a negative Sharpe
is not negligible.

By the criteria in
[Statistical Validation](../backtesting/statistical_validation.md),
this strategy would be marked `review`, not `pass`. It is a candidate
for further research, not for deployment.

## What to Try Next

Three concrete experiments:

1. **Reduce turnover.** Crossovers trade frequently. Try a
   slower signal (e.g., 50/200 SMA) and see whether the Sharpe
   improves after costs.
2. **Add a filter.** Require the trend to be confirmed by the index
   (e.g., NIFTY 50 itself above its 200-SMA) before taking long
   positions.
3. **Change the sizing.** Volatility-scaled sizing (see
   [Position Management](../strategies/position_management.md))
   typically improves risk-adjusted return.

Each experiment should be run through the full pipeline, not just
Tier 2. A single backtest is a hypothesis, not a result.

## Related

- [Writing Strategies](../strategies/writing_strategies.md)
- [Cost Modeling](../backtesting/cost_modeling.md)
- [Statistical Validation](../backtesting/statistical_validation.md)
