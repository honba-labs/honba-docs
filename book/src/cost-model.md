# Indian Cost Model

Trading costs in India are the difference between a strategy that looks
profitable on a spreadsheet and one that is actually profitable. A
delivery equity round-trip costs roughly **0.14% per side** once STT,
stamp duty, exchange fees, SEBI fee, GST, and brokerage are summed. At
that level, a strategy trading weekly needs a gross edge of several
hundred basis points annually just to break even.

Honba models every cost component separately so that a strategy's
sensitivity to each can be measured.

*Last verified: 2026-09-30. STT rates reflect the Finance Act 2026, effective 1 April 2026.*

## The Six Components

| Component | Rate | Charged on | Side |
|---|---|---|---|
| STT | varies by segment | transaction value | see below |
| Exchange transaction charges | ~0.00325% (NSE equity) | turnover | both |
| SEBI turnover fee | ₹10 per crore (0.0001%) | turnover | both |
| Stamp duty | 0.003% (varies by state) | value | buy only |
| GST | 18% | brokerage + exchange + SEBI | both |
| Brokerage | broker-defined | per order or % | both |

## STT — Rates Effective 1 April 2026

The Finance Act 2026 raised STT on derivatives. Equity delivery and
intraday rates are unchanged.[reference:5]

| Transaction | STT rate | Side |
|---|---|---|
| Equity delivery | 0.1% | buy **and** sell |
| Equity intraday | 0.025% | sell only |
| Equity futures | 0.05% | sell only |
| Equity options (premium) | 0.15% | sell only (writer) |
| Equity options (exercise) | 0.15% of intrinsic value | buy only |
| Sale of unlisted IPO shares | 0.2% | sell |
| Sale of equity MF units | 0.001% | sell |

The derivative rates were raised specifically to curb very-short-expiry
options trading: futures went from 0.02% to 0.05%, and options premium
from 0.10% to 0.15%.[reference:6]

## Exchange Transaction Charges

NSE equity: 0.00325% of turnover.
NSE equity options: 0.035% of premium.
NSE equity futures: 0.0019% of turnover.
BSE rates differ slightly.

These are charged on **both** sides of every trade.

## SEBI Turnover Fee

SEBI levies a turnover fee of **₹10 per crore** (0.0001%) on all buy and
sell turnover for non-debt securities, and ₹2.5 per crore for debt
securities.[reference:7] From April 2025, this fee attracts 18% GST.[reference:8]

## Stamp Duty

Stamp duty is a **state-level** tax, charged on the **buy side only**.
For equity delivery, the rate is 0.003% (₹3 per lakh) in most states,
capped at ₹1,500 per day per security. For intraday and F&O, the rate
is 0.002% (₹2 per lakh).

No GST is levied on stamp duty — it is a pure reimbursement passed
through to the state government.[reference:9]

## GST

GST at **18%** applies to the sum of brokerage, exchange transaction
charges, SEBI turnover fee, and (for F&O) clearing charges.[reference:10]

This means GST is **not** charged on STT or stamp duty. A common mistake
in simple cost models is to apply 18% to the full cost stack.

## Brokerage

Brokerage varies widely. For backtesting, Honba uses a configurable
model with sensible defaults per broker type:

| Broker style | Default model | Example |
|---|---|---|
| Discount, per-order | ₹20 per executed order | Zerodha |
| Discount, percentage | 0.03% or ₹20, lower | Zerodha (F&O) |
| Full-service, percentage | 0.1% – 0.5% | Traditional brokers |
| Zero-brokerage | ₹0 | Some discount brokers on delivery |

The `brokers.md` document lists per-broker defaults.

## The `CostModel` API

    use honba_algo_testing::cost::{CostModel, IndiaEquityCost, IndiaOptionsCost};

    let model = IndiaEquityCost::delivery()
        .with_brokerage(Brokerage::PerOrder(20.0))
        .with_state(State::Maharashtra);

    let cost = model.round_trip(
        buy_price: dec!(2450.50),
        sell_price: dec!(2510.75),
        quantity: 100,
    );

    println!("{}", cost.breakdown());

Output:

    STT (buy):        ₹245.05  (0.1%)
    STT (sell):       ₹251.08  (0.1%)
    Exchange (buy):   ₹7.96    (0.00325%)
    Exchange (sell):  ₹8.16    (0.00325%)
    SEBI (buy):       ₹0.25
    SEBI (sell):      ₹0.25
    Stamp duty (buy): ₹7.35    (0.003%)
    GST:              ₹4.48    (18% on brokerage+exchange+SEBI)
    Brokerage (buy):  ₹20.00
    Brokerage (sell): ₹20.00
    ─────────────────────────
    Total:            ₹564.58
    Effective:        0.114% of buy value, 0.114% of sell value

## Presets

    IndiaEquityCost::delivery()           # STT both sides, no intraday rules
    IndiaEquityCost::intraday()           # STT sell only
    IndiaFuturesCost::index()             # STT 0.05% sell only
    IndiaOptionsCost::index()             # STT 0.15% on premium (sell)
    IndiaOptionsCost::index_exercise()    # STT 0.15% on intrinsic (buy)

Each preset encodes the segment-specific rules so a backtest cannot
accidentally use delivery rates for an intraday strategy.

## Sensitivity Analysis

Because costs can dominate a strategy's P&L, Honba provides a helper to
measure sensitivity:

    let sweep = cost_sensitivity(
        &node,
        &SmaCrossover,
        brokerage_range = (0.0, 50.0, 10),   # ₹0 to ₹50 per order
    );
    sweep.plot("cost_sensitivity.html");

This produces a chart showing Sharpe ratio as a function of per-order
brokerage. If a strategy's edge disappears at ₹20 per order, it is not
a viable retail strategy regardless of backtested returns.

## Why This Matters

A strategy that trades 500 times per year on a ₹10 lakh portfolio pays
roughly:

    500 round trips × 0.114% per side × 2 sides × ₹10,00,000
    = 500 × ₹2,280
    = ₹11,40,000 in costs

That is **more than the initial capital**. Any backtest that ignores
costs would show this strategy as profitable even if it loses money in
reality. The cost model is not an optional refinement — it is the
difference between a valid backtest and a fiction.

## Configuration

    # configs/backtest/nifty50_momentum.toml
    [cost]
    model = "india_equity_delivery"
    brokerage = { type = "per_order", value = 20.0 }
    state = "Maharashtra"
    stt_rates = "finance_act_2026"    # pinned to a known version

Pinning `stt_rates` to a named version means a historical backtest
reproduces exactly, even after rates change.

## Source of Truth

- STT: Finance Act, published annually; NSE circular for operational
  details.
- Exchange charges: NSE/BSE transaction charges circulars.
- SEBI fee: SEBI circular on turnover fees.
- Stamp duty: state Stamp Act; consolidated by NSE.
