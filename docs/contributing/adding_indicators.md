# Adding Indicators

An indicator is a stateful object that consumes a stream of values and
produces a single value (or a small tuple). Honba's indicators are
implemented in Rust and exposed to Python via PyO3.

Adding a new indicator involves:

1. Implementing the indicator in `crates/honba-algo-indicators/`.
2. Adding unit tests.
3. Exposing it to Python in `python/honba/strategies/indicators/`.
4. Documenting it in `docs/strategies/indicators.md`.

## The Indicator Trait

Every indicator implements the `Indicator` trait:

    pub trait Indicator {
        type Input;
        type Output;

        fn update(&mut self, input: Self::Input) -> Option<Self::Output>;
        fn reset(&mut self);
        fn is_ready(&self) -> bool;
    }

The `update` method consumes one observation and returns `None` until
the indicator has seen enough data. The engine never calls an indicator
before it is ready; the strategy is responsible for checking `None`.

## A Minimal Indicator: Rate of Change

Rate of Change is the percentage change over a period:

    ROC(n) = (price_t - price_{t-n}) / price_{t-n}

Implementation in `crates/honba-algo-indicators/src/momentum/roc.rs`:

    use crate::indicator::Indicator;
    use std::collections::VecDeque;

    #[derive(Debug, Clone)]
    pub struct ROC {
        period: usize,
        prices: VecDeque<f64>,
        value: Option<f64>,
    }

    impl ROC {
        pub fn new(period: usize) -> Self {
            assert!(period > 0, "ROC period must be positive");
            Self {
                period,
                prices: VecDeque::with_capacity(period + 1),
                value: None,
            }
        }

        pub fn value(&self) -> Option<f64> {
            self.value
        }
    }

    impl Indicator for ROC {
        type Input = f64;
        type Output = f64;

        fn update(&mut self, price: f64) -> Option<f64> {
            self.prices.push_back(price);
            if self.prices.len() > self.period + 1 {
                self.prices.pop_front();
            }

            if self.prices.len() < self.period + 1 {
                return None;
            }

            let oldest = self.prices.front().unwrap();
            let newest = self.prices.back().unwrap();
            let roc = (newest - oldest) / oldest;
            self.value = Some(roc);
            Some(roc)
        }

        fn reset(&mut self) {
            self.prices.clear();
            self.value = None;
        }

        fn is_ready(&self) -> bool {
            self.value.is_some()
        }
    }

The structure is uniform across all indicators: a fixed-size buffer,
a current value, and the three trait methods.

## Naming and Placement

Indicators are grouped by category:

    src/
    ├── trend/          — SMA, EMA, MACD, ADX, Supertrend
    ├── momentum/       — RSI, Stochastic, CCI, ROC, Williams %R
    ├── volatility/     — Bollinger, ATR, Keltner, Donchian
    ├── volume/         — OBV, VWAP, MFI, VolumeProfile
    ├── india/          — PivotPoints, CPR, Gap
    └── gpu/            — GPU-accelerated versions

Place the indicator in the category that best describes what it
measures. If a new category is needed (for example, "sentiment" for
indicators built on news data), create the directory and add
`mod sentiment;` to `src/lib.rs`.

## Registering in `lib.rs`

Add the new module to the appropriate `mod.rs`:

    // crates/honba-algo-indicators/src/momentum/mod.rs
    pub mod cci;
    pub mod roc;         // new
    pub mod rsi;
    pub mod stochastic;
    pub mod williams_r;

Then re-export from the crate root:

    // crates/honba-algo-indicators/src/lib.rs
    pub use momentum::{CCI, ROC, RSI, Stochastic, WilliamsR};

## Unit Tests

Every indicator needs tests. Place them in the same file as the
implementation under `#[cfg(test)] mod tests`:

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn roc_returns_none_until_warmed_up() {
            let mut roc = ROC::new(5);
            for i in 1..=5 {
                assert!(roc.update(i as f64).is_none());
            }
            assert!(roc.update(6.0).is_some());
        }

        #[test]
        fn roc_computes_correctly() {
            let mut roc = ROC::new(5);
            for price in [100.0, 101.0, 102.0, 103.0, 104.0, 105.0] {
                roc.update(price);
            }
            // (105 - 100) / 100 = 0.05
            assert!((roc.value().unwrap() - 0.05).abs() < 1e-10);
        }

        #[test]
        fn roc_resets_cleanly() {
            let mut roc = ROC::new(5);
            for price in 1..=10 {
                roc.update(price as f64);
            }
            roc.reset();
            assert!(!roc.is_ready());
            assert!(roc.value().is_none());
        }

        #[test]
        fn roc_handles_flat_prices() {
            let mut roc = ROC::new(5);
            for _ in 0..10 {
                roc.update(100.0);
            }
            assert_eq!(roc.value().unwrap(), 0.0);
        }
    }

Three tests are mandatory: the warm-up behavior, a known-value
computation, and reset. Additional tests for edge cases (flat prices,
zero values, NaN inputs) are strongly encouraged.

## Verification Against a Reference

For indicators that match a standard definition, verify against a
reference implementation. TA-Lib is the common choice:

    #[test]
    fn roc_matches_talib() {
        let prices: Vec<f64> = load_test_data("prices.csv");
        let mut roc = ROC::new(14);
        let our_values: Vec<f64> = prices.iter()
            .filter_map(|&p| roc.update(p))
            .collect();

        // Talib values for the same input, precomputed and checked in
        let talib_values: Vec<f64> = load_test_data("roc_14_expected.csv");

        assert_approx_eq_slice(&our_values, &talib_values, 1e-8);
    }

If the indicator does not match a reference, either the
implementation is wrong or the reference uses a different convention.
Both are worth knowing.

## Exposing to Python

Create a Python wrapper in
`python/honba/strategies/indicators/<name>.py`:

    from honba._lib import ROC as _ROC
    from honba.strategies.indicators.base import Indicator


    class ROC(Indicator):
        """Rate of Change.

        Computes the percentage change over a period.

        Example:
            roc = ROC(period=14)
            value = roc.update(price)
        """

        def __init__(self, period: int):
            self._inner = _ROC(period)

        def update(self, price: float) -> float | None:
            return self._inner.update(price)

        def reset(self) -> None:
            self._inner.reset()

        @property
        def value(self) -> float | None:
            return self._inner.value()

        @property
        def is_ready(self) -> bool:
            return self._inner.is_ready()

Add it to `python/honba/strategies/indicators/__init__.py`:

    from .roc import ROC

    __all__ = [
        # ...
        "ROC",
        # ...
    ]

And to the type stubs in `__init__.pyi`:

    class ROC(Indicator):
        def __init__(self, period: int) -> None: ...
        def update(self, price: float) -> float | None: ...
        @property
        def value(self) -> float | None: ...
        @property
        def is_ready(self) -> bool: ...

## Benchmarks

Add a benchmark in `benchmarks/src/indicator_bench.rs`:

    use criterion::{black_box, criterion_group, criterion_main, Criterion};
    use honba_algo_indicators::ROC;

    fn bench_roc(c: &mut Criterion) {
        let prices: Vec<f64> = (0..10_000).map(|i| 100.0 + i as f64 * 0.1).collect();

        c.bench_function("roc_14", |b| {
            b.iter(|| {
                let mut roc = ROC::new(14);
                for &p in &prices {
                    black_box(roc.update(p));
                }
            });
        });
    }

    criterion_group!(benches, bench_roc);
    criterion_main!(benches);

Run:

    cargo bench -p honba-benchmarks -- roc

An indicator that takes more than a few nanoseconds per update needs
investigation. Most indicators should be sub-nanosecond in release
mode.

## Documentation

Add the indicator to `docs/strategies/indicators.md` under the
appropriate category:

    ### Rate of Change

        roc = ROC(period=10)
        roc.update(price)

Brief, with the update signature. If the indicator has non-obvious
parameters or conventions, add a paragraph explaining them.

## Checklist

Before opening a pull request:

- [ ] Indicator implemented in the correct category
- [ ] Registered in `mod.rs` and re-exported from `lib.rs`
- [ ] Unit tests for warm-up, correctness, and reset
- [ ] Verified against a reference implementation (if applicable)
- [ ] Python wrapper in `python/honba/strategies/indicators/`
- [ ] Wrapper exported in `__init__.py` and `__init__.pyi`
- [ ] Benchmark added
- [ ] Documentation updated in `docs/strategies/indicators.md`
- [ ] `cargo test -p honba-algo-indicators` passes
- [ ] `cargo clippy` passes with no warnings
- [ ] `dependency_graph.py` still passes

## A Note on Numerical Stability

Financial data has outliers, missing values, and edge cases. An
indicator must handle:

- Zero prices or volumes (rare but possible in thin markets).
- NaN inputs (from missing data upstream).
- Very large values (should not overflow f64).
- Very small values (should not lose precision).

For RSI-like indicators that divide by a rolling sum, handle the case
where the sum is zero (flat prices over the period). For ATR-like
indicators, handle gaps and missing bars.

The unit tests should cover at least the flat-price case. If the
indicator produces NaN or infinity on any input, that is a bug.
