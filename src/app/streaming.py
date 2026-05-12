from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os

import httpx
from sqlalchemy.orm import Session

from .models import PriceTick

STREAM_SOURCE_URL = os.getenv("STREAM_SOURCE_URL", "https://api.binance.com/api/v3/ticker/price")
STREAM_SYMBOL = os.getenv("STREAM_SYMBOL", "BTCUSDT")
STREAM_SOURCE_NAME = os.getenv("STREAM_SOURCE_NAME", "binance")


@dataclass(frozen=True)
class StreamTick:
    symbol: str
    price: float
    source: str
    observed_at: datetime


def fetch_price_tick() -> StreamTick:
    params = {"symbol": STREAM_SYMBOL}
    with httpx.Client(timeout=10) as client:
        response = client.get(STREAM_SOURCE_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    symbol = str(payload.get("symbol") or STREAM_SYMBOL)
    price_raw = payload.get("price")
    if price_raw is None:
        raise ValueError("Streaming API response missing price")

    price = float(price_raw)
    observed_at = datetime.now(timezone.utc)

    return StreamTick(
        symbol=symbol,
        price=price,
        source=STREAM_SOURCE_NAME,
        observed_at=observed_at,
    )


def ingest_price_tick(db: Session, tick: StreamTick) -> PriceTick:
    record = PriceTick(
        symbol=tick.symbol,
        price=tick.price,
        source=tick.source,
        observed_at=tick.observed_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
