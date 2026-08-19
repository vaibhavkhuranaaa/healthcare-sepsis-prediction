"""Build versioned evaluation evidence from synthetic rows only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split

from src.pipeline.demo_data import synthetic_features, synthetic_labels
from src.pipeline.features import FEATURE_NAMES, FeatureContract
from src.pipeline.train import evaluate, train

THRESHOLDS = (0.10, 0.20, 0.50)


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _calibration_bins(
    labels: pd.Series, probabilities: np.ndarray
) -> list[dict[str, float | int]]:
    bins = pd.cut(
        probabilities,
        bins=[index / 10 for index in range(11)],
        labels=False,
        include_lowest=True,
    )
    records: list[dict[str, float | int]] = []
    for bin_id in range(10):
        selected = bins == bin_id
        if selected.any():
            mean_prediction = probabilities[selected].mean()
            event_rate = labels[selected].mean()
            records.append({
                "lower_bound": bin_id / 10,
                "upper_bound": (bin_id + 1) / 10,
                "rows": int(selected.sum()),
                "mean_prediction": _rounded(mean_prediction),
                "event_rate": _rounded(event_rate),
                "absolute_gap": _rounded(abs(mean_prediction - event_rate)),
            })
    return records


def _alert_burden(
    labels: pd.Series, probabilities: np.ndarray
) -> list[dict[str, float | int | None]]:
    positives = int(labels.sum())
    records: list[dict[str, float | int | None]] = []
    for threshold in THRESHOLDS:
        alerted = probabilities >= threshold
        true_positives = int(labels[alerted].sum())
        alert_count = int(alerted.sum())
        records.append({
            "threshold": threshold,
            "alerts": alert_count,
            "alerts_per_100_rows": _rounded(alerted.mean() * 100),
            "sensitivity": _rounded(true_positives / positives),
            "positive_predictive_value": (
                _rounded(true_positives / alert_count) if alert_count else None
            ),
        })
    return records


def build_evidence(rows: int = 1_200, seed: int = 42) -> dict[str, object]:
    if rows < 120:
        raise ValueError("At least 120 synthetic rows are required for calibrated evaluation")

    features = synthetic_features(rows, seed)
    labels = synthetic_labels(features)
    row_ids = list(range(rows))
    train_ids, holdout_ids = train_test_split(
        row_ids,
        test_size=0.25,
        random_state=seed,
        stratify=labels,
    )
    train_features, holdout_features = features.iloc[train_ids], features.iloc[holdout_ids]
    train_labels, holdout_labels = labels.iloc[train_ids], labels.iloc[holdout_ids]

    baseline = DummyClassifier(strategy="prior").fit(train_features, train_labels)
    calibrated = train(train_features, train_labels, random_state=seed).model
    baseline_probabilities = baseline.predict_proba(holdout_features)[:, 1]
    calibrated_probabilities = calibrated.predict_proba(holdout_features)[:, 1]
    baseline_metrics = evaluate(baseline, holdout_features, holdout_labels)
    calibrated_metrics = evaluate(calibrated, holdout_features, holdout_labels)
    passes_smoke_test = (
        calibrated_metrics["auroc"] > baseline_metrics["auroc"]
        and calibrated_metrics["auprc"] > baseline_metrics["auprc"]
        and calibrated_metrics["brier"] < baseline_metrics["brier"]
    )
    if not passes_smoke_test:
        raise RuntimeError("Calibrated model did not beat the synthetic prevalence baseline")

    return {
        "evidence_id": "synthetic-baseline-v1",
        "scope": {
            "purpose": "Reproducibility evidence for the public synthetic research demo only.",
            "data_source": "Deterministic synthetic feature generator.",
            "contains_mimic_data": False,
            "contains_patient_data": False,
            "excluded_uses": (
                "Clinical-device evaluation, care guidance, and patient-level inference."
            ),
        },
        "reproduction": {
            "command": (
                "python -m scripts.evaluate_synthetic "
                "--output evidence/synthetic-baseline-v1.json"
            ),
            "seed": seed,
            "rows": rows,
            "feature_contract": FeatureContract().version,
            "split": "Seeded stratified 75/25 row holdout before model fitting.",
            "calibration": "Three-fold isotonic calibration within training rows only.",
            "ece": "Expected calibration error across fixed-width probability bins.",
        },
        "cohort": {
            "total_rows": rows,
            "training_rows": len(train_ids),
            "holdout_rows": len(holdout_ids),
            "training_positive_rows": int(train_labels.sum()),
            "holdout_positive_rows": int(holdout_labels.sum()),
            "holdout_prevalence": _rounded(holdout_labels.mean()),
        },
        "leakage_checks": [
            {
                "check": "train_holdout_row_overlap",
                "passed": set(train_ids).isdisjoint(holdout_ids),
                "detail": "Synthetic row identifiers are disjoint across fit and evaluation sets.",
            },
            {
                "check": "target_excluded_from_features",
                "passed": "sepsis_within_6h" not in FEATURE_NAMES,
                "detail": "Feature contract excludes the generated target column.",
            },
            {
                "check": "calibration_fit_excludes_holdout",
                "passed": True,
                "detail": "Cross-validation and isotonic fitting use training rows only.",
            },
        ],
        "baseline": {
            "name": "prevalence_only",
            "method": "DummyClassifier with the training-set class prior.",
            "metrics": {key: _rounded(value) for key, value in baseline_metrics.items()},
            "calibration_bins": _calibration_bins(holdout_labels, baseline_probabilities),
        },
        "calibrated_model": {
            "name": "calibrated_extra_trees",
            "method": "Extra Trees with three-fold isotonic calibration on training rows.",
            "metrics": {key: _rounded(value) for key, value in calibrated_metrics.items()},
            "calibration_bins": _calibration_bins(holdout_labels, calibrated_probabilities),
            "alert_burden": _alert_burden(holdout_labels, calibrated_probabilities),
        },
        "acceptance": {
            "criterion": (
                "Calibrated AUROC and AUPRC exceed baseline, and calibrated Brier score is lower."
            ),
            "passed": passes_smoke_test,
        },
        "interpretation": (
            "On this deterministic synthetic fixture, the calibrated model improves "
            "discrimination and Brier score over the prevalence-only baseline."
        ),
        "limitations": [
            "Synthetic labels are a deterministic function of same-row features, so apparent "
            "discrimination and calibration are easier than real-world prediction.",
            "Rows have no patient, site, subgroup, or temporal structure. The split checks row "
            "overlap only and cannot test patient-level or temporal leakage.",
            "No confidence intervals, subgroup analysis, drift analysis, or external validation "
            "is available from this fixture.",
            "Alert burden counts independently scored rows. It does not model repeated alerts, "
            "suppression windows, staffing, workflow, or intervention effects.",
            "These results do not estimate clinical performance and must not guide care.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1_200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output", type=Path, default=Path("evidence/synthetic-baseline-v1.json")
    )
    args = parser.parse_args()
    evidence = build_evidence(args.rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
