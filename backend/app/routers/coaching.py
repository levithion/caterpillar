import pandas as pd
from fastapi import APIRouter

from app.data import load_all

router = APIRouter(prefix="/api", tags=["coaching"])


def _records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notnull(df), None).to_dict(orient="records")


@router.get("/coaching")
def get_coaching_events(machine_id: str | None = None, severity: str | None = None):
    events = load_all()["coaching_events"].copy()
    if events.empty:
        return []

    # newest first
    events = events.sort_values("Timestamp", ascending=False)

    if machine_id:
        events = events[events["Machine ID"] == machine_id]
    if severity:
        events = events[events["Severity"].str.lower() == severity.lower()]

    return _records(events)
