# Synthetic public boundary

## Decision

Publish only deterministic synthetic observations, evaluation summaries, and screenshots. Keep MIMIC files, patient-level derivatives, research models, experiment runs, explanations, and reports local and excluded from Git and Docker contexts.

## Why

The public product exists to demonstrate research method and interface behavior. Restricted patient data is unnecessary for those goals and would create unacceptable privacy, licensing, and claim risks.

## Alternatives rejected

Publishing MIMIC-derived aggregates was rejected because cohort and licensing review is outside this release. Shipping a research model in the public container was rejected because it would blur the safety boundary. Removing the local research path was rejected because it remains useful for separately governed study.

## Not done

No data was downloaded, copied, deleted, uploaded, or deployed. No clinical performance, device, diagnosis, treatment, or care claim was introduced.

## Changed

Private delivery state moved to a sibling ops folder. Public ignore and Docker rules remain the enforcement boundary for data and generated artifacts.
