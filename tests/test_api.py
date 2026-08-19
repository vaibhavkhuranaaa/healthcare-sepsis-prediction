import math

from src.app import create_app
from src.pipeline.features import FEATURE_NAMES


def _payload():
    values = [110, 2, 65, 24, 38, 94, 15, 1.5, 3, 10]
    return {
        "encounter_id": "synthetic-1",
        "observations": dict(zip(FEATURE_NAMES, values, strict=True)),
    }


def test_score_is_synthetic_and_has_disclaimer():
    client = create_app().test_client()
    response = client.post("/v1/score", json=_payload())
    assert response.status_code == 200
    assert response.json["mode"] == "synthetic-demo"
    assert response.json["disclaimer"] == "Not for clinical use."


def test_score_rejects_incomplete_payload():
    client = create_app().test_client()
    response = client.post("/v1/score", json={"encounter_id": "x", "observations": {}})
    assert response.status_code == 422


def test_public_score_rejects_non_synthetic_ids_and_invalid_features():
    client = create_app().test_client()
    payload = _payload()
    payload["encounter_id"] = "real-record"
    assert client.post("/v1/score", json=payload).status_code == 422

    payload = _payload()
    payload["observations"]["unexpected"] = 1
    assert client.post("/v1/score", json=payload).status_code == 422

    payload = _payload()
    payload["observations"]["lactate_last"] = math.inf
    assert client.post("/v1/score", json=payload).status_code == 422


def test_public_mode_does_not_load_model_without_explicit_opt_in(monkeypatch, tmp_path):
    model_path = tmp_path / "research.joblib"
    model_path.touch()
    monkeypatch.setenv("MODEL_PATH", str(model_path))
    monkeypatch.delenv("ALLOW_LOCAL_RESEARCH_MODEL", raising=False)
    assert create_app().test_client().get("/healthz").json["mode"] == "synthetic-demo"


def test_health_reports_deployed_source(monkeypatch):
    source_sha = "a" * 40
    monkeypatch.setenv("SOURCE_SHA", source_sha)
    assert create_app().test_client().get("/healthz").json["source_sha"] == source_sha


def test_risk_band_boundaries():
    from src.app import _band

    assert _band(0.2999) == "low"
    assert _band(0.3) == "medium"
    assert _band(0.5999) == "medium"
    assert _band(0.6) == "high"


def test_synthetic_timeline_has_non_linear_change():
    client = create_app().test_client()
    points = client.get("/v1/demo/timeline/synthetic-1").json["points"]
    changes = [
        round(points[index + 1]["risk"] - point["risk"], 3)
        for index, point in enumerate(points[:-1])
    ]
    assert len(set(changes)) > 1
    assert points[-1]["risk"] == 0.653
