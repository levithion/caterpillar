import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.config import get_settings
from app.data import clear_cache, load_csv, preload
from app.ml.train import models_ready, train_all
from app.routers import (
    anomalies,
    auth,
    coaching,
    dashboard,
    environment,
    ergonomics,
    machines,
    ml,
    predictor,
    safety,
    stream,
    training,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    logging.getLogger().setLevel(settings.log_level)
    logger.info("Starting %s", settings.app_name)
    # Create (and, on first run, seed) the operators database before
    # anything reads from it.
    db.init_db()
    preload()
    # Train (or load the cached joblib model) once at startup instead of on
    # the first prediction request, so that request doesn't pay for training.
    predictor.get_model()
    try:
        meta = train_all()
        logger.info("ML models ready (%s ergonomics samples)", meta.get("ergonomics_samples", 0))
    except Exception as exc:  # noqa: BLE001
        logger.error("ML training failed: %s — live stream will use rule fallback", exc)
    yield
    clear_cache()
    logger.info("Shutdown complete")


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(predictor.router)
app.include_router(safety.router)
app.include_router(coaching.router)
app.include_router(training.router)
app.include_router(anomalies.router)
app.include_router(ergonomics.router)
app.include_router(environment.router)
app.include_router(machines.router)
app.include_router(ml.router)
app.include_router(stream.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    required = ("ergonomics.csv", "environment.csv")
    missing = [f for f in required if not (settings.data_dir / f).exists()]
    if missing:
        return {"status": "not_ready", "missing": missing}
    try:
        load_csv("ergonomics.csv")
        load_csv("environment.csv")
    except Exception as exc:  # noqa: BLE001
        return {"status": "not_ready", "error": str(exc)}
    return {
        "status": "ready",
        "ml_models": models_ready(),
        "engine": "ml" if models_ready() else "rules",
    }
