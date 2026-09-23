from datetime import date

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.data import load_all
from app.ml import detect_anomalies, predict_task_time, train_task_time_model

app = FastAPI(title="Smart Operator Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_task_time_model = None


def _records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notnull(df), None).to_dict(orient="records")


@app.get("/api/machines")
def get_machines():
    return _records(load_all()["machines"])


@app.get("/api/operators")
def get_operators():
    return _records(load_all()["operators"])


@app.get("/api/tasks")
def get_tasks(task_date: date | None = None):
    tasks = load_all()["tasks"]
    if task_date:
        tasks = tasks[tasks["Date"] == task_date.isoformat()]
    return _records(tasks)


@app.get("/api/telemetry")
def get_telemetry(machine_id: str | None = None):
    telemetry = load_all()["telemetry"]
    if machine_id:
        telemetry = telemetry[telemetry["Machine ID"] == machine_id]
    return _records(telemetry)


@app.get("/api/incidents")
def get_incidents():
    return _records(load_all()["incidents"])


@app.get("/api/training/modules")
def get_training_modules():
    return _records(load_all()["training_modules"])


@app.get("/api/training/records")
def get_training_records(operator_id: str | None = None):
    records = load_all()["training_records"]
    if operator_id:
        records = records[records["Operator ID"] == operator_id]
    return _records(records)


@app.get("/api/anomalies")
def get_anomalies():
    return detect_anomalies()


class TaskTimePredictionRequest(BaseModel):
    task_type: str
    weather: str
    skill_level: str
    machine_age: float


@app.post("/api/predict/task-time")
def predict_task_time_endpoint(request: TaskTimePredictionRequest):
    global _task_time_model
    if _task_time_model is None:
        _task_time_model = train_task_time_model()
    try:
        predicted = predict_task_time(
            _task_time_model,
            request.task_type,
            request.weather,
            request.skill_level,
            request.machine_age,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"predicted_minutes": round(predicted, 1)}
