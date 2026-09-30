# Tutorials

End-to-end walkthroughs that combine several parts of Honba into a
complete workflow. Each tutorial is self-contained and can be
completed in 30–60 minutes.

## The Tutorials

- **[First NIFTY 50 Strategy](first-nifty50-strategy.md)** — a moving
  average crossover on the NIFTY 50 universe. Start here if you are
  new to Honba.
- **[BANKNIFTY Options Backtest](banknifty-options-backtest.md)** — a
  short straddle on BANKNIFTY weekly options. Covers expiry cycles,
  Greeks, and the STT asymmetry between premium and exercise.
- **[Alpha30 Factor Model](alpha30-factor-model.md)** — a
  cross-sectional momentum factor on the NSE Alpha 30 universe.
  Covers universe rebalancing and look-ahead safety.
- **[SIP Backtest](sip-backtest.md)** — a systematic investment plan on
  a mutual fund scheme. Covers AMFI NAV data, direct-vs-regular
  plans, and XIRR.
- **[Autoresearch Loop](autoresearch-loop.md)** — running the LLM-driven
  research loop on Alpha 30 and inspecting the surviving hypotheses.

## A Note on Data

Tutorials that require historical data use the small synthetic
dataset that ships with the repository. Tutorials that require real
data (options, mutual funds) ship with a truncated real dataset
covering 2023–2024, which is enough to demonstrate the workflow
without requiring a full catalog download.

For your own work, populate the catalog with real data from the
sources described in each tutorial.
