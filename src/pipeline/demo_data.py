"""Synthetic fixtures for tests, local UI demos, and cloud deployment."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .features import FEATURE_NAMES


def synthetic_features(rows: int = 240, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    values = pd.DataFrame({
        "heart_rate_last": rng.normal(88, 18, rows),
        "heart_rate_slope_6h": rng.normal(1, 2, rows),
        "map_last": rng.normal(75, 12, rows),
        "resp_rate_last": rng.normal(20, 5, rows),
        "temperature_last": rng.normal(37.2, 0.8, rows),
        "spo2_last": rng.normal(96, 2, rows),
        "wbc_last": rng.lognormal(2.2, 0.35, rows),
        "creatinine_last": rng.lognormal(0, 0.4, rows),
        "lactate_last": rng.lognormal(0.3, 0.5, rows),
        "measurement_count_6h": rng.integers(3, 15, rows),
    })
    return values.loc[:, FEATURE_NAMES]


def synthetic_labels(features: pd.DataFrame) -> pd.Series:
    logit = ((features.heart_rate_last - 90) / 20 + features.heart_rate_slope_6h / 3
             + (70 - features.map_last) / 15 + (features.lactate_last - 2) / 1.5
             + (features.wbc_last - 11) / 8 - 1.8)
    probability = 1 / (1 + np.exp(-logit))
    return pd.Series((probability > 0.5).astype(int), name="sepsis_within_6h")
