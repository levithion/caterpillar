"""Train and persist ML models from historical sensor CSVs."""

import json
import logging
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor

from app.config import get_settings
from app.data import load_csv
from app.ml.features import (
    DAMPING_LABELS,
    build_environment_training_frame,
    build_ergonomics_training_frame,
)

logger = logging.getLogger(__name__)

MODEL_FILES = {
    "ergo_reg": "ergonomics_regressor.joblib",
    "ergo_damp": "ergonomics_damping.joblib",
    "ergo_shock": "ergonomics_shock.joblib",
    "ergo_anomaly": "ergonomics_anomaly.joblib",
    "env_reg": "environment_regressor.joblib",
    "env_hvac": "environment_hvac.joblib",
    "env_anomaly": "environment_anomaly.joblib",
    "meta": "model_meta.json",
}


def models_dir() -> Path:
    return get_settings().models_dir


def models_ready() -> bool:
    d = models_dir()
    return all((d / name).exists() for name in MODEL_FILES.values())


def train_all(force: bool = False) -> dict:
    """Train all models from CSV history. Returns training metadata."""
    d = models_dir()
    d.mkdir(parents=True, exist_ok=True)

    if models_ready() and not force:
        logger.info("ML models already exist — skipping training")
        return load_meta()

    logger.info("Training ML models from sensor history…")
    ergo_df = load_csv("ergonomics.csv")
    env_df = load_csv("environment.csv")

    machines = sorted(set(ergo_df["Machine ID"].unique()) | set(env_df["Machine ID"].unique()))
    machine_codes = {m: i for i, m in enumerate(machines)}

    X_ergo, y_ergo = build_ergonomics_training_frame(ergo_df, machine_codes)
    X_env, y_env = build_environment_training_frame(env_df, machine_codes)

    ergo_reg = RandomForestRegressor(
        n_estimators=120, max_depth=12, random_state=42, n_jobs=-1,
    )
    ergo_reg.fit(X_ergo, y_ergo["regression"])

    ergo_damp = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1,
    )
    ergo_damp.fit(X_ergo, y_ergo["damping"])

    ergo_shock = RandomForestClassifier(
        n_estimators=100, max_depth=8, random_state=42, n_jobs=-1,
    )
    ergo_shock.fit(X_ergo, y_ergo["shock"])

    ergo_anomaly = IsolationForest(contamination=0.04, random_state=42, n_jobs=-1)
    ergo_anomaly.fit(X_ergo)

    env_reg = RandomForestRegressor(
        n_estimators=120, max_depth=12, random_state=42, n_jobs=-1,
    )
    env_reg.fit(X_env, y_env["regression"])

    env_hvac = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1,
    )
    env_hvac.fit(X_env, y_env["hvac"])

    env_anomaly = IsolationForest(contamination=0.04, random_state=42, n_jobs=-1)
    env_anomaly.fit(X_env)

    joblib.dump(ergo_reg, d / MODEL_FILES["ergo_reg"])
    joblib.dump(ergo_damp, d / MODEL_FILES["ergo_damp"])
    joblib.dump(ergo_shock, d / MODEL_FILES["ergo_shock"])
    joblib.dump(ergo_anomaly, d / MODEL_FILES["ergo_anomaly"])
    joblib.dump(env_reg, d / MODEL_FILES["env_reg"])
    joblib.dump(env_hvac, d / MODEL_FILES["env_hvac"])
    joblib.dump(env_anomaly, d / MODEL_FILES["env_anomaly"])

    meta = {
        "version": 1,
        "engine": "ml",
        "machine_codes": machine_codes,
        "damping_labels": DAMPING_LABELS,
        "ergonomics_samples": len(X_ergo),
        "environment_samples": len(X_env),
        "shock_positive_rate": float(np.mean(y_ergo["shock"])),
        "hvac_positive_rate": float(np.mean(y_env["hvac"])),
        "models": list(MODEL_FILES.keys()),
    }
    (d / MODEL_FILES["meta"]).write_text(json.dumps(meta, indent=2))
    logger.info(
        "ML training complete — %d ergonomics, %d environment samples",
        len(X_ergo), len(X_env),
    )
    return meta


def load_meta() -> dict:
    path = models_dir() / MODEL_FILES["meta"]
    if not path.exists():
        return {}
    return json.loads(path.read_text())
