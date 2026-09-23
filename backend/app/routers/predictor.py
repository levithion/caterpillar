from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.task_time_ml import load_or_train_task_time_model, predict_task_time_range

router = APIRouter(tags=["predictor"])

_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_or_train_task_time_model()
    return _model


class TaskTimePredictionRequest(BaseModel):
    task_type: str
    weather: str
    skill_level: str
    machine_age: float


@router.post("/api/predict/task-time")
def predict_task_time_endpoint(request: TaskTimePredictionRequest):
    try:
        point, lower, upper = predict_task_time_range(
            get_model(),
            request.task_type,
            request.weather,
            request.skill_level,
            request.machine_age,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "predicted_minutes": round(point, 1),
        "lower_bound_minutes": round(lower, 1),
        "upper_bound_minutes": round(upper, 1),
    }
