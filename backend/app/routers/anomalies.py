from fastapi import APIRouter

from app.task_time_ml import detect_anomalies

router = APIRouter(tags=["anomalies"])


@router.get("/api/anomalies")
def get_anomalies():
    return detect_anomalies()


# TODO (Member 4): pattern-based flags beyond idling/fuel z-scores
# (repeated Safety Alert Triggered events, RPM/load-cycle combinations).
