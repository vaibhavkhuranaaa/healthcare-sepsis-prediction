"""Synthetic-only Flask service. Local mode can load a separately stored model."""
from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from pydantic import BaseModel, Field, ValidationError

from src.pipeline.features import FEATURE_NAMES
from src.pipeline.train import load_model


class ScoreRequest(BaseModel):
    encounter_id: str = Field(min_length=1, max_length=64)
    observations: dict[str, float]


def create_app() -> Flask:
    static_directory = Path(__file__).parent / "static"
    app = Flask(__name__, static_folder=str(static_directory))
    model_path = os.getenv("MODEL_PATH")
    model = load_model(model_path) if model_path and Path(model_path).exists() else None

    @app.get("/")
    def dashboard():
        return send_from_directory(static_directory, "index.html")

    @app.get("/healthz")
    def health():
        return {"status": "ok", "mode": "local-model" if model else "synthetic-demo"}

    @app.get("/v1/demo/timeline/<encounter_id>")
    def timeline(encounter_id: str):
        now = datetime.now(UTC)
        # Current-to-past values: synthetic, irregular deterioration with brief recovery.
        risks = [0.653, 0.58, 0.61, 0.53, 0.41, 0.45, 0.38, 0.29, 0.31, 0.27]
        points = []
        for index in range(6):
            points.append({
                "time": (now - timedelta(minutes=15 * index)).isoformat(),
                "risk": risks[index],
            })
        return jsonify({
            "encounter_id": encounter_id,
            "synthetic": model is None,
            "points": list(reversed(points)),
        })

    @app.post("/v1/score")
    def score():
        try:
            payload = ScoreRequest.model_validate(request.get_json(force=True))
        except ValidationError as exc:
            return jsonify({"error": exc.errors()}), 422
        missing = [name for name in FEATURE_NAMES if name not in payload.observations]
        if missing:
            return jsonify({"error": "missing required features", "features": missing}), 422
        vector = np.array([[payload.observations[name] for name in FEATURE_NAMES]])
        if model:
            probability = float(model.predict_proba(vector)[0, 1])
            mode = "local-research"
        else:
            logit = (
                (vector[0, 0] - 90) / 20
                + (70 - vector[0, 2]) / 15
                + (vector[0, 8] - 2) / 1.5
                - 1.8
            )
            probability = float(1 / (1 + np.exp(-logit)))
            mode = "synthetic-demo"
        drivers = _drivers(payload.observations)
        return jsonify({
            "encounter_id": payload.encounter_id,
            "risk": round(probability, 4),
            "risk_band": _band(probability),
            "drivers": drivers,
            "mode": mode,
            "disclaimer": "Not for clinical use.",
        })

    return app


def _band(probability: float) -> str:
    return "high" if probability >= 0.6 else "medium" if probability >= 0.3 else "low"


def _drivers(values: dict[str, float]) -> list[dict[str, float | str]]:
    raw = {
        "heart_rate_last": (values["heart_rate_last"] - 90) / 20,
        "map_last": (70 - values["map_last"]) / 15,
        "lactate_last": (values["lactate_last"] - 2) / 1.5,
    }
    ranked = sorted(raw.items(), key=lambda item: abs(item[1]), reverse=True)
    return [{"feature": key, "contribution": round(value, 3)} for key, value in ranked]


app = create_app()
