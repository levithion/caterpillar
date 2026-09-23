import pandas as pd

from app.config import get_settings
from app.data import load_csv, records


def get_environment_df(machine_id: str | None = None, operator_id: str | None = None) -> pd.DataFrame:
    df = load_csv("environment.csv")
    if machine_id:
        df = df[df["Machine ID"] == machine_id]
    if operator_id:
        df = df[df["Operator ID"] == operator_id]
    return df


def list_machine_ids() -> list[str]:
    return load_csv("environment.csv")["Machine ID"].unique().tolist()


def _warnings(row: pd.Series) -> list[str]:
    settings = get_settings()
    warnings: list[str] = []
    co2 = float(row["Cab CO2 (ppm)"])
    facial_temp = float(row["Operator Facial Temp (C)"])
    if co2 > settings.co2_warning_threshold:
        warnings.append(f"Elevated CO₂ ({co2:.0f} ppm) — HVAC override active")
    if facial_temp > settings.facial_temp_warning_threshold:
        warnings.append(f"Elevated facial temperature ({facial_temp:.1f}°C) — hydration/rest recommended")
    if not warnings and row["HVAC Override Active"] == "Yes":
        warnings.append("HVAC recovering cabin conditions — consider a short rest break")
    return warnings


def current_state(df: pd.DataFrame) -> dict | None:
    if df.empty:
        return None
    latest = df.iloc[-1]
    return {
        "timestamp": latest["Timestamp"],
        "operator_id": latest["Operator ID"],
        "machine_id": latest["Machine ID"],
        "co2_ppm": float(latest["Cab CO2 (ppm)"]),
        "pm25_ug_m3": float(latest["Cab PM2.5 (µg/m³)"]),
        "cab_temp_c": float(latest["Cab Temp (C)"]),
        "cab_humidity_pct": float(latest["Cab Humidity (%)"]),
        "facial_temp_c": float(latest["Operator Facial Temp (C)"]),
        "hvac_override_active": latest["HVAC Override Active"] == "Yes",
        "fresh_air_flush_active": latest["Fresh Air Flush Active"] == "Yes",
        "warnings": _warnings(latest),
    }


def build_response(
    machine_id: str | None,
    operator_id: str | None,
    limit: int,
) -> dict:
    df = get_environment_df(machine_id, operator_id)
    return {
        "current": current_state(df),
        "series": records(df.tail(limit)),
    }
