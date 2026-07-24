"""Train and evaluate from ignored, locally derived features only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from src.pipeline.features import FEATURE_NAMES
from src.pipeline.train import evaluate, log_mlflow, save_model, train

parser = argparse.ArgumentParser()
parser.add_argument("--input", default="data/derived/labelled_hourly_features.parquet")
parser.add_argument("--model-output", default="artifacts/local-research-model.joblib")
parser.add_argument("--metrics-output", default="reports/local-research-metrics.json")
args = parser.parse_args()

data = pd.read_parquet(args.input)
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_index, test_index = next(splitter.split(data, groups=data.stay_id))
train_data, test_data = data.iloc[train_index], data.iloc[test_index]
result = train(train_data.loc[:, FEATURE_NAMES], train_data.sepsis_within_6h)
metrics = evaluate(result.model, test_data.loc[:, FEATURE_NAMES], test_data.sepsis_within_6h)
save_model(result, args.model_output)
Path(args.metrics_output).parent.mkdir(parents=True, exist_ok=True)
Path(args.metrics_output).write_text(json.dumps(metrics, indent=2))
log_mlflow(result, metrics)
print(json.dumps(metrics, indent=2))
