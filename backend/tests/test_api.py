import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize(
    "path",
    [
        "/api/machines",
        "/api/tasks",
        "/api/operators",
        "/api/telemetry",
        "/api/incidents",
        "/api/training/modules",
        "/api/training/records",
        "/api/anomalies",
    ],
)
def test_list_endpoints_return_ok(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_returns_snapshot(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"tasks", "machines", "summary"}
    assert body["summary"]["total_tasks"] == len(body["tasks"])


def test_dashboard_filters_by_unknown_operator_is_404(client):
    response = client.get("/api/dashboard", params={"operator_id": "NOPE"})
    assert response.status_code == 404


def test_tasks_filters_by_unknown_operator_is_404(client):
    response = client.get("/api/tasks", params={"operator_id": "NOPE"})
    assert response.status_code == 404


def test_telemetry_filters_by_unknown_machine_is_404(client):
    response = client.get("/api/telemetry", params={"machine_id": "NOPE"})
    assert response.status_code == 404


def test_training_records_filters_by_unknown_operator_is_404(client):
    response = client.get("/api/training/records", params={"operator_id": "NOPE"})
    assert response.status_code == 404


def test_predict_task_time_returns_point_and_range(client):
    response = client.post(
        "/api/predict/task-time",
        json={
            "task_type": "Trenching",
            "weather": "Sunny",
            "skill_level": "Expert",
            "machine_age": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"predicted_minutes", "lower_bound_minutes", "upper_bound_minutes"}
    assert body["lower_bound_minutes"] <= body["predicted_minutes"] <= body["upper_bound_minutes"]


def test_predict_task_time_rejects_bad_payload(client):
    response = client.post("/api/predict/task-time", json={"task_type": "Trenching"})
    assert response.status_code == 422
