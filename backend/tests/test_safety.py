import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_coaching_returns_events_newest_first(client):
    response = client.get("/api/coaching")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and body
    timestamps = [e["Timestamp"] for e in body]
    assert timestamps == sorted(timestamps, reverse=True)


def test_coaching_severity_filter_is_case_insensitive(client):
    response = client.get("/api/coaching", params={"severity": "WARNING"})
    assert response.status_code == 200
    for event in response.json():
        assert event["Severity"].lower() == "warning"


def test_coaching_machine_filter_rejects_unknown_is_not_implemented(client):
    # Unknown machines simply return an empty list (no 404, by design).
    response = client.get("/api/coaching", params={"machine_id": "NOPE"})
    assert response.status_code == 200
    assert response.json() == []


def test_safety_summary_returns_three_sections(client):
    response = client.get("/api/safety/summary")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"seatbelt_compliance", "proximity_hazards", "latest_fatigue"}
    assert body["seatbelt_compliance"]
    for hazard in body["proximity_hazards"]:
        assert hazard["distance_m"] < 2
    for fatigue in body["latest_fatigue"]:
        assert 0 <= fatigue["fatigue_score"] <= 100
        assert fatigue["alert_level"].lower() in {"normal", "caution", "critical"}


def test_create_incident_appends_row(client):
    create = client.post(
        "/api/incidents",
        json={
            "machine_id": "EXC001",
            "operator_id": "OP1001",
            "incident_type": "Fatigue Alert",
            "severity": "High",
            "description": "test incident",
        },
    )
    assert create.status_code == 200
    created = create.json()
    assert created["Resolved"] == "No"

    listing = client.get("/api/incidents").json()
    assert any(row["Incident ID"] == created["Incident ID"] for row in listing)


def test_create_incident_rejects_unknown_machine(client):
    response = client.post(
        "/api/incidents",
        json={
            "machine_id": "NOPE",
            "operator_id": "OP1001",
            "incident_type": "Other",
            "severity": "Low",
        },
    )
    assert response.status_code == 404


def test_fatigue_endpoint_returns_records(client):
    response = client.get("/api/fatigue")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and body
    assert "Fatigue Score" in body[0]
