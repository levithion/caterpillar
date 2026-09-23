from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.services import environment as svc

router = APIRouter(prefix="/api/environment", tags=["environment"])


@router.get("")
def get_environment(
    machine_id: str | None = None,
    operator_id: str | None = None,
    limit: int = Query(default=None, ge=1),
):
    settings = get_settings()
    effective_limit = limit or settings.default_series_limit
    if effective_limit > settings.max_series_limit:
        raise HTTPException(
            status_code=422,
            detail=f"limit must be <= {settings.max_series_limit}",
        )

    try:
        if machine_id and machine_id not in svc.list_machine_ids():
            raise HTTPException(status_code=404, detail=f"Unknown machine ID: {machine_id}")
        result = svc.build_response(machine_id, operator_id, effective_limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if operator_id and result["current"] is None:
        raise HTTPException(status_code=404, detail=f"Unknown operator ID: {operator_id}")

    return result


@router.get("/machines")
def list_machines():
    try:
        return {"machines": svc.list_machine_ids()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
