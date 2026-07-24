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


def test_synthetic_timeline_has_non_linear_change():
    client = create_app().test_client()
    points = client.get("/v1/demo/timeline/synthetic-1").json["points"]
    changes = [
        round(points[index + 1]["risk"] - point["risk"], 3)
        for index, point in enumerate(points[:-1])
    ]
    assert len(set(changes)) > 1
    assert points[-1]["risk"] == 0.653
