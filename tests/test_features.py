import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.evaluate_synthetic import build_evidence
from scripts.train_local import split_by_patient
from src.pipeline.demo_data import synthetic_features, synthetic_labels
from src.pipeline.features import FEATURE_NAMES, build_hourly_features
from src.pipeline.ingest import _available_events
from src.pipeline.labels import attach_horizon_labels
from src.pipeline.train import evaluate, train


def test_hourly_features_do_not_use_future_values():
    events = pd.DataFrame([
        {
            "subject_id": 10,
            "stay_id": 1,
            "available_time": "2025-01-01T00:00:00Z",
            "feature": "heart_rate",
            "value": 80,
        },
        {
            "subject_id": 10,
            "stay_id": 1,
            "available_time": "2025-01-01T02:10:00Z",
            "feature": "heart_rate",
            "value": 120,
        },
    ])
    result = build_hourly_features(events)
    assert result.iloc[0].heart_rate_last == 80
    assert result.iloc[1].heart_rate_last == 80
    assert result.iloc[2].heart_rate_last == 80
    assert set(FEATURE_NAMES).issubset(result.columns)


def test_features_require_contract_columns():
    with pytest.raises(ValueError):
        build_hourly_features(pd.DataFrame({"stay_id": [1]}))


def test_event_availability_uses_later_record_time():
    events = pd.DataFrame({
        "subject_id": [10],
        "stay_id": [1],
        "charttime": ["2025-01-01T01:00:00Z"],
        "storetime": ["2025-01-01T03:00:00Z"],
        "feature": ["lactate"],
        "value": [2.4],
    })
    result = _available_events(events)
    assert result.iloc[0].available_time == pd.Timestamp("2025-01-01T03:00:00Z")


def test_horizon_labels_exclude_post_onset_rows():
    features = pd.DataFrame({"stay_id": [1, 1, 1], "prediction_time": [
        "2025-01-01T00:00:00Z", "2025-01-01T05:00:00Z", "2025-01-01T07:00:00Z",
    ]})
    onset = pd.DataFrame({"stay_id": [1], "sepsis_onset": ["2025-01-01T06:00:00Z"]})
    labelled = attach_horizon_labels(features, onset)
    assert labelled.sepsis_within_6h.tolist() == [1, 1]


def test_held_out_evaluation_reports_calibration_metrics():
    features = synthetic_features(120)
    labels = synthetic_labels(features)
    result = train(features.iloc[:90], labels.iloc[:90])
    metrics = evaluate(result.model, features.iloc[90:], labels.iloc[90:])
    assert {"auroc", "auprc", "brier", "ece_10"} <= metrics.keys()


def test_ece_uses_fixed_probability_bins():
    class FixedModel:
        def predict_proba(self, features):
            probabilities = np.array([0.41, 0.49])
            return np.column_stack([1 - probabilities, probabilities])

    features = synthetic_features(2)
    metrics = evaluate(FixedModel(), features, pd.Series([0, 1]))
    assert metrics["ece_10"] == pytest.approx(0.05)


def test_local_split_keeps_patients_in_one_partition():
    data = pd.DataFrame({
        "subject_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        "stay_id": [10, 11, 20, 20, 30, 31, 40, 40, 50, 51],
    })
    train_data, test_data = split_by_patient(data)
    assert set(train_data.subject_id).isdisjoint(test_data.subject_id)


def test_synthetic_evidence_covers_public_safety_and_decision_metrics():
    evidence = build_evidence()
    committed = json.loads(Path("evidence/synthetic-baseline-v1.json").read_text())
    assert evidence == committed
    assert evidence["scope"]["contains_mimic_data"] is False
    assert evidence["scope"]["contains_patient_data"] is False
    assert all(check["passed"] for check in evidence["leakage_checks"])
    assert evidence["acceptance"]["passed"] is True
    assert {"auroc", "auprc", "brier", "ece_10"} <= evidence["baseline"]["metrics"].keys()
    assert len(evidence["calibrated_model"]["alert_burden"]) == 3
    assert len(evidence["limitations"]) >= 5
