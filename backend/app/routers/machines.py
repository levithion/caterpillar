from fastapi import APIRouter, HTTPException

from app.services import machines as svc

router = APIRouter(tags=["machines"])


@router.get("/api/machine-capabilities")
def get_machine_capabilities():
    try:
        return {"machines": svc.list_machines()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/api/machine-capabilities/{machine_id}")
def get_machine_capability(machine_id: str):
    try:
        machine = svc.get_machine(machine_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not machine:
        raise HTTPException(status_code=404, detail=f"Unknown machine ID: {machine_id}")
    return machine
