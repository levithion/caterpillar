import pytest
from fastapi.testclient import TestClient

from app.ml.train import models_ready, train_all


@pytest.fixture(scope="module", autouse=True)
def trained_models():
    train_all(force=True)
    assert models_ready()


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_meta_includes_member2_models():
    meta = train_all(force=False)
    assert meta["fatigue_samples"] > 100
    assert meta["telemetry_samples"] > 100
    assert set(meta["fatigue_classes"]) == {"Normal", "Caution", "Critical"}
    assert "fatigue_clf" in meta["models"]
    assert "telemetry_anomaly" in meta["models"]


def test_fatigue_compare_endpoint(client):
    response = client.get("/api/ml/fatigue-compare", params={"limit": 15})
    assert response.status_code == 200
    body = response.json()
    assert body
    for row in body:
        assert set(row.keys()) >= {"rule_alert_level", "model_alert_level", "model_probability", "agreement"}
        assert row["model_alert_level"].lower() in {"normal", "caution", "critical"}
        assert 0 <= row["model_probability"] <= 1
        assert isinstance(row["agreement"], bool)


def test_fatigue_compare_disagreements_first(client):
    body = client.get("/api/ml/fatigue-compare", params={"limit": 15}).json()
    if not all(row["agreement"] for row in body):
        first_disagree = next(i for i, row in enumerate(body) if not row["agreement"])
        assert first_disagree == 0


def test_telemetry_anomalies_endpoint(client):
    response = client.get("/api/ml/telemetry-anomalies", params={"limit": 20})
    assert response.status_code == 200
    body = response.json()
    assert body
    for row in body:
        assert set(row.keys()) >= {"timestamp", "machine_id", "operator_id", "anomaly_score", "severity", "top_drivers"}
        assert row["anomaly_score"] >= 0
        assert len(row["top_drivers"]) == 3
