# Reinforcement Learning Training

Honba supports training RL agents on its simulator. This document is
deliberately cautious: RL for trading is a research area with a high
failure rate, and most published results do not survive out-of-sample.
The tooling exists because it is occasionally useful, not because it
is a reliable path to profitability.

## What RL Training Is

An RL agent observes market state, chooses actions (buy, sell, hold,
or position sizes), and receives a reward (P&L, Sharpe contribution,
or a custom objective). Over many episodes, the agent learns a policy
that maximizes expected reward.

Honba's contribution is the simulator: the same engine that runs
backtests runs RL training, so the environment is realistic (costs,
latency, market hours) and the trained policy can be evaluated in the
same simulator it was trained on.

## What RL Training Is Not

- **It is not a shortcut to profitable strategies.** Most RL agents
  trained on financial data overfit to the training period and lose
  money out-of-sample. This is not a bug in Honba; it is what the
  literature reports.
- **It is not a replacement for signal design.** The best RL
  applications use RL for position sizing or execution, not for
  discovering signals from raw prices.
- **It is not fast.** Training a policy takes hours to days, not
  minutes.

## The Environment

Honba exposes a Gymnasium environment that wraps the backtest engine:

    from honba.ai.rl import TradingEnv
    import gymnasium as gym

    env = TradingEnv(
        universe="nifty50",
        start="2018-01-01",
        end="2022-12-31",
        initial_capital=1_000_000,
        cost_model="india_equity_delivery",
        action_space="discrete",        # or "continuous"
        observation_space="features",   # or "raw_bars"
        features=[
            "return_1d", "return_5d", "return_20d",
            "rsi_14", "atr_14", "volume_ratio",
            "vix_proxy", "regime_flag",
        ],
        reward="sharpe",                # "pnl", "sharpe", "calmar"
        max_episode_steps=252,
    )

    obs, info = env.reset()
    # obs: shape (num_instruments, num_features), e.g. (50, 8)

## The Action Space

### Discrete

Three actions per instrument: hold, buy, sell.

    action_space = "discrete"   # MultiDiscrete([3] * num_instruments)
    # action[i] ∈ {0: hold, 1: buy, 2: sell}
    # Order size is fixed by the environment (equal-weight).

### Continuous

Target position weight per instrument, in [-1, 1].

    action_space = "continuous"   # Box(-1, 1, shape=(num_instruments,))
    # action[i] = target weight for instrument i
    # -1 = full short, 0 = flat, 1 = full long

Continuous is more expressive but harder to train. Discrete is the
recommended starting point.

## The Observation Space

### `raw_bars`

The last N bars of OHLCV per instrument.

    observation_space = "raw_bars"
    lookback = 20
    # obs shape: (num_instruments, lookback, 5)

This is high-dimensional and slow to train. Use only for research.

### `features`

Precomputed features from the indicator library.

    observation_space = "features"
    features = ["return_1d", "return_5d", "rsi_14", "atr_14"]
    # obs shape: (num_instruments, num_features)

This is the practical choice. Features are computed once and cached.

## The Reward Function

| Reward | Definition | Notes |
|---|---|---|
| `pnl` | Change in portfolio value | Simple, high variance |
| `sharpe` | Rolling Sharpe over last K steps | Slower, more stable |
| `calmar` | Return / max drawdown | Penalizes drawdowns |
| `differential_sharpe` | Moody & Saffell (2001) | Differentiable, works well |

The **differential Sharpe ratio** is usually the best choice for
trading RL. It provides a dense, differentiable signal that accounts
for risk.

    reward = "differential_sharpe"
    reward_params = {"eta": 0.01, "window": 60}

## Training

    from honba.ai.rl import train
    from stable_baselines3 import PPO

    result = train(
        env=env,
        algorithm=PPO,
        policy="MlpPolicy",
        total_timesteps=1_000_000,
        hyperparams={
            "learning_rate": 3e-4,
            "n_steps": 2048,
            "batch_size": 64,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "ent_coef": 0.01,
            "clip_range": 0.2,
        },
        eval_env=TradingEnv(  # separate evaluation environment
            universe="nifty50",
            start="2023-01-01",
            end="2024-12-31",
            ...
        ),
        eval_freq=10_000,
        save_dir="./models/rl",
    )

    result.plot_learning_curve().save("learning_curve.html")
    result.best_model_path      # path to the checkpoint with best eval reward

Training runs on CPU for small feature sets. For raw-bar observations,
a GPU is required.

## Evaluation Is the Hard Part

A trained policy's backtest result on the test period is not evidence
that it will work live. Three additional checks are necessary:

### 1. Test on a holdout period never seen during training

    test_env = TradingEnv(
        universe="nifty50",
        start="2024-01-01",
        end="2025-06-30",
        ...
    )

    evaluation = evaluate(result.best_model, test_env)
    print(evaluation.summary())

### 2. Test on a different universe

A policy trained on NIFTY 50 and evaluated on NIFTY MIDCAP 150 tests
whether it learned generalizable structure or NIFTY-specific quirks.

### 3. Compare to baselines

The policy must beat:

- Buy-and-hold on the same universe
- An equal-weight monthly rebalance
- A simple momentum rule

If it does not beat these baselines out-of-sample, the training effort
produced nothing.

## Honest Assessment

RL for trading has produced very few robust, publicly-verified
results. The most common failure modes:

- **Overfitting to training period.** The policy memorizes specific
  price sequences rather than learning generalizable patterns.
- **Non-stationarity.** Financial markets change; a policy trained on
  2018–2022 may not work in 2024.
- **Reward hacking.** The policy finds ways to maximize reward that do
  not correspond to actual trading skill (e.g., exploiting simulator
  bugs).
- **Instability.** Small changes in hyperparameters produce
  dramatically different policies.

These are not Honba-specific. They are properties of the problem.
Honba provides the tooling; whether it produces a useful result
depends on the problem and the researcher.

## When RL Is Worth Trying

- **Position sizing given a fixed signal.** Train the agent to size
  positions for a signal you already trust, rather than to discover
  signals.
- **Execution optimization.** Given a target position, learn when and
  how to trade to minimize cost.
- **Regime switching.** Train a small policy to switch between a
  fixed set of strategies based on detected regime.

These are narrower problems with better-defined reward functions and
more likely to produce usable results than end-to-end signal discovery.

## Configuration

    # configs/ai/rl_training.toml
    [env]
    universe = "nifty50"
    start = "2018-01-01"
    end = "2022-12-31"
    initial_capital = 1_000_000
    cost_model = "india_equity_delivery"
    action_space = "discrete"
    observation_space = "features"
    reward = "differential_sharpe"
    max_episode_steps = 252

    [env.features]
    list = ["return_1d", "return_5d", "return_20d", "rsi_14", "atr_14", "volume_ratio"]

    [training]
    algorithm = "PPO"
    total_timesteps = 1_000_000
    learning_rate = 3e-4
    n_steps = 2048
    batch_size = 64
    save_dir = "./models/rl"

    [evaluation]
    eval_start = "2023-01-01"
    eval_end = "2024-12-31"
    eval_freq = 10_000

## Next Steps

- **[MCP Gateway](mcp_gateway.md)** — connecting external AI agents to
  Honba.
- **[Natural Language Verification](nl_verification.md)** — using an
  LLM to critique a strategy you wrote.
