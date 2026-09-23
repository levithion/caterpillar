"""Replay historical sensor rows in real time + ML scoring on each tick."""

from datetime import datetime, timezone

import pandas as pd

from app.config import get_settings
from app.data import load_csv
from app.ml.features import (
    DAMPING_MAP,
    environment_history_to_row,
    ergonomics_history_to_row,
)
from app.ml.inference import _load_models
from app.ml.train import models_ready
from app.services import environment as env_svc


class ReplayMLEngine:
    """
    Advances through real CSV time-series each second so values visibly change,
    while ML classifiers score shock/HVAC risk and anomaly on every reading.
    """

    def __init__(self, machine_id: str, operator_id: str, has_ergonomics: bool):
        if not models_ready():
            raise RuntimeError("ML models not trained")

        self.machine_id = machine_id
        self.operator_id = operator_id
        self.has_ergonomics = has_ergonomics
        self.models = _load_models()
        self.machine_code = self.models["meta"]["machine_codes"].get(machine_id, 0)
        self.idx = 0

        self.ergo_rows: list[pd.Series] = []
        self.env_rows: list[pd.Series] = []
        self._load_rows()

        self.ergo_hist: list[dict] = []
        self.env_hist: list[dict] = []

    def _load_rows(self) -> None:
        env_df = load_csv("environment.csv")
        env_df = env_df[env_df["Machine ID"] == self.machine_id].sort_values("Timestamp")
        self.env_rows = [row for _, row in env_df.iterrows()]

        if self.has_ergonomics:
            ergo_df = load_csv("ergonomics.csv")
            ergo_df = ergo_df[ergo_df["Machine ID"] == self.machine_id].sort_values("Timestamp")
            self.ergo_rows = [row for _, row in ergo_df.iterrows()]

        if not self.env_rows:
            raise ValueError(f"No environment data for {self.machine_id}")

    def _ml_ergo_scores(self, history: list[dict]) -> dict:
        if len(history) < 1:
            return {"shock_probability": 0.0, "anomaly_score": 0.0}
        X = ergonomics_history_to_row(history, self.machine_code).reshape(1, -1)
        shock_proba = float(self.models["ergo_shock"].predict_proba(X)[0][1])
        anomaly = float(-self.models["ergo_anomaly"].decision_function(X)[0])
        return {"shock_probability": shock_proba, "anomaly_score": anomaly}

    def _ml_env_scores(self, history: list[dict]) -> dict:
        if len(history) < 1:
            return {"hvac_probability": 0.0, "anomaly_score": 0.0}
        X = environment_history_to_row(history, self.machine_code).reshape(1, -1)
        hvac_proba = float(self.models["env_hvac"].predict_proba(X)[0][1])
        anomaly = float(-self.models["env_anomaly"].decision_function(X)[0])
        return {"hvac_probability": hvac_proba, "anomaly_score": anomaly}

    def _tick_ergonomics(self, ts: datetime, row: pd.Series) -> dict:
        settings = get_settings()
        chassis_z = float(row["Chassis Accel Z"])
        shock_detected = chassis_z > settings.chassis_shock_threshold

        hist_entry = {
            "chassis_x": float(row["Chassis Accel X"]),
            "chassis_y": float(row["Chassis Accel Y"]),
            "chassis_z": chassis_z,
            "seat_x": float(row["Seat Accel X"]),
            "seat_y": float(row["Seat Accel Y"]),
            "seat_z": float(row["Seat Accel Z"]),
            "wbv": float(row["WBV Exposure Index"]),
            "damping": DAMPING_MAP.get(row["Damping Setting"], 1),
        }
        self.ergo_hist.append(hist_entry)
        if len(self.ergo_hist) > 10:
            self.ergo_hist.pop(0)

        ml = self._ml_ergo_scores(self.ergo_hist)
        if ml["shock_probability"] >= 0.5:
            shock_detected = True

        damping = row["Damping Setting"]
        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": row["Operator ID"],
            "Machine ID": self.machine_id,
            "Chassis Accel X": float(row["Chassis Accel X"]),
            "Chassis Accel Y": float(row["Chassis Accel Y"]),
            "Chassis Accel Z": chassis_z,
            "Seat Accel X": float(row["Seat Accel X"]),
            "Seat Accel Y": float(row["Seat Accel Y"]),
            "Seat Accel Z": float(row["Seat Accel Z"]),
            "Seat Pressure Center X": float(row["Seat Pressure Center X"]),
            "Seat Pressure Center Y": float(row["Seat Pressure Center Y"]),
            "Seat Air Pressure (kPa)": float(row["Seat Air Pressure (kPa)"]),
            "Damping Setting": damping,
            "WBV Exposure Index": float(row["WBV Exposure Index"]),
        }
        current = {
            "timestamp": reading["Timestamp"],
            "operator_id": str(row["Operator ID"]),
            "machine_id": self.machine_id,
            "chassis_accel_x": float(row["Chassis Accel X"]),
            "chassis_accel_y": float(row["Chassis Accel Y"]),
            "chassis_accel_z": chassis_z,
            "seat_accel_x": float(row["Seat Accel X"]),
            "seat_accel_y": float(row["Seat Accel Y"]),
            "seat_accel_z": float(row["Seat Accel Z"]),
            "seat_pressure_center_x": float(row["Seat Pressure Center X"]),
            "seat_pressure_center_y": float(row["Seat Pressure Center Y"]),
            "seat_air_pressure_kpa": float(row["Seat Air Pressure (kPa)"]),
            "damping_setting": damping,
            "wbv_exposure_index": float(row["WBV Exposure Index"]),
            "shock_detected": shock_detected,
            "shock_probability": round(ml["shock_probability"], 3),
            "anomaly_score": round(ml["anomaly_score"], 3),
            "prediction_source": "ml",
            "recommendation": (
                f"ML shock risk {ml['shock_probability']:.0%} — damping {damping}"
                if shock_detected
                else f"ML: vibration normal (risk {ml['shock_probability']:.0%})"
            ),
        }
        return {"current": current, "reading": reading}

    def _tick_environment(self, ts: datetime, row: pd.Series) -> dict:
        hist_entry = {
            "co2": float(row["Cab CO2 (ppm)"]),
            "facial_temp": float(row["Operator Facial Temp (C)"]),
            "cab_temp": float(row["Cab Temp (C)"]),
            "humidity": float(row["Cab Humidity (%)"]),
            "pm25": float(row["Cab PM2.5 (µg/m³)"]),
        }
        self.env_hist.append(hist_entry)
        if len(self.env_hist) > 10:
            self.env_hist.pop(0)

        ml = self._ml_env_scores(self.env_hist)
        hvac_override = row["HVAC Override Active"] == "Yes" or ml["hvac_probability"] >= 0.5
        fresh_air = row["Fresh Air Flush Active"] == "Yes" or hvac_override

        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": row["Operator ID"],
            "Machine ID": self.machine_id,
            "Cab CO2 (ppm)": int(row["Cab CO2 (ppm)"]),
            "Cab PM2.5 (µg/m³)": float(row["Cab PM2.5 (µg/m³)"]),
            "Cab Temp (C)": float(row["Cab Temp (C)"]),
            "Cab Humidity (%)": int(row["Cab Humidity (%)"]),
            "Operator Facial Temp (C)": float(row["Operator Facial Temp (C)"]),
            "HVAC Override Active": "Yes" if hvac_override else "No",
            "Fresh Air Flush Active": "Yes" if fresh_air else "No",
        }
        warnings = env_svc._warnings(pd.Series(reading))
        if ml["hvac_probability"] > 0.35 and not warnings:
            warnings.append(f"ML HVAC risk {ml['hvac_probability']:.0%}")

        current = {
            "timestamp": reading["Timestamp"],
            "operator_id": str(row["Operator ID"]),
            "machine_id": self.machine_id,
            "co2_ppm": float(row["Cab CO2 (ppm)"]),
            "pm25_ug_m3": float(row["Cab PM2.5 (µg/m³)"]),
            "cab_temp_c": float(row["Cab Temp (C)"]),
            "cab_humidity_pct": float(row["Cab Humidity (%)"]),
            "facial_temp_c": float(row["Operator Facial Temp (C)"]),
            "hvac_override_active": hvac_override,
            "fresh_air_flush_active": fresh_air,
            "hvac_probability": round(ml["hvac_probability"], 3),
            "anomaly_score": round(ml["anomaly_score"], 3),
            "prediction_source": "ml",
            "warnings": warnings,
        }
        return {"current": current, "reading": reading}

    def tick(self) -> dict:
        ts = datetime.now(timezone.utc)
        env_row = self.env_rows[self.idx % len(self.env_rows)]

        payload: dict = {
            "timestamp": ts.isoformat(),
            "machine_id": self.machine_id,
            "operator_id": str(env_row["Operator ID"]),
            "engine": "ml",
            "replay_index": self.idx % len(self.env_rows),
        }

        if self.has_ergonomics and self.ergo_rows:
            ergo_row = self.ergo_rows[self.idx % len(self.ergo_rows)]
            payload["ergonomics"] = self._tick_ergonomics(ts, ergo_row)
        else:
            payload["ergonomics"] = None

        payload["environment"] = self._tick_environment(ts, env_row)
        self.idx += 1
        return payload


_replay_engines: dict[str, ReplayMLEngine] = {}


def get_replay_engine(machine_id: str, operator_id: str, has_ergonomics: bool) -> ReplayMLEngine:
    if machine_id not in _replay_engines:
        _replay_engines[machine_id] = ReplayMLEngine(machine_id, operator_id, has_ergonomics)
    return _replay_engines[machine_id]


def reset_replay_engine(machine_id: str) -> None:
    _replay_engines.pop(machine_id, None)
