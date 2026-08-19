# Azure demo deployment

These Bicep templates provision only the synthetic public demo. They must never be used for MIMIC files, derived data, research model artifacts, or SHAP exports.

1. Publish the synthetic runtime as a public container image.
2. Set a globally unique lowercase `APP_NAME`.
3. Run `APP_NAME=<name> IMAGE=ghcr.io/<owner>/<image>:<tag> SOURCE_SHA=<commit> bash infra/deploy.sh`.

The template uses a Consumption environment, disables platform log ingestion, and scales to zero.
It does not provision a paid container registry, storage account, or monitoring workspace. Set a
subscription budget alert before sharing the URL and review actual usage in Azure Cost Management.

The research-enclave design is intentionally not provisioned until data-governance approval exists.
