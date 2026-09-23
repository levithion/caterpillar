from fastapi import APIRouter, HTTPException

from app.services import machines as svc

router = APIRouter(prefix="/api/machines", tags=["machines"])


@router.get("")
def get_machines():
    try:
        return {"machines": svc.list_machines()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{machine_id}")
def get_machine(machine_id: str):
    try:
        machine = svc.get_machine(machine_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not machine:
        raise HTTPException(status_code=404, detail=f"Unknown machine ID: {machine_id}")
    return machine
