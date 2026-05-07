from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .db import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PredictionFeature(Base):
    __tablename__ = "prediction_features"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(
        Integer,
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    text_length = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    has_url = Column(Boolean, nullable=False)
    has_email = Column(Boolean, nullable=False)
    exclamation_count = Column(Integer, nullable=False)
    question_count = Column(Integer, nullable=False)
    uppercase_ratio = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
