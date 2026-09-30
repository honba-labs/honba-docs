# Index Options

NIFTY and BANK NIFTY options are among the most actively traded
derivative contracts in the world. Backtesting them correctly requires
handling weekly expiry cycles, strike intervals, exercise style, and
segment-specific costs — none of which are trivial.

*Last verified: 2026-09-30 against NSE contract specifications.*

## Expiry Cycles

### NIFTY 50

NIFTY 50 index options have a richer contract structure than any other
Indian derivative:[reference:20]

- **4 weekly expirations** (excluding monthly contracts)
- **3 monthly expirations** (near, mid, far month)
- **3 quarterly expirations** (March, June, September, December cycle)
- **8 half-yearly expirations** (June and December cycle)

### BANK NIFTY

- **3 monthly expirations**
- **3 quarterly expirations**

BANK NIFTY does **not** have weekly options; only NIFTY 50 (and SENSEX
on BSE) do.

### Expiry Day

All index options expire on **Tuesday** of the expiry week. If Tuesday
is a trading holiday, expiry moves to the previous trading day.[reference:21]

This is a recent change — until 2025, NIFTY weekly expiry was Thursday.
Strategies written before this change that assumed Thursday expiry will
silently produce wrong results if backtested on post-change data.

## Strike Intervals

Strike intervals for index options are set by NSE and have changed
recently:

- **Monthly and quarterly NIFTY 50 contracts:** strike interval
  changed from 100 to **25 points**, with the strike scheme changing
  from 25-1-25 to 100-1-100.[reference:22]
- **Weekly and 0DTE contracts:** retain the existing scheme.
- **BANK NIFTY:** strike interval is 100 points.

    let chain = OptionChain::new(
        underlying: Index::Nifty50,
        expiry: NaiveDate::from_ymd_opt(2026, 10, 27).unwrap(),
    );
    chain.strikes()          // Vec<Decimal>
    chain.atm_strike(24500)  // nearest strike to spot

## Option Greeks

Honba computes Greeks using the Black-Scholes model with continuous
dividend yield, calibrated to the Indian risk-free rate (typically the
91-day T-bill yield).

    let greeks = option.greeks(spot, volatility, time_to_expiry, rate);
    greeks.delta    // ∂V/∂S
    greeks.gamma    // ∂²V/∂S²
    greeks.theta    // ∂V/∂t
    greeks.vega     // ∂V/∂σ
    greeks.rho      // ∂V/∂r

For index options, implied volatility is backed out from the traded
premium by Newton-Raphson. The `OptionChain` type provides a full IV
surface:

    let surface = chain.iv_surface();
    surface.at(strike=24500, expiry=2026-10-27)  // → 0.142

## Weekly vs Monthly Backtesting

A weekly options strategy needs data at a granularity that monthly
strategies do not. Honba's backtest engine handles both, but the data
requirements differ:

| Strategy type | Required data | Catalog size (1 year, NIFTY) |
|---|---|---|
| Monthly expiry, ATM only | Daily EOD | ~50 MB |
| Weekly expiry, ATM ± 5 strikes | 1-minute | ~8 GB |
| 0DTE, full chain | Tick | ~200 GB |

The scaffold does not ship options tick data. You must source it from a
broker or vendor and import it via `honba-algo-import::nse::options`.

## Cost Model for Options

STT on options is **0.15% of premium** on the sell side, and **0.15% of
intrinsic value** on exercise (buy side).[reference:23]

    let cost = IndiaOptionsCost::index();

    // For a short straddle:
    let sell_call = cost.sell(premium: dec!(120.50), qty: 50);
    let sell_put  = cost.sell(premium: dec!(98.25),  qty: 50);
    // STT: 0.15% of each premium

    // For exercise:
    let exercise = cost.exercise(intrinsic: dec!(200.00), qty: 50);
    // STT: 0.15% of intrinsic

Note that STT on options **premium** is charged on the sell side only,
but STT on **exercise** is charged on the buy side. This asymmetry
matters for strategies that alternate between closing positions and
letting them expire.

## Expiry Day Handling

Expiry day is where most options backtests go wrong. Three issues:

1. **Expiry timing.** NIFTY weekly options expire at 3:30 PM on the
   expiry day. Any position not closed by then is settled at intrinsic
   value (cash settlement for index options).

2. **Settlement price.** Index options are cash-settled at the closing
   price of the underlying on expiry day, not the closing price of the
   option.

3. **STT on exercise.** If a position is held to expiry and has
   intrinsic value, STT is charged on that value.

    config = BacktestConfig {
        options: OptionsConfig {
            settlement = Settlement::Cash,
            exercise_on_expiry = ExerciseRule::AutoExercise,
            stt_on_exercise = true,
        },
        // ...
    };

## A Short Straddle Example

    from honba.strategies.base import Strategy
    from honba.india.options import OptionChain, Index

    class NiftyShortStraddle(Strategy):
        def on_start(self):
            self.chain = OptionChain.live(Index.Nifty50)

        def on_expiry_cycle(self, expiry):
            atm = self.chain.atm_strike(self.spot)
            call = self.chain.option(atm, OptionType.CE, expiry)
            put  = self.chain.option(atm, OptionType.PE, expiry)
            self.sell(call, qty=50)
            self.sell(put, qty=50)

        def on_bar(self, bar):
            if self.greeks.delta > 30:
                self.close(nearest=self.chain.atm_strike(self.spot))

## Data Sourcing

Options data is the hardest data to obtain in India:

- **Broker APIs** provide historical option data, but usually only
  minute-level and only for a limited window.
- **NSE bhavcopy** provides daily EOD option data (strike, expiry,
  open, high, low, close, OI, volume) in the F&O bhavcopy file.
- **Vendors** (TrueData, GDFL, etc.) provide tick-level historical
  options data for a fee.

Honba's importer handles the NSE F&O bhavcopy format:

    from honba.india.options import import_nse_bhavcopy_fno

    import_nse_bhavcopy_fno(
        path="FO_Bhavcopy_20261027.zip",
        catalog="./data/catalog",
    )

## Source of Truth

- Contract specifications: NSE equity derivatives contract
  specifications page.
- Expiry day changes: NSE circulars, most recently FAOP/68747.
- STT on options: Finance Act, effective 1 April 2026.
