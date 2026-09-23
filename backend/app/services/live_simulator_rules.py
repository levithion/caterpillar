"""Rule-based fallback engine when ML models are unavailable."""

import random
from datetime import datetime, timezone

from app.config import get_settings
from app.services import environment as env_svc

DAMPING_LEVELS = ["soft", "medium", "firm"]


class MachineLiveSimulator:
    def __init__(self, machine_id: str, operator_id: str, has_ergonomics: bool):
        self.machine_id = machine_id
        self.operator_id = operator_id
        self.has_ergonomics = has_ergonomics
        self.rng = random.Random(sum(ord(c) for c in machine_id))
        self.damping_idx = 1
        self.wbv_index = round(self.rng.uniform(5, 15), 1)
        self.pressure_x = round(self.rng.uniform(0.45, 0.55), 3)
        self.pressure_y = round(self.rng.uniform(0.45, 0.55), 3)
        self.co2 = float(self.rng.randint(650, 850))
        self.facial_temp = round(self.rng.uniform(36.2, 36.8), 1)
        self.cab_temp = round(self.rng.uniform(22, 26), 1)
        self.humidity = float(self.rng.randint(45, 60))
        self.pm25 = round(self.rng.uniform(8, 25), 1)
        self.hvac_override = False
        self.fresh_air_flush = False

    def _tick_ergonomics(self, ts: datetime) -> dict:
        settings = get_settings()
        chassis_x = round(self.rng.uniform(-0.15, 0.15), 3)
        chassis_y = round(self.rng.uniform(-0.12, 0.12), 3)
        chassis_z = round(self.rng.uniform(0.08, 0.35), 3)
        if self.rng.random() < 0.04:
            chassis_z = round(self.rng.uniform(0.75, 1.2), 3)

        damp_factor = {0: 0.55, 1: 0.35, 2: 0.2}[self.damping_idx]
        seat_z = round(chassis_z * damp_factor + self.rng.uniform(0, 0.05), 3)
        seat_x = round(chassis_x * damp_factor, 3)
        seat_y = round(chassis_y * damp_factor, 3)

        if chassis_z > settings.chassis_shock_threshold:
            self.damping_idx = min(2, self.damping_idx + 1)
        elif chassis_z < 0.2 and self.damping_idx > 0:
            self.damping_idx = max(0, self.damping_idx - 1)

        self.wbv_index = round(self.wbv_index + abs(chassis_z) * 0.15 + abs(seat_z) * 0.1, 1)
        self.pressure_x = round(max(0.3, min(0.7, self.pressure_x + self.rng.uniform(-0.02, 0.02))), 3)
        self.pressure_y = round(max(0.3, min(0.7, self.pressure_y + self.rng.uniform(-0.02, 0.02))), 3)
        air_pressure = round(self.rng.uniform(180, 240) - self.damping_idx * 15, 1)
        shock_detected = chassis_z > settings.chassis_shock_threshold

        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": self.operator_id,
            "Machine ID": self.machine_id,
            "Chassis Accel X": chassis_x,
            "Chassis Accel Y": chassis_y,
            "Chassis Accel Z": chassis_z,
            "Seat Accel X": seat_x,
            "Seat Accel Y": seat_y,
            "Seat Accel Z": seat_z,
            "Seat Pressure Center X": self.pressure_x,
            "Seat Pressure Center Y": self.pressure_y,
            "Seat Air Pressure (kPa)": air_pressure,
            "Damping Setting": DAMPING_LEVELS[self.damping_idx],
            "WBV Exposure Index": self.wbv_index,
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
            "seat_pressure_center_x": self.pressure_x,
            "seat_pressure_center_y": self.pressure_y,
            "seat_air_pressure_kpa": air_pressure,
            "damping_setting": DAMPING_LEVELS[self.damping_idx],
            "wbv_exposure_index": self.wbv_index,
            "shock_detected": shock_detected,
            "prediction_source": "rules",
            "recommendation": (
                "Chassis shock detected — damping stepped to firm"
                if shock_detected
                else "Vibration within normal range"
            ),
        }
        return {"current": current, "reading": reading}

    def _tick_environment(self, ts: datetime) -> dict:
        import pandas as pd

        settings = get_settings()
        self.co2 += self.rng.randint(-8, 12)
        self.co2 = max(500.0, min(1400.0, self.co2))
        self.facial_temp = round(self.facial_temp + self.rng.uniform(-0.05, 0.08), 1)
        self.cab_temp = round(self.cab_temp + self.rng.uniform(-0.1, 0.15), 1)
        self.humidity = max(35.0, min(75.0, self.humidity + self.rng.randint(-2, 2)))
        self.pm25 = round(max(5.0, self.pm25 + self.rng.uniform(-1, 2)), 1)

        if self.co2 > settings.co2_warning_threshold or self.facial_temp > settings.facial_temp_warning_threshold:
            self.hvac_override = True
            self.fresh_air_flush = True
            self.co2 = max(600.0, self.co2 - self.rng.randint(30, 80))
            self.facial_temp = round(self.facial_temp - self.rng.uniform(0.1, 0.3), 1)
        elif self.co2 < 850 and self.facial_temp < 36.9:
            self.hvac_override = False
            self.fresh_air_flush = False

        reading = {
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Operator ID": self.operator_id,
            "Machine ID": self.machine_id,
            "Cab CO2 (ppm)": int(self.co2),
            "Cab PM2.5 (µg/m³)": self.pm25,
            "Cab Temp (C)": self.cab_temp,
            "Cab Humidity (%)": int(self.humidity),
            "Operator Facial Temp (C)": self.facial_temp,
            "HVAC Override Active": "Yes" if self.hvac_override else "No",
            "Fresh Air Flush Active": "Yes" if self.fresh_air_flush else "No",
        }
        row = pd.Series(reading)
        current = {
            "timestamp": reading["Timestamp"],
            "operator_id": self.operator_id,
            "machine_id": self.machine_id,
            "co2_ppm": float(reading["Cab CO2 (ppm)"]),
            "pm25_ug_m3": self.pm25,
            "cab_temp_c": self.cab_temp,
            "cab_humidity_pct": self.humidity,
            "facial_temp_c": self.facial_temp,
            "hvac_override_active": self.hvac_override,
            "fresh_air_flush_active": self.fresh_air_flush,
            "prediction_source": "rules",
            "warnings": env_svc._warnings(row),
        }
        return {"current": current, "reading": reading}

    def tick(self) -> dict:
        ts = datetime.now(timezone.utc)
        payload: dict = {
            "timestamp": ts.isoformat(),
            "machine_id": self.machine_id,
            "operator_id": self.operator_id,
            "engine": "rules",
        }
        payload["ergonomics"] = self._tick_ergonomics(ts) if self.has_ergonomics else None
        payload["environment"] = self._tick_environment(ts)
        return payload
