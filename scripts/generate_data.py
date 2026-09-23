import csv
import hashlib
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))
from app.security import hash_password  # noqa: E402

random.seed(42)
# Every seed operator gets this password (hashed, not stored in plaintext) so the
# demo has known login credentials: email or Operator ID + this password. The salt
# is fixed (derived, not random) purely so scripts/generate_data.py stays
# deterministic across reruns like the rest of the dataset.
DEMO_PASSWORD = "Demo@123"
DEMO_SALT = hashlib.sha256(b"smart-operator-assistant-demo-salt").hexdigest()[:32]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# ---------- machines ----------
machine_types = ["Excavator", "Loader", "Bulldozer", "Grader", "Dump Truck", "Compactor"]
machines = []
for i in range(1, 9):
    mtype = machine_types[(i - 1) % len(machine_types)]
    prefix = {"Excavator": "EXC", "Loader": "LDR", "Bulldozer": "BDZ",
              "Grader": "GRD", "Dump Truck": "DMP", "Compactor": "CMP"}[mtype]
    mid = f"{prefix}{i:03d}"
    age = random.randint(1, 8)
    purchase = TODAY - timedelta(days=age * 365)
    last_maint = TODAY - timedelta(days=random.randint(5, 90))
    next_maint = last_maint + timedelta(days=180)
    machines.append({
        "Machine ID": mid,
        "Type": mtype,
        "Model": f"CAT {random.choice(['320', '950', 'D6', '140', '735', 'CS74'])}",
        "Age (yrs)": age,
        "Purchase Date": purchase.date().isoformat(),
        "Last Maintenance Date": last_maint.date().isoformat(),
        "Next Maintenance Due": next_maint.date().isoformat(),
        "Total Engine Hours": round(random.uniform(800, 6000), 1),
        "Status": random.choices(["Active", "Idle", "Maintenance"], weights=[7, 2, 1])[0],
        "Has IR Camera": random.choices(["Yes", "No"], weights=[8, 2])[0],
        "Has Active Suspension": random.choices(["Yes", "No"], weights=[7, 3])[0],
        "Has Thermal Camera": random.choices(["Yes", "No"], weights=[6, 4])[0],
    })

with open(f"{OUT}/machines.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(machines[0].keys()))
    w.writeheader()
    w.writerows(machines)

# ---------- operators ----------
first_names = ["Raj", "Amit", "Priya", "Sara", "John", "Wei", "Fatima", "Carlos", "Elena", "Tom"]
last_names = ["Kumar", "Singh", "Patel", "Lee", "Smith", "Chen", "Khan", "Diaz", "Rossi", "Brown"]
skills = ["Beginner", "Intermediate", "Expert"]
operators = []
weight_classes = ["Light", "Medium", "Heavy"]
demo_country_codes = ["+1", "+44", "+91", "+61", "+27", "+971"]
demo_password_hash, demo_password_salt = hash_password(DEMO_PASSWORD, DEMO_SALT)
for i in range(1, 11):
    join = TODAY - timedelta(days=random.randint(60, 3000))
    license_exp = TODAY + timedelta(days=random.randint(30, 800))
    shift = random.choice(["Day", "Night"])
    # Night shifts carry a higher baseline fatigue risk; used to bias fatigue_events.csv.
    fatigue_risk_weights = [3, 4, 5] if shift == "Night" else [6, 3, 1]
    operators.append({
        "Operator ID": f"OP{1000 + i}",
        "Name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Skill Level": random.choices(skills, weights=[3, 4, 3])[0],
        "Certifications": random.choice(["Heavy Equipment Cert", "Safety Cert Level 2",
                                          "Heavy Equipment Cert, Safety Cert Level 2", "None"]),
        "License Expiry": license_exp.date().isoformat(),
        "Date of Joining": join.date().isoformat(),
        "Shift": shift,
        "Email": f"op{1000 + i}@caterpillar-demo.local",
        "Phone": f"{random.choice(demo_country_codes)} {random.randint(1000000000, 9999999999)}",
        "Password Hash": demo_password_hash,
        "Password Salt": demo_password_salt,
        "Typical Fatigue Risk": random.choices(["Low", "Medium", "High"], weights=fatigue_risk_weights)[0],
        "Weight Class": random.choice(weight_classes),
    })

with open(f"{OUT}/operators.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(operators[0].keys()))
    w.writeheader()
    w.writerows(operators)

# ---------- tasks ----------
task_types = ["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition", "Compaction", "Hauling"]
weathers = ["Sunny", "Rainy", "Cloudy", "Windy", "Foggy"]
base_time = {"Earth Excavation": 60, "Trenching": 45, "Material Loading": 30,
             "Grading": 35, "Demolition": 90, "Compaction": 40, "Hauling": 50}
sites = ["Site A - North Yard", "Site B - Quarry", "Site C - Highway Ext", "Site D - Residential"]

tasks = []
start_date = TODAY - timedelta(days=22)
for i in range(1, 51):
    day = start_date + timedelta(days=random.randint(0, 20))
    op = random.choice(operators)
    mach = random.choice(machines)
    ttype = random.choice(task_types)
    weather = random.choice(weathers)
    est = base_time[ttype] + random.randint(-5, 5)

    skill_factor = {"Beginner": 1.25, "Intermediate": 1.05, "Expert": 0.9}[op["Skill Level"]]
    weather_factor = {"Sunny": 1.0, "Cloudy": 1.02, "Windy": 1.08, "Rainy": 1.15, "Foggy": 1.2}[weather]
    age_factor = 1 + (mach["Age (yrs)"] * 0.01)
    actual = round(est * skill_factor * weather_factor * age_factor + random.uniform(-4, 4))

    status = "Completed" if day < TODAY else random.choice(["Scheduled", "In Progress"])
    start_time = day.replace(hour=random.choice([6, 7, 8, 13, 14]))
    end_time = start_time + timedelta(minutes=actual) if status == "Completed" else None

    # Placeholder model output: a plausible predicted duration + confidence range
    # persisted alongside the task. The live model (backend/app/ml.py) recomputes
    # and overwrites this at inference time; these values just keep the column
    # populated so the dataset schema never needs to change later.
    pred_center = actual if status == "Completed" else est
    predicted = round(pred_center * random.uniform(0.95, 1.05))
    pred_lower = round(predicted * 0.88)
    pred_upper = round(predicted * 1.12)

    tasks.append({
        "Task ID": f"T{i:04d}",
        "Date": day.date().isoformat(),
        "Machine ID": mach["Machine ID"],
        "Operator ID": op["Operator ID"],
        "Task Type": ttype,
        "Site": random.choice(sites),
        "Weather": weather,
        "Priority": random.choice(["Low", "Medium", "High"]),
        "Estimated Time (min)": est,
        "Actual Time (min)": actual if status == "Completed" else "",
        "Predicted Time (min)": predicted,
        "Prediction Lower Bound (min)": pred_lower,
        "Prediction Upper Bound (min)": pred_upper,
        "Start Time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else "",
        "Status": status,
    })

with open(f"{OUT}/tasks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(tasks[0].keys()))
    w.writeheader()
    w.writerows(tasks)

# ---------- telemetry (time series, safety + anomaly detection + coaching) ----------
bucket_positions = ["Rest", "Hoist", "Dump", "Dig"]
telemetry = []
for mach in machines:
    engine_hours = mach["Total Engine Hours"] - random.uniform(50, 150)
    ts = (TODAY - timedelta(days=8)).replace(hour=7)
    for _ in range(30):
        ts += timedelta(hours=random.choice([1, 2, 3]))
        engine_hours += round(random.uniform(0.8, 2.5), 1)
        idling = random.choices([5, 10, 15, 20, 30, 45, 60, 75], weights=[20, 20, 20, 15, 10, 8, 4, 3])[0]
        seatbelt = random.choices(["Fastened", "Unfastened"], weights=[19, 1])[0]
        proximity_dist = round(random.uniform(0.5, 25), 1)
        proximity_alert = "Yes" if proximity_dist < 2 else "No"
        excessive_idle = idling >= 60
        safety_alert = "Yes" if (seatbelt == "Unfastened" or proximity_alert == "Yes" or excessive_idle) else "No"
        op = random.choice(operators)
        speed = round(random.uniform(0, 25), 1)
        bucket_position = random.choices(bucket_positions, weights=[5, 2, 2, 3])[0]
        # Hoisting puts the most load on the hydraulics; feeds the coaching rules.
        hydraulic_pressure = round(random.uniform(180, 280) if bucket_position == "Hoist"
                                    else random.uniform(50, 180), 1)
        slippage_events = random.choices([0, 1, 2, 3], weights=[12, 4, 2, 1])[0]

        telemetry.append({
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Machine ID": mach["Machine ID"],
            "Operator ID": op["Operator ID"],
            "Engine Hours": round(engine_hours, 1),
            "Fuel Used (L)": round(random.uniform(1.5, 8.0), 1),
            "Load Cycles": random.randint(0, 15),
            "Idling Time (min)": idling,
            "Engine RPM": random.randint(700, 2200),
            "Speed (km/h)": speed,
            "Hydraulic Pressure (bar)": hydraulic_pressure,
            "Slippage Events": slippage_events,
            "Bucket Position": bucket_position,
            "Seatbelt Status": seatbelt,
            "Proximity Distance (m)": proximity_dist,
            "Proximity Alert": proximity_alert,
            "Safety Alert Triggered": safety_alert,
        })

telemetry.sort(key=lambda r: r["Timestamp"])
with open(f"{OUT}/telemetry.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(telemetry[0].keys()))
    w.writeheader()
    w.writerows(telemetry)

operators_by_id = {op["Operator ID"]: op for op in operators}

# ---------- fatigue events (one row per telemetry reading; IR-camera simulation) ----------
alert_thresholds = [(70, "Critical"), (45, "Caution")]
fatigue_events = []
risk_baseline = {"Low": 15, "Medium": 28, "High": 40}
for i, row in enumerate(telemetry):
    op = operators_by_id[row["Operator ID"]]
    baseline = risk_baseline[op["Typical Fatigue Risk"]]
    if op["Shift"] == "Night":
        baseline += 10
    # Embed a handful of deliberate fatigue-spike scenarios so the demo has
    # something dramatic to show, without making every reading alarming.
    is_spike = random.random() < 0.08
    eye_closure = round(random.uniform(1.6, 2.4) if is_spike else random.uniform(0.0, 0.6), 2)
    blink_rate = random.randint(6, 11) if is_spike else random.randint(12, 22)
    head_pitch = random.randint(-18, -8) if is_spike else random.randint(-6, 6)
    score = min(100, round(baseline + eye_closure * 30 + max(0, 18 - blink_rate) * 1.5 + abs(min(0, head_pitch)) * 0.8))
    alert_level = "Normal"
    for threshold, label in alert_thresholds:
        if score >= threshold:
            alert_level = label
            break
    haptic = "Yes" if (eye_closure > 1.5 or alert_level == "Critical") else "No"

    fatigue_events.append({
        "Timestamp": row["Timestamp"],
        "Machine ID": row["Machine ID"],
        "Operator ID": row["Operator ID"],
        "Fatigue Score": score,
        "Eye Closure Duration (s)": eye_closure,
        "Blink Rate (per min)": blink_rate,
        "Head Pitch (deg)": head_pitch,
        "Alert Level": alert_level,
        "Haptic Triggered": haptic,
    })

with open(f"{OUT}/fatigue_events.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(fatigue_events[0].keys()))
    w.writeheader()
    w.writerows(fatigue_events)

# ---------- ergonomics (seat + chassis vibration simulation) ----------
ergonomics = []
wbv_running_total = {}  # per operator, cumulative exposure for the (synthetic) shift
weight_center_bias = {"Light": 0.45, "Medium": 0.50, "Heavy": 0.55}
for row in telemetry:
    op = operators_by_id[row["Operator ID"]]
    rough_terrain = random.random() < 0.15
    chassis_x = round(random.uniform(-0.3, 0.3) + (random.uniform(0.8, 1.5) if rough_terrain else 0), 2)
    chassis_y = round(random.uniform(-0.3, 0.3) + (random.uniform(0.8, 1.5) if rough_terrain else 0), 2)
    chassis_z = round(random.uniform(-0.4, 0.4) + (random.uniform(1.0, 1.8) if rough_terrain else 0), 2)
    # Active suspension damps roughly 55-70% of chassis shock before it reaches the seat.
    damp_factor = random.uniform(0.3, 0.45)
    seat_x = round(chassis_x * damp_factor, 2)
    seat_y = round(chassis_y * damp_factor, 2)
    seat_z = round(chassis_z * damp_factor, 2)
    damping_setting = "Firm" if abs(chassis_z) > 1.0 else ("Medium" if abs(chassis_z) > 0.4 else "Soft")
    seat_air_pressure = {"Soft": random.uniform(30, 45), "Medium": random.uniform(45, 65),
                          "Firm": random.uniform(65, 80)}[damping_setting]
    center_bias = weight_center_bias[op["Weight Class"]]
    pressure_center_x = round(min(1.0, max(0.0, random.gauss(center_bias, 0.05))), 2)
    pressure_center_y = round(min(1.0, max(0.0, random.gauss(0.5, 0.05))), 2)
    exposure_increment = abs(seat_z) * random.uniform(1.5, 2.5)
    wbv_running_total[row["Operator ID"]] = wbv_running_total.get(row["Operator ID"], 0) + exposure_increment

    ergonomics.append({
        "Timestamp": row["Timestamp"],
        "Machine ID": row["Machine ID"],
        "Operator ID": row["Operator ID"],
        "Chassis Accel X (g)": chassis_x,
        "Chassis Accel Y (g)": chassis_y,
        "Chassis Accel Z (g)": chassis_z,
        "Seat Accel X (g)": seat_x,
        "Seat Accel Y (g)": seat_y,
        "Seat Accel Z (g)": seat_z,
        "Seat Pressure Center X": pressure_center_x,
        "Seat Pressure Center Y": pressure_center_y,
        "Seat Air Pressure (kPa)": round(seat_air_pressure, 1),
        "Damping Setting": damping_setting,
        "WBV Exposure Index": round(wbv_running_total[row["Operator ID"]], 1),
    })

with open(f"{OUT}/ergonomics.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ergonomics[0].keys()))
    w.writeheader()
    w.writerows(ergonomics)

# ---------- environment (cabin air quality + thermal monitoring) ----------
environment = []
for row in telemetry:
    co2_spike = random.random() < 0.1
    co2 = round(random.uniform(1000, 1600) if co2_spike else random.uniform(450, 950))
    hvac_override = "Yes" if co2 > 1000 else "No"
    fresh_air_flush = "Yes" if co2 > 1200 else "No"
    facial_temp_spike = random.random() < 0.08
    facial_temp = round(random.uniform(37.3, 37.9) if facial_temp_spike else random.uniform(35.9, 37.1), 1)

    environment.append({
        "Timestamp": row["Timestamp"],
        "Machine ID": row["Machine ID"],
        "Operator ID": row["Operator ID"],
        "Cab CO2 (ppm)": co2,
        "Cab PM2.5 (ug/m3)": round(random.uniform(5, 80), 1),
        "Cab Temp (C)": round(random.uniform(20, 32), 1),
        "Cab Humidity (%)": round(random.uniform(40, 75)),
        "Operator Facial Temp (C)": facial_temp,
        "HVAC Override Active": hvac_override,
        "Fresh Air Flush Active": fresh_air_flush,
    })

with open(f"{OUT}/environment.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(environment[0].keys()))
    w.writeheader()
    w.writerows(environment)

# ---------- coaching events (sparse, rule-triggered from telemetry) ----------
coaching_events = []
coach_id = 1
for row in telemetry:
    event_type = None
    severity = None
    message = None
    action = None
    if row["Bucket Position"] == "Hoist" and row["Speed (km/h)"] > 2:
        event_type, severity = "hoist_while_tramming", "Warning"
        message, action = "Hoist while tramming detected.", "Complete the lift before tramming forward."
    elif row["Hydraulic Pressure (bar)"] > 250 and row["Engine RPM"] < 1000:
        event_type, severity = "high_pressure_low_rpm", "Warning"
        message, action = "High hydraulic pressure at low RPM.", "Increase RPM before continuing the heavy lift."
    elif row["Slippage Events"] >= 2:
        event_type, severity = "repeated_slippage", "Critical"
        message, action = "Repeated track/wheel slippage detected.", "Reduce throttle and reposition for traction."
    elif row["Idling Time (min)"] >= 60:
        event_type, severity = "excessive_idling", "Info"
        message, action = "Excessive idling detected.", "Shut down the engine if the machine will be idle for over 5 minutes."

    if event_type:
        coaching_events.append({
            "Coaching Event ID": f"CE{coach_id:04d}",
            "Timestamp": row["Timestamp"],
            "Machine ID": row["Machine ID"],
            "Operator ID": row["Operator ID"],
            "Event Type": event_type,
            "Severity": severity,
            "Message": message,
            "Recommended Action": action,
        })
        coach_id += 1

with open(f"{OUT}/coaching_events.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(coaching_events[0].keys()))
    w.writeheader()
    w.writerows(coaching_events)

# ---------- safety incidents (derived from flagged telemetry + a few extra) ----------
incident_types_map = {
    "Unfastened": "Seatbelt Violation",
}
incidents = []
inc_id = 1
for row in telemetry:
    if row["Safety Alert Triggered"] == "Yes":
        if row["Seatbelt Status"] == "Unfastened":
            itype = "Seatbelt Violation"
            severity = "Medium"
        elif row["Proximity Alert"] == "Yes":
            itype = "Proximity Breach"
            severity = "High"
        else:
            itype = "Excessive Idling"
            severity = "Low"
        incidents.append({
            "Incident ID": f"INC{inc_id:04d}",
            "Timestamp": row["Timestamp"],
            "Machine ID": row["Machine ID"],
            "Operator ID": row["Operator ID"],
            "Incident Type": itype,
            "Severity": severity,
            "Location": random.choice(sites),
            "Description": f"{itype} detected during routine telemetry monitoring.",
            "Action Taken": random.choice(["Operator notified", "Supervisor alerted", "Task paused", "Logged only"]),
            "Resolved": random.choices(["Yes", "No"], weights=[7, 3])[0],
        })
        inc_id += 1

with open(f"{OUT}/safety_incidents.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(incidents[0].keys()))
    w.writeheader()
    w.writerows(incidents)

# ---------- training modules ----------
modules = [
    ("MOD001", "Seatbelt & Cabin Safety Basics", "Safety", "Video", 15, "Beginner"),
    ("MOD002", "Proximity Hazard Awareness", "Safety", "Video", 20, "Beginner"),
    ("MOD003", "Excavator Operation Fundamentals", "Operation", "Simulation", 45, "Beginner"),
    ("MOD004", "Advanced Grading Techniques", "Operation", "Simulation", 60, "Intermediate"),
    ("MOD005", "Fuel-Efficient Operation Practices", "Operation", "Video", 25, "Intermediate"),
    ("MOD006", "Incident Reporting Procedures", "Safety", "Instructor-led", 30, "Beginner"),
    ("MOD007", "Demolition Site Safety", "Safety", "Instructor-led", 40, "Advanced"),
    ("MOD008", "Preventive Maintenance Checks", "Maintenance", "Video", 20, "Intermediate"),
]
with open(f"{OUT}/training_modules.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Module ID", "Title", "Category", "Format", "Duration (min)", "Difficulty"])
    w.writerows(modules)

# ---------- training records ----------
records = []
rec_id = 1
for op in operators:
    n = random.randint(2, 5)
    chosen = random.sample(modules, n)
    for mod in chosen:
        status = random.choices(["Completed", "In Progress", "Not Started"], weights=[6, 2, 2])[0]
        completion = None
        score = ""
        if status == "Completed":
            completion = TODAY - timedelta(days=random.randint(1, 200))
            score = random.randint(70, 100)
        records.append({
            "Record ID": f"TR{rec_id:04d}",
            "Operator ID": op["Operator ID"],
            "Module ID": mod[0],
            "Status": status,
            "Completion Date": completion.date().isoformat() if completion else "",
            "Score": score,
            "Certification Expiry": (completion + timedelta(days=365)).date().isoformat() if completion else "",
        })
        rec_id += 1

with open(f"{OUT}/training_records.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    w.writeheader()
    w.writerows(records)

print("machines:", len(machines))
print("operators:", len(operators))
print("tasks:", len(tasks))
print("telemetry:", len(telemetry))
print("incidents:", len(incidents))
print("fatigue_events:", len(fatigue_events))
print("ergonomics:", len(ergonomics))
print("environment:", len(environment))
print("coaching_events:", len(coaching_events))
print("training_modules:", len(modules))
print("training_records:", len(records))
