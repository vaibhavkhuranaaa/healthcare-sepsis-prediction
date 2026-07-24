"""Label alignment for a six-hour early-warning horizon."""
from __future__ import annotations

import pandas as pd


def attach_horizon_labels(features: pd.DataFrame, sepsis_onsets: pd.DataFrame) -> pd.DataFrame:
    """Attach onset-within-six-hours labels and remove post-onset rows.

    ``sepsis_onsets`` is a local output from reviewed MIMIC-code Sepsis-3 logic and
    contains ``stay_id`` and ``sepsis_onset``. This function does not infer labels.
    """
    required = {"stay_id", "prediction_time"}
    if missing := required - set(features.columns):
        raise ValueError(f"Missing feature columns: {sorted(missing)}")
    if missing := {"stay_id", "sepsis_onset"} - set(sepsis_onsets.columns):
        raise ValueError(f"Missing onset columns: {sorted(missing)}")
    result = features.merge(sepsis_onsets[["stay_id", "sepsis_onset"]], on="stay_id", how="left")
    result["prediction_time"] = pd.to_datetime(result.prediction_time, utc=True)
    result["sepsis_onset"] = pd.to_datetime(result.sepsis_onset, utc=True)
    pre_onset = result.sepsis_onset.isna() | (result.prediction_time < result.sepsis_onset)
    result = result[pre_onset].copy()
    result["sepsis_within_6h"] = (
        result.sepsis_onset.notna()
        & (result.sepsis_onset <= result.prediction_time + pd.offsets.Hour(6))
    ).astype(int)
    return result.drop(columns="sepsis_onset")
