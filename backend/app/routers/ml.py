from fastapi import APIRouter, HTTPException

from app.ml.inference import (
    fatigue_rule_model_compare,
    get_ml_status,
    telemetry_model_anomalies,
)
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


@router.get("/fatigue-compare")
def fatigue_compare(limit: int = 15):
    """Rule vs learned-model alert verdicts on the latest fatigue readings,
    disagreements first — the model is trained, not threshold-coded."""
    try:
        return fatigue_rule_model_compare(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/telemetry-anomalies")
def telemetry_anomalies(limit: int = 20):
    """IsolationForest flags over ALL telemetry signals, z-normalized per
    machine — jointly unusual readings, not single big numbers."""
    try:
        return telemetry_model_anomalies(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc