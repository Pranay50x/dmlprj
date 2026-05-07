import re
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from .models import Prediction, PredictionFeature


_URL_RE = re.compile(r"(https?://\S+|www\.[^\s]+)", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


@dataclass(frozen=True)
class ETLResult:
    processed: int


def _compute_uppercase_ratio(text: str) -> float:
    alpha_chars = [ch for ch in text if ch.isalpha()]
    if not alpha_chars:
        return 0.0
    upper = sum(1 for ch in alpha_chars if ch.isupper())
    return upper / len(alpha_chars)


def compute_features(text: str) -> dict[str, object]:
    words = [w for w in text.strip().split() if w]
    return {
        "text_length": len(text),
        "word_count": len(words),
        "has_url": bool(_URL_RE.search(text)),
        "has_email": bool(_EMAIL_RE.search(text)),
        "exclamation_count": text.count("!"),
        "question_count": text.count("?"),
        "uppercase_ratio": float(_compute_uppercase_ratio(text)),
    }


def _iter_unfeatured_predictions(db: Session, batch_size: int) -> Iterable[Prediction]:
    # Select predictions with no corresponding feature row.
    # This is portable across Postgres + SQLite.
    query = (
        db.query(Prediction)
        .outerjoin(PredictionFeature, Prediction.id == PredictionFeature.prediction_id)
        .filter(PredictionFeature.prediction_id.is_(None))
        .order_by(Prediction.id.asc())
        .limit(batch_size)
    )
    return query.all()


def run_feature_etl(db: Session, *, batch_size: int = 500, max_rows: int | None = None) -> ETLResult:
    processed = 0

    while True:
        if max_rows is not None and processed >= max_rows:
            break

        remaining = None if max_rows is None else max_rows - processed
        effective_batch = batch_size if remaining is None else min(batch_size, remaining)

        candidates = _iter_unfeatured_predictions(db, effective_batch)
        if not candidates:
            break

        for pred in candidates:
            feats = compute_features(pred.text)
            db.add(PredictionFeature(prediction_id=pred.id, **feats))
            processed += 1

        db.commit()

    return ETLResult(processed=processed)
