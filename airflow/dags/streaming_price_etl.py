from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.db import Base, SessionLocal, engine
from app.etl_features import run_feature_etl
from app.streaming import fetch_price_tick, ingest_price_tick


def ingest_tick() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        tick = fetch_price_tick()
        ingest_price_tick(db, tick)
    finally:
        db.close()


def run_tick_etl() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_feature_etl(db, max_rows=1000)
    finally:
        db.close()


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="streaming_price_etl",
    description="Poll a public price API and derive tick features.",
    default_args=default_args,
    start_date=datetime(2026, 5, 12),
    schedule="*/1 * * * *",
    catchup=False,
    tags=["streaming", "etl"],
) as dag:
    ingest_task = PythonOperator(task_id="ingest_price_tick", python_callable=ingest_tick)
    etl_task = PythonOperator(task_id="compute_tick_features", python_callable=run_tick_etl)

    ingest_task >> etl_task
