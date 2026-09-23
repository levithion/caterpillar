import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)
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
        "Contact": f"op{1000 + i}@caterpillar-demo.local",
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

# ---------- telemetry (time series, safety + anomaly detection) ----------
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

        telemetry.append({
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Machine ID": mach["Machine ID"],
            "Operator ID": random.choice(operators)["Operator ID"],
            "Engine Hours": round(engine_hours, 1),
            "Fuel Used (L)": round(random.uniform(1.5, 8.0), 1),
            "Load Cycles": random.randint(0, 15),
            "Idling Time (min)": idling,
            "Engine RPM": random.randint(700, 2200),
            "Speed (km/h)": round(random.uniform(0, 25), 1),
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
print("training_modules:", len(modules))
print("training_records:", len(records))
