# Architecture

## Public demonstration

Deterministic synthetic features feed a reproducible evaluation command and a synthetic-only Flask API. The static dashboard consumes the score, timeline, and health endpoints. CI verifies source, tests, and container build. The public image runs in one Azure Container App with zero minimum replicas and no provisioned registry, storage account, or monitoring workspace.

## Local research boundary

Optional MIMIC files remain under ignored local storage. Chunked ingestion builds hourly features without future values. Patient-level splits, calibrated modelling, MLflow, and explanations remain local. No patient row, derived feature table, trained research model, or explanation enters the public repository or container.

## Scaling limit

This architecture supports low-traffic portfolio review only and may cold start after scaling to zero. It has no clinical integration, identity, audit, monitoring, validation, or operational reliability required for medical use.
