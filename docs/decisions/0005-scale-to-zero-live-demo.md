# Scale-to-zero live demo

## Decision

Run the synthetic-only dashboard as one permanent Azure Container App with zero minimum replicas. Publish its source-linked image through GitHub Actions and allow anonymous pulls from the public container package.

## Why

The deployment provides a verifiable HTTPS surface while preserving the public data boundary. Scale to zero and a public package remove the need for an always-on replica, paid container registry, storage account, or monitoring workspace.

## Alternatives rejected

Azure Container Registry was rejected because its fixed daily charge was unnecessary for a public synthetic image. An always-on replica was rejected because the low-traffic review surface can tolerate cold starts. Deploying any MIMIC data, trained research model, or patient-level artifact was rejected by the project boundary.

## Not done

No patient data, clinical model, load test, availability claim, custom domain, authentication layer, paid registry, storage account, or monitoring workspace was deployed. The live result does not establish clinical validity, care utility, production readiness, or a guaranteed zero bill.

## Changed

The public image workflow now builds native AMD64 containers. The Azure template provisions only a Consumption environment and synthetic app. Live health, timeline, scoring, source identity, and scale settings were verified over HTTPS.
