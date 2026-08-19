# Reproducible synthetic evaluation

## Decision

Evaluate the public synthetic model against a prevalence-only baseline on a seeded,
stratified row holdout. Version the scalar metrics, fixed-width calibration bins, and
threshold alert counts as JSON. Fail evidence generation unless the calibrated model
improves AUROC, AUPRC, and Brier score against that baseline.

## Why

A baseline and explicit gate make the synthetic result interpretable and reproducible.
Calibration bins expose where predicted probabilities differ from generated event rates.
Threshold results show the sensitivity, positive predictive value, and alert-count tradeoff
without presenting a threshold as care guidance.

## Alternatives rejected

AUROC-only reporting was rejected because it hides calibration and alert burden. A random
row split presented as a patient split was rejected because synthetic rows contain no
patient identity or longitudinal structure. Committing a fitted model was rejected because
the evidence can be regenerated from source and no model artifact is needed for review.
XGBoost was rejected for the public challenger after fixed-seed probabilities differed
between macOS and Linux. A single-threaded Extra Trees classifier preserves the calibrated
tree comparison without platform-dependent evidence.

## Not done

No MIMIC data, patient-level artifact, confidence interval, subgroup result, external
validation, deployment result, clinical claim, or care recommendation was produced. The
synthetic evaluation does not validate local research performance.

## Changed

Added a deterministic Extra Trees evaluation command and versioned synthetic evidence.
Expected calibration error now uses fixed probability bins. Local research contracts now retain
`subject_id`, split by patient, and build features from recording or result availability
time rather than observation time alone.
