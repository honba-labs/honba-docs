# Contributing

Honba is a multi-repository workspace. This section is the guide for
changing the code.

## The Documents

- **[Development Setup](development_setup.md)** — the toolchain, the
  test loop, pre-commit hooks, and common workflows.
- **[Dependency Rules](dependency_rules.md)** — the crate hierarchy,
  why each edge exists, and what to do when you need a forbidden
  dependency.
- **[Adding Indicators](adding_indicators.md)** — implementing a new
  technical indicator in Rust and exposing it to Python.
- **[Adding Adapters](adding_adapters.md)** — adding support for a new
  Indian broker.

## Before You Start

Two things worth knowing before your first contribution:

1. **The dependency hierarchy is enforced in CI.** If your pull
   request adds an edge that violates the allowed table in
   [Dependency Rules](dependency_rules.md), it will fail. Read that
   document before adding a `honba-*` dependency.

2. **The workspace spans six repositories.** The core engine
   (`honba/honba`) does not import broker adapters
   (`honba/honba-adapters`) or strategies (`honba/honba-strategies`).
   Which repository you contribute to depends on what you are adding.

## The Contribution Flow

1. Open an issue describing the change.
2. Wait for a maintainer to confirm the approach.
3. Fork, branch, implement.
4. Run `make lint && make test` locally.
5. Open a pull request.

For small changes (typos, doc fixes, adding an indicator that follows
an existing pattern), steps 1 and 2 can be skipped. For anything that
touches the crate hierarchy, the dependency table, or the adapter
interface, they cannot.

## What We Are Looking For

- **Bug reports** with a minimal reproduction.
- **Indicator implementations** verified against a reference.
- **Broker adapters** for brokers not yet supported.
- **Strategy examples** that demonstrate a real edge, not just an API.
- **Documentation improvements** — especially for Indian-market
  specifics that are easy to get wrong.

## What We Are Not Looking For

- New top-level crates without prior discussion.
- Changes to the adapter interface that break existing adapters.
- Strategies with high in-sample Sharpe that have not been validated.
- LLM-generated code without human review.
