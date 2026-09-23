import pytest
from fastapi.testclient import TestClient

from app.main import app


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


def test_machine_capabilities_list(client):
    res = client.get("/api/machine-capabilities")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    machines = res.json()["machines"]
    assert len(machines) > 0
    assert "capabilities" in machines[0]


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ready(client):
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] in ("ready", "not_ready")


def test_ergonomics_machines(client):
    res = client.get("/api/ergonomics/machines")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    assert "machines" in res.json()
    assert len(res.json()["machines"]) > 0


def test_ergonomics_series(client):
    res = client.get("/api/ergonomics?limit=10")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    body = res.json()
    assert "current" in body
    assert "series" in body
    assert len(body["series"]) <= 10


def test_ergonomics_unknown_machine(client):
    res = client.get("/api/ergonomics?machine_id=INVALID")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 404


def test_environment_machines(client):
    res = client.get("/api/environment/machines")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    assert len(res.json()["machines"]) > 0


def test_environment_series(client):
    res = client.get("/api/environment?limit=10")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    body = res.json()
    assert body["current"] is not None
    assert "warnings" in body["current"]


def test_environment_unknown_machine(client):
    res = client.get("/api/environment?machine_id=INVALID")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 404
