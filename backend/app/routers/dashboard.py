from datetime import date

from fastapi import APIRouter, HTTPException

from app.data import load_all
from app.utils import records

router = APIRouter(tags=["dashboard"])


def _known_operator_ids() -> set[str]:
    return set(load_all()["operators"]["Operator ID"])


def _known_machine_ids() -> set[str]:
    return set(load_all()["machines"]["Machine ID"])


@router.get("/api/machines")
def get_machines():
    return records(load_all()["machines"])


@router.get("/api/tasks")
def get_tasks(task_date: date | None = None, operator_id: str | None = None):
    tasks = load_all()["tasks"]
    if operator_id and operator_id not in _known_operator_ids():
        raise HTTPException(status_code=404, detail=f"Unknown operator_id: {operator_id}")
    if task_date:
        tasks = tasks[tasks["Date"] == task_date.isoformat()]
    if operator_id:
        tasks = tasks[tasks["Operator ID"] == operator_id]
    return records(tasks)


@router.get("/api/dashboard")
def get_dashboard(task_date: date | None = None, operator_id: str | None = None):
    """Aggregated snapshot for the dashboard landing view: today's (or the
    given date's) tasks, joined machine status, so the frontend doesn't have
    to fetch tasks + machines separately and cross-reference them client-side."""
    data = load_all()
    tasks = data["tasks"]
    machines = data["machines"]

    if operator_id and operator_id not in _known_operator_ids():
        raise HTTPException(status_code=404, detail=f"Unknown operator_id: {operator_id}")

    filtered = tasks
    if task_date:
        filtered = filtered[filtered["Date"] == task_date.isoformat()]
    if operator_id:
        filtered = filtered[filtered["Operator ID"] == operator_id]

    used_machine_ids = set(filtered["Machine ID"])
    relevant_machines = machines[machines["Machine ID"].isin(used_machine_ids)] if used_machine_ids else machines

    return {
        "tasks": records(filtered),
        "machines": records(relevant_machines),
        "summary": {
            "total_tasks": len(filtered),
            "completed": int((filtered["Status"] == "Completed").sum()),
            "in_progress": int((filtered["Status"] == "In Progress").sum()),
            "scheduled": int((filtered["Status"] == "Scheduled").sum()),
        },
    }
