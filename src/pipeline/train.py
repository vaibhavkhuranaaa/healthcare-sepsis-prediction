"""Training and calibration for synthetic demos or separately governed local research."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline

from .features import FEATURE_NAMES


@dataclass
class TrainingResult:
    model: Pipeline
    metrics: dict[str, float]


def train(features: pd.DataFrame, labels: pd.Series, random_state: int = 42) -> TrainingResult:
    """Fit a deterministic calibrated tree ensemble. Split data before invoking this function."""
    x = features.loc[:, FEATURE_NAMES]
    y = labels.astype(int)
    if y.nunique() != 2:
        raise ValueError("Training labels must contain both classes")
    base = ExtraTreesClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_leaf=3,
        random_state=random_state,
        n_jobs=1,
    )
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("classifier", CalibratedClassifierCV(base, method="isotonic", cv=3)),
    ])
    model.fit(x, y)
    probabilities = model.predict_proba(x)[:, 1]
    return TrainingResult(model, {
        "auroc_train": float(roc_auc_score(y, probabilities)),
        "auprc_train": float(average_precision_score(y, probabilities)),
        "brier_train": float(brier_score_loss(y, probabilities)),
    })


def save_model(result: TrainingResult, destination: str | Path) -> None:
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result.model, destination)


def load_model(path: str | Path) -> Pipeline:
    return joblib.load(path)


def evaluate(model: Pipeline, features: pd.DataFrame, labels: pd.Series) -> dict[str, float]:
    """Evaluate a held-out cohort; call after a patient-level split."""
    y = labels.astype(int)
    probabilities = model.predict_proba(features.loc[:, FEATURE_NAMES])[:, 1]
    bins = pd.cut(
        probabilities,
        bins=[index / 10 for index in range(11)],
        labels=False,
        include_lowest=True,
    )
    calibration_error = 0.0
    for bin_id in range(10):
        selected = bins == bin_id
        if selected.any():
            difference = abs(probabilities[selected].mean() - y[selected].mean())
            calibration_error += selected.mean() * difference
    return {
        "auroc": float(roc_auc_score(y, probabilities)),
        "auprc": float(average_precision_score(y, probabilities)),
        "brier": float(brier_score_loss(y, probabilities)),
        "ece_10": float(calibration_error),
    }


def log_mlflow(result: TrainingResult, metrics: dict[str, float]) -> None:
    """Log locally when the research dependency is installed; never upload MIMIC artifacts."""
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("Install the research extra to log MLflow experiments") from exc
    with mlflow.start_run():
        mlflow.log_params({
            "model": "ExtraTreesClassifier",
            "calibration": "isotonic",
            "feature_count": len(FEATURE_NAMES),
        })
        mlflow.log_metrics({**result.metrics, **metrics})
