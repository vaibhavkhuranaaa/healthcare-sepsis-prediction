# CLAUDE.md — healthcare-sepsis-prediction

## Project Context
- **Industry:** Healthcare
- **Role focus:** Data Scientist
- **Portfolio goal:** early-warning risk prediction on *real* de-identified ICU data, not synthetic tabular data. Mirrors real hospital early-warning systems (e.g. NEWS2-style tools). Explainability is mandatory in healthcare — this is not optional polish.

## Data
- **Dataset:** MIMIC-IV — real de-identified ICU records from Beth Israel Deaconess Medical Center
- **Source:** physionet.org/content/mimiciv
- **Access constraints:** requires completing PhysioNet's free CITI "Data or Specimens Only Research" training course before credentialed access is granted. Start this early — it's a lead-time item, not a blocker to begin scaffolding the repo.

## Required Stack
Python, pandas for time-series feature engineering on vitals/labs, XGBoost or LSTM for the model, MLflow for experiment tracking, SHAP for explainability, Flask API, Docker, Azure Container Apps.

## Standard Repo Structure
```
src/
├── app.py                  # Flask risk-scoring endpoint
├── pipeline/
│   ├── features.py            # time-series feature engineering on vitals/labs
│   ├── train.py                 # model training + MLflow logging
│   └── explain.py               # SHAP explainability
notebooks/                    # EDA on de-identified data only
data/                            # DO NOT commit raw MIMIC-IV — see constraints below
tests/
docker/
infra/
.github/workflows/ci.yml
```

## Subagent Ownership
1. **Architect subagent** — confirm structure, plan features → train → explain → API flow
2. **Pipeline subagent** — owns `src/pipeline/`
3. **API subagent** — owns `src/app.py`
4. **Infra subagent** — owns `docker/` and `infra/`
5. **Docs/test subagent** — owns `tests/`, README must include a SHAP explainability example, not just an AUROC number

## Hard Constraints
- **Never commit raw MIMIC-IV data or anything derived that could re-identify a patient.** Use `.gitignore` for the full data directory; only commit fully de-identified, aggregated, or synthetic-example artifacts.
- Data use is bound by the PhysioNet Credentialed Health Data Use Agreement — review it before starting, and don't share raw files even privately
- Report calibration and explainability alongside discrimination metrics — a black-box AUROC number is not sufficient for a healthcare portfolio piece

## Definition of Done (v1)
- [ ] PhysioNet credentialing completed, data use agreement reviewed
- [ ] Time-series feature pipeline on vitals/labs
- [ ] Model trained with MLflow tracking, reported AUROC + calibration
- [ ] SHAP explainability example included in README
- [ ] Flask risk-scoring API
- [ ] Dockerized, deployed to Azure
- [ ] README complete (no raw data committed), tagged `v1.0`
