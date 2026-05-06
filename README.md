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
The Deploy workflow triggers after a successful CI run on main.
Set this secret to enable it:
- DEPLOY_WEBHOOK_URL

Example deployment targets:
- Render deploy hook URL
- Railway webhook
- Custom webhook in your hosting platform

## Roadmap status (prj.md)

- Phase 1 (Containerization & Local Dev): Implemented (FastAPI + Docker + Compose + Postgres logging).
- Phase 2 (Branching strategy): Repo structure is implemented; enforcing "no direct to main" requires GitHub branch protection.
- Phase 3 (CI pipeline): Implemented via GitHub Actions (pytest + flake8 + bandit).
- Phase 4 (CD pipeline): Implemented as a deploy webhook workflow; you must set hosting + secrets.
- Phase 5 (Monitoring & Logging): /health is implemented; external log platform is optional (not configured by default).
- Phase 6 (Documentation & Presentation): Basic README exists; you still need to write your course report.

## GitHub setup to finish Phase 2 + Phase 4

### 1) Turn on branch protection (recommended)
In GitHub repo settings, add a branch protection rule for main:
- Require a pull request before merging
- Require status checks to pass before merging
- Select the CI workflow checks as required

This is what actually enforces: "no code reaches main without passing automated checks".

### 2) Configure deployment webhook (optional)
If you want automated deployments only after CI passes:
- Create a deploy hook on Render/Railway (or your host)
- Add repository secret: DEPLOY_WEBHOOK_URL

Without this secret, the Deploy workflow will fail by design (so you notice it is not configured).

## Render (free-tier friendly) deployment: build from GitHub

This setup uses Render to build from your GitHub repo, but uses GitHub Actions to *trigger* deployments only after CI passes.

### Render steps (one-time)
1) In Render: New + → Web Service
2) Connect your GitHub repo
3) Environment: choose Docker (so Render uses the Dockerfile in this repo)
4) Branch: main
5) Auto-Deploy: set to Off/Manual (so CI controls when deploy happens)
6) Health Check Path: /health
7) Environment variables (optional):
	- DATABASE_URL: set this only if you have a managed Postgres (recommended for persistence)

### GitHub steps (one-time)
1) In your Render service settings, create a Deploy Hook and copy its URL
2) In GitHub repo settings → Secrets and variables → Actions:
	- Add a new repository secret named DEPLOY_WEBHOOK_URL
	- Paste the Render deploy hook URL as the value

After this, a push to main will run CI; if it succeeds, GitHub Actions will POST the deploy hook and Render will redeploy.

## Environment variables
- DATABASE_URL (used by the API to connect to Postgres)

Example for docker-compose:
```
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/appdb
```

## Optional Terraform
See infra/README.md for the optional IaC example.
