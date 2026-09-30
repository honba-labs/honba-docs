# Indicators

Honba ships with 40+ technical indicators implemented in Rust and
wrapped for Python. All indicators follow the same incremental API:
O(1) update per bar, `None` until warmed up.

Indicators are defined in `honba.strategies.indicators` (Python) and
`honba_algo_indicators` (Rust). The Python wrappers call into the Rust
implementations via PyO3, so a Python strategy gets Rust performance.

## The Indicator Contract

    class Indicator:
        def update(self, *values) -> float | None: ...
        def reset(self) -> None: ...
        @property
        def value(self) -> float | None: ...
        @property
        def is_ready(self) -> bool: ...

- `update()` consumes one observation and returns the current value,
  or `None` if the indicator has not seen enough data yet.
- `reset()` clears state. This is called automatically at the start of
  each backtest.
- `value` returns the most recent value without updating.
- `is_ready` is `True` once the warm-up period has elapsed.

## Trend Indicators

### Simple Moving Average

    from honba.strategies.indicators import SMA

    sma = SMA(period=20)
    sma.update(price)       # → None until 20 values seen
    # ... 20 values later
    sma.update(price)       # → float

### Exponential Moving Average

    ema = EMA(period=20)          # standard EMA
    ema = EMA(period=20, alpha=0.1)  # explicit smoothing factor

### Weighted Moving Average

    wma = WMA(period=20)

### MACD

    macd = MACD(fast=12, slow=26, signal=9)
    macd.update(price)
    # → MACDResult(macd_line, signal_line, histogram)

### ADX (Average Directional Index)

    adx = ADX(period=14)
    adx.update(high, low, close)
    # → ADXResult(adx, plus_di, minus_di)

### Supertrend

Popular in Indian retail trading, especially on intraday timeframes:

    supertrend = SuperTrend(period=10, multiplier=3.0)
    supertrend.update(high, low, close)
    # → SuperTrendResult(value, direction)   # direction: 1 (up) or -1 (down)

## Momentum Indicators

### RSI

    rsi = RSI(period=14)
    rsi.update(price)         # → 0..100

    # Wilder's smoothing is the default
    # Use EMA-style smoothing if you need a different variant:
    rsi = RSI(period=14, smoothing="ema")

### Stochastic

    stoch = Stochastic(k_period=14, d_period=3, smoothing=3)
    stoch.update(high, low, close)
    # → StochasticResult(k, d)

### CCI

    cci = CCI(period=20)
    cci.update(high, low, close)

### Williams %R

    wr = WilliamsR(period=14)
    wr.update(high, low, close)

### Rate of Change

    roc = ROC(period=10)
    roc.update(price)

## Volatility Indicators

### Bollinger Bands

    bb = Bollinger(period=20, stddev=2.0)
    bb.update(price)
    # → BollingerResult(upper, middle, lower)
    # .percent_b(price)    # position within the bands
    # .bandwidth()          # (upper - lower) / middle

### ATR

    atr = ATR(period=14)
    atr.update(high, low, close)

### Keltner Channel

    kc = Keltner(period=20, atr_period=10, multiplier=2.0)
    kc.update(high, low, close)
    # → KeltnerResult(upper, middle, lower)

### Donchian Channel

    dc = Donchian(period=20)
    dc.update(high, low)
    # → DonchianResult(upper, middle, lower)

## Volume Indicators

### On-Balance Volume

    obv = OBV()
    obv.update(close, volume)

### VWAP

VWAP is session-relative for intraday use; it resets each trading day:

    vwap = VWAP(reset="session")
    vwap.update(high, low, close, volume)

    # Or cumulative across the backtest:
    vwap = VWAP(reset=None)

### Money Flow Index

    mfi = MFI(period=14)
    mfi.update(high, low, close, volume)

### Volume Profile

Returns a histogram of traded volume by price:

    vp = VolumeProfile(bins=50, lookback_bars=390)
    vp.update(price=bar.close, volume=bar.volume)
    vp.histogram()          # dict[price_bin, volume]
    vp.poc()                # point of control (highest-volume price)
    vp.value_area(0.70)     # (low, high) for 70% of volume

## India-Specific Indicators

The `honba.strategies.indicators.india` module contains indicators
popular in Indian retail and algorithmic trading:

### Pivot Points

    from honba.strategies.indicators.india import PivotPoints

    pp = PivotPoints(method="classic")
    pp.update(prev_high, prev_low, prev_close)
    # → PivotResult(pp, r1, r2, r3, s1, s2, s3)

Supported methods: `"classic"`, `"fibonacci"`, `"camarilla"`,
`"woodie"`, `"demark"`.

### CPR (Central Pivot Range)

Widely used by Indian intraday traders:

    cpr = CPR()
    cpr.update(prev_high, prev_low, prev_close)
    # → CPRResult(pivot, tc, bc)   # top central, bottom central
    # .is_narrow()                  # narrow CPR = trending day expected
    # .is_wide()                    # wide CPR = range-bound day expected

### Gap Analysis

Detects opening gaps relative to the prior close:

    gap = Gap()
    gap.update(prev_close, today_open)
    # → GapResult(direction, size, pct)
    # direction: "up", "down", "flat"

## Composite Indicators

Some indicators wrap others:

    # RSI on top of a moving average
    smoothed_rsi = Composite(
        primary=RSI(14),
        smoother=SMA(3),
        field="value",
    )

    # Bollinger on RSI (popular for overbought/oversold confirmation)
    bb_rsi = Bollinger(period=14, stddev=2.0)
    def on_bar(self, bar):
        rsi_val = self.rsi.update(bar.close)
        if rsi_val is not None:
            bands = bb_rsi.update(rsi_val)

## GPU-Accelerated Indicators

For vectorized research (Tier 1 backtests), indicators are available in
GPU-accelerated form for bulk computation:

    from honba.research.vectorized import gpu_sma, gpu_rsi

    prices = load_prices("RELIANCE", start="2015-01-01")
    sma_20 = gpu_sma(prices, period=20)     # returns a Series

This requires a CUDA-capable GPU. Falls back to CPU if unavailable.

## Writing a Custom Indicator

    from honba.strategies.indicators import Indicator


    class CustomMomentum(Indicator):
        def __init__(self, period: int):
            self.period = period
            self.buffer = []
            self._value = None

        def update(self, price: float) -> float | None:
            self.buffer.append(price)
            if len(self.buffer) > self.period:
                self.buffer.pop(0)
            if len(self.buffer) < self.period:
                return None
            self._value = (self.buffer[-1] - self.buffer[0]) / self.buffer[0]
            return self._value

        def reset(self) -> None:
            self.buffer.clear()
            self._value = None

        @property
        def value(self) -> float | None:
            return self._value

        @property
        def is_ready(self) -> bool:
            return self._value is not None

Custom indicators can be written in Python for research, but for
production use, port them to Rust in `honba-algo-indicators` and expose
them via a Python wrapper. The performance difference is significant
for strategies that trade many instruments.

## A Note on Warm-Up

Every indicator has a warm-up period. An SMA(50) returns `None` for
the first 49 updates. A strategy must check for `None` before using an
indicator value:

    if sma is None:
        return

The engine does not skip bars during warm-up; the strategy decides how
to handle them. A common pattern is to subscribe to a longer history
than the strategy needs and let the engine feed the extra bars to the
indicator before the strategy starts trading.

## Sources

The indicator implementations follow the definitions in:

- Wilder, J. Welles. *New Concepts in Technical Trading Systems* (1978)
  — RSI, ATR, ADX.
- Appel, Gerald. *Technical Analysis: Power Tools for Active Investors*
  (2005) — MACD.
- Bollinger, John. *Bollinger on Bollinger Bands* (2001).
- NSE Technical Analysis documentation — pivot points, CPR.
