# Mutual Funds

Mutual fund backtesting differs from equity backtesting in three ways:
there is no intraday trading (NAV is struck once daily), there is no
order book (you get the end-of-day NAV), and the relevant questions are
usually about SIP returns and category rotation rather than signals.

Honba models mutual funds as a distinct instrument type with their own
cost and tax treatment.

*Last verified: 2026-09-30.*

## NAV Data from AMFI

The Association of Mutual Funds in India publishes daily NAVs for every
scheme. NAVs are uploaded by 11:00 PM on every business day and can be
downloaded as a flat file from the AMFI portal.[reference:17]

Honba's importer reads this file:

    from honba.india.mutual_funds import fetch_amfi_nav, AmfiNavImporter

    # Download the current AMFI NAV file
    df = fetch_amfi_nav()          # returns a DataFrame

    # Or import into the Parquet catalog
    importer = AmfiNavImporter(catalog="./data/catalog")
    importer.import_latest()       # fetches and stores today's NAVs
    importer.import_history(start="2015-01-01")

The resulting catalog partition holds, per scheme:

    date | scheme_code | scheme_name | amc | category | nav | plan | isin

## Scheme Identification

Each scheme has a **six-digit AMFI scheme code** (stable) and a
**direct/regular plan** flag. A common source of bugs is mixing up
direct and regular plans, which have different NAVs and different
expense ratios.

    from honba.india.mutual_funds import Scheme, SchemeCode

    scheme = Scheme.by_code(120503)     # e.g. Axis Bluechip - Direct
    assert scheme.plan == Plan.Direct
    assert scheme.category == Category.EquityLargeCap

## Total Expense Ratio (TER)

TER is the annual fee deducted from the scheme's assets. It is disclosed
daily by each AMC and aggregated on the AMFI website in a downloadable
spreadsheet.[reference:18]

    ter = Scheme.ter_history(120503)
    ter.mean()      # average TER over the period
    ter.latest()    # most recent value

For a backtest, TER is deducted from the scheme's gross return:

    net_return = gross_nav_return - (ter / 365)   # daily deduction

Honba applies TER automatically when a scheme is used in a portfolio
backtest. If you are using a **direct plan**, the TER is already netted
into the published NAV and should not be deducted again. Set
`plan_ter_applied = true` in the config to avoid double-counting.

## SEBI Scheme Categories

SEBI's 2017 categorisation circular defines the canonical scheme
categories. Honba uses them for category rotation strategies:

    pub enum Category {
        EquityLargeCap,
        EquityMidCap,
        EquitySmallCap,
        EquityMultiCap,
        EquityFlexiCap,
        EquityValue,
        EquityContra,
        EquityFocused,
        EquityELSS,
        // ...
        DebtLiquid,
        DebtOvernight,
        DebtUltraShort,
        // ...
        HybridAggressive,
        HybridBalanced,
        HybridConservative,
        IndexNifty50,
        IndexNiftyNext50,
        // ...
    }

Category rotation strategies compare trailing returns within a category
and rotate into the top-performing scheme:

    let universe = CategoryUniverse::new(Category::EquityMidCap, Plan::Direct);
    let signals = rank_by_trailing_return(&universe, window=90);
    let target = signals.top(3);   // rotate into top 3 schemes

## SIP Backtesting

A Systematic Investment Plan invests a fixed amount on a fixed schedule
(usually monthly). The backtest question is different from a signal
strategy: "if I had invested ₹10,000 on the 5th of every month since
2015, what would my portfolio be worth today?"

    from honba.india.mutual_funds import SipBacktest

    bt = SipBacktest(
        scheme=120503,
        amount=10_000,
        frequency=Frequency.Monthly,
        day_of_month=5,
        start="2015-01-01",
        end="2025-12-31",
    )
    result = bt.run()

    print(result.total_invested)    # sum of SIP installments
    print(result.final_value)       # portfolio value at end
    print(result.xirr())            # annualised return
    print(result.cagr())            # CAGR of the NAV

SIP is the one place where XIRR (money-weighted return) is more
informative than CAGR (time-weighted return), because the investment
amount varies over time.

## Stamp Duty on Mutual Funds

Stamp duty on mutual fund purchases is **0.005%** (₹0.05 per ₹1,000),
charged on the subscription amount. It does not apply on redemptions.
This was introduced in 2020 and is in addition to any exit load.[reference:19]

Exit loads vary by scheme and holding period:

    scheme.exit_load(days_held=180)  # → 0.0 if scheme has no exit load
    scheme.exit_load(days_held=30)   # → 1.0 if within 3 months

Honba applies both automatically in mutual fund backtests.

## Category Analysis

    from honba.india.mutual_funds import CategoryAnalyzer

    analyzer = CategoryAnalyzer(plan=Plan.Direct)
    report = analyzer.report(
        category=Category.EquityMidCap,
        start="2020-01-01",
        end="2025-12-31",
    )
    report.rank_by("xirr").head(10)

This produces a ranked table of schemes in a category by trailing
return, volatility, Sharpe, and maximum drawdown.

## Portfolio Optimization

Mutual fund portfolios are often built with a risk-parity or
mean-variance objective across categories rather than schemes:

    from honba.india.mutual_funds import portfolio_optimize

    weights = portfolio_optimize(
        schemes=[120503, 118989, 125354],
        objective="risk_parity",
        lookback_days=252,
    )

The optimizer uses the NAV history from the catalog, so it inherits the
same data integrity guarantees as equity backtests.

## Direct vs Regular Plans

A subtle but large effect: a regular plan carries an additional
0.5–1.5% annual distribution expense. Over 20 years, this compounds
to a 10–25% reduction in terminal wealth. Honba's default is **direct
plans** for all backtests, because regular plans compensate a
distributor who is not present in an algorithmic strategy.

If you need to model a specific investor's actual holdings (which are
often regular plans), set:

    plan = Plan.Regular

## Source of Truth

- NAV: AMFI daily flat file (`portal.amfiindia.com/spages/NAVAll.txt`).
- TER: AMFI TER spreadsheet, updated daily.
- Categories: SEBI (Mutual Funds) Regulations 1996, plus the October
  2017 categorisation circular.
- Stamp duty: Finance Act 2020, effective 1 July 2020.
