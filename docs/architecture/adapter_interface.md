# Adapter Interface

Broker adapters connect Honba to the outside world. They live in a
**separate repository** (`honba-adapters`) and are installed as Python
packages. The core engine never imports a specific adapter.

## Why Adapters Are Separate

The core `honba` crate defines what a data client and an execution client
must do. It does not define how any specific broker does it. This means:

- Adding a new broker does not require touching the core repository.
- A broken adapter cannot break the engine.
- Adapters can be versioned independently and released at their own pace.

This mirrors StockSharp's `Connectors` repository, which maintains dozens
of broker integrations without any of them living in the core.

## The Two Interfaces

Every adapter implements two abstract classes:

### `DataClient`

Provides market data and instrument definitions.

    class DataClient(ABC):
        @abstractmethod
        async def connect(self) -> None: ...

        @abstractmethod
        async def disconnect(self) -> None: ...

        @abstractmethod
        async def subscribe_quotes(self, instruments: list[Instrument]) -> None: ...

        @abstractmethod
        async def subscribe_trades(self, instruments: list[Instrument]) -> None: ...

        @abstractmethod
        async def subscribe_bars(
            self, instruments: list[Instrument], bar_type: BarType
        ) -> None: ...

        @abstractmethod
        async def request_instruments(self) -> list[Instrument]: ...

        @abstractmethod
        async def request_historical_bars(
            self, instrument: Instrument, bar_type: BarType,
            start: datetime, end: datetime,
        ) -> list[Bar]: ...

### `ExecutionClient`

Places orders and reports fills.

    class ExecutionClient(ABC):
        @abstractmethod
        async def connect(self) -> None: ...

        @abstractmethod
        async def disconnect(self) -> None: ...

        @abstractmethod
        async def submit_order(self, order: Order) -> str: ...

        @abstractmethod
        async def cancel_order(self, client_order_id: str) -> None: ...

        @abstractmethod
        async def modify_order(self, order: Order) -> None: ...

        @abstractmethod
        async def query_order(self, client_order_id: str) -> OrderStatusReport: ...

        @abstractmethod
        async def query_positions(self) -> list[Position]: ...

## The Adapter Contract

An adapter does three things and nothing else:

1. **Translate.** Convert broker-specific JSON into Honba `Message` types
   and Honba `Order` commands into broker-specific HTTP requests.
2. **Transport.** Manage WebSocket connections, reconnection, heartbeat,
   rate limiting, and authentication.
3. **Report.** Emit every state change as an event — connection status,
   order acknowledgement, fill, error.

An adapter **never** makes trading decisions, computes indicators, or
maintains strategy state. If an adapter is doing any of those things, it
is doing too much.

## Uniform Internal Structure

Every adapter follows the same file layout, so a developer moving from one
broker to another recognises the code instantly:

    honba_dhan/
    ├── __init__.py
    ├── config.py        — DhanConfig (pydantic model)
    ├── data.py          — DhanDataClient(DataClient)
    ├── execution.py     — DhanExecutionClient(ExecutionClient)
    ├── instruments.py   — InstrumentProvider
    ├── websocket.py     — WS connection, reconnection, heartbeat
    ├── http.py          — REST client wrapper
    ├── parsing.py       — JSON → Message translations
    └── constants.py     — endpoint URLs, error codes

The names are identical in every adapter. `config.py` is always the
configuration model. `parsing.py` is always where JSON becomes Honba
types.

## A Minimal Adapter

Here is a skeleton `data.py` for a hypothetical broker:

    from honba.adapters.base import DataClient
    from honba.entities import Instrument
    from honba.messages import Bar, BarType, QuoteTick

    from .config import DhanConfig
    from .http import DhanHTTP
    from .websocket import DhanWebSocket
    from .parsing import parse_quote


    class DhanDataClient(DataClient):
        def __init__(self, config: DhanConfig):
            self.config = config
            self.http = DhanHTTP(config)
            self.ws = DhanWebSocket(config)
            self._on_quote = None

        async def connect(self) -> None:
            await self.http.authenticate()
            await self.ws.connect()

        async def disconnect(self) -> None:
            await self.ws.close()

        async def subscribe_quotes(self, instruments):
            symbols = [i.symbol for i in instruments]
            await self.ws.subscribe(symbols, callback=self._handle_message)

        def _handle_message(self, raw: dict) -> None:
            quote = parse_quote(raw)
            if self._on_quote:
                self._on_quote(quote)

        def set_quote_callback(self, cb):
            self._on_quote = cb

The engine calls `set_quote_callback()` at registration time and then
never touches the adapter again — messages flow through the callback.

## Registration

Adapters are registered with the engine by name:

    from honba.adapters import registry
    import honba_dhan

    registry.register("dhan", honba_dhan.DhanAdapter)

Then configuration references the adapter by name:

    # configs/live/dhan_paper.toml
    [adapter]
    name = "dhan"
    mode = "paper"
    client_id = "${DHAN_CLIENT_ID}"
    access_token = "${DHAN_ACCESS_TOKEN}"

The engine resolves `"dhan"` to the registered adapter at startup. If the
adapter is not installed, startup fails with a clear error.

## Error Handling

Adapters must distinguish between **recoverable** and **fatal** errors:

- **Recoverable:** WebSocket disconnect, transient HTTP 5xx, rate limit
  hit. The adapter reconnects or backs off automatically.
- **Fatal:** Invalid credentials, account suspended, malformed response
  from a documented endpoint. The adapter raises `AdapterFatalError` and
  the engine halts cleanly.

A recoverable error must **never** lose a message silently. If the adapter
cannot deliver a fill event because the connection dropped mid-order, it
must reconcile with the broker's order status endpoint on reconnect.

## Testing Adapters

The `honba-adapters-shared` package provides test helpers:

    from honba_adapters_shared.testing import FakeWebSocket, record_replay

    @pytest.mark.asyncio
    async def test_dhan_parses_quote():
        raw = load_fixture("dhan_quote.json")
        quote = parse_quote(raw)
        assert quote.instrument.symbol == "RELIANCE"
        assert quote.bid == Decimal("2450.50")

Every adapter has a `tests/fixtures/` directory of recorded broker
responses. These are checked into git and used for regression testing.

## The Paper Adapter

`honba-paper` is a special adapter that provides a simulated execution
client. It is used for live-data paper trading:

- Market data comes from a real broker adapter.
- Order execution is simulated locally using the same fill models as
  `honba-algo-testing`.
- Positions and P&L are tracked in-memory.

This is the recommended way to validate a strategy before risking capital.

## The Sandbox Adapter

`honba-sandbox` provides **synthetic** market data for testing. It
generates deterministic price paths from a seed, so tests that rely on
market behaviour are reproducible.

    from honba_sandbox import SyntheticDataClient

    client = SyntheticDataClient(
        seed=42,
        instruments=["NIFTY50"],
        start_price=20000.0,
        volatility=0.15,
    )

Use this for unit-testing strategies without needing a data catalog or a
broker connection.

## Adding a New Adapter

1. Create a new directory in `honba-adapters/` mirroring the structure
   above.
2. Implement `DataClient` and `ExecutionClient`.
3. Add fixtures and tests.
4. Register the adapter in `honba_adapters_shared/registry.py`.
5. Submit a pull request.

The adapter repository's CI runs each adapter's tests independently, so a
failure in one adapter never blocks a pull request touching another.
