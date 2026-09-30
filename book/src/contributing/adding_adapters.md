# Adding Broker Adapters

Adapter development happens in the `honba-adapters` repository, not in
the core `honba` repository. This document describes how to add a new
adapter, test it, and publish it.

## Before You Start

Adding an adapter is a substantial piece of work — typically 2–5 days
for a broker you have never integrated before. Before starting:

1. Check whether the broker is already supported. Adapters exist for
   Dhan, Zerodha, Angel One, Fyers, Upstox, Kotak, IIFL, and Motilal
   Oswal.
2. Read [Adapter Interface](../architecture/adapter_interface.md).
3. Get API access from the broker. Most Indian brokers require
   registration and a static IP for order placement.

## The Uniform Structure

Every adapter in `honba-adapters/` follows the same file layout. This
is not a stylistic preference — it means a developer familiar with one
adapter can read any other.

    honba-<broker>/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   └── honba_<broker>/
    │       ├── __init__.py
    │       ├── config.py           # Pydantic config model
    │       ├── data.py             # DataClient implementation
    │       ├── execution.py        # ExecutionClient implementation
    │       ├── instruments.py      # InstrumentProvider
    │       ├── websocket.py        # WebSocket connection
    │       ├── http.py             # REST client wrapper
    │       ├── parsing.py          # JSON → Honba types
    │       └── constants.py        # Endpoints, error codes
    └── tests/
        ├── conftest.py
        ├── fixtures/
        │   ├── instruments.json
        │   ├── quotes.json
        │   ├── orders.json
        │   └── ...
        ├── test_config.py
        ├── test_data.py
        ├── test_execution.py
        └── test_parsing.py

## Step 1: Create the Package Skeleton

    cd honba-adapters
    cp -r dhan/ mybroker/       # Copy an existing adapter as a template
    cd mybroker

    # Rename the package directory
    mv src/honba_dhan src/honba_mybroker

    # Rename the module references
    grep -rl "honba_dhan\|honba-dhan\|Dhan" . | xargs sed -i 's/honba_dhan/honba_mybroker/g; s/honba-dhan/honba-mybroker/g; s/Dhan/MyBroker/g'

The Dhan adapter is the recommended template because it has the
cleanest structure. The Zerodha adapter is a good second reference
for brokers with a daily-refresh OAuth flow.

## Step 2: Define the Configuration Model

`config.py`:

    from pydantic import BaseModel, Field, SecretStr


    class MyBrokerConfig(BaseModel):
        client_id: str = Field(..., description="API client ID")
        access_token: SecretStr = Field(..., description="Access token")
        base_url: str = "https://api.mybroker.com"
        ws_url: str = "wss://ws.mybroker.com"

        # Connection tuning
        reconnect_attempts: int = 5
        reconnect_backoff_seconds: float = 2.0
        heartbeat_seconds: int = 30

        # Rate limits
        rate_limit_per_second: int = 10
        order_rate_limit_per_second: int = 3

        class Config:
            extra = "forbid"

The `SecretStr` type prevents the token from appearing in logs.

## Step 3: Implement the REST Client

`http.py`:

    import httpx
    from tenacity import retry, stop_after_attempt, wait_exponential

    from .config import MyBrokerConfig


    class MyBrokerHTTP:
        def __init__(self, config: MyBrokerConfig):
            self.config = config
            self.client = httpx.AsyncClient(
                base_url=config.base_url,
                timeout=10.0,
                headers={"Authorization": f"Bearer {config.access_token.get_secret_value()}"},
            )

        async def authenticate(self) -> None:
            resp = await self.client.post("/auth/verify")
            resp.raise_for_status()

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
        )
        async def get(self, path: str, **params) -> dict:
            resp = await self.client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()

        async def post(self, path: str, json: dict) -> dict:
            resp = await self.client.post(path, json=json)
            resp.raise_for_status()
            return resp.json()

        async def close(self) -> None:
            await self.client.aclose()

Retry logic belongs here, not in the client implementation. A 5xx
response is retried; a 4xx response is raised immediately.

## Step 4: Implement the WebSocket Client

`websocket.py`:

    import asyncio
    import json
    import logging
    from typing import Callable

    import websockets

    from .config import MyBrokerConfig

    log = logging.getLogger(__name__)


    class MyBrokerWebSocket:
        def __init__(self, config: MyBrokerConfig):
            self.config = config
            self.ws = None
            self._handlers: dict[str, Callable[[dict], None]] = {}
            self._running = False

        async def connect(self) -> None:
            self.ws = await websockets.connect(self.config.ws_url)
            self._running = True
            asyncio.create_task(self._receive_loop())

        async def _receive_loop(self) -> None:
            while self._running:
                try:
                    raw = await self.ws.recv()
                    message = json.loads(raw)
                    self._dispatch(message)
                except websockets.ConnectionClosed:
                    log.warning("WebSocket closed, reconnecting")
                    await self._reconnect()
                except Exception:
                    log.exception("Error in receive loop")

        def _dispatch(self, message: dict) -> None:
            msg_type = message.get("type")
            handler = self._handlers.get(msg_type)
            if handler:
                handler(message)

        def on(self, msg_type: str, handler: Callable[[dict], None]) -> None:
            self._handlers[msg_type] = handler

        async def subscribe(self, symbols: list[str]) -> None:
            await self.ws.send(json.dumps({
                "action": "subscribe",
                "symbols": symbols,
            }))

        async def _reconnect(self) -> None:
            for attempt in range(self.config.reconnect_attempts):
                try:
                    await asyncio.sleep(self.config.reconnect_backoff_seconds * (2 ** attempt))
                    await self.connect()
                    return
                except Exception:
                    continue
            log.error("Failed to reconnect after %d attempts", self.config.reconnect_attempts)

        async def close(self) -> None:
            self._running = False
            if self.ws:
                await self.ws.close()

The reconnect loop is mandatory. Indian broker WebSockets drop
regularly; an adapter without reconnection logic is unusable for live
trading.

## Step 5: Implement the Data Client

`data.py`:

    from honba.adapters.base import DataClient
    from honba.entities import Instrument
    from honba.messages import Bar, BarType, QuoteTick

    from .config import MyBrokerConfig
    from .http import MyBrokerHTTP
    from .websocket import MyBrokerWebSocket
    from .parsing import parse_quote, parse_bars


    class MyBrokerDataClient(DataClient):
        def __init__(self, config: MyBrokerConfig):
            self.config = config
            self.http = MyBrokerHTTP(config)
            self.ws = MyBrokerWebSocket(config)
            self._quote_cb = None

        async def connect(self) -> None:
            await self.http.authenticate()
            await self.ws.connect()
            self.ws.on("quote", self._on_quote_message)

        async def disconnect(self) -> None:
            await self.ws.close()
            await self.http.close()

        async def subscribe_quotes(self, instruments: list[Instrument]) -> None:
            symbols = [i.symbol for i in instruments]
            await self.ws.subscribe(symbols)

        async def request_instruments(self) -> list[Instrument]:
            data = await self.http.get("/instruments")
            return [parse_instrument(row) for row in data["instruments"]]

        async def request_historical_bars(
            self, instrument: Instrument, bar_type: BarType,
            start, end,
        ) -> list[Bar]:
            data = await self.http.get(
                "/historical",
                symbol=instrument.symbol,
                interval=bar_type.to_broker_interval(),
                from_ts=start.timestamp(),
                to_ts=end.timestamp(),
            )
            return parse_bars(data, instrument, bar_type)

        def set_quote_callback(self, cb) -> None:
            self._quote_cb = cb

        def _on_quote_message(self, message: dict) -> None:
            quote = parse_quote(message)
            if self._quote_cb:
                self._quote_cb(quote)

## Step 6: Implement the Execution Client

`execution.py`:

    from honba.adapters.base import ExecutionClient
    from honba.entities import Order, Position
    from honba.messages import OrderStatusReport

    from .config import MyBrokerConfig
    from .http import MyBrokerHTTP
    from .parsing import parse_order_response


    class MyBrokerExecutionClient(ExecutionClient):
        def __init__(self, config: MyBrokerConfig):
            self.config = config
            self.http = MyBrokerHTTP(config)

        async def connect(self) -> None:
            await self.http.authenticate()

        async def disconnect(self) -> None:
            await self.http.close()

        async def submit_order(self, order: Order) -> str:
            payload = {
                "symbol": order.instrument.symbol,
                "side": order.side.value.upper(),
                "quantity": order.quantity,
                "order_type": order.order_type.value.upper(),
                "price": str(order.price) if order.price else None,
                "client_order_id": order.client_order_id,
            }
            resp = await self.http.post("/orders", json=payload)
            return parse_order_response(resp).broker_order_id

        async def cancel_order(self, client_order_id: str) -> None:
            await self.http.post(f"/orders/{client_order_id}/cancel", json={})

        async def modify_order(self, order: Order) -> None:
            payload = {
                "quantity": order.quantity,
                "price": str(order.price) if order.price else None,
            }
            await self.http.post(f"/orders/{order.client_order_id}/modify", json=payload)

        async def query_order(self, client_order_id: str) -> OrderStatusReport:
            resp = await self.http.get(f"/orders/{client_order_id}")
            return parse_order_response(resp)

        async def query_positions(self) -> list[Position]:
            resp = await self.http.get("/positions")
            return [parse_position(p) for p in resp["positions"]]

## Step 7: Parsing

`parsing.py` is where broker-specific JSON becomes Honba types. This
is where most bugs live, so keep it small and test it thoroughly:

    from decimal import Decimal

    from honba.entities import Instrument, InstrumentId
    from honba.messages import Bar, BarType, QuoteTick, UnixNanos


    def parse_quote(raw: dict) -> QuoteTick:
        return QuoteTick(
            instrument=InstrumentId(symbol=raw["symbol"], venue="NSE"),
            bid=Decimal(str(raw["bid"])),
            ask=Decimal(str(raw["ask"])),
            bid_size=int(raw.get("bid_qty", 0)),
            ask_size=int(raw.get("ask_qty", 0)),
            timestamp=UnixNanos.from_millis(raw["timestamp_ms"]),
        )


    def parse_bars(raw: list[dict], instrument: Instrument, bar_type: BarType) -> list[Bar]:
        return [
            Bar(
                instrument=instrument.id,
                bar_type=bar_type,
                open=Decimal(str(row["open"])),
                high=Decimal(str(row["high"])),
                low=Decimal(str(row["low"])),
                close=Decimal(str(row["close"])),
                volume=int(row["volume"]),
                timestamp=UnixNanos.from_millis(row["timestamp_ms"]),
            )
            for row in raw
        ]

Three rules for parsing code:

1. **Always use `Decimal` for prices.** Broker JSON often uses
   floats; converting through `float` loses precision. Parse as string,
   then Decimal.
2. **Always validate.** If a required field is missing, raise a
   descriptive error, do not return a partially-populated object.
3. **Always test.** Every parsing function gets a test with a real
   broker fixture.

## Step 8: Tests

`tests/test_parsing.py`:

    import json
    from decimal import Decimal
    from pathlib import Path

    import pytest

    from honba_mybroker.parsing import parse_quote


    FIXTURES = Path(__file__).parent / "fixtures"


    def load(name: str) -> dict:
        return json.loads((FIXTURES / name).read_text())


    def test_parse_quote():
        raw = load("quote_reliance.json")
        quote = parse_quote(raw)
        assert quote.instrument.symbol == "RELIANCE"
        assert quote.instrument.venue == "NSE"
        assert quote.bid == Decimal("2450.50")
        assert quote.ask == Decimal("2450.75")


    def test_parse_quote_missing_bid_raises():
        raw = load("quote_missing_bid.json")
        with pytest.raises(KeyError):
            parse_quote(raw)

The fixtures directory contains recorded broker responses. Save them
from your own API calls or from the broker's documentation examples.

## Step 9: Registration

In `honba_adapters_shared/registry.py`, add an entry:

    from honba_mybroker import MyBrokerAdapter

    register_adapter("mybroker", MyBrokerAdapter)

Also add the adapter to the CI workflow in `.github/workflows/ci.yml`
so its tests run:

    - run: pip install -e ./mybroker
    - run: pytest mybroker/

## Step 10: Documentation

Create `mybroker/README.md` with:

- Installation: `pip install -e ./mybroker`
- Configuration: required credentials and optional settings
- Authentication flow: how tokens are obtained and refreshed
- Known limitations: what the adapter does not support
- Example: a minimal script that connects, subscribes, and places an
  order

The README is the primary documentation users see. It should be
complete enough that someone can use the adapter without reading the
source.

## Testing Against a Live Broker

Live tests are gated by environment variables. In `conftest.py`:

    import os
    import pytest


    @pytest.fixture
    def live_credentials():
        client_id = os.environ.get("MYBROKER_CLIENT_ID")
        access_token = os.environ.get("MYBROKER_ACCESS_TOKEN")
        if not client_id or not access_token:
            pytest.skip("Live credentials not configured")
        return MyBrokerConfig(client_id=client_id, access_token=access_token)

Tests that need live credentials are marked `@pytest.mark.live` and
skipped by default. CI does not run them.

## Publishing

Once the adapter passes its tests and has been used for a week of
paper trading without issues:

1. Bump the version in `pyproject.toml`.
2. Update the adapter list in `honba-adapters/README.md`.
3. Open a pull request. The adapter repository maintains its own
   release cycle and does not depend on the core.

## Common Mistakes

### Using `float` for prices

Broker prices must be parsed as `Decimal`. Using `float` produces
sub-paisa errors that compound across thousands of trades.

### Blocking the event loop

All I/O must be `async`. A synchronous HTTP call inside an `async`
method blocks the entire engine.

### Forgetting to close connections

Every `connect()` needs a matching `disconnect()`. The engine calls
`disconnect()` on shutdown, but a bug in `connect()` can leave a
dangling WebSocket.

### Not handling broker-side rate limits

Indian brokers rate-limit aggressively. Use the token-bucket helper in
`honba_adapters_shared/rate_limit.py`.

### Assuming the order ID is stable

Most brokers return a broker-assigned order ID that differs from your
`client_order_id`. Preserve both. The engine tracks orders by
`client_order_id`; the broker sees its own.

### Testing only the happy path

Most production bugs come from error paths — a rejected order, a
disconnected WebSocket, a malformed response. Test these explicitly
with fixtures.

## Checklist

Before opening a pull request:

- [ ] Package skeleton created with uniform structure
- [ ] `config.py` with Pydantic model and `SecretStr` for tokens
- [ ] `http.py` with retry logic for transient failures
- [ ] `websocket.py` with reconnection
- [ ] `data.py` implementing `DataClient`
- [ ] `execution.py` implementing `ExecutionClient`
- [ ] `parsing.py` using `Decimal` for prices
- [ ] Fixtures recorded for all message types
- [ ] Tests for parsing, data, execution, and error paths
- [ ] Registered in `honba_adapters_shared/registry.py`
- [ ] Added to CI workflow
- [ ] README with installation, configuration, and example
- [ ] All tests pass
- [ ] `ruff check` and `mypy` pass
