# Streaming ETL Web Server (Local Postgres)

This repository implements a streaming-style ETL pipeline using a public price API
and FastAPI for ingestion + feature derivation. All data is stored in your local
Postgres service on localhost:5432.

## What is included
- FastAPI service that stores streaming price ticks
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

## Optional Render CD (kept for CI/CD demonstration)
This repo still includes a deploy workflow that can trigger a Render deploy hook.
It is optional and not used for the local Airflow demo.

### Render steps (optional)
1) In Render: New + → Web Service
2) Connect your GitHub repo
3) Environment: choose Docker
4) Branch: main
5) Auto-Deploy: set to Off/Manual (CI controls deploy)
6) Health Check Path: /health
7) Environment variables (optional):
	- DATABASE_URL: a Render Postgres URL for the web app (local demo uses localhost)

### GitHub steps (optional)
1) In Render service settings, create a Deploy Hook and copy its URL
2) In GitHub repo settings → Secrets and variables → Actions:
	- Add `DEPLOY_WEBHOOK_URL` with the Render deploy hook

After this, a push to main runs CI; if it succeeds, GitHub Actions will POST the
deploy hook and Render will redeploy the container.
