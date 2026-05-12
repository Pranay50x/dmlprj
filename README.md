# Streaming ETL with Airflow (Local Postgres)

This repository implements a streaming-style ETL pipeline using a public price API,
FastAPI for inspection endpoints, and Airflow for ingestion + feature derivation.
All data is stored in your local Postgres service on localhost:5432.

## What is included
- FastAPI service that stores streaming price ticks
- Airflow DAG that polls a public API every minute
- ETL feature table derived from ticks
- Dockerfile and docker-compose for the API service
- CI pipeline: tests, linting, security scan

## Endpoints
- GET /health
- POST /stream/ingest
- POST /stream/ticks
- GET /stream/ticks
- POST /etl/stream/run
- GET /etl/stream/status
- GET /stream/features

## Local development

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2) Ensure local Postgres is running

The app is hardcoded to use:

```
postgresql+psycopg2://postgres:my-new-password@localhost:5432/postgres
```

### 3) Run the API locally

```bash
uvicorn --app-dir src app.main:app --reload
```

### 4) Run with Docker Compose (API only)

```bash
docker compose up --build
```

## Airflow

Airflow lives in the [airflow](airflow) directory. See [airflow/README.md](airflow/README.md)
to start the webserver + scheduler and run the streaming ETL DAG.

## Test, lint, security scan

```bash
pytest
flake8 src tests
bandit -r src -c bandit.yaml
```

## Environment variables
- `STREAM_SOURCE_URL` (default: Binance price endpoint)
- `STREAM_SYMBOL` (default: BTCUSDT)
- `STREAM_SOURCE_NAME` (default: binance)
- `ETL_API_KEY` (optional header protection for `POST /etl/stream/run`)

## Optional Terraform
See infra/README.md for the optional IaC example.
