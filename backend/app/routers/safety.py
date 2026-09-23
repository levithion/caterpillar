from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data import DATA_DIR, load_all
from app.utils import records

router = APIRouter(tags=["safety"])


@router.get("/api/telemetry")
def get_telemetry(machine_id: str | None = None):
    telemetry = load_all()["telemetry"]
    if machine_id:
        if machine_id not in set(load_all()["machines"]["Machine ID"]):
            raise HTTPException(status_code=404, detail=f"Unknown machine_id: {machine_id}")
        telemetry = telemetry[telemetry["Machine ID"] == machine_id]
    return records(telemetry)


@router.get("/api/incidents")
def get_incidents():
    return records(load_all()["incidents"])


class CreateIncidentRequest(BaseModel):
    machine_id: str
    operator_id: str
    incident_type: str
    severity: str
    description: str = ""
    action_taken: str = "Logged via assistant"
    location: str = "Unknown"


@router.post("/api/incidents")
def create_incident(request: CreateIncidentRequest):
    data = load_all()
    incidents = data["incidents"]

    if request.machine_id not in set(data["machines"]["Machine ID"]):
        raise HTTPException(status_code=404, detail=f"Unknown machine_id: {request.machine_id}")
    if request.operator_id not in set(data["operators"]["Operator ID"]):
        raise HTTPException(status_code=404, detail=f"Unknown operator_id: {request.operator_id}")

    next_id = 1
    if not incidents.empty:
        numeric = incidents["Incident ID"].str.extract(r"(\d+)").astype(int)
        next_id = int(numeric[0].max()) + 1

    new_row = {
        "Incident ID": f"INC{next_id:04d}",
        "Timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "Machine ID": request.machine_id,
        "Operator ID": request.operator_id,
        "Incident Type": request.incident_type,
        "Severity": request.severity,
        "Location": request.location,
        "Description": request.description,
        "Action Taken": request.action_taken,
        "Resolved": "No",
    }

    # Append to the CSV system-of-record. data.load_all() caches with an
    # mtime check, so the next GET picks the new row up automatically.
    incidents_path = DATA_DIR / "safety_incidents.csv"
    with open(incidents_path, "a", newline="") as f:
        pd.DataFrame([new_row]).to_csv(f, index=False, header=False)

    return new_row


@router.get("/api/fatigue")
def get_fatigue(machine_id: str | None = None):
    """Fatigue readings from the (simulated) IR-camera feed, newest first."""
    fatigue = load_all()["fatigue_events"].copy().sort_values("Timestamp", ascending=False)
    if machine_id:
        if machine_id not in set(load_all()["machines"]["Machine ID"]):
            raise HTTPException(status_code=404, detail=f"Unknown machine_id: {machine_id}")
        fatigue = fatigue[fatigue["Machine ID"] == machine_id]
    return records(fatigue)


@router.get("/api/safety/summary")
def get_safety_summary():
    """One snapshot for the Safety tab: seatbelt compliance and proximity
    hazards from telemetry, plus the latest fatigue state per operator
    (from fatigue_events.csv, i.e. the IR-camera simulation)."""
    data = load_all()
    telemetry = data["telemetry"].copy()
    if telemetry.empty:
        return {"seatbelt_compliance": [], "proximity_hazards": [], "latest_fatigue": []}

    latest = telemetry.sort_values("Timestamp").groupby(["Machine ID", "Operator ID"]).last().reset_index()

    seatbelt = latest[["Machine ID", "Operator ID", "Seatbelt Status", "Timestamp"]].rename(
        columns={"Seatbelt Status": "seatbelt_status", "Timestamp": "last_seen"}
    )
    seatbelt["compliant"] = seatbelt["seatbelt_status"] == "Fastened"

    hazards = latest[latest["Proximity Alert"] == "Yes"][
        ["Machine ID", "Operator ID", "Proximity Distance (m)", "Timestamp"]
    ].rename(columns={"Proximity Distance (m)": "distance_m"})
    hazards = hazards.sort_values("distance_m")

    fatigue = data["fatigue_events"].copy()
    fatigue_latest = fatigue.sort_values("Timestamp").groupby(["Machine ID", "Operator ID"]).last().reset_index()
    fatigue_latest = fatigue_latest.rename(columns={
        "Fatigue Score": "fatigue_score",
        "Alert Level": "alert_level",
        "Eye Closure Duration (s)": "eye_closure_seconds",
        "Haptic Triggered": "haptic_triggered",
        "Timestamp": "last_seen",
    })[["Machine ID", "Operator ID", "fatigue_score", "alert_level",
        "eye_closure_seconds", "haptic_triggered", "last_seen"]]

    return {
        "seatbelt_compliance": records(seatbelt),
        "proximity_hazards": records(hazards),
        "latest_fatigue": records(fatigue_latest),
    }
