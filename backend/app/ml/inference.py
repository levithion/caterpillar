"""Load trained models and run real-time inference."""

import logging
from collections import deque
from datetime import datetime, timezone

import joblib
import numpy as np

from app.config import get_settings
from app.data import load_csv
from app.ml.features import (
    DAMPING_LABELS,
    DAMPING_MAP,
    environment_history_to_row,
    ergonomics_history_to_row,
    fatigue_feature_row,
    telemetry_anomaly_features,
    TELEMETRY_ANOMALY_FEATURES,
)
from app.ml.train import MODEL_FILES, load_meta, models_dir, models_ready
from app.services import environment as env_svc

logger = logging.getLogger(__name__)

_model_bundle: dict | None = None


def _load_models() -> dict:
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    d = models_dir()
    _model_bundle = {
        "ergo_reg": joblib.load(d / MODEL_FILES["ergo_reg"]),
        "ergo_damp": joblib.load(d / MODEL_FILES["ergo_damp"]),
        "ergo_shock": joblib.load(d / MODEL_FILES["ergo_shock"]),
        "ergo_anomaly": joblib.load(d / MODEL_FILES["ergo_anomaly"]),
        "env_reg": joblib.load(d / MODEL_FILES["env_reg"]),
        "env_hvac": joblib.load(d / MODEL_FILES["env_hvac"]),
        "env_anomaly": joblib.load(d / MODEL_FILES["env_anomaly"]),
        "fatigue_clf": joblib.load(d / MODEL_FILES["fatigue_clf"]),
        "telemetry_anomaly": joblib.load(d / MODEL_FILES["telemetry_anomaly"]),
        "meta": load_meta(),
    }
    return _model_bundle


def get_ml_status() -> dict:
    meta = load_meta()
    return {
        "ready": models_ready(),
        "engine": "ml" if models_ready() else "unavailable",
        **meta,
    }


# ---------------------------------------------------------------------------
# Member 2: learned fatigue alerts + telemetry-wide anomaly flags
# ---------------------------------------------------------------------------
FATIGUE_CLASSES_CAPS = {"normal", "caution", "critical"}


def predict_fatigue_alerts(rows: list[dict]) -> list[dict]:
    """Model-based alert prediction for fatigue rows:
    each row needs Machine ID, Eye Closure Duration (s), Blink Rate (per min),
    Head Pitch (deg), Timestamp."""
    if not models_ready():
        raise RuntimeError("ML models not trained — run scripts/train_models.py")

    bundle = _load_models()
    meta = bundle["meta"]
    machine_codes: dict[str, int] = meta["machine_codes"]

    import pandas as pd

    frame = pd.DataFrame(rows)
    ts = pd.to_datetime(frame["Timestamp"])
    X = np.array(
        [
            fatigue_feature_row(
                machine_codes.get(machine, 0),
                float(eye),
                float(blink),
                float(pitch),
                int(hour),
            )
            for machine, eye, blink, pitch, hour in zip(
                frame["Machine ID"],
                frame["Eye Closure Duration (s)"],
                frame["Blink Rate (per min)"],
                frame["Head Pitch (deg)"],
                ts.dt.hour,
            )
        ],
        dtype=np.float32,
    )
    clf = bundle["fatigue_clf"]
    labels = clf.predict(X)
    prob_matrix = clf.predict_proba(X)
    classes = list(clf.classes_)
    results = []
    for i, label in enumerate(labels):
        idx = classes.index(label)
        results.append({
            "alert_level": label,
            "probability": round(float(prob_matrix[i][idx]), 3),
        })
    return results


def telemetry_model_anomalies(limit: int = 20) -> list[dict]:
    """Learned multivariate anomaly flags over telemetry, per-machine norm."""
    if not models_ready():
        raise RuntimeError("ML models not trained — run scripts/train_models.py")

    bundle = _load_models()
    model = bundle["telemetry_anomaly"]

    df = load_csv("telemetry.csv")
    normalized = telemetry_anomaly_features(df)
    scores = -model.decision_function(normalized)
    flagged_mask = np.array(model.predict(normalized) == -1)

    flagged_norm = normalized[flagged_mask]
    flagged_raw = df[flagged_mask]
    flagged_scores = scores[flagged_mask]
    rows: list[dict] = []
    for pos, (_, raw) in enumerate(flagged_raw.iterrows()):
        norm_row = flagged_norm.iloc[pos]
        drivers = sorted(
            TELEMETRY_ANOMALY_FEATURES,
            key=lambda c: abs(float(norm_row[c])),
            reverse=True,
        )[:3]
        rows.append({
            "timestamp": raw["Timestamp"],
            "machine_id": raw["Machine ID"],
            "operator_id": raw["Operator ID"],
            "anomaly_score": round(float(flagged_scores[pos]), 3),
            "severity": "high",
            "top_drivers": drivers,
        })
    rows.sort(key=lambda r: r["anomaly_score"], reverse=True)
    return rows[:limit]


def fatigue_rule_model_compare(limit: int = 15) -> list[dict]:
    """Rule vs learned model on the most recent fatigue readings.
    Disagreements first — that's the demo moment."""
    if not models_ready():
        raise RuntimeError("ML models not trained — run scripts/train_models.py")

    df = load_csv("fatigue_events.csv").sort_values("Timestamp", ascending=False).head(limit)
    rows = df.to_dict(orient="records")
    predictions = predict_fatigue_alerts(rows)

    comparisons = []
    for row, prediction in zip(rows, predictions):
        rule = str(row["Alert Level"])
        model_label = prediction["alert_level"]
        comparisons.append({
            "timestamp": row["Timestamp"],
            "machine_id": row["Machine ID"],
            "operator_id": row["Operator ID"],
            "fatigue_score": int(row["Fatigue Score"]),
            "eye_closure_seconds": float(row["Eye Closure Duration (s)"]),
            "rule_alert_level": rule,
            "model_alert_level": model_label,
            "model_probability": prediction["probability"],
            "agreement": rule.lower() == model_label.lower(),
        })
    comparisons.sort(key=lambda c: (c["agreement"], -c["fatigue_score"]))
    return comparisons


class MLLiveEngine:
    """Per-machine stateful ML inference for real-time sensor streaming."""

    def __init__(self, machine_id: str, operator_id: str, has_ergonomics: bool):
        if not models_ready():
            raise RuntimeError("ML models not trained — run scripts/train_models.py or restart backend")

        self.machine_id = machine_id
        self.operator_id = operator_id
        self.has_ergonomics = has_ergonomics
        self.models = _load_models()
        self.machine_code = self.models["meta"]["machine_codes"].get(machine_id, 0)

        self.ergo_history: deque[dict] = deque(maxlen=10)
        self.env_history: deque[dict] = deque(maxlen=10)
        self._seed_history()

    def _seed_history(self) -> None:
        try:
            if self.has_ergonomics:
                df = load_csv("ergonomics.csv")
                df = df[df["Machine ID"] == self.machine_id].tail(10)
                for _, row in df.iterrows():
                    self.ergo_history.append({
                        "chassis_x": float(row["Chassis Accel X"]),
                        "chassis_y": float(row["Chassis Accel Y"]),
                        "chassis_z": float(row["Chassis Accel Z"]),
                        "seat_x": float(row["Seat Accel X"]),
                        "seat_y": float(row["Seat Accel Y"]),
                        "seat_z": float(row["Seat Accel Z"]),
                        "wbv": float(row["WBV Exposure Index"]),
                        "damping": DAMPING_MAP.get(row["Damping Setting"], 1),
                    })

            env_df = load_csv("environment.csv")
            env_df = env_df[env_df["Machine ID"] == self.machine_id].tail(10)
            for _, row in env_df.iterrows():
                self.env_history.append({
                    "co2": float(row["Cab CO2 (ppm)"]),
                    "facial_temp": float(row["Operator Facial Temp (C)"]),
                    "cab_temp": float(row["Cab Temp (C)"]),
                    "humidity": float(row["Cab Humidity (%)"]),
                    "pm25": float(row["Cab PM2.5 (µg/m³)"]),
                })
        except FileNotFoundError:
            logger.warning("Could not seed ML history for %s", self.machine_id)

        if not self.ergo_history and self.has_ergonomics:
            self.ergo_history.append({
                "chassis_x": 0.0, "chassis_y": 0.0, "chassis_z": 0.2,
                "seat_x": 0.0, "seat_y": 0.0, "seat_z": 0.08,
                "wbv": 10.0, "damping": 1,
            })
        if not self.env_history:
            self.env_history.append({
                "co2": 750.0, "facial_temp": 36.5,
                "cab_temp": 24.0, "humidity": 50.0, "pm25": 15.0,
            })

    def _tick_ergonomics_ml(self, ts: datetime) -> dict:
        settings = get_settings()
        X = ergonomics_history_to_row(list(self.ergo_history), self.machine_code).reshape(1, -1)

        reg = self.models["ergo_reg"].predict(X)[0]
        damp_idx = int(self.models["ergo_damp"].predict(X)[0])
        damp_idx = max(0, min(2, damp_idx))
        shock_proba = float(self.models["ergo_shock"].predict_proba(X)[0][1])
        shock_detected = shock_proba >= 0.5
        anomaly_score = float(-self.models["ergo_anomaly"].decision_function(X)[0])

        chassis_x, chassis_y, chassis_z = float(reg[0]), float(reg[1]), float(reg[2])
        seat_x, seat_y, seat_z = float(reg[3]), float(reg[4]), float(reg[5])
        wbv = max(0.0, float(reg[6]))
        pressure_x, pressure_y = float(reg[7]), float(reg[8])
        air_pressure = float(reg[9])

        # Also flag shock if predicted acceleration exceeds threshold
        if chassis_z > settings.chassis_shock_threshold:
            shock_detected = True

        self.ergo_history.append({
            "chassis_x": chassis_x, "chassis_y": chassis_y, "chassis_z": chassis_z,
            "seat_x": seat_x, "seat_y": seat_y, "seat_z": seat_z,
            "wbv": wbv, "damping": damp_idx,
        })

        damping_label = DAMPING_LABELS[damp_idx]
        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": self.operator_id,
            "Machine ID": self.machine_id,
            "Chassis Accel X": round(chassis_x, 3),
            "Chassis Accel Y": round(chassis_y, 3),
            "Chassis Accel Z": round(chassis_z, 3),
            "Seat Accel X": round(seat_x, 3),
            "Seat Accel Y": round(seat_y, 3),
            "Seat Accel Z": round(seat_z, 3),
            "Seat Pressure Center X": round(pressure_x, 3),
            "Seat Pressure Center Y": round(pressure_y, 3),
            "Seat Air Pressure (kPa)": round(air_pressure, 1),
            "Damping Setting": damping_label,
            "WBV Exposure Index": round(wbv, 1),
        }
        current = {
            "timestamp": reading["Timestamp"],
            "operator_id": self.operator_id,
            "machine_id": self.machine_id,
            "chassis_accel_x": chassis_x,
            "chassis_accel_y": chassis_y,
            "chassis_accel_z": chassis_z,
            "seat_accel_x": seat_x,
            "seat_accel_y": seat_y,
            "seat_accel_z": seat_z,
            "seat_pressure_center_x": pressure_x,
            "seat_pressure_center_y": pressure_y,
            "seat_air_pressure_kpa": air_pressure,
            "damping_setting": damping_label,
            "wbv_exposure_index": wbv,
            "shock_detected": shock_detected,
            "shock_probability": round(shock_proba, 3),
            "anomaly_score": round(anomaly_score, 3),
            "prediction_source": "ml",
            "recommendation": (
                f"ML shock risk {shock_proba:.0%} — damping predicted {damping_label}"
                if shock_detected
                else f"ML prediction: vibration normal (confidence {1 - shock_proba:.0%})"
            ),
        }
        return {"current": current, "reading": reading}

    def _tick_environment_ml(self, ts: datetime) -> dict:
        import pandas as pd

        X = environment_history_to_row(list(self.env_history), self.machine_code).reshape(1, -1)

        reg = self.models["env_reg"].predict(X)[0]
        hvac_proba = float(self.models["env_hvac"].predict_proba(X)[0][1])
        hvac_override = hvac_proba >= 0.5
        anomaly_score = float(-self.models["env_anomaly"].decision_function(X)[0])

        co2 = max(400.0, float(reg[0]))
        facial_temp = float(reg[1])
        cab_temp = float(reg[2])
        humidity = max(20.0, min(90.0, float(reg[3])))
        pm25 = max(1.0, float(reg[4]))
        fresh_air = hvac_override

        self.env_history.append({
            "co2": co2, "facial_temp": facial_temp, "cab_temp": cab_temp,
            "humidity": humidity, "pm25": pm25,
        })

        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": self.operator_id,
            "Machine ID": self.machine_id,
            "Cab CO2 (ppm)": int(co2),
            "Cab PM2.5 (µg/m³)": round(pm25, 1),
            "Cab Temp (C)": round(cab_temp, 1),
            "Cab Humidity (%)": int(humidity),
            "Operator Facial Temp (C)": round(facial_temp, 1),
            "HVAC Override Active": "Yes" if hvac_override else "No",
            "Fresh Air Flush Active": "Yes" if fresh_air else "No",
        }
        row = pd.Series(reading)
        warnings = env_svc._warnings(row)
        if hvac_proba > 0.3 and not warnings:
            warnings.append(f"ML elevated HVAC risk ({hvac_proba:.0%}) — monitoring cabin conditions")

        current = {
            "timestamp": reading["Timestamp"],
            "operator_id": self.operator_id,
            "machine_id": self.machine_id,
            "co2_ppm": co2,
            "pm25_ug_m3": pm25,
            "cab_temp_c": cab_temp,
            "cab_humidity_pct": humidity,
            "facial_temp_c": facial_temp,
            "hvac_override_active": hvac_override,
            "fresh_air_flush_active": fresh_air,
            "hvac_probability": round(hvac_proba, 3),
            "anomaly_score": round(anomaly_score, 3),
            "prediction_source": "ml",
            "warnings": warnings,
        }
        return {"current": current, "reading": reading}

    def tick(self) -> dict:
        ts = datetime.now(timezone.utc)
        payload: dict = {
            "timestamp": ts.isoformat(),
            "machine_id": self.machine_id,
            "operator_id": self.operator_id,
            "engine": "ml",
        }
        if self.has_ergonomics:
            payload["ergonomics"] = self._tick_ergonomics_ml(ts)
        else:
            payload["ergonomics"] = None
        payload["environment"] = self._tick_environment_ml(ts)
        return payload


_engines: dict[str, MLLiveEngine] = {}


def get_ml_engine(machine_id: str, operator_id: str, has_ergonomics: bool) -> MLLiveEngine:
    if machine_id not in _engines:
        _engines[machine_id] = MLLiveEngine(machine_id, operator_id, has_ergonomics)
    return _engines[machine_id]


def reset_ml_engine(machine_id: str) -> None:
    _engines.pop(machine_id, None)
