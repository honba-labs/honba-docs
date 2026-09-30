# Your First Backtest

This walkthrough runs a simple moving-average crossover on the NIFTY 50
universe and produces a performance tearsheet. No broker credentials are
required.

## The Strategy

We'll buy when the 20-day SMA crosses above the 50-day SMA, and sell when it
crosses back below. Position size is equal-weight across the universe.

Create `first_backtest.py`:

    from honba.strategies.base import Strategy
    from honba.strategies.indicators import SMA
    from honba.india.universes import nifty50
    from honba.backtest import BacktestNode, BacktestConfig


    class SmaCrossover(Strategy):
        fast_period = 20
        slow_period = 50

        def on_start(self):
            self.fast = SMA(self.fast_period)
            self.slow = SMA(self.slow_period)

        def on_bar(self, bar):
            f = self.fast.update(bar.close)
            s = self.slow.update(bar.close)
            if f is None or s is None:
                return
            if f > s and not self.position.is_long:
                self.buy(bar.instrument, size=self.target_size)
            elif f < s and self.position.is_long:
                self.close(bar.instrument)


    config = BacktestConfig(
        universe=nifty50(as_of="2023-01-01"),
        start="2023-01-01",
        end="2024-12-31",
        initial_capital=1_000_000,
        cost_model="india_equity_delivery",
        latency_ms=50,
    )

    node = BacktestNode(config)
    result = node.run(SmaCrossover)

    print(result.summary())
    result.tearsheet().save("sma_crossover.html")

## Running It

    python3 first_backtest.py

Expected output:

    Backtest: SmaCrossover  (2023-01-01 → 2024-12-31)
    Universe: NIFTY 50  (50 instruments)
    Initial capital: ₹1,000,000

    Trades:     412
    Win rate:   54.1%
    CAGR:       14.2%
    Sharpe:     1.18
    Sortino:    1.62
    Max DD:     -11.4%
    Total P&L:  ₹298,450

    Tearsheet saved: sma_crossover.html

## What Just Happened

The `BacktestNode` ran three stages:

1. **Cost model** — every fill was charged STT, exchange fees, GST, stamp
   duty, and a brokerage estimate. For a delivery strategy on NSE, that's
   roughly 0.14% per side.
2. **Latency simulation** — each signal was delayed by 50 ms before reaching
   the matching engine, which is realistic for retail broker APIs.
3. **Portfolio accounting** — P&L, position tracking, and drawdown were
   computed bar-by-bar by the engine, not by the strategy.

## Inspecting the Result

    result.trades           # DataFrame of every fill
    result.equity_curve     # Time series of portfolio value
    result.positions        # Position history
    result.stats            # Full statistics dictionary

## Next Steps

- **[Cost Modeling](../backtesting/cost_modeling.md)** — how the Indian
  equity cost model is defined and how to customize it.
- **[Latency Modeling](../backtesting/latency_modeling.md)** — why realistic
  latency matters more for intraday than for delivery strategies.
- **[Statistical Validation](../backtesting/statistical_validation.md)** —
  how to tell if a 1.18 Sharpe is real or lucky.
- **[Writing Strategies](../strategies/writing_strategies.md)** — the full
  strategy API.

## A Note on Overfitting

A single backtest is a hypothesis, not a result. Before drawing any conclusion
from the numbers above, run walk-forward validation and Monte Carlo:

    from honba.algo_analytics import walk_forward, monte_carlo

    wf = walk_forward(node, SmaCrossover, folds=8)
    mc = monte_carlo(node, SmaCrossover, iterations=1000)

    print(wf.summary())
    print(mc.confidence_interval(0.95))

The scaffold ships both utilities in `honba-algo-analytics`. They are not
optional — treat any backtest without them as a preliminary screen only.
