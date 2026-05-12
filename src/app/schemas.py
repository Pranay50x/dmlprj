from datetime import datetime

from pydantic import BaseModel, Field


class TickIngestRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    price: float
    source: str = Field(..., min_length=1, max_length=50)
    observed_at: datetime | None = None


class TickRow(BaseModel):
    id: int
    symbol: str
    price: float
    source: str
    observed_at: datetime
    created_at: datetime


class ETLRunResponse(BaseModel):
    processed: int


class ETLStatusResponse(BaseModel):
    total_ticks: int
    total_features: int
    pending_ticks: int


class TickFeatureRow(BaseModel):
    tick_id: int
    previous_price: float | None
    price_delta: float | None
    percent_change: float | None
    is_up: bool | None
    created_at: datetime
