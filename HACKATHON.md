# Smart Operator Assistant — 24-Hour Hackathon Plan

> **The Intelligent Cab: Operator-Centered, Non-Contact, Edge-Powered**
>
> A standalone demo showing one operator's shift through a single intelligent interface: real-time fatigue detection, machine coaching, ergonomic adaptation, and environmental health monitoring — all without wearables.

---

## 1. Hackathon Goal

Build a **single, demoable, end-to-end Smart Operator Assistant** that tells a clear story in under 5 minutes. The focus is on **one operator, one machine, one shift**. Every feature must be visible on screen within seconds of the demo starting.

**The narrative in one sentence:**

> "We show one operator's shift in one screen: their tasks, their real-time fatigue risk, the machine coaching them, and the cab protecting their body and air — all without wearables."

---

## 2. Why This Idea Wins

| Judge Lens | How This Project Delivers |
|------------|---------------------------|
| **Practicality** | Based on real Caterpillar telemetry, CAN bus data, and in-cab sensors that already exist on modern machines. |
| **Creativity** | Shifts focus from fleet management to the operator as a human system — fatigue, ergonomics, cognitive load. |
| **Technical Depth** | Combines Edge AI simulation, real-time streaming, machine learning prediction, and responsive UI. |
| **Demo Impact** | One dashboard tells a complete story: task → risk → intervention → protection. |

**Core insight:** Most OEM telematics optimize the *machine*. This assistant optimizes the *operator* — the single largest variable in fuel burn, component life, incident rates, and daily throughput.

---

## 3. Scope for 24 Hours

We build **five tightly integrated features**. Everything else is cut.

| # | Feature | What It Does | How It Looks |
|---|---------|--------------|--------------|
| 1 | **Shift Dashboard** | Shows active task, schedule, and predicted completion time. | Hero card at top of screen. |
| 2 | **Fatigue AI** | Simulates IR camera eye-closure / head-pose detection. | Live fatigue gauge + event log + haptic alert. |
| 3 | **Coach AI** | Simulates CAN bus coaching for dangerous/inefficient moves. | Alert card: "Hoist while tramming detected — complete lift first." |
| 4 | **Ergo AI** | Simulates active seat suspension responding to chassis vibration. | Live vibration chart + damping setting log. |
| 5 | **Environment AI** | Simulates cabin CO₂ and facial temperature monitoring. | CO₂ trend + thermal warning + HVAC override. |

**What we simulate:** The physical sensors (IR camera, accelerometers, CAN bus, HVAC sensors). The UI treats these as real feeds, and we generate a believable synthetic stream.

**What we actually build:** A real FastAPI backend, a real React frontend, a real ML model for task-time prediction, and a real SSE streaming endpoint.

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │   Dashboard  │ │  Live Sensors│ │    Coaching Feed     │ │
│  │   & Tasks    │ │   Panels     │ │    & Anomalies       │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP + SSE
┌───────────────────────────▼─────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  /dashboard  │ │ /sensors/    │ │  /predict/task-time  │ │
│  │              │ │   stream     │ │                      │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐                          │
│  │  /coaching   │ │  /anomalies  │                          │
│  └──────────────┘ └──────────────┘                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ in-memory / CSV
┌───────────────────────────▼─────────────────────────────────┐
│              SYNTHETIC DATA GENERATOR                        │
│   operators, machines, tasks, telemetry, fatigue,            │
│   ergonomics, environment events                             │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Backend | Python + FastAPI | Fast, async, JSON-native, easy SSE support. |
| Data | pandas + CSVs, in-memory | Zero database setup time. |
| ML | scikit-learn `RandomForestRegressor` | Task-time prediction with confidence intervals. |
| Real-time | Server-Sent Events (SSE) | Simulates live sensor stream without WebSocket complexity. |
| Frontend | Vite + React + TypeScript + Tailwind CSS | Fast dev server, easy styling, tablet-friendly. |
| Charts | Recharts | Live-updating line charts and gauges. |
| Icons | Lucide React | Clean, professional icons. |

---

## 5. Backend API Endpoints

### Static / Setup Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/operator` | Returns the demo operator profile. |
| GET | `/api/machine` | Returns the demo machine profile. |
| GET | `/api/tasks` | Returns today's task list. |
| GET | `/api/dashboard` | Aggregated snapshot for the hero dashboard. |

### Dynamic Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sensors/stream` | **SSE stream** of live sensor data (telemetry, fatigue, ergonomics, environment). |
| GET | `/api/coaching` | Returns latest coaching event if any. |
| GET | `/api/anomalies` | Returns flagged anomalies from telemetry. |
| POST | `/api/predict/task-time` | Predicts completion time for a given task type + conditions. |

### SSE Stream Payload (every 1 second)

```json
{
  "timestamp": "2026-09-23T22:14:18Z",
  "telemetry": {
    "rpm": 1450,
    "speed": 3.2,
    "hydraulic_pressure": 210,
    "engine_load": 68,
    "seatbelt": true,
    "proximity_distance": 4.5,
    "bucket_position": "hoist"
  },
  "fatigue": {
    "score": 62,
    "eye_closure_seconds": 0.0,
    "blink_rate": 14,
    "head_pitch": -3,
    "alert_level": "normal"
  },
  "ergonomics": {
    "chassis_accel_z": 0.42,
    "seat_accel_z": 0.18,
    "seat_pressure_center_x": 0.52,
    "seat_pressure_center_y": 0.48,
    "damping_setting": "medium",
    "wbv_exposure_index": 34.2
  },
  "environment": {
    "co2_ppm": 820,
    "cab_temp_c": 24,
    "facial_temp_c": 36.4,
    "humidity_pct": 55,
    "hvac_override_active": false
  }
}
```

---

## 6. Frontend Layout

### Single-Page Tablet Layout (1024 × 768 target)

```
┌────────────────────────────────────────────────────────────────────┐
│  SMART OPERATOR ASSISTANT    OP-001  •  M-336E-42  •  22:14         │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐ │
│  │ ACTIVE TASK                  │  │ FATIGUE AI                  │ │
│  │ Site prep — 28 min remaining │  │ [gauge] Score: 62 (Normal)  │ │
│  │ Est: 45 min | Pred: 42 min   │  │ Blink: 14/min | Head: -3°   │ │
│  │ Weather: Clear               │  │ Last alert: 4 min ago       │ │
│  └──────────────────────────────┘  └─────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐ │
│  │ COACHING FEED                │  │ ERGONOMICS                  │ │
│  │ ⚠️ Hoist while tramming      │  │ [Vibration chart]           │ │
│  │    Complete lift first       │  │ Chassis: 0.42g | Seat: 0.18g│ │
│  │ 🔔 Reduce throttle, slip     │  │ Damping: Medium             │ │
│  └──────────────────────────────┘  └─────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐ │
│  │ ENVIRONMENT AI               │  │ ANOMALIES                   │ │
│  │ CO₂: 820 ppm ↗               │  │ • Excessive idling (12 min) │ │
│  │ Facial temp: 36.4°C          │  │ • Hard braking event        │ │
│  │ HVAC: Normal                 │  │ • High RPM/low load         │ │
│  └──────────────────────────────┘  └─────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────┤
│  TODAY'S TASKS                                                     │
│  [ ] Site prep      In Progress  28/45 min   Fuel: 14L             │
│  [ ] Trenching      Scheduled    est. 90 min                       │
│  [ ] Loading        Scheduled    est. 60 min                       │
└────────────────────────────────────────────────────────────────────┘
```

### Design Notes

- Use a dark, industrial theme (slate/black + CAT yellow accents).
- Cards have soft borders and subtle glows for alert states.
- Critical alerts pulse red/orange.
- Charts animate left-to-right like a live EKG.

---

## 7. Synthetic Dataset Design

All data is generated deterministically (seeded) so the demo is reproducible.

### 7.1 Operator

| Field | Value | Notes |
|-------|-------|-------|
| `operator_id` | OP-001 | Demo operator. |
| `name` | Alex Carter | Humanizes the demo. |
| `skill_level` | Intermediate | Makes coaching tips believable. |
| `shift` | Night | Fatigue events more plausible. |
| `certifications` | CAT 336E, Safety II | Training hub hook. |
| `license_expiry` | 2026-12-01 | Safety/certification pressure. |

### 7.2 Machine

| Field | Value | Notes |
|-------|-------|-------|
| `machine_id` | M-336E-42 | Specific model for realism. |
| `type` | Excavator | Common CAT machine. |
| `model` | 336E | Recognizable CAT model. |
| `age_years` | 4 | Has wear patterns. |
| `engine_hours` | 14250 | Realistic usage. |
| `status` | Active | In use during demo. |

### 7.3 Tasks (Today's Shift)

| task_id | type | priority | estimated_min | actual_min | weather | ground | status |
|---------|------|----------|---------------|------------|---------|--------|--------|
| T-001 | Site prep | Medium | 45 | — | Clear | Firm | in_progress |
| T-002 | Trenching | High | 90 | — | Clear | Rocky | scheduled |
| T-003 | Loading | High | 60 | — | Clear | Firm | scheduled |
| T-004 | Grade finish | Low | 30 | — | Clear | Firm | scheduled |

### 7.4 Telemetry Stream (1 Hz)

| Field | Range / Values | Notes |
|-------|----------------|-------|
| `timestamp` | ISO 8601 | One row per second. |
| `rpm` | 800–2200 | Engine speed. |
| `speed_kmh` | 0–12 | Machine speed. |
| `hydraulic_pressure_bar` | 50–280 | Pressure spikes trigger coaching. |
| `engine_load_pct` | 10–95 | Combined with RPM for anomaly detection. |
| `fuel_used_l` | cumulative | Increments slowly. |
| `seatbelt_status` | on / off | Safety compliance. |
| `proximity_distance_m` | 0.5–20 | Hazard warning if < 3m. |
| `proximity_alert` | bool | True when distance < 3m. |
| `bucket_position` | rest / hoist / dump / dig | Used for coaching rules. |
| `safety_alert_triggered` | bool | Generic safety flag. |

### 7.5 Fatigue Events (1 Hz)

| Field | Range / Values | Notes |
|-------|----------------|-------|
| `fatigue_score` | 0–100 | Composite score. |
| `eye_closure_seconds` | 0.0–3.0 | >1.5s triggers haptic alert. |
| `blink_rate` | 8–25 / min | Slow blink = fatigue. |
| `head_pitch_deg` | -20 to +20 | Nodding detection. |
| `alert_level` | normal / caution / critical | UI color coding. |
| `haptic_triggered` | bool | Seat vibration fired. |

**Scenario built into data:** Around minute 18 of the demo, fatigue score rises to 78, eye closure hits 1.8s, and a critical alert fires.

### 7.6 Ergonomics Stream (1 Hz)

| Field | Range / Values | Notes |
|-------|----------------|-------|
| `chassis_accel_x/y/z` | ±2g | Raw terrain shock. |
| `seat_accel_x/y/z` | ±0.8g | What reaches operator after damping. |
| `seat_pressure_center_x` | 0.0–1.0 | Operator posture proxy. |
| `seat_pressure_center_y` | 0.0–1.0 | Operator posture proxy. |
| `seat_air_pressure_kpa` | 30–80 | Active suspension state. |
| `damping_setting` | soft / medium / firm | Active adjustment. |
| `wbv_exposure_index` | cumulative | Daily whole-body vibration dose. |

**Scenario:** Rough terrain segment where chassis Z accel spikes to 1.5g and damping switches to "firm" in response.

### 7.7 Environment Stream (1 Hz)

| Field | Range / Values | Notes |
|-------|----------------|-------|
| `co2_ppm` | 400–1600 | >1000 = drowsiness risk. |
| `cab_temp_c` | 20–32 | Thermal comfort. |
| `cab_humidity_pct` | 40–75 | Comfort metric. |
| `facial_temp_c` | 35.8–37.8 | Heat stress proxy. |
| `pm25_ug_m3` | 5–80 | Particulate load. |
| `hvac_override_active` | bool | System took action. |
| `fresh_air_flush_active` | bool | High ventilation mode. |

**Scenario:** CO₂ climbs to 1150 ppm; HVAC override activates, fresh air flush turns on, and verbal warning fires.

### 7.8 Coaching Events

| Field | Notes |
|-------|-------|
| `timestamp` | |
| `event_type` | `hoist_while_tramming`, `high_pressure_low_rpm`, `repeated_slippage`, `hard_braking`, `excessive_idling` |
| `severity` | info / warning / critical |
| `message` | Human-readable tip. |
| `recommended_action` | Specific correction. |

### 7.9 Anomalies

Derived from telemetry patterns:

| Anomaly | Rule |
|---------|------|
| Excessive idling | Idling time > 15 min in window. |
| High RPM / low load | RPM > 1800 and engine load < 30%. |
| Seatbelt violation | Seatbelt off while speed > 0. |
| Proximity breach | Proximity alert + speed not reduced. |
| Hard braking | Speed drop > 5 km/h in 2 seconds. |
| Fuel spike | Fuel consumption z-score > 2.5. |

### 7.10 Training Records (Static)

| Field | Notes |
|-------|-------|
| `module_id` | |
| `title` | e.g., "Efficient Bucket Loading" |
| `category` | Safety, Efficiency, Machine Care, Ergonomics |
| `format` | Video, Simulation, Quiz |
| `duration_min` | |
| `difficulty` | Beginner / Intermediate / Advanced |
| `status` | Not Started / In Progress / Completed |
| `score` | 0–100 |
| `certification_expiry` | date |

---

## 8. Machine Learning Components

### 8.1 Task Time Prediction

- **Model:** `RandomForestRegressor`
- **Inputs:** task type, machine age, operator skill, weather, ground condition, engine hours.
- **Output:** predicted duration + confidence interval (using per-tree variance).
- **Training data:** Synthetic historical tasks with actual completion times.
- **Demo value:** Dashboard shows "Est. 45 min → Pred. 42 min (38–46 min)".

### 8.2 Anomaly Detection

- **Method:** Z-score on idling time and fuel use + rule-based flags.
- **Demo value:** Anomalies panel updates live as the shift progresses.

### 8.3 Fatigue Scoring (Simulated but Realistic)

- **Formula:** `fatigue_score = baseline + (eye_closure * 30) + (slow_blink_penalty) + (head_nod_penalty)`
- **Baseline** rises slightly over the night shift.
- **Demo value:** Gauge changes color and haptic alert fires at threshold.

---

## 9. 24-Hour Execution Timeline

### Hour 0–1: Setup
- [ ] Initialize repo structure: `backend/`, `frontend/`, `data/`, `scripts/`.
- [ ] Create Python virtual environment and install FastAPI, uvicorn, pandas, scikit-learn, numpy.
- [ ] Create Vite React + TypeScript project with Tailwind and Recharts.
- [ ] Verify backend and frontend dev servers run.

### Hour 1–3: Data Generation
- [ ] Write `scripts/generate_data.py` to create all CSVs.
- [ ] Embed demo scenarios: fatigue spike, rough terrain, CO₂ rise, hoist-while-tramming.
- [ ] Seed RNG for reproducibility.
- [ ] Verify CSVs are coherent and join correctly.

### Hour 3–6: Backend Core
- [ ] Build `/api/operator`, `/api/machine`, `/api/tasks`, `/api/dashboard`.
- [ ] Build `/api/sensors/stream` SSE endpoint.
- [ ] Build `/api/coaching` and `/api/anomalies`.
- [ ] Train and expose `/api/predict/task-time`.
- [ ] Test all endpoints with `curl` or HTTP client.

### Hour 6–10: Frontend Shell
- [ ] Build top navigation / header.
- [ ] Build dashboard hero card.
- [ ] Build task list component.
- [ ] Build live sensor panels (fatigue, ergonomics, environment).
- [ ] Build coaching feed and anomalies panel.
- [ ] Wire `api.ts` to backend.

### Hour 10–14: Real-Time Integration
- [ ] Connect SSE stream to UI state.
- [ ] Make charts live-update.
- [ ] Add alert animations for critical events.
- [ ] Add haptic alert indicator.

### Hour 14–18: Polish & Demo Script
- [ ] Apply CAT-inspired dark industrial theme.
- [ ] Add responsive layout for tablet screens.
- [ ] Write demo script / talking points.
- [ ] Record a short GIF or screen capture if time allows.

### Hour 18–22: Buffer & Bug Fixes
- [ ] Test full demo flow end-to-end.
- [ ] Fix CORS, SSE reconnect, chart memory leaks.
- [ ] Add loading and error states.
- [ ] Add `README.md` with run instructions.

### Hour 22–24: Final Packaging
- [ ] Ensure `docker-compose.yml` or single-script launch works.
- [ ] Final README, screenshots, and repo cleanup.
- [ ] Dry-run demo twice.

---

## 10. Demo Script (5 Minutes)

### Slide 1: Problem (30s)
"Mining operators work 12-hour night shifts in hostile cabs. Fatigue, bad habits, whole-body vibration, and stale air cause accidents, injuries, and machine damage. Wearables don't survive — dust, vibration, PPE rules kill them."

### Slide 2: Vision (30s)
"We built an intelligent cab companion that monitors the operator without wearables — using IR cameras, CAN bus data, seat sensors, and HVAC sensors."

### Slide 3: Dashboard (1m)
"Here's Alex Carter on a night shift in a CAT 336E. The dashboard shows the active task, estimated vs predicted completion time, and live vitals."

### Slide 4: Fatigue AI (1m)
"The IR camera tracks eye closure and head pose locally. Watch — around now, Alex's eyes close for 1.8 seconds. The system fires a haptic seat vibration and logs a critical fatigue alert. No video leaves the cab."

### Slide 5: Coach AI (1m)
"The CAN bus sees hydraulic pressure spike while the bucket is hoisted and the machine is moving. The assistant interrupts the display: 'Complete the lift before tramming.' This prevents hydraulic pump damage."

### Slide 6: Ergo + Environment AI (1m)
"Rough terrain spikes chassis vibration; the active seat firms its damping. Meanwhile, cabin CO₂ climbs; the HVAC flushes fresh air and warns Alex to hydrate."

### Closing (30s)
"This is operator-centric intelligence. It protects the human, the machine, and the operation — and it's built entirely from sensors Caterpillar can deploy today."

---

## 11. Files to Create

```
caterpillar/
├── README.md
├── PLAN.md
├── docker-compose.yml
├── scripts/
│   └── generate_data.py
├── data/
│   ├── operator.csv
│   ├── machine.csv
│   ├── tasks.csv
│   ├── telemetry.csv
│   ├── fatigue_events.csv
│   ├── ergonomics.csv
│   ├── environment.csv
│   ├── coaching_events.csv
│   ├── anomalies.csv
│   ├── training_modules.csv
│   └── training_records.csv
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   └── predictor.py
│   └── data_loader.py
└── frontend/
    ├── package.json
    ├── index.html
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── api.ts
    │   ├── components/
    │   │   ├── Header.tsx
    │   │   ├── DashboardHero.tsx
    │   │   ├── TaskList.tsx
    │   │   ├── FatiguePanel.tsx
    │   │   ├── CoachingFeed.tsx
    │   │   ├── ErgonomicsPanel.tsx
    │   │   ├── EnvironmentPanel.tsx
    │   │   └── AnomaliesPanel.tsx
    │   └── index.css
```

---

## 12. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SSE too complex | Fallback to 1-second polling if needed. |
| ML model overfits | Use simple RandomForest with small synthetic data; focus on UI value. |
| Time runs out | Cut training hub and certification cards first; core demo is dashboard + 3 AI panels. |
| CORS issues | Configure FastAPI `CORSMiddleware` immediately. |
| Demo fails live | Pre-generate data; seed RNG; test full flow before sleeping. |

---

## 13. Future Roadmap (Post-Hackathon)

1. Connect to real CAN bus feed and IR camera Edge AI node.
2. Add multi-operator / multi-machine fleet view.
3. Replace synthetic CSVs with time-series database (InfluxDB/TimescaleDB).
4. Expand coaching rules to full expert-system or reinforcement-learning policy.
5. Build operator digital twin with per-shift strain score.
6. Add machine-operator matching based on skill and fatigue history.
