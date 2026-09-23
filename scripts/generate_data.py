#!/usr/bin/env python3
"""Generate synthetic ergonomics & environment datasets (deterministic, seed=42)."""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
SAMPLES_PER_MACHINE = int(os.environ.get("SAMPLES_PER_MACHINE", "300"))


def generate_machines():
    machine_types = ["Excavator", "Loader", "Bulldozer", "Grader", "Dump Truck", "Compactor"]
    prefix_map = {
        "Excavator": "EXC", "Loader": "LDR", "Bulldozer": "BDZ",
        "Grader": "GRD", "Dump Truck": "DMP", "Compactor": "CMP",
    }
    machines = []
    for i in range(1, 9):
        mtype = machine_types[(i - 1) % len(machine_types)]
        mid = f"{prefix_map[mtype]}{i:03d}"
        machines.append({
            "Machine ID": mid,
            "Type": mtype,
            "Model": f"CAT {random.choice(['320', '950', 'D6', '140', '735', 'CS74'])}",
            "Has Active Suspension": random.choice(["Yes", "Yes", "No"]),
            "Status": random.choices(["Active", "Idle", "Maintenance"], weights=[7, 2, 1])[0],
        })
    _write_csv("machines.csv", machines)
    return machines


def generate_operators():
    first_names = ["Raj", "Amit", "Priya", "Sara", "John", "Wei", "Fatima", "Carlos", "Elena", "Tom"]
    last_names = ["Kumar", "Singh", "Patel", "Lee", "Smith", "Chen", "Khan", "Diaz", "Rossi", "Brown"]
    weight_classes = ["light", "medium", "heavy"]
    fatigue_risks = ["low", "medium", "high"]
    operators = []
    for i in range(1, 11):
        operators.append({
            "Operator ID": f"OP{1000 + i}",
            "Name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "Shift": random.choice(["Day", "Night"]),
            "Weight Class": random.choice(weight_classes),
            "Typical Fatigue Risk": random.choice(fatigue_risks),
        })
    _write_csv("operators.csv", operators)
    return operators


def generate_ergonomics(machines_list, operators_list):
    damping_levels = ["soft", "medium", "firm"]
    rows = []
    shift_start = TODAY.replace(hour=6, minute=0, second=0, microsecond=0)

    for mach in machines_list:
        if mach["Has Active Suspension"] == "No":
            continue
        op = random.choice(operators_list)
        damping_idx = 1
        wbv_index = round(random.uniform(5, 15), 1)
        pressure_x = round(random.uniform(0.45, 0.55), 3)
        pressure_y = round(random.uniform(0.45, 0.55), 3)

        for i in range(SAMPLES_PER_MACHINE):
            ts = shift_start + timedelta(seconds=i)
            chassis_x = round(random.uniform(-0.15, 0.15), 3)
            chassis_y = round(random.uniform(-0.12, 0.12), 3)
            chassis_z = round(random.uniform(0.08, 0.35), 3)
            if random.random() < 0.04:
                chassis_z = round(random.uniform(0.75, 1.2), 3)

            damp_factor = {0: 0.55, 1: 0.35, 2: 0.2}[damping_idx]
            seat_z = round(chassis_z * damp_factor + random.uniform(0, 0.05), 3)
            seat_x = round(chassis_x * damp_factor, 3)
            seat_y = round(chassis_y * damp_factor, 3)

            if chassis_z > 0.7:
                damping_idx = min(2, damping_idx + 1)
            elif chassis_z < 0.2 and damping_idx > 0:
                damping_idx = max(0, damping_idx - 1)

            wbv_index = round(wbv_index + abs(chassis_z) * 0.15 + abs(seat_z) * 0.1, 1)
            pressure_x = round(max(0.3, min(0.7, pressure_x + random.uniform(-0.02, 0.02))), 3)
            pressure_y = round(max(0.3, min(0.7, pressure_y + random.uniform(-0.02, 0.02))), 3)
            air_pressure = round(random.uniform(180, 240) - damping_idx * 15, 1)

            rows.append({
                "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Operator ID": op["Operator ID"],
                "Machine ID": mach["Machine ID"],
                "Chassis Accel X": chassis_x,
                "Chassis Accel Y": chassis_y,
                "Chassis Accel Z": chassis_z,
                "Seat Accel X": seat_x,
                "Seat Accel Y": seat_y,
                "Seat Accel Z": seat_z,
                "Seat Pressure Center X": pressure_x,
                "Seat Pressure Center Y": pressure_y,
                "Seat Air Pressure (kPa)": air_pressure,
                "Damping Setting": damping_levels[damping_idx],
                "WBV Exposure Index": wbv_index,
            })

    rows.sort(key=lambda r: r["Timestamp"])
    _write_csv("ergonomics.csv", rows)
    return rows


def generate_environment(machines_list, operators_list):
    rows = []
    shift_start = TODAY.replace(hour=6, minute=0, second=0, microsecond=0)

    for mach in machines_list:
        op = random.choice(operators_list)
        co2 = random.randint(650, 850)
        facial_temp = round(random.uniform(36.2, 36.8), 1)
        cab_temp = round(random.uniform(22, 26), 1)
        humidity = random.randint(45, 60)
        pm25 = round(random.uniform(8, 25), 1)
        hvac_override = False
        fresh_air_flush = False

        for i in range(SAMPLES_PER_MACHINE):
            ts = shift_start + timedelta(seconds=i)
            co2 += random.randint(-8, 12)
            co2 = max(500, min(1400, co2))
            facial_temp = round(facial_temp + random.uniform(-0.05, 0.08), 1)
            cab_temp = round(cab_temp + random.uniform(-0.1, 0.15), 1)
            humidity = max(35, min(75, humidity + random.randint(-2, 2)))
            pm25 = round(max(5, pm25 + random.uniform(-1, 2)), 1)

            if co2 > 1000 or facial_temp > 37.2:
                hvac_override = True
                fresh_air_flush = True
                co2 = max(600, co2 - random.randint(30, 80))
                facial_temp = round(facial_temp - random.uniform(0.1, 0.3), 1)
            elif co2 < 850 and facial_temp < 36.9:
                hvac_override = False
                fresh_air_flush = False

            rows.append({
                "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Operator ID": op["Operator ID"],
                "Machine ID": mach["Machine ID"],
                "Cab CO2 (ppm)": co2,
                "Cab PM2.5 (µg/m³)": pm25,
                "Cab Temp (C)": cab_temp,
                "Cab Humidity (%)": humidity,
                "Operator Facial Temp (C)": facial_temp,
                "HVAC Override Active": "Yes" if hvac_override else "No",
                "Fresh Air Flush Active": "Yes" if fresh_air_flush else "No",
            })

    rows.sort(key=lambda r: r["Timestamp"])
    _write_csv("environment.csv", rows)
    return rows


def _write_csv(filename, rows):
    if not rows:
        return
    path = os.path.join(OUT, filename)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    machines = generate_machines()
    operators = generate_operators()
    ergonomics = generate_ergonomics(machines, operators)
    environment = generate_environment(machines, operators)
    print(f"machines: {len(machines)}")
    print(f"operators: {len(operators)}")
    print(f"ergonomics: {len(ergonomics)}")
    print(f"environment: {len(environment)}")


if __name__ == "__main__":
    main()
