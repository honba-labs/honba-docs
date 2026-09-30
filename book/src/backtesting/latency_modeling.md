# Latency Modeling

Latency is the time between a strategy's decision and the exchange
acknowledging the resulting order. In a backtest, latency determines
which price a strategy actually gets. For intraday strategies, latency
is often the difference between profit and loss.

Honba models latency explicitly. The default is 50 ms, which is
realistic for a retail broker API in India.

## What Latency Includes

The full round trip from signal to fill includes:

| Component | Typical range | Notes |
|---|---|---|
| Strategy computation | 1–50 ms | Python overhead |
| Order serialization | < 1 ms | JSON encoding |
| Network to broker | 10–100 ms | Varies by ISP and region |
| Broker processing | 5–50 ms | Broker-side validation |
| Broker to exchange | 5–20 ms | Co-located, usually fast |
| Exchange matching | < 1 ms | NSE matching is fast |
| **Total** | **30–250 ms** | Retail typical |

For a retail trader using a broker's REST API from a home connection,
100–200 ms is realistic. For a colocated HFT setup, sub-millisecond is
possible, but that is not the target user of Honba.

## The Latency Model

    from honba.backtest.latency import (
        FixedLatency,
        GaussianLatency,
        EmpiricalLatency,
    )

    # Every order delayed by exactly 50 ms
    latency = FixedLatency(ms=50)

    # Normally distributed around 80 ms with std dev 20 ms
    latency = GaussianLatency(mean_ms=80, std_ms=20)

    # Sampled from an empirical distribution of recorded latencies
    latency = EmpiricalLatency(samples="latency_samples.parquet")

## How Latency Affects Fills

The engine applies latency as follows:

1. Strategy calls `self.buy(...)` at simulated time `T`.
2. The order is queued with a submission time of `T + latency`.
3. When the simulated clock advances past `T + latency`, the order is
   submitted to the simulated exchange.
4. The exchange fills the order at the price prevailing at that
   submission time.

If the price moved between `T` and `T + latency`, the strategy gets
the new price, not the price it saw.

### Example

Suppose a strategy sees a bar closing at ₹100 and decides to buy. With
zero latency, it fills at ₹100. With 200 ms latency on a fast-moving
stock, the price might be ₹100.20 by the time the order reaches the
exchange. The strategy has paid a 0.2% premium for the delay.

Over 250 trades per year, a 0.2% latency cost is 50% of capital.

## Choosing a Latency Value

| Strategy type | Recommended latency |
|---|---|
| Daily bars, EOD rebalance | 0 ms (irrelevant) |
| Weekly/monthly rebalance | 0 ms |
| Intraday bars, 15-min+ | 50 ms |
| Intraday bars, 1-min | 100 ms |
| Tick-level scalping | 200 ms+ |
| Options expiry-day scalping | 500 ms+ |

For any strategy that trades intraday, run the backtest with at least
two latency values and compare. A strategy whose edge disappears at
100 ms is not viable on a retail connection.

## Latency and Slippage Are Different

Latency and slippage are often conflated. They are different:

- **Latency** delays the order. The price the strategy gets is the
  price that existed when the order arrived, not when it was sent.
- **Slippage** is the difference between the price the order should
  have received (the quoted price) and the price it actually received
  (due to market impact, spread, or depth).

Honba models both separately. Latency is configured as above. Slippage
is configured in the simulated exchange:

    from honba.backtest.simulator import SimulatedExchange

    exchange = SimulatedExchange(
        fill_model="next_bar_open",
        slippage=Slippage.fixed_bps(5),      # 5 basis points per trade
    )

    # Or spread-based:
    exchange = SimulatedExchange(
        fill_model="next_bar_open",
        slippage=Slippage.half_spread(),
    )

## Fill Models

The simulated exchange supports several fill models:

### `next_bar_open`

The default. An order submitted during bar N fills at the open of bar
N+1. This is the most conservative realistic model for daily and
intraday bars.

### `next_bar_close`

Fills at the close of the bar during which the order was submitted.
Slightly optimistic.

### `same_bar_close`

Fills at the closing price of the bar whose close triggered the
signal. This is what most vectorized backtests do and is the **most
optimistic** model. Avoid it for validation.

### `intrabar_touch`

For limit orders: fills if the price touches the limit during the bar.
The fill price is the limit price.

### `intrabar_worst`

For market orders: fills at the worst price in the bar. Very
pessimistic; useful for stress-testing.

## The Interaction of Latency, Fill Model, and Bar Size

The three parameters are not independent. Some combinations produce
unrealistic results:

| Combination | Realistic? |
|---|---|
| 0 latency + `same_bar_close` + 1-min bars | No, way too optimistic |
| 50 ms latency + `next_bar_open` + 1-min bars | Yes |
| 200 ms latency + `next_bar_open` + daily bars | Latency irrelevant |
| 0 latency + `intrabar_touch` + tick data | Yes for HFT sim |

Honba warns at backtest start if the combination is likely unrealistic.

## The `latency_sensitivity` Helper

    from honba.backtest.latency import sensitivity

    sweep = sensitivity(
        node=node,
        strategy=SmaCrossover,
        latency_ms=[0, 25, 50, 100, 200, 500],
    )

    sweep.plot().save("latency_sensitivity.html")

The plot shows net return as a function of latency. A robust strategy
has a gentle slope; a fragile one collapses quickly.

## Latency in Live Trading

In live trading, latency cannot be configured — it is whatever it is.
The engine records actual latency for every order and includes it in
the performance report:

    result.live_metrics.latency_p50_ms    # median
    result.live_metrics.latency_p95_ms    # 95th percentile
    result.live_metrics.latency_p99_ms    # 99th percentile

If live latency is significantly worse than the backtest assumption,
the strategy's real performance will diverge from the backtest. This
is a common cause of "the backtest said 20% but live gives 5%."

## A Note on Colocation and Co-location

NSE offers colocation at its data center in Mumbai (BKC). Colocated
servers can achieve sub-millisecond latencies. This is not the target
use case for Honba. If your strategy requires colocation to be
profitable, it is not a strategy that Honba is designed to validate.

The realistic latency band for Honba backtests is **20 ms to 500 ms**.

## Next Steps

- **[Statistical Validation](statistical_validation.md)** — how to
  know if the result after costs and latency is real.
