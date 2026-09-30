# Index Universes

A "universe" in Honba is a named set of instruments with a defined
selection rule and rebalance schedule. The three most commonly used
universes for Indian equity strategies are NIFTY 50, BANK NIFTY, and the
Alpha 30 family.

The critical difference from a static ticker list is that **constituents
change over time**. A backtest that uses today's NIFTY 50 list for a
2020 start date will include stocks that were not in the index then,
and exclude stocks that were. This introduces look-ahead bias and
invalidates the result.

*Last verified: 2026-09-30 against NSE Indices methodology documents.*

## NIFTY 50

The flagship large-cap index. 50 stocks selected from the NIFTY 100
based on free-float market capitalisation, liquidity, and trading
frequency.

- **Parent universe:** NIFTY 100
- **Constituents:** 50
- **Rebalance:** semi-annual (March and September)
- **Weighting:** free-float market cap

Selection criteria require a minimum listing history of one year, 100%
trading frequency over the last year, and positive net worth as per
audited results.[reference:11]

## BANK NIFTY

The banking sector index, and the most-traded index options contract in
the world by volume.

- **Constituents:** 12 (largest and most liquid Indian banks)
- **Rebalance:** semi-annual
- **Weighting:** free-float market cap
- **Expiry:** weekly and monthly options

BANK NIFTY does not have the same liquidity filter as NIFTY 50 because
it is sector-constrained.

## The Alpha 30 Family

NSE publishes two Alpha 30 indices:

### NIFTY100 Alpha 30

Consists of **30 companies from the NIFTY 100**, selected based on
**Jensen's Alpha** computed using 1-year trailing prices (adjusted for
corporate actions).[reference:12]

**Selection criteria:**[reference:13]

1. Stock must be a constituent of NIFTY 100 at review time.
2. Minimum listing history of 1 year.
3. Companies undergoing demerger/capital restructuring are eligible
   after twelve calendar months of trading on an ex-basis.
4. Jensen's Alpha is computed using 1-year trailing prices.
5. Top 30 stocks by alpha score form the index.

**Weighting:** a combination of alpha score and free-float market
capitalisation ("tilt weighted").[reference:14] Each stock is capped at
the lower of 5% or its free-float weight.

**Rebalance:** **quarterly**, using data from the six-month period
ending the last trading day of February, May, August, and November.[reference:15]

### NIFTY200 Alpha 30

Same methodology, but the parent universe is NIFTY 200 instead of
NIFTY 100. Stocks move out of the NIFTY 200 also move out of this
index.[reference:16]

The key practical consequence for backtesting: **Alpha 30 rebalances
four times a year**, not two. A backtest spanning 2020–2025 must apply
20 distinct constituent lists, each effective from its announcement
date (not its effective date — NSE announces changes in advance).

## The `Universe` Trait

    use honba_india::universes::{Universe, UniverseId};

    pub trait Universe {
        /// Constituents effective on a given date.
        fn constituents_at(&self, date: NaiveDate) -> Vec<Instrument>;

        /// Weight for a constituent on a given date.
        fn weight_at(&self, date: NaiveDate, instr: &Instrument) -> Option<f64>;

        /// Dates on which the constituent list changes.
        fn rebalance_dates(&self, from: NaiveDate, to: NaiveDate) -> Vec<NaiveDate>;

        /// Announcement date for a given effective date.
        fn announcement_date(&self, effective: NaiveDate) -> Option<NaiveDate>;
    }

Built-in implementations:

    Nifty50::new()
    BankNifty::new()
    Alpha30::nifty100()
    Alpha30::nifty200()

## Look-Ahead Safety

The most important property of the `Universe` trait is that
`constituents_at(date)` returns the constituents **as they were known on
that date**. If NSE announced on 2023-02-20 that a stock would enter the
index on 2023-03-31, then:

- A backtest iterating over dates through 2023-03-30 sees the old list.
- The new list becomes active on 2023-03-31.

`announcement_date()` is provided separately for strategies that want to
trade the announcement (a common "index inclusion" strategy).

    let u = Alpha30::nifty100();
    let entry = NaiveDate::from_ymd_opt(2023, 3, 31).unwrap();
    let announced = u.announcement_date(entry).unwrap();
    // → 2023-02-20

## Historical Constituent Data

Honba ships with constituent history from 2015 onward for NIFTY 50,
BANK NIFTY, and both Alpha 30 variants. The data lives in
`honba-india/src/universes/data/` as Parquet files with the schema:

    effective_date | symbol | weight | announced_date

When NSE publishes a new review, the data file is updated and the
`honba-india` patch version is bumped.

## The Rebalance Event

Backtests handle rebalances through the engine's event stream:

    [universe]
    name = "alpha30_nifty100"
    rebalance_mode = "trade"     # or "signal_only"

With `rebalance_mode = "trade"`, the engine emits synthetic
`UniverseRebalance` events on each effective date. Strategies can
subscribe to these and adjust positions accordingly. With
`signal_only`, the universe changes but no orders are generated — the
strategy decides what to do.

## Equal Weight vs Market Weight

Most strategies in practice use an equal-weight portfolio regardless of
the index's actual weights, because market-cap weights concentrate risk
in the top few names. Honba supports both:

    let weights = u.weights_at(date);
    let equal = equal_weight(&u.constituents_at(date));

    config = BacktestConfig {
        universe: u,
        weighting: Weighting::Equal,      // or Weighting::Index
        // ...
    };

For Alpha 30 specifically, equal-weight is common because the alpha
score tilt is already captured by constituent selection.

## Custom Universes

Any user-defined set of instruments can be wrapped as a universe:

    let my_universe = StaticUniverse::new(vec![
        instrument("RELIANCE"),
        instrument("TCS"),
        instrument("INFY"),
    ]);

    // Or a filtered universe
    let liquid = FilteredUniverse::new(
        Nifty500::new(),
        |instr| instr.avg_daily_volume_30d > 1_000_000,
    );

Custom universes are useful for factor research where the selection
rule itself is the subject of the experiment.

## Source of Truth

- NIFTY 50, BANK NIFTY: NSE Indices methodology document (published
  annually, amended by circular).
- Alpha 30: NSE Indices "Methodology Document" PDF, section 13.
- Constituent changes: NSE Indices press releases, typically 4–6 weeks
  before effective date.
