# Agent Handoff — Sepsis Early Warning

## Current state

- The repository is a working synthetic-only Flask dashboard plus local MIMIC research pipeline.
- Local verification: pytest, Ruff, mypy, Docker build, and container health endpoint pass.
- The local dashboard runs at `http://localhost:8000` via Docker Compose.
- Azure CLI is authenticated, but cloud resources have not yet been provisioned.

## Non-negotiable data boundary

- Never commit, upload, log, screenshot, or deploy MIMIC-IV/Demo files, derived feature tables, trained research models, MLflow artifacts, SHAP outputs, or patient-level metrics.
- `data/`, `artifacts/`, `mlruns/`, and `reports/` are ignored. Azure deployment is synthetic-only.
- For actual MIMIC research, use local encrypted storage and provide reviewed Sepsis-3 onset labels to `scripts.build_features`.

## Architecture

| Concern | Implementation |
| --- | --- |
| Local research | pandas chunked ingestion, hourly features, patient-level split, XGBoost/isotonic calibration, MLflow, SHAP |
| Public demo | Flask API and static dashboard; deterministic synthetic observations and explanations |
| Runtime | Docker/Gunicorn on Azure Container Apps, scale-to-zero |
| Cloud | ACR Basic, Container Apps Environment, App Insights/Log Analytics, Storage, managed identity |
| IaC | `infra/foundation.bicep` then `infra/app.bicep`; `infra/deploy.sh` automates both |

## Commands

```bash
# Local dashboard
docker compose -f docker/docker-compose.yml up --build

# Local checks
.venv/bin/python -m mypy src
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .

# Cloud deployment: choose a unique lowercase name first
APP_NAME=sepsisewsdemo123 bash infra/deploy.sh
```

## Deployment notes

- The deployment script sends the Docker context to Azure Container Registry. `.dockerignore` excludes data, models, local environments, Git history, tests, and documentation.
- Expected low-traffic cost is roughly $7–20/month. Delete the resource group when finished: `az group delete --name rg-<app-name> --yes`.
- The initial demo URL is public and synthetic-only. Add Entra authentication before sharing it beyond a portfolio review.

## Remaining work requiring external state

1. Download MIMIC-IV Demo/full data and create the reviewed local `sepsis_onsets.csv` file.
2. Train/evaluate locally and create synthetic-only portfolio screenshots.
3. Optionally add Entra authentication, a cost budget, and a custom domain to Azure.
