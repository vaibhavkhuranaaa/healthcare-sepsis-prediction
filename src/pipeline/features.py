"""Leakage-safe hourly feature engineering for local MIMIC research."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

FEATURE_NAMES = (
    "heart_rate_last", "heart_rate_slope_6h", "map_last", "resp_rate_last",
    "temperature_last", "spo2_last", "wbc_last", "creatinine_last", "lactate_last",
    "measurement_count_6h",
)


@dataclass(frozen=True)
class FeatureContract:
    names: tuple[str, ...] = FEATURE_NAMES
    version: str = "v1"


def build_hourly_features(events: pd.DataFrame) -> pd.DataFrame:
    """Create features using only observations at or before each hourly timestamp.

    Input columns: subject_id, stay_id, available_time, feature, value. Availability
    must reflect recording or result time, not specimen or observation time alone.
    """
    required = {"subject_id", "stay_id", "available_time", "feature", "value"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"Missing event columns: {sorted(missing)}")
    data = events.copy()
    data["available_time"] = pd.to_datetime(data["available_time"], utc=True)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna(
        subset=["subject_id", "stay_id", "available_time", "value"]
    ).sort_values(["stay_id", "available_time"])
    rows: list[dict[str, object]] = []
    for stay_id, stay in data.groupby("stay_id", sort=False):
        subject_ids = stay.subject_id.unique()
        if len(subject_ids) != 1:
            raise ValueError(f"stay_id {stay_id} must map to exactly one subject_id")
        hours = pd.date_range(
            stay.available_time.min().floor("h"), stay.available_time.max().floor("h"), freq="h"
        )
        for hour in hours:
            hour = pd.to_datetime(hour, utc=True)
            history = stay[stay.available_time <= hour]
            row: dict[str, object] = {
                "subject_id": subject_ids[0],
                "stay_id": stay_id,
                "prediction_time": hour,
            }
            for feature in (
                "heart_rate",
                "map",
                "resp_rate",
                "temperature",
                "spo2",
                "wbc",
                "creatinine",
                "lactate",
            ):
                values = history[history.feature == feature].set_index("available_time").value
                row[f"{feature}_last"] = values.iloc[-1] if not values.empty else np.nan
            cutoff = hour - pd.offsets.Hour(6)
            hr = history[
                (history.feature == "heart_rate") & (history.available_time > cutoff)
            ]
            row["heart_rate_slope_6h"] = _slope(hr)
            row["measurement_count_6h"] = int((history.available_time > cutoff).sum())
            rows.append(row)
    return pd.DataFrame(rows).reindex(
        columns=("subject_id", "stay_id", "prediction_time", *FEATURE_NAMES)
    )


def _slope(events: pd.DataFrame) -> float:
    if len(events) < 2:
        return float("nan")
    x = (
        (events.available_time - events.available_time.iloc[0]).dt.total_seconds().to_numpy()
        / 3600
    )
    return float(np.polyfit(x, events.value.to_numpy(), 1)[0])
