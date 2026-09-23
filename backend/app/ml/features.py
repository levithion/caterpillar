"""Feature engineering for time-series ML models."""

import numpy as np
import pandas as pd

LAG_STEPS = 5
DAMPING_MAP = {"soft": 0, "medium": 1, "firm": 2}
DAMPING_LABELS = ["soft", "medium", "firm"]


def ergonomics_history_to_row(history: list[dict], machine_code: int) -> np.ndarray:
    """Build feature vector from last LAG_STEPS ergonomics readings."""
    rows = []
    for h in history[-LAG_STEPS:]:
        rows.append([
            machine_code,
            h["chassis_z"],
            h["seat_z"],
            h["wbv"],
            h["damping"],
            h.get("chassis_x", 0.0),
            h.get("chassis_y", 0.0),
        ])
    while len(rows) < LAG_STEPS:
        rows.insert(0, rows[0] if rows else [machine_code, 0.2, 0.1, 10.0, 1, 0.0, 0.0])
    flat = [v for row in rows for v in row]
    return np.array(flat, dtype=np.float32)


def environment_history_to_row(history: list[dict], machine_code: int) -> np.ndarray:
    rows = []
    for h in history[-LAG_STEPS:]:
        rows.append([
            machine_code,
            h["co2"],
            h["facial_temp"],
            h["cab_temp"],
            h["humidity"],
            h["pm25"],
        ])
    while len(rows) < LAG_STEPS:
        rows.insert(0, rows[0] if rows else [machine_code, 750.0, 36.5, 24.0, 50.0, 15.0])
    flat = [v for row in rows for v in row]
    return np.array(flat, dtype=np.float32)


def build_ergonomics_training_frame(df: pd.DataFrame, machine_codes: dict[str, int]) -> tuple[np.ndarray, dict]:
    """Create supervised learning dataset from ergonomics CSV."""
    X_list, y_reg_list, y_damp_list, y_shock_list = [], [], [], []

    for machine_id, group in df.groupby("Machine ID"):
        group = group.sort_values("Timestamp").reset_index(drop=True)
        code = machine_codes[machine_id]
        history: list[dict] = []

        for _, row in group.iterrows():
            chassis_z = float(row["Chassis Accel Z"])
            entry = {
                "chassis_x": float(row["Chassis Accel X"]),
                "chassis_y": float(row["Chassis Accel Y"]),
                "chassis_z": chassis_z,
                "seat_x": float(row["Seat Accel X"]),
                "seat_y": float(row["Seat Accel Y"]),
                "seat_z": float(row["Seat Accel Z"]),
                "wbv": float(row["WBV Exposure Index"]),
                "damping": DAMPING_MAP.get(row["Damping Setting"], 1),
                "pressure_x": float(row["Seat Pressure Center X"]),
                "pressure_y": float(row["Seat Pressure Center Y"]),
                "air_pressure": float(row["Seat Air Pressure (kPa)"]),
            }

            if len(history) >= LAG_STEPS:
                X_list.append(ergonomics_history_to_row(history, code))
                y_reg_list.append([
                    entry["chassis_x"], entry["chassis_y"], entry["chassis_z"],
                    entry["seat_x"], entry["seat_y"], entry["seat_z"],
                    entry["wbv"], entry["pressure_x"], entry["pressure_y"], entry["air_pressure"],
                ])
                y_damp_list.append(entry["damping"])
                y_shock_list.append(1 if chassis_z > 0.7 else 0)

            history.append(entry)

    return (
        np.array(X_list, dtype=np.float32),
        {
            "regression": np.array(y_reg_list, dtype=np.float32),
            "damping": np.array(y_damp_list, dtype=np.int32),
            "shock": np.array(y_shock_list, dtype=np.int32),
        },
    )


def build_environment_training_frame(df: pd.DataFrame, machine_codes: dict[str, int]) -> tuple[np.ndarray, dict]:
    X_list, y_reg_list, y_hvac_list = [], [], []

    for machine_id, group in df.groupby("Machine ID"):
        group = group.sort_values("Timestamp").reset_index(drop=True)
        code = machine_codes[machine_id]
        history: list[dict] = []

        for _, row in group.iterrows():
            entry = {
                "co2": float(row["Cab CO2 (ppm)"]),
                "facial_temp": float(row["Operator Facial Temp (C)"]),
                "cab_temp": float(row["Cab Temp (C)"]),
                "humidity": float(row["Cab Humidity (%)"]),
                "pm25": float(row["Cab PM2.5 (µg/m³)"]),
            }
            hvac = 1 if row["HVAC Override Active"] == "Yes" else 0

            if len(history) >= LAG_STEPS:
                X_list.append(environment_history_to_row(history, code))
                y_reg_list.append([
                    entry["co2"], entry["facial_temp"], entry["cab_temp"],
                    entry["humidity"], entry["pm25"],
                ])
                y_hvac_list.append(hvac)

            history.append(entry)

    return (
        np.array(X_list, dtype=np.float32),
        {
            "regression": np.array(y_reg_list, dtype=np.float32),
            "hvac": np.array(y_hvac_list, dtype=np.int32),
        },
    )


def build_fatigue_training_frame(
    df: pd.DataFrame, machine_codes: dict[str, int]
) -> tuple[np.ndarray, list[str]]:
    """Supervised fatigue-alert learning from the IR-camera simulation feed.

    Feature row: [machine_code, eye_closure, blink_rate, head_pitch, hour].
    Label: the Alert Level already recorded on the row (rule-labelled, but the
    model learns the *composition* of signals that makes an alert, and can
    disagree with the flat formula at the boundaries)."""
    X_list, y_list = [], []
    for _, row in df.iterrows():
        machine = row["Machine ID"]
        if machine not in machine_codes:
            continue
        ts = pd.to_datetime(row["Timestamp"])
        X_list.append([
            machine_codes[machine],
            float(row["Eye Closure Duration (s)"]),
            float(row["Blink Rate (per min)"]),
            float(row["Head Pitch (deg)"]),
            ts.hour,
        ])
        y_list.append(str(row["Alert Level"]))
    return np.array(X_list, dtype=np.float32), y_list


def fatigue_feature_row(
    machine_code: int, eye_closure: float, blink_rate: float, head_pitch: float, hour: int
) -> list[float]:
    """Single fatigue inference feature vector (order matches training frame)."""
    return [machine_code, eye_closure, blink_rate, head_pitch, hour]


TELEMETRY_ANOMALY_FEATURES = [
    "Engine RPM", "Speed (km/h)", "Hydraulic Pressure (bar)",
    "Load Cycles", "Idling Time (min)", "Fuel Used (L)", "Slippage Events",
]


def telemetry_anomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    """Per-machine z-normalized telemetry so one IsolationForest can learn
    each machine's own norm, mirroring the ergo/env anomaly inputs."""
    normalized = df.copy()
    for column in TELEMETRY_ANOMALY_FEATURES:
        if column not in normalized.columns:
            continue
        grouped = normalized.groupby("Machine ID")[column]
        mean = grouped.transform("mean")
        std = grouped.transform("std").replace(0, 1)
        normalized[column] = (normalized[column] - mean) / std
    return normalized[TELEMETRY_ANOMALY_FEATURES]
