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
        return vitals
    stays = pd.read_csv(
        root / "icu" / "icustays.csv.gz", usecols=["stay_id", "hadm_id", "intime", "outtime"]
    )
    stays["intime"] = pd.to_datetime(stays["intime"], utc=True)
    stays["outtime"] = pd.to_datetime(stays["outtime"], utc=True)
    labs = labs.merge(stays, on="hadm_id", how="inner")
    labs = labs[(labs.charttime >= labs.intime) & (labs.charttime <= labs.outtime)]
    labs = labs[["stay_id", "charttime", "feature", "value"]]
    return pd.concat([vitals, labs], ignore_index=True).sort_values(["stay_id", "charttime"])


def _read_events(
    path: Path, item_map: dict[int, str], identifier: str, value_column: str, chunksize: int
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    columns = [identifier, "itemid", "charttime", value_column]
    for chunk in pd.read_csv(path, usecols=columns, chunksize=chunksize):
        chunk = chunk[chunk.itemid.isin(item_map)]
        if not chunk.empty:
            chunk["feature"] = chunk.itemid.map(item_map)
            chunk = chunk.rename(columns={value_column: "value"})
            parts.append(chunk[[identifier, "charttime", "feature", "value"]])
    return (
        pd.concat(parts, ignore_index=True)
        if parts
        else pd.DataFrame(columns=[identifier, "charttime", "feature", "value"])
    )
