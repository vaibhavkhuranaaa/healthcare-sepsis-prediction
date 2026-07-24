"""Create a local synthetic model for smoke testing only."""
from pathlib import Path

from src.pipeline.demo_data import synthetic_features, synthetic_labels
from src.pipeline.train import save_model, train

features = synthetic_features()
result = train(features, synthetic_labels(features))
save_model(result, Path("artifacts/synthetic-model.joblib"))
print(result.metrics)
