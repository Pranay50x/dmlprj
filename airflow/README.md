# Airflow setup (local Postgres only)

This Airflow setup runs against your local Postgres service on localhost:5432.
It mounts the repo's DAGs and source code so the DAG can reuse the app's
SQLAlchemy models and streaming ingestion code.

## Prereqs
- Local Postgres running on localhost:5432
- Docker engine available

## Start Airflow

From the repo root:

```bash
docker compose -f airflow/docker-compose.airflow.yml up airflow-init
```

Then start the scheduler and webserver:

```bash
docker compose -f airflow/docker-compose.airflow.yml up
```

Open Airflow UI at http://localhost:8080 and log in with:
- user: admin
- password: admin

## DAG
- DAG ID: streaming_price_etl
- Schedule: every minute
- Tasks: ingest price tick, compute tick features

## Notes
- This compose file uses host networking so Airflow can reach localhost:5432.
- If you need a different symbol or API, edit [src/app/streaming.py](src/app/streaming.py).
