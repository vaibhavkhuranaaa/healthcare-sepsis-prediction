# Sepsis Early Warning

An educational ICU early-warning project: local research uses the MIMIC-IV Demo dataset; the deployable dashboard uses synthetic data only. **It is not a clinical device and must not guide care.**

## Data and safety

Download the open [MIMIC-IV Demo](https://physionet.org/content/mimic-iv-demo/) locally into `data/`. Nothing under `data/`, nor generated features, models, MLflow runs, metrics, or SHAP exports, may be committed or deployed. The full MIMIC-IV dataset additionally requires credentialed access and a signed DUA.

## Architecture

`local demo data → pandas hourly features → XGBoost + calibration → local MLflow/SHAP`

`synthetic replay → Flask API → synthetic timeline dashboard`

The Flask dashboard is deliberately dependency-light and refreshes its synthetic case every 30 seconds. Azure Container Apps hosts only this synthetic surface.

## Local use

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev,research]'
pytest -q
python -m scripts.train_synthetic
MODEL_PATH=$PWD/artifacts/synthetic-model.joblib flask --app src.app run
```

For a synthetic-only dashboard without any local model, omit `MODEL_PATH`. Visit `http://localhost:5000`.

## MIMIC Demo workflow

1. Keep downloaded files in `data/mimic-iv-demo/` only.
2. Create a local `sepsis_onsets.csv` with `stay_id,sepsis_onset` from reviewed, versioned MIMIC-code Sepsis-3 logic. This repository deliberately does not guess clinical labels.
3. Run `python -m scripts.build_features --demo-root data/mimic-iv-demo --onsets data/sepsis_onsets.csv`; this reads CSV files in chunks and writes ignored local Parquet output.
4. Use `build_hourly_features`; perform patient-level splits before `train`.
5. Run `python -m scripts.train_local`. It performs a patient-level held-out split, logs AUROC/AUPRC/Brier/ECE to local MLflow, and writes ignored model/metrics files.
6. Run `explain` locally and publish only synthetic illustrations, never real patient-level SHAP output.

## API

- `POST /v1/score` — validated observation feature vector; response includes risk, risk band, drivers, mode, and disclaimer.
- `GET /v1/demo/timeline/{synthetic_id}` — synthetic replay timeline.
- `GET /healthz` — liveness endpoint.

## Deployment

Build locally with `docker compose -f docker/docker-compose.yml up --build`. `infra/main.bicep` defines the low-cost East US 2 synthetic deployment: Container Apps, ACR Basic, Storage, Application Insights, and Log Analytics. Add Entra authentication and subscription budget alerts before sharing it. Container Apps can scale to zero; estimated low-traffic demo cost is roughly $7–20/month, excluding any future private research environment.

## Evaluation requirements

Report AUROC, AUPRC, Brier score, calibration plot, threshold sensitivity/PPV and alert burden—not AUROC alone. Include cohort definition, leakage controls, data version, limitations, and subgroup analysis with confidence intervals before claiming performance.
