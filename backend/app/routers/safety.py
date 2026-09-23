from datetime import date, datetime
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data import DATA_DIR, load_all

router = APIRouter(prefix="/api", tags=["safety"])


def _records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notnull(df), None).to_dict(orient="records")


@router.get("/incidents")
def get_incidents():
    return _records(load_all()["incidents"])


class CreateIncidentRequest(BaseModel):
    machine_id: str
    operator_id: str
    incident_type: str
    severity: str
    description: str = ""
    action_taken: str = "Logged via assistant"
    location: str = "Unknown"


@router.post("/incidents")
def create_incident(request: CreateIncidentRequest):
    data = load_all()
    incidents = data["incidents"]

    next_id = 1
    if not incidents.empty:
        numeric = incidents["Incident ID"].str.extract(r"(\d+)").astype(int)
        next_id = int(numeric[0].max()) + 1

    new_row = {
        "Incident ID": f"INC{next_id:04d}",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Machine ID": request.machine_id,
        "Operator ID": request.operator_id,
        "Incident Type": request.incident_type,
        "Severity": request.severity,
        "Location": request.location,
        "Description": request.description,
        "Action Taken": request.action_taken,
        "Resolved": "No",
    }

    incidents_path = DATA_DIR / "safety_incidents.csv"
    file_exists = incidents_path.exists()
    with open(incidents_path, "a", newline="") as f:
        pd.DataFrame([new_row]).to_csv(f, index=False, header=not file_exists)

    return new_row


@router.get("/safety/summary")
def get_safety_summary():
    data = load_all()
    telemetry = data["telemetry"].copy()
    if telemetry.empty:
        return {"seatbelt_compliance": [], "proximity_hazards": [], "latest_fatigue": []}

    # Latest row per machine-operator pair for compliance
    latest = telemetry.sort_values("Timestamp").groupby(["Machine ID", "Operator ID"]).last().reset_index()
    seatbelt = latest[["Machine ID", "Operator ID", "Seatbelt Status", "Timestamp"]].rename(
        columns={"Seatbelt Status": "seatbelt_status", "Timestamp": "last_seen"}
    )
    seatbelt["compliant"] = seatbelt["seatbelt_status"] == "Fastened"

    # Ranked proximity hazards
    hazards = latest[latest["Proximity Alert"] == "Yes"][
        ["Machine ID", "Operator ID", "Proximity Distance (m)", "Timestamp"]
    ].rename(columns={"Proximity Distance (m)": "distance_m"})
    hazards = hazards.sort_values("distance_m").to_dict(orient="records")

    # Latest fatigue snapshot per operator
    fatigue_cols = ["Machine ID", "Operator ID", "Fatigue Score", "Alert Level",
                    "Eye Closure Duration (s)", "Haptic Triggered", "Timestamp"]
    fatigue = latest[fatigue_cols].rename(columns={
        "Fatigue Score": "fatigue_score",
        "Alert Level": "alert_level",
        "Eye Closure Duration (s)": "eye_closure_seconds",
        "Haptic Triggered": "haptic_triggered",
        "Timestamp": "last_seen",
    }).to_dict(orient="records")

    return {
        "seatbelt_compliance": seatbelt.to_dict(orient="records"),
        "proximity_hazards": hazards,
        "latest_fatigue": fatigue,
    }
