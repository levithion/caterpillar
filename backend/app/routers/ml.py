from fastapi import APIRouter, HTTPException

from app.ml.inference import get_ml_status
from app.ml.train import train_all

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.get("/status")
def ml_status():
    return get_ml_status()


@router.post("/train")
def retrain_models(force: bool = True):
    try:
        meta = train_all(force=force)
        return {"status": "trained", **meta}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
