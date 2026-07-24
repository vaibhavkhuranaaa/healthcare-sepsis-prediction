"""SHAP explanations are intentionally optional and remain local."""
from __future__ import annotations

import pandas as pd
from sklearn.pipeline import Pipeline

from .features import FEATURE_NAMES


def explain(model: Pipeline, rows: pd.DataFrame) -> pd.DataFrame:
    """Return local SHAP values; importing SHAP lazily keeps API memory small."""
    try:
        import shap
    except ImportError as exc:
        raise RuntimeError("Install the research extra to generate SHAP explanations") from exc
    classifier = model.named_steps["classifier"].calibrated_classifiers_[0].estimator
    prepared = model.named_steps["imputer"].transform(rows.loc[:, FEATURE_NAMES])
    values = shap.TreeExplainer(classifier).shap_values(prepared)
    return pd.DataFrame(values[:, :len(FEATURE_NAMES)], columns=FEATURE_NAMES, index=rows.index)
