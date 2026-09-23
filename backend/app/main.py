from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    anomalies,
    auth,
    coaching,
    dashboard,
    environment,
    ergonomics,
    predictor,
    safety,
    training,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Train (or load the cached joblib model) once at startup instead of on
    # the first prediction request, so that request doesn't pay for training.
    predictor.get_model()
    yield


app = FastAPI(title="Smart Operator Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
