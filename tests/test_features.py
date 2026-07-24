import pandas as pd
import pytest

from src.pipeline.demo_data import synthetic_features, synthetic_labels
from src.pipeline.features import FEATURE_NAMES, build_hourly_features
from src.pipeline.labels import attach_horizon_labels
from src.pipeline.train import evaluate, train


def test_hourly_features_do_not_use_future_values():
    events = pd.DataFrame([
        {"stay_id": 1, "charttime": "2025-01-01T00:00:00Z", "feature": "heart_rate", "value": 80},
        {"stay_id": 1, "charttime": "2025-01-01T02:10:00Z", "feature": "heart_rate", "value": 120},
    ])
    result = build_hourly_features(events)
    assert result.iloc[0].heart_rate_last == 80
    assert result.iloc[1].heart_rate_last == 80
    assert result.iloc[2].heart_rate_last == 80
    assert set(FEATURE_NAMES).issubset(result.columns)


def test_features_require_contract_columns():
    with pytest.raises(ValueError):
        build_hourly_features(pd.DataFrame({"stay_id": [1]}))


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
