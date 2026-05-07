from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .etl_features import run_feature_etl
from .model import predict_sentiment
from .models import Prediction, PredictionFeature
from .schemas import ETLRunResponse, ETLStatusResponse, FeatureRow, PredictRequest, PredictResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="ML Prediction API", version="1.0.0", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db)) -> PredictResponse:
    label, score = predict_sentiment(payload.text)
    record = Prediction(text=payload.text, label=label, score=score)
    db.add(record)
    db.commit()
    return PredictResponse(label=label, score=score)


@app.get("/predictions")
def list_predictions(limit: int = 20, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    items = db.query(Prediction).order_by(Prediction.id.desc()).limit(limit).all()
    return [
        {
            "id": item.id,
            "text": item.text,
            "label": item.label,
            "score": item.score,
            "created_at": item.created_at,
        }
        for item in items
    ]


@app.post("/etl/features/run", response_model=ETLRunResponse)
def run_etl_features(
    max_rows: int = 5000,
    db: Session = Depends(get_db),
    x_etl_api_key: str | None = Header(default=None, alias="X-ETL-API-KEY"),
) -> ETLRunResponse:
    required_key = os.getenv("ETL_API_KEY")
    if required_key and x_etl_api_key != required_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = run_feature_etl(db, max_rows=max_rows)
    return ETLRunResponse(processed=result.processed)


@app.get("/etl/features/status", response_model=ETLStatusResponse)
def etl_features_status(db: Session = Depends(get_db)) -> ETLStatusResponse:
    total_predictions = int(db.query(func.count(Prediction.id)).scalar() or 0)
    total_features = int(db.query(func.count(PredictionFeature.id)).scalar() or 0)
    pending = max(total_predictions - total_features, 0)
    return ETLStatusResponse(
        total_predictions=total_predictions,
        total_features=total_features,
        pending_predictions=pending,
    )


@app.get("/features", response_model=list[FeatureRow])
def list_features(limit: int = 20, db: Session = Depends(get_db)) -> list[FeatureRow]:
    items = db.query(PredictionFeature).order_by(PredictionFeature.id.desc()).limit(limit).all()
    return [
        FeatureRow(
            prediction_id=item.prediction_id,
            text_length=item.text_length,
            word_count=item.word_count,
            has_url=item.has_url,
            has_email=item.has_email,
            exclamation_count=item.exclamation_count,
            question_count=item.question_count,
            uppercase_ratio=item.uppercase_ratio,
            created_at=item.created_at,
        )
        for item in items
    ]
