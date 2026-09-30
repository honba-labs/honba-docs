# Architecture

Honba is organized as four layers with a strict, machine-enforced
dependency direction. This section explains the reasoning behind that
organization.

## Reading Order

The four documents in this section are meant to be read in order:

1. **[Overview](overview.md)** — the four-layer system, the three-tier
   backtesting pipeline, and the reasoning for the Rust + Python split.
2. **[Crate Hierarchy](crate_hierarchy.md)** — the twelve Rust crates,
   the allowed dependency graph, and why each edge exists.
3. **[Message Flow](message_flow.md)** — the path of a market tick from
   broker WebSocket to strategy decision to fill.
4. **[Adapter Interface](adapter_interface.md)** — how brokers plug in
   without touching the core.

## The Two Rules

If you take nothing else from this section, take these two rules:

- **Dependencies flow downward only.** Nothing in Layer 2 imports from
  Layer 3. This is enforced by `scripts/dependency_graph.py` and fails
  CI when violated.
- **The engine never knows about specific brokers.** Broker adapters
  live in a separate repository and implement interfaces defined by the
  core.

Everything else in this section is an elaboration of those two rules.

## What This Buys You

The hierarchy is not academic. It means:

- Adding a broker does not require touching the engine.
- A change to SEBI cost rules lives in one crate and does not ripple
  outward.
- The Indian market module can be tested without an event loop, so
  calendar tests run in milliseconds.
- The strategy research loop (Tier 1 → Tier 2 → Tier 3) can replace
  any tier without touching the others.

The costs of the hierarchy — the discipline of not importing across
layers, the occasional awkwardness of moving code down a layer — are
paid back the first time SEBI changes a rule and the fix is one file.
