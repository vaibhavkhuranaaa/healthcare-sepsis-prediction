"""Build local, ignored hourly features and labels from MIMIC-IV Demo files."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.pipeline.features import build_hourly_features
from src.pipeline.ingest import normalize_demo_events
from src.pipeline.labels import attach_horizon_labels

parser = argparse.ArgumentParser()
parser.add_argument("--demo-root", required=True)
parser.add_argument(
    "--onsets", required=True, help="Local CSV from reviewed Sepsis-3 labeling logic"
)
parser.add_argument("--output", default="data/derived/labelled_hourly_features.parquet")
args = parser.parse_args()

features = build_hourly_features(normalize_demo_events(args.demo_root))
labelled = attach_horizon_labels(features, pd.read_csv(args.onsets))
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
labelled.to_parquet(args.output, index=False)
print(f"Wrote {len(labelled)} local rows to {args.output}")
