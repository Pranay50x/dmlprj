from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .etl_features import run_feature_etl
from .models import PriceTick, PriceTickFeature
from .schemas import ETLRunResponse, ETLStatusResponse, TickFeatureRow, TickIngestRequest, TickRow
from .streaming import fetch_price_tick, ingest_price_tick


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Streaming ETL API", version="1.0.0", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stream/ingest", response_model=TickRow)
def ingest_stream_tick(db: Session = Depends(get_db)) -> TickRow:
    tick = fetch_price_tick()
    record = ingest_price_tick(db, tick)
    return TickRow(
        id=record.id,
        symbol=record.symbol,
        price=record.price,
        source=record.source,
        observed_at=record.observed_at,
        created_at=record.created_at,
    )


@app.post("/stream/ticks", response_model=TickRow)
def create_tick(payload: TickIngestRequest, db: Session = Depends(get_db)) -> TickRow:
    observed_at = payload.observed_at or datetime.now(timezone.utc)
    record = PriceTick(
        symbol=payload.symbol,
        price=payload.price,
        source=payload.source,
        observed_at=observed_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return TickRow(
        id=record.id,
        symbol=record.symbol,
        price=record.price,
        source=record.source,
        observed_at=record.observed_at,
        created_at=record.created_at,
    )


@app.get("/stream/ticks", response_model=list[TickRow])
def list_ticks(limit: int = 20, db: Session = Depends(get_db)) -> list[TickRow]:
    items = db.query(PriceTick).order_by(PriceTick.id.desc()).limit(limit).all()
    return [
        TickRow(
            id=item.id,
            symbol=item.symbol,
            price=item.price,
            source=item.source,
            observed_at=item.observed_at,
            created_at=item.created_at,
        )
        for item in items
    ]


@app.post("/etl/stream/run", response_model=ETLRunResponse)
def run_etl_stream(
    max_rows: int = 5000,
    db: Session = Depends(get_db),
    x_etl_api_key: str | None = Header(default=None, alias="X-ETL-API-KEY"),
) -> ETLRunResponse:
    required_key = os.getenv("ETL_API_KEY")
    if required_key and x_etl_api_key != required_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = run_feature_etl(db, max_rows=max_rows)
    return ETLRunResponse(processed=result.processed)


@app.get("/etl/stream/status", response_model=ETLStatusResponse)
def etl_stream_status(db: Session = Depends(get_db)) -> ETLStatusResponse:
    total_ticks = int(db.query(func.count(PriceTick.id)).scalar() or 0)
    total_features = int(db.query(func.count(PriceTickFeature.id)).scalar() or 0)
    pending = max(total_ticks - total_features, 0)
    return ETLStatusResponse(
        total_ticks=total_ticks,
        total_features=total_features,
        pending_ticks=pending,
    )


@app.get("/stream/features", response_model=list[TickFeatureRow])
def list_stream_features(limit: int = 20, db: Session = Depends(get_db)) -> list[TickFeatureRow]:
    items = db.query(PriceTickFeature).order_by(PriceTickFeature.id.desc()).limit(limit).all()
    return [
        TickFeatureRow(
            tick_id=item.tick_id,
            previous_price=item.previous_price,
            price_delta=item.price_delta,
            percent_change=item.percent_change,
            is_up=item.is_up,
            created_at=item.created_at,
        )
        for item in items
    ]
