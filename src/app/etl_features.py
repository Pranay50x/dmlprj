from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from .models import PriceTick, PriceTickFeature


@dataclass(frozen=True)
class ETLResult:
    processed: int


def _iter_unfeatured_ticks(db: Session, batch_size: int) -> Iterable[PriceTick]:
    query = (
        db.query(PriceTick)
        .outerjoin(PriceTickFeature, PriceTick.id == PriceTickFeature.tick_id)
        .filter(PriceTickFeature.tick_id.is_(None))
        .order_by(PriceTick.id.asc())
        .limit(batch_size)
    )
    return query.all()


def _previous_price(db: Session, tick: PriceTick) -> float | None:
    previous = (
        db.query(PriceTick)
        .filter(PriceTick.symbol == tick.symbol, PriceTick.id < tick.id)
        .order_by(PriceTick.id.desc())
        .first()
    )
    if previous is None:
        return None
    return float(previous.price)


def run_feature_etl(
    db: Session, *, batch_size: int = 500, max_rows: int | None = None
) -> ETLResult:
    processed = 0

    while True:
        if max_rows is not None and processed >= max_rows:
            break

        remaining = None if max_rows is None else max_rows - processed
        effective_batch = batch_size if remaining is None else min(batch_size, remaining)

        candidates = _iter_unfeatured_ticks(db, effective_batch)
        if not candidates:
            break

        for tick in candidates:
            prev_price = _previous_price(db, tick)
            if prev_price is None:
                feature = PriceTickFeature(
                    tick_id=tick.id,
                    previous_price=None,
                    price_delta=None,
                    percent_change=None,
                    is_up=None,
                )
            else:
                delta = float(tick.price) - prev_price
                percent = None if prev_price == 0 else (delta / prev_price) * 100
                feature = PriceTickFeature(
                    tick_id=tick.id,
                    previous_price=prev_price,
                    price_delta=delta,
                    percent_change=percent,
                    is_up=delta > 0,
                )

            db.add(feature)
            processed += 1

        db.commit()

    return ETLResult(processed=processed)
