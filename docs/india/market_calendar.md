
# Market Calendar

`honba-india` models the Indian trading calendar as two traits plus one
concrete implementation. No holiday data is hardcoded — you supply it.

## Traits

### `TradingCalendar`

The interface every exchange calendar implements.

| Method | Purpose |
|---|---|
| `is_trading_day(date) -> bool` | Weekday and not a holiday |
| `session_open(date) -> Option<Time>` | Opening time, `None` on closed days |
| `session_close(date) -> Option<Time>` | Closing time |
| `next_trading_day(date) -> Option<NaiveDate>` | First trading day strictly after `date` |
| `prev_trading_day(date) -> Option<NaiveDate>` | First trading day strictly before `date` |
| `trading_days_between(start, end) -> Vec<NaiveDate>` | Inclusive range, holidays removed |

### `HolidaySource`

Anything that can produce a set of holiday dates. Implement this for a
static list, a CSV file, or a network-backed source.

| Method | Purpose |
|---|---|
| `holidays(year: i32) -> Result<BTreeSet<NaiveDate>, Self::Error>` | All holidays for a calendar year |

## Concrete implementation: `NseCalendar`

Two constructors:

```rust
use honba_india::{NseCalendar, HolidaySource};

// From an in-memory list
let cal = NseCalendar::from_holidays(vec![
    "2025-01-26".parse().unwrap(), // Republic Day
    "2025-03-14".parse().unwrap(), // Holi
]);

// From any HolidaySource
let cal = NseCalendar::from_source(my_csv_source)?;
```

`from_holidays` is the path to use in tests and examples. `from_source`
wires in a real holiday feed.

## Session windows

NSE equity sessions run 09:15–15:30 IST. The calendar exposes them
per-date so a closed day returns `None`:

```rust
match cal.session_open(date) {
    Some(t) => println!("opens at {t}"),
    None    => println!("market closed"),
}
```

## Navigating around holidays

```rust
let next = cal.next_trading_day(NaiveDate::from_ymd_opt(2025, 1, 24).unwrap());
// skips the weekend and Republic Day → 2025-01-27 (Monday)

let days = cal.trading_days_between(
    NaiveDate::from_ymd_opt(2025, 1, 20).unwrap(),
    NaiveDate::from_ymd_opt(2025, 1, 31).unwrap(),
);
// 7 weekdays, minus any holidays in that window
```

## Why no bundled data

Exchange holidays are revised yearly and differ by segment (equity vs
F&O vs currency). Shipping a hardcoded list guarantees the calendar goes
stale. Instead:

1. Ship the traits and the NSE session times.
2. Let the user provide holidays via `HolidaySource`.
3. Provide a CSV-backed source as a convenience.

## Testing

`NseCalendar::from_holidays(vec![])` gives a pure weekday calendar. Use
it in unit tests where holidays would only obscure the logic under test.
# Cost Model

`honba-india` separates *rates* (what the tax and fee schedule looks
like) from *application* (how they are applied to a specific fill).

## Rates: `SttRates`

Securities Transaction Tax is charged per segment, and the rate differs
between delivery and intraday. `SttRates::new` takes the full schedule:

```rust
use honba_india::{SttRates, Segment};

let stt = SttRates::new(
    /* delivery_buy_bps  */ 10.0,
    /* delivery_sell_bps */ 10.0,
    /* intraday_sell_bps */ 2.5,
    /* options_sell_bps  */ 6.25,
);
```

All rates are **basis points** (1 bps = 0.01%). Buy-side rates are zero
for intraday and options on NSE — that is the actual rule, not an
oversight.

## Segments

`Segment` identifies which rate table applies:

| Variant | Applies to |
|---|---|
| `Segment::EquityDelivery` | CNC equity |
| `Segment::EquityIntraday` | MIS equity |
| `Segment::Futures` | F&O futures |
| `Segment::Options` | F&O options |

## The model: `CostModel`

`CostModel::new` takes the full set of charges and produces a
`CostBreakdown` per fill:

```rust
use honba_india::{CostModel, SttRates, Segment};

let model = CostModel::new(
    stt,
    /* brokerage_bps  */ 3.0,
    /* exchange_bps   */ 0.325,
    /* gst_pct        */ 18.0,
    /* stamp_bps      */ 0.3,
    /* sebi_bps       */ 0.01,
);

let breakdown = model.compute(
    /* price   */ 22_450.0,
    /* qty     */ 50.0,
    /* side    */ Side::Buy,
    /* segment */ Segment::EquityDelivery,
);
```

## `CostBreakdown`

The return type itemises every charge so you can attribute them
separately in analytics:

| Field | Description |
|---|---|
| `brokerage` | Broker commission |
| `stt` | Securities Transaction Tax |
| `exchange` | Exchange transaction charge |
| `gst` | GST on brokerage and exchange |
| `stamp` | Stamp duty (buy side only) |
| `sebi` | SEBI turnover fee |
| `total` | Sum of the above |

## Wiring into a run

In a `Sim`, attach one `CostModel` as a child of the top-level container
and let the execution component look it up. The reference Python bridge
uses `sim.find("cost_model")` for exactly this.

```python
CostModel(brokerage_bps=3.0, stt_bps=1.0, parent=sim)
BarFill(slippage_bps=2.0, cost_model=sim.find("cost_model"), parent=sim)
```

## Sources for the `CostModelSource` trait

Like `HolidaySource`, the rates are not hardcoded — you supply them.
`CostModelSource` lets you load a rate sheet from a TOML file or a
database and produce a fresh `SttRates` and `CostModel` each session.

```rust
pub trait CostModelSource {
    type Error;
    fn load(&self, as_of: NaiveDate) -> Result<CostModel, Self::Error>;
}
```

Use `as_of` for the rate-schedule date, not the trade date — brokers
sometimes back-date a rate change by a session.

## Testing

Cost models are easy to test because the arithmetic is deterministic:

```rust
let got = model.compute(100.0, 1.0, Side::Buy, Segment::EquityDelivery);
let want = CostBreakdown { brokerage: 0.03, stt: 0.1, /* ... */ };
assert_eq!(got, want);
```

Keep a golden table of expected values per segment, updated whenever the
schedule changes. That is what catches a silently-wrong rate before it
hits a live P&L report.

