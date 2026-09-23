import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.data import clear_cache, load_csv, preload
from app.ml.train import train_all
from app.routers import ergonomics, environment, machines, ml, stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    logging.getLogger().setLevel(settings.log_level)
    logger.info("Starting %s", settings.app_name)
    preload()
    try:
        meta = train_all()
        logger.info("ML models ready (%s samples)", meta.get("ergonomics_samples", 0))
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

app.include_router(machines.router)
app.include_router(ml.router)
app.include_router(stream.router)
app.include_router(ergonomics.router)
app.include_router(environment.router)


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
    from app.ml.train import models_ready

    return {
        "status": "ready",
        "ml_models": models_ready(),
        "engine": "ml" if models_ready() else "rules",
    }
