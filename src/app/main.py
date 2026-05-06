from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .model import predict_sentiment
from .models import Prediction
from .schemas import PredictRequest, PredictResponse

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
