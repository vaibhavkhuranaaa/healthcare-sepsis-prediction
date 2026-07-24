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

    Input columns: stay_id, charttime, feature, value. ``charttime`` is the source
    availability time; callers must not substitute a later result/recording time.
    """
    required = {"stay_id", "charttime", "feature", "value"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"Missing event columns: {sorted(missing)}")
    data = events.copy()
    data["charttime"] = pd.to_datetime(data["charttime"], utc=True)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna(subset=["value"]).sort_values(["stay_id", "charttime"])
    rows: list[dict[str, object]] = []
    for stay_id, stay in data.groupby("stay_id", sort=False):
        hours = pd.date_range(
            stay.charttime.min().floor("h"), stay.charttime.max().floor("h"), freq="h"
        )
        for hour in hours:
            hour = pd.to_datetime(hour, utc=True)
            history = stay[stay.charttime <= hour]
            row: dict[str, object] = {"stay_id": stay_id, "prediction_time": hour}
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
                values = history[history.feature == feature].set_index("charttime").value
                row[f"{feature}_last"] = values.iloc[-1] if not values.empty else np.nan
            cutoff = hour - pd.offsets.Hour(6)
            hr = history[(history.feature == "heart_rate") & (history.charttime > cutoff)]
            row["heart_rate_slope_6h"] = _slope(hr)
            row["measurement_count_6h"] = int((history.charttime > cutoff).sum())
            rows.append(row)
    return pd.DataFrame(rows).reindex(columns=("stay_id", "prediction_time", *FEATURE_NAMES))


def _slope(events: pd.DataFrame) -> float:
    if len(events) < 2:
        return float("nan")
    x = (events.charttime - events.charttime.iloc[0]).dt.total_seconds().to_numpy() / 3600
    return float(np.polyfit(x, events.value.to_numpy(), 1)[0])
