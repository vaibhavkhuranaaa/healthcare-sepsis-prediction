"""Memory-bounded MIMIC-IV Demo event normalization; never writes into the repo."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

VITAL_ITEMIDS = {
    220045: "heart_rate", 220181: "map", 220210: "resp_rate",
    223761: "temperature", 220277: "spo2",
}
LAB_ITEMIDS = {51300: "wbc", 50912: "creatinine", 50813: "lactate"}


def normalize_demo_events(root: str | Path, chunksize: int = 250_000) -> pd.DataFrame:
    """Read selected MIMIC Demo CSV rows in chunks into the feature contract.

    The calling process retains the returned frame locally; no raw data, output, or
    identifiers are uploaded, logged, or committed.
    """
    root = Path(root)
    vitals = _read_events(
        root / "icu" / "chartevents.csv.gz", VITAL_ITEMIDS, "stay_id", "valuenum", chunksize
    )
    labs = _read_events(
        root / "hosp" / "labevents.csv.gz", LAB_ITEMIDS, "hadm_id", "valuenum", chunksize
    )
    if labs.empty:
        return _available_events(vitals).drop(columns=["hadm_id"], errors="ignore")
    stays = pd.read_csv(
        root / "icu" / "icustays.csv.gz",
        usecols=["subject_id", "stay_id", "hadm_id", "intime", "outtime"],
    )
    stays["intime"] = pd.to_datetime(stays["intime"], utc=True)
    stays["outtime"] = pd.to_datetime(stays["outtime"], utc=True)
    labs = labs.merge(stays, on=["subject_id", "hadm_id"], how="inner")
    labs["charttime"] = pd.to_datetime(labs["charttime"], utc=True)
    labs = labs[(labs.charttime >= labs.intime) & (labs.charttime <= labs.outtime)]
    events = pd.concat([_available_events(vitals), _available_events(labs)], ignore_index=True)
    return events.sort_values(["stay_id", "available_time"])


def _read_events(
    path: Path, item_map: dict[int, str], identifier: str, value_column: str, chunksize: int
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    columns = ["subject_id", identifier, "itemid", "charttime", "storetime", value_column]
    for chunk in pd.read_csv(path, usecols=columns, chunksize=chunksize):
        chunk = chunk[chunk.itemid.isin(item_map)]
        if not chunk.empty:
            chunk["feature"] = chunk.itemid.map(item_map)
            chunk = chunk.rename(columns={value_column: "value"})
            parts.append(
                chunk[["subject_id", identifier, "charttime", "storetime", "feature", "value"]]
            )
    return (
        pd.concat(parts, ignore_index=True)
        if parts
        else pd.DataFrame(
            columns=["subject_id", identifier, "charttime", "storetime", "feature", "value"]
        )
    )


def _available_events(events: pd.DataFrame) -> pd.DataFrame:
    result = events.copy()
    result["charttime"] = pd.to_datetime(result["charttime"], utc=True)
    result["storetime"] = pd.to_datetime(result["storetime"], utc=True)
    result = result.dropna(subset=["charttime", "storetime"])
    result["available_time"] = result[["charttime", "storetime"]].max(axis=1)
    return result[["subject_id", "stay_id", "available_time", "feature", "value"]]
