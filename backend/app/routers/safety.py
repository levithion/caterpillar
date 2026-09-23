from fastapi import APIRouter, HTTPException

from app.data import load_all
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


# TODO (Member 2): POST /api/incidents to create an incident from the UI,
# and the fatigue endpoint (backed by data/fatigue_events.csv).
