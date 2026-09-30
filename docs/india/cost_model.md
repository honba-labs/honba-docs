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

### `CostBreakdown`

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
