from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .db import Base


class PriceTick(Base):
    __tablename__ = "price_ticks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    source = Column(String, nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PriceTickFeature(Base):
    __tablename__ = "price_tick_features"

    id = Column(Integer, primary_key=True, index=True)
    tick_id = Column(
        Integer,
        ForeignKey("price_ticks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    previous_price = Column(Float, nullable=True)
    price_delta = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)
    is_up = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
