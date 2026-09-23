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
for i in range(1, 11):
    join = TODAY - timedelta(days=random.randint(60, 3000))
    license_exp = TODAY + timedelta(days=random.randint(30, 800))
    operators.append({
        "Operator ID": f"OP{1000 + i}",
        "Name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Skill Level": random.choices(skills, weights=[3, 4, 3])[0],
        "Certifications": random.choice(["Heavy Equipment Cert", "Safety Cert Level 2",
                                          "Heavy Equipment Cert, Safety Cert Level 2", "None"]),
        "License Expiry": license_exp.date().isoformat(),
        "Date of Joining": join.date().isoformat(),
        "Shift": random.choice(["Day", "Night"]),
        "Contact": f"op{1000 + i}@caterpillar-demo.local",
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
        "Start Time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else "",
        "Status": status,
    })

with open(f"{OUT}/tasks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(tasks[0].keys()))
    w.writeheader()
    w.writerows(tasks)


# ---------- Member 2: safety telemetry (time series) ----------
def generate_safety_telemetry(machines, operators):
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

            rpm = random.randint(700, 2200)
            speed = round(random.uniform(0, 25), 1)
            hydraulic_pressure = round(random.uniform(50, 280), 1)
            slippage_events = random.choices([0, 1, 2, 3], weights=[70, 20, 7, 3])[0]
            bucket_position = random.choice(["rest", "hoist", "dump", "dig"])

            baseline_fatigue = random.randint(25, 45)
            eye_closure = round(random.uniform(0, 0.3), 2)
            blink_rate = random.randint(12, 20)
            head_pitch = random.randint(-5, 5)

            # Inject realistic fatigue events
            if random.random() < 0.15:
                eye_closure = round(random.uniform(1.6, 2.5), 2)
                baseline_fatigue = random.randint(70, 90)
                blink_rate = random.randint(6, 10)
                head_pitch = random.randint(-15, -5)

            # Inject realistic coaching scenarios
            if random.random() < 0.15:
                bucket_position = "hoist"
                speed = round(random.uniform(2, 10), 1)
                hydraulic_pressure = round(random.uniform(200, 280), 1)

            if speed < 3 and hydraulic_pressure > 200 and random.random() < 0.3:
                rpm = random.randint(700, 1100)

            if eye_closure > 1.5:
                alert_level = "critical"
                haptic_triggered = "Yes"
            elif baseline_fatigue > 60 or blink_rate < 10:
                alert_level = "caution"
                haptic_triggered = random.choice(["Yes", "No"])
            else:
                alert_level = "normal"
                haptic_triggered = "No"

            telemetry.append({
                "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Machine ID": mach["Machine ID"],
                "Operator ID": random.choice(operators)["Operator ID"],
                "Engine Hours": round(engine_hours, 1),
                "Fuel Used (L)": round(random.uniform(1.5, 8.0), 1),
                "Load Cycles": random.randint(0, 15),
                "Idling Time (min)": idling,
                "Engine RPM": rpm,
                "Speed (km/h)": speed,
                "Seatbelt Status": seatbelt,
                "Proximity Distance (m)": proximity_dist,
                "Proximity Alert": proximity_alert,
                "Safety Alert Triggered": safety_alert,
                "Hydraulic Pressure (bar)": hydraulic_pressure,
                "Slippage Events": slippage_events,
                "Bucket Position": bucket_position,
                "Fatigue Score": baseline_fatigue,
                "Eye Closure Duration (s)": eye_closure,
                "Blink Rate": blink_rate,
                "Head Pitch (deg)": head_pitch,
                "Alert Level": alert_level,
                "Haptic Triggered": haptic_triggered,
            })
    telemetry.sort(key=lambda r: r["Timestamp"])
    return telemetry


telemetry = generate_safety_telemetry(machines, operators)
with open(f"{OUT}/telemetry.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(telemetry[0].keys()))
    w.writeheader()
    w.writerows(telemetry)

# ---------- Member 2: safety incidents (derived from flagged telemetry) ----------
def generate_safety_incidents(telemetry, sites):
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
    return incidents


incidents = generate_safety_incidents(telemetry, sites)
with open(f"{OUT}/safety_incidents.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(incidents[0].keys()))
    w.writeheader()
    w.writerows(incidents)

# ---------- Member 2: coaching events (sparse, rule-derived) ----------
def generate_coaching_events(telemetry):
    events = []
    event_id = 1
    prev_speed = {}
    for row in telemetry:
        machine_id = row["Machine ID"]
        speed = float(row["Speed (km/h)"])
        rpm = int(row["Engine RPM"])
        pressure = float(row["Hydraulic Pressure (bar)"])
        slippage = int(row["Slippage Events"])
        bucket = row["Bucket Position"]

        if bucket == "hoist" and speed > 0:
            events.append({
                "Event ID": f"COACH{event_id:04d}",
                "Timestamp": row["Timestamp"],
                "Machine ID": machine_id,
                "Operator ID": row["Operator ID"],
                "Event Type": "hoist_while_tramming",
                "Severity": "warning",
                "Message": "Hoisting bucket while machine is moving",
                "Recommended Action": "Complete the lift before tramming forward.",
            })
            event_id += 1

        if pressure > 200 and rpm < 1200:
            events.append({
                "Event ID": f"COACH{event_id:04d}",
                "Timestamp": row["Timestamp"],
                "Machine ID": machine_id,
                "Operator ID": row["Operator ID"],
                "Event Type": "high_pressure_low_rpm",
                "Severity": "warning",
                "Message": "High hydraulic pressure at low engine RPM",
                "Recommended Action": "Increase RPM before applying heavy load.",
            })
            event_id += 1

        if slippage >= 2:
            events.append({
                "Event ID": f"COACH{event_id:04d}",
                "Timestamp": row["Timestamp"],
                "Machine ID": machine_id,
                "Operator ID": row["Operator ID"],
                "Event Type": "repeated_slippage",
                "Severity": "info",
                "Message": "Repeated track/wheel slippage detected",
                "Recommended Action": "Reduce throttle and reposition for traction.",
            })
            event_id += 1

        prev = prev_speed.get(machine_id, speed)
        if prev - speed > 5:
            events.append({
                "Event ID": f"COACH{event_id:04d}",
                "Timestamp": row["Timestamp"],
                "Machine ID": machine_id,
                "Operator ID": row["Operator ID"],
                "Event Type": "hard_braking",
                "Severity": "info",
                "Message": "Sudden deceleration detected",
                "Recommended Action": "Anticipate stops to reduce brake and drivetrain wear.",
            })
            event_id += 1
        prev_speed[machine_id] = speed

    events.sort(key=lambda e: e["Timestamp"])
    return events


coaching_events = generate_coaching_events(telemetry)
with open(f"{OUT}/coaching_events.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(coaching_events[0].keys()))
    w.writeheader()
    w.writerows(coaching_events)

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
print("coaching_events:", len(coaching_events))
print("training_modules:", len(modules))
print("training_records:", len(records))
