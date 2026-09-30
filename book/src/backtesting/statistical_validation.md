# Statistical Validation

A backtest produces a number. Whether that number means anything is a
separate question. This document covers the tools Honba provides to
answer it.

## The Problem

Given 100 strategies and 5 years of data, roughly 5 will show a Sharpe
ratio above 2.0 purely by chance. If you test enough strategies, you
will find one that looks great — and it will be pure noise. This is
the fundamental problem of backtest overfitting.

Honba's statistical validation toolkit is designed to catch this. A
strategy is not considered validated until it passes all of the checks
below.

## The Six Tests

### 1. Out-of-Sample Sharpe > 50% of In-Sample Sharpe

Split the data into train and test. Fit on train, evaluate on test. If
the out-of-sample Sharpe is less than half the in-sample Sharpe, the
strategy is overfit.

    from honba.algo_analytics import train_test_split

    is_result, oos_result = train_test_split(
        node=node, strategy=SmaCrossover,
        train_end="2023-12-31",
    )

    ratio = oos_result.sharpe / is_result.sharpe
    # Require: ratio > 0.5

### 2. Walk-Forward Stability

Walk-forward validation rolls the train/test split forward through
time and measures the variability of out-of-sample Sharpe across
folds.

    from honba.algo_analytics import walk_forward

    wf = walk_forward(
        node=node, strategy=SmaCrossover,
        train_months=24, test_months=6, n_folds=8,
    )

    print(wf.summary())
    # OOS Sharpe per fold: [1.12, 0.87, 1.34, 0.91, 1.05, 1.28, 0.74, 1.18]
    # Mean: 1.06   Std: 0.21   Min: 0.74   Max: 1.34
    # Fraction of folds profitable: 8/8

Requirements:

- Mean OOS Sharpe > 0.8
- Std dev of fold Sharpe < 0.5
- At least 6 of 8 folds profitable

A strategy whose OOS Sharpe is 1.0 on average but ranges from -0.5 to
2.5 across folds is not robust; it is a strategy that happens to work
in some regimes and fails in others.

### 3. Monte Carlo Distribution

Monte Carlo generates alternative price paths or trade orderings from
the same underlying distribution and runs the strategy on each.

    from honba.algo_analytics import monte_carlo

    mc = monte_carlo(
        node=node, strategy=SmaCrossover,
        iterations=1000,
        method="bootstrap",
    )

    mc.plot_distribution().save("mc.html")
    print(mc.summary())
    # Sharpe: 5th=0.72, 25th=0.94, 50th=1.17, 75th=1.41, 95th=1.62
    # Max DD: 5th=-22.4%, 50th=-12.8%, 95th=-6.1%
    # P(negative Sharpe): 0.4%

Requirements:

- 5th percentile Sharpe > 0
- Median Sharpe > 0.8
- 95th percentile Max DD > -30%

### 4. Parameter Robustness

A strategy that works only at one specific parameter value is
overfit. Robust strategies have broad plateaus in parameter space.

    from honba.algo_analytics import parameter_surface

    surface = parameter_surface(
        node=node, strategy=SmaCrossover,
        params={
            "fast_period": range(5, 31, 5),
            "slow_period": range(30, 121, 10),
        },
    )

    surface.heatmap().save("param_heatmap.html")
    print(surface.plateau_score())
    # A measure of how flat the top region is
    # Require: plateau_score > 0.4

If the best Sharpe is 1.8 at (20, 50) and drops to 0.3 at (21, 50),
the strategy is fitting noise. If the top 20% of parameter combinations
all have Sharpe > 1.3, it is robust.

### 5. Regime Performance

A strategy that only works in bull markets is not a strategy; it is
leverage. Check performance across regimes.

    from honba.algo_analytics.regime import detect_regimes, regime_performance

    regimes = detect_regimes(
        benchmark="NIFTY50",
        start="2015-01-01",
        end="2024-12-31",
        method="hmm",
    )

    report = regime_performance(
        result=result,
        regimes=regimes,
    )

    print(report.table())
    # Regime            Days   Sharpe   Return   Max DD
    # ─────────────────────────────────────────────────
    # Bull (low vol)    834    1.62     22.4%    -6.2%
    # Bull (high vol)   402    1.18     14.1%    -9.8%
    # Bear (low vol)    318   -0.24     -3.8%    -11.4%
    # Bear (high vol)   189    0.41      2.1%    -14.7%
    # Choppy            647    0.87      8.1%    -8.9%

Requirements:

- Positive Sharpe in at least 3 of 5 regimes
- No regime with Sharpe < -0.5
- No single regime contributing more than 60% of total P&L

### 6. Trade Count and Outlier Sensitivity

A strategy whose P&L is dominated by 3 outlier trades is not
statistically valid.

    print(result.trade_stats())
    # Total trades: 342
    # Avg trade P&L: ₹1,240
    # Median trade P&L: ₹680
    # Top 5 trades contribute: 42% of total P&L

Requirements:

- Minimum 100 trades over the backtest period
- Top 5 trades contribute < 30% of total P&L
- Removing the best trade reduces Sharpe by < 30%

    trimmed = result.remove_top_trades(5)
    print(trimmed.sharpe)   # Should still be > 0.6

## The Deflated Sharpe Ratio

The most rigorous test is the **Deflated Sharpe Ratio** (Bailey &
López de Prado, 2014), which adjusts the observed Sharpe for the
number of trials and the non-normality of returns.

    from honba.algo_analytics import deflated_sharpe

    dsr = deflated_sharpe(
        result=result,
        num_trials=500,             # how many strategies you tested
        benchmark_sharpe=0.0,
    )

    print(dsr)
    # Observed Sharpe: 1.18
    # Deflated Sharpe: 0.42
    # p-value: 0.087
    # Conclusion: NOT SIGNIFICANT at 5% level

If you tested 500 strategies and the winner has an observed Sharpe of
1.18, the deflated Sharpe corrects for the selection. A deflated
Sharpe above 0.5 with p < 0.05 is required for a strategy to be
considered statistically significant.

This is the single most important metric in the toolkit. It is also
the one most often ignored.

## The Validation Report

Honba produces a validation report that summarises all six tests:

    from honba.algo_analytics import validate

    report = validate(
        node=node,
        strategy=SmaCrossover,
        num_trials=500,
        config=ValidationConfig(
            min_oos_is_ratio=0.5,
            min_folds_profitable=0.75,
            min_mc_sharpe_5pct=0.0,
            min_trades=100,
            max_top5_contribution=0.30,
            min_deflated_sharpe=0.5,
        ),
    )

    report.print()
    # Validation Report: SmaCrossover
    # ────────────────────────────────────────
    # ✓ OOS/IS ratio: 0.67 (> 0.50 required)
    # ✓ Walk-forward: 7/8 folds profitable (> 6 required)
    # ✓ Monte Carlo 5th Sharpe: 0.72 (> 0.00 required)
    # ✓ Parameter plateau score: 0.61 (> 0.40 required)
    # ✓ Regimes: 4/5 positive Sharpe
    # ✓ Trade count: 342 (> 100 required)
    # ✓ Top 5 contribution: 24% (< 30% required)
    # ✗ Deflated Sharpe: 0.42 (< 0.50 required)
    # ────────────────────────────────────────
    # RESULT: FAILED (1 of 7 checks failed)

    report.save_html("validation_report.html")

A strategy that fails any required check is not promoted to paper
trading. The failed check indicates the specific weakness.

## Why This Is Not Optional

The purpose of statistical validation is not to produce a
conservative-looking report. It is to prevent you from deploying a
strategy that will lose money. The number of strategies that fail
these tests is not a small fraction — for retail-style strategies on
Indian equities, the pass rate is typically 1–5% of ideas tested.

Running the tests is what makes Honba useful. Skipping them is what
makes a backtester a random-number generator.
