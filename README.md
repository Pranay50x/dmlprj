# Automated CI/CD Pipeline for Secure Containerized Web Applications

This repository implements the full project roadmap from prj.md using a FastAPI app, Docker, GitHub Actions, and an optional Terraform example.

## What is included
- FastAPI service with a pre-trained sentiment analyzer (VADER)
- Postgres logging for predictions
- Dockerfile and docker-compose for local dev
- CI pipeline: tests, linting, security scan
- CD pipeline: build and push container image, optional deploy webhook
- Optional Terraform skeleton for a managed container service

## Endpoints
- GET /health
- POST /predict
- GET /predictions

## Local development

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2) Run the API locally

```bash
uvicorn --app-dir src app.main:app --reload
```

Alternative (equivalent):

```bash
uvicorn src.app.main:app --reload
```

The default database is SQLite when DATABASE_URL is not set.

### 3) Run with Docker Compose (Postgres)

```bash
docker compose up --build
```

## Test, lint, security scan

```bash
pytest
flake8 src tests
bandit -r src -c bandit.yaml
```

## CI/CD workflows

### CI
CI runs on every push and pull request:
- pytest
- flake8
- bandit

### Docker publish
A successful CI run on main triggers the Docker Publish workflow:
- builds the container image
- pushes to GHCR as ghcr.io/<owner>/<repo>:latest and :<sha>

### Deploy (webhook)
The Deploy workflow triggers after a successful Docker Publish run.
Set this secret to enable it:
- DEPLOY_WEBHOOK_URL

Example deployment targets:
- Render deploy hook URL
- Railway webhook
- Custom webhook in your hosting platform

## Environment variables
- DATABASE_URL (used by the API to connect to Postgres)

Example for docker-compose:
```
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/appdb
```

## Optional Terraform
See infra/README.md for the optional IaC example.
