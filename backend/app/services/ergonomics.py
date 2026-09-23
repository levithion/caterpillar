import pandas as pd

from app.config import get_settings
from app.data import load_csv
from app.utils import records


def get_ergonomics_df(machine_id: str | None = None, operator_id: str | None = None) -> pd.DataFrame:
    df = load_csv("ergonomics.csv")
    if machine_id:
        df = df[df["Machine ID"] == machine_id]
    if operator_id:
        df = df[df["Operator ID"] == operator_id]
    return df


def list_machine_ids() -> list[str]:
    return load_csv("ergonomics.csv")["Machine ID"].unique().tolist()


def current_state(df: pd.DataFrame) -> dict | None:
    if df.empty:
        return None
    settings = get_settings()
    latest = df.iloc[-1]
    chassis_z = float(latest["Chassis Accel Z"])
    shock_detected = chassis_z > settings.chassis_shock_threshold
    return {
        "timestamp": latest["Timestamp"],
        "operator_id": latest["Operator ID"],
        "machine_id": latest["Machine ID"],
        "chassis_accel_x": float(latest["Chassis Accel X"]),
        "chassis_accel_y": float(latest["Chassis Accel Y"]),
        "chassis_accel_z": chassis_z,
        "seat_accel_x": float(latest["Seat Accel X"]),
        "seat_accel_y": float(latest["Seat Accel Y"]),
        "seat_accel_z": float(latest["Seat Accel Z"]),
        "seat_pressure_center_x": float(latest["Seat Pressure Center X"]),
        "seat_pressure_center_y": float(latest["Seat Pressure Center Y"]),
        "seat_air_pressure_kpa": float(latest["Seat Air Pressure (kPa)"]),
        "damping_setting": latest["Damping Setting"],
        "wbv_exposure_index": float(latest["WBV Exposure Index"]),
        "shock_detected": shock_detected,
        "recommendation": (
            "Chassis shock detected — damping stepped to firm"
            if shock_detected
            else "Vibration within normal range"
        ),
    }


def build_response(
    machine_id: str | None,
    operator_id: str | None,
    limit: int,
) -> dict:
    df = get_ergonomics_df(machine_id, operator_id)
    return {
        "current": current_state(df),
        "series": records(df.tail(limit)),
    }
