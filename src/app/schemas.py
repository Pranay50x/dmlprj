from datetime import datetime

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class PredictResponse(BaseModel):
    label: str
    score: float


class ETLRunResponse(BaseModel):
    processed: int


class ETLStatusResponse(BaseModel):
    total_predictions: int
    total_features: int
    pending_predictions: int


class FeatureRow(BaseModel):
    prediction_id: int
    text_length: int
    word_count: int
    has_url: bool
    has_email: bool
    exclamation_count: int
    question_count: int
    uppercase_ratio: float
    created_at: datetime
