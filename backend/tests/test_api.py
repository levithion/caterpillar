import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_machines_list():
    res = client.get("/api/machines")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    machines = res.json()["machines"]
    assert len(machines) > 0
    assert "capabilities" in machines[0]


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ready():
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] in ("ready", "not_ready")


def test_ergonomics_machines():
    res = client.get("/api/ergonomics/machines")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    assert "machines" in res.json()
    assert len(res.json()["machines"]) > 0


def test_ergonomics_series():
    res = client.get("/api/ergonomics?limit=10")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    body = res.json()
    assert "current" in body
    assert "series" in body
    assert len(body["series"]) <= 10


def test_ergonomics_unknown_machine():
    res = client.get("/api/ergonomics?machine_id=INVALID")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 404


def test_environment_machines():
    res = client.get("/api/environment/machines")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    assert len(res.json()["machines"]) > 0


def test_environment_series():
    res = client.get("/api/environment?limit=10")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 200
    body = res.json()
    assert body["current"] is not None
    assert "warnings" in body["current"]


def test_environment_unknown_machine():
    res = client.get("/api/environment?machine_id=INVALID")
    if res.status_code == 503:
        pytest.skip("Data not seeded")
    assert res.status_code == 404
