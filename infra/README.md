# Azure demo deployment

These Bicep templates provision only the synthetic public demo. They must never be used for MIMIC files, derived data, research model artifacts, or SHAP exports.

1. Set a globally unique lowercase `APP_NAME`.
2. Run `APP_NAME=<name> bash infra/deploy.sh`.
3. Add Microsoft Entra authentication and budget alerts in the subscription before sharing the URL.

The research-enclave design is intentionally not provisioned until data-governance approval exists.
