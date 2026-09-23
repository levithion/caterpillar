# PLAN.md

## Project idea

**Smart Operator Assistant** is an end-to-end intelligent companion for CAT machine
operators (excavators, loaders, etc.). Instead of a single-purpose tool, it wraps a
day's work in one interface: what to do, whether it's being done safely, how the cab
is protecting the operator's body and mind in real time, how to get better at doing
it, and how long it should take.

The brief (see `CLAUDE.md`) calls for five outcomes — daily task dashboard, safety
features, an operator training hub, anomaly detection, and task time estimation. This
plan keeps that as the practical core already built and buildable today, and extends
it with four additional, non-contact operator-augmentation features grounded in
capabilities Caterpillar already runs foundational versions of across its fleet
(see "Vision" below). The goal is a plan that is grounded and realistic in the near
term, but creative and differentiated as the end state.

## Vision & creative north star

Most OEM telematics optimize the *machine*. This assistant optimizes the *operator* —
the single largest variable in fuel burn, component life, incident rates, and daily
throughput. The differentiator is **non-contact sensing**: no wearables, because dust,
vibration, and PPE rules kill wearables in real mining/construction environments. All
operator-state data instead comes from sensors already mounted in the cab and machine:
a dashboard IR camera, seat pressure/accelerometers, the machine's own CAN bus, and
HVAC-duct air/thermal sensors.

Four capabilities extend the software prototype into this vision:

1. **Predictive fatigue & alertness detection** — IR camera + Edge AI tracks eye-closure
   duration and head pose (not full body movement), triggering a haptic seat alert
   before a critical event, not after.
2. **Real-time operator coaching** — reads the machine's CAN bus (engine load,
   hydraulic pressure, slippage) and interrupts the display with a corrective tip when
   it sees a damaging move (e.g. hoisting while tramming).
3. **Biomechanical & ergonomic adaptation** — seat pressure pads + chassis/seat
   accelerometers drive an active pneumatic suspension that adjusts damping in
   milliseconds to absorb terrain shock before it reaches the operator's spine.
4. **Operator health & environmental monitoring** — cabin CO₂, particulate, and thermal
   sensors detect drowsiness- and heatstroke-inducing conditions and trigger an
   automatic HVAC override plus a hydration/rest warning.

All four are **privacy-first** (facial data processed locally at the edge; only scores
and alerts leave the device) and **non-contact** (nothing worn by the operator).

## Expected outcomes

| # | Outcome | What it does |
|---|---------|---------------|
| 1 | **Daily task dashboard** | Scheduled tasks for the day, estimated vs. predicted completion time, priority. |
| 2 | **Safety suite** | Seatbelt compliance, proximity hazards, incident logging. |
| 3 | **Operator training hub** | E-learning catalog, certification-expiry warnings, simulation/quiz stub. |
| 4 | **Anomaly detection** | Excessive idling, unsafe operation patterns, fuel/RPM/load outliers. |
| 5 | **Task time estimation** | Predicted completion time (with confidence range) from history + conditions. |
| 6 | **Real-time operator coaching** *(new)* | CAN-bus-driven digital co-pilot flagging damaging machine usage as it happens. |
| 7 | **Ergonomic adaptation** *(new)* | Active seat suspension responding to chassis vibration in real time. |
| 8 | **Environmental health monitoring** *(new)* | Cabin air quality + thermal monitoring with automatic HVAC intervention. |

Outcomes 1–5 are the brief's core scope and are already built (see status below).
Outcomes 6–8 are the creative extension — simulated with synthetic data today, on an
architecture designed so real sensor feeds can be swapped in later without changing
the API surface.

## Architecture

- **Backend** — FastAPI (`backend/app`), reading the CSVs directly with pandas
  (no database yet). Exposes REST endpoints per domain object plus derived endpoints:
  `/api/anomalies` (z-score + rule-based outlier detection over telemetry),
  `/api/predict/task-time` (a scikit-learn `RandomForestRegressor`), and — for the new
  outcomes — `/api/coaching`, `/api/fatigue`, `/api/ergonomics`, `/api/environment`.
- **Frontend** — Vite + React + TypeScript (`frontend/src`), a tabbed single-page app
  (`Dashboard`, `Safety`, `Training`, `Anomalies`, `Predictor` components today; `Coaching`,
  `Ergonomics`, `Environment` panels to add) calling the backend over `fetch`
  (`frontend/src/api.ts`).
- **Data** — flat CSVs as the system of record for this prototype; swapped for a real
  telemetry/CAN-bus feed and database later without changing the API surface.
- **Future edge layer** (not built yet, architecture reserves the seam for it) — an
  in-cab Edge AI processor sits between the physical sensors (IR camera, seat sensors,
  CAN bus/ECMs, HVAC/thermal sensors) and the backend, doing local inference for
  fatigue scoring and coaching rules so alerts fire with low latency and facial video
  never leaves the cab.

```
  IR camera / Seat sensors / CAN bus / HVAC+thermal sensors   (future: physical)
                        │
                Edge AI processor                              (future: local inference)
                        │
                FastAPI backend  ── reads CSVs today, live feeds later
                        │
          React frontend (Dashboard, Safety, Training,
          Anomalies, Predictor, Coaching, Ergonomics, Environment)
```

## Status: what's already built

- [x] Sample data generator (`scripts/generate_data.py`, seeded/deterministic)
- [x] FastAPI backend with CRUD-style read endpoints for all seven tables
- [x] Anomaly detection (z-score over idling time & fuel use, per machine)
- [x] Task time prediction model (RandomForest over task type / weather / skill / machine age)
- [x] React frontend scaffold with tabs for all five outcome areas
- [x] Project-root `.venv` (uv-managed) with backend deps installed
- [x] Repo published to GitHub (`levithion/caterpillar`, private)
- [ ] Coaching, ergonomics, and environment features (outcomes 6–8) — not started; see Phase 2

## Feature deep-dives (new: outcomes 6–8, plus fatigue as part of 2)

### Predictive fatigue & alertness detection (extends outcome 2)
- **Signals:** `fatigue_score` (0–100 composite), `eye_closure_seconds`, `blink_rate`,
  `head_pitch_deg`, `alert_level` (normal/caution/critical).
- **Rule:** eyes closed > 1.5s → `haptic_triggered = true` + critical alert.
- **Demo/UI value:** live gauge on the Safety tab, color-coded by `alert_level`.

### Real-time operator coaching (outcome 6)
- **Signals:** read from telemetry's CAN-bus-style fields — `hydraulic_pressure_bar`,
  `engine_load_pct`, `bucket_position`, `slippage_events`.
- **Rule examples:** hoist + tramming simultaneously → "Complete lift before tramming";
  high pressure at low RPM → "Increase RPM before heavy lift"; repeated slippage →
  "Reduce throttle, reposition for traction."
- **Demo/UI value:** a coaching feed card, most-recent-first, severity-colored.

### Biomechanical & ergonomic adaptation (outcome 7)
- **Signals:** `chassis_accel_x/y/z`, `seat_accel_x/y/z`, `seat_pressure_center_x/y`,
  `seat_air_pressure_kpa`, `damping_setting`, `wbv_exposure_index`.
- **Rule:** chassis shock spike → `damping_setting` steps toward `firm`; cumulative
  `wbv_exposure_index` tracked per shift as an operator-health metric.
- **Demo/UI value:** a live vibration chart + current damping setting.

### Operator health & environmental monitoring (outcome 8)
- **Signals:** `co2_ppm`, `cab_temp_c`, `cab_humidity_pct`, `facial_temp_c`,
  `pm25_ug_m3`, `hvac_override_active`, `fresh_air_flush_active`.
- **Rule:** CO₂ > 1000ppm or facial temp spike → `hvac_override_active = true`,
  `fresh_air_flush_active = true`, plus a hydration/rest warning.
- **Demo/UI value:** CO₂ trend line + HVAC status + thermal warning banner.

## Proposed dataset schema

Extends the existing seven CSVs and adds three new ones. Join keys stay `Machine ID`,
`Operator ID`, `Module ID`. Regenerate via `scripts/generate_data.py` (seeded,
deterministic) once the schema below is implemented — hand-editing CSVs directly is
fine too as long as join keys/column names stay stable.

**Extend `machines.csv`** — add `Has IR Camera`, `Has Active Suspension`,
`Has Thermal Camera` (bools; lets the UI gracefully hide panels for machines without
the relevant simulated hardware).

**Extend `operators.csv`** — add `Typical Fatigue Risk` (low/med/high, shift-correlated)
and `Weight Class` (feeds the ergonomic seat-pressure baseline).

**Extend `tasks.csv`** — add `Predicted Time (min)`, `Prediction Lower Bound`,
`Prediction Upper Bound` (persists the model's confidence range alongside the task
instead of recomputing it client-side every load).

**Extend `telemetry.csv`** — add `Hydraulic Pressure (bar)`, `Slippage Events`,
`Bucket Position` (rest/hoist/dump/dig) — these three feed the coaching rules and
don't exist in the current schema.

**New `fatigue_events.csv`** (time-series, 1 row/sec, per operator+machine):
`Timestamp`, `Operator ID`, `Machine ID`, `Fatigue Score`, `Eye Closure Duration (s)`,
`Blink Rate`, `Head Pitch (deg)`, `Alert Level`, `Haptic Triggered`.

**New `ergonomics.csv`** (time-series, 1 row/sec, per operator+machine):
`Timestamp`, `Operator ID`, `Machine ID`, `Chassis Accel X/Y/Z`, `Seat Accel X/Y/Z`,
`Seat Pressure Center X/Y`, `Seat Air Pressure (kPa)`, `Damping Setting`,
`WBV Exposure Index`.

**New `environment.csv`** (time-series, 1 row/sec, per operator+machine):
`Timestamp`, `Operator ID`, `Machine ID`, `Cab CO2 (ppm)`, `Cab PM2.5 (µg/m³)`,
`Cab Temp (C)`, `Cab Humidity (%)`, `Operator Facial Temp (C)`, `HVAC Override Active`,
`Fresh Air Flush Active`.

**New `coaching_events.csv`** (sparse — one row per triggered event, not per second):
`Timestamp`, `Operator ID`, `Machine ID`, `Event Type` (`hoist_while_tramming`,
`high_pressure_low_rpm`, `repeated_slippage`, `hard_braking`, `excessive_idling`),
`Severity` (info/warning/critical), `Message`, `Recommended Action`.

`safety_incidents.csv`, `training_modules.csv`, `training_records.csv` stay as-is.

## Creative additions for Caterpillar (post-core, differentiators)

- **Operator digital twin lite** — aggregate fatigue, ergonomics, coaching, and task
  data into a per-operator "daily strain score" predicting tomorrow's risk and
  recommending rest/training.
- **Machine-operator matching** — recommend which operator suits which machine/task
  each shift, based on skill + current fatigue + task history.
- **Predictive component wear link** — correlate coaching events (e.g. repeated
  hoist-while-tramming) with hydraulic/track stress to predict component wear per
  operator style.
- **Adaptive training** — recommend training modules based on mistakes the coaching
  engine actually detected, not just certification expiry.
- **Shift handoff briefing** — a 30-second auto-generated summary at shift change:
  tasks completed, anomalies, fatigue exposure, ergonomic load, open coaching items.

## Execution steps (remaining)

### Phase 1 — Harden the existing five outcomes
- [ ] Cache `load_all()` (currently re-reads every CSV on every request) — load once
      at startup, or memoize with a `functools.lru_cache` / file-mtime check.
- [ ] Persist the trained task-time model instead of retraining lazily on first
      request (train at startup, or cache to disk with `joblib`).
- [ ] Add `/api/dashboard/{operator_id}` or `?date=` filtering so the frontend
      doesn't need to fetch and filter all tasks client-side.
- [ ] Basic input validation / error responses for unknown machine/operator IDs.
- [ ] Tests: at least smoke tests for each endpoint and the anomaly/prediction logic
      (`pytest` — not yet in `requirements.txt`).
- [ ] Seatbelt compliance: surface live/most-recent `Seatbelt Status` per
      machine-operator pair, not just raw telemetry rows.
- [ ] Proximity hazards: turn `Proximity Distance` / `Proximity Alert` into a
      ranked "active hazards" view instead of a flat table.
- [ ] Incident logging: add a way to *create* an incident from the UI (currently
      read-only), wired to `POST /api/incidents`.
- [ ] Training hub format decision (recommend: e-learning video catalog + a
      lightweight quiz/simulation stub) + certification-expiry warnings surfaced
      prominently.
- [ ] Expand anomaly detection beyond idling/fuel z-scores to pattern-based flags
      (repeated `Safety Alert Triggered` events, RPM/load-cycle combinations).
- [ ] Surface anomalies in the Dashboard tab (currently its own separate tab).
- [ ] Confidence range on task-time predictions (quantile regression or the
      RandomForest's per-tree spread); feed predicted time into the Dashboard
      task list ("est. vs predicted").
- [ ] Loading/error states for all `fetch` calls in `api.ts`.

### Phase 2 — Add the four operator-augmentation features (simulated, edge-ready)
- [ ] Extend `scripts/generate_data.py` for the new/extended CSVs above (fatigue,
      ergonomics, environment, coaching events, plus schema extensions).
- [ ] Build `/api/fatigue`, `/api/coaching`, `/api/ergonomics`, `/api/environment`
      backend endpoints implementing the rules in "Feature deep-dives" above.
- [ ] Build matching frontend panels: Fatigue gauge, Coaching feed, Ergonomics
      vibration chart, Environment/HVAC status.
- [ ] Cross-link coaching + fatigue alerts into the Dashboard and Safety tabs
      (not siloed in their own tabs), matching the anomaly-surfacing work in Phase 1.
- [ ] Real dashboard landing view replacing tab-only navigation once safety,
      anomalies, fatigue, and coaching are cross-linked.
- [ ] Basic responsive layout check (in-cab, tablet-sized screen).

### Phase 3 — Ops / deployment
- [ ] `docker-compose` (or similar) to run backend + frontend together for demo.
- [ ] CI: lint (`oxlint`, backend `ruff`/`black` if added) + test on push.
- [ ] Replace synthetic CSVs with a real ingestion path (real telemetry/CAN-bus feed,
      real IR camera Edge AI node) before any production use — explicitly called out
      in `CLAUDE.md`, and prerequisite to actually deploying outcomes 6–8 beyond a demo.

## Suggested next milestone

Ship a coherent demo: cached data loading + trained-at-startup model, incident
creation, certification-expiry banner, anomalies surfaced on the dashboard, and
predicted time shown per task (all Phase 1) — plus at least the fatigue and coaching
panels from Phase 2, since those two features carry the most "creative differentiator"
weight in a demo. That turns the eight outcome areas from independent tabs into one
connected assistant that protects, coaches, and adapts to the operator in real time,
which is both the brief's actual ask and the creative extension of it.

## Team assignments

Four workstreams, each owning exactly two outcomes **end-to-end** (backend logic,
data schema, frontend component, API client) with **no outcome, file, or task
assigned to more than one member**. Fill in names below.

Current repo files, for reference:
`backend/app/{main.py, data.py, ml.py}`, `frontend/src/{App.tsx, api.ts}`,
`frontend/src/components/{Dashboard,Safety,Training,Anomalies,Predictor}.tsx`.

### Ground rules to prevent overlap

1. **Backend gets split into one router per domain** — `backend/app/routers/<domain>.py`
   — instead of everyone editing `main.py`. Only the person who owns a domain touches
   its router file. Member 1 does the one-time split (moving existing logic out of
   `main.py` into `routers/dashboard.py` and `routers/predictor.py`) and scaffolds
   empty router files for the others to fill in.
2. **Frontend API calls get split the same way** — `frontend/src/api/<domain>.ts`
   instead of a monolithic `api.ts`. Same rule: one owner per file.
3. **Each member owns their component file(s) outright** — nobody edits another
   member's `.tsx` file. If Member A's dashboard needs data from Member B's feature,
   Member B exports a small summary component (e.g. `AnomaliesSummary`) from their
   own file, and Member A imports and places it — Member A never edits Member B's file.
4. **Two files stay genuinely shared and are append-only**: `frontend/src/App.tsx`
   (tab/route registration) and `scripts/generate_data.py` (each member adds their own
   `generate_<domain>()` function; Member 1 wires the calls together). Append-only
   means: add your own import/line, never edit a line someone else added.
5. Backend infra (caching, model persistence, tests, CI, docker) lives in
   `data.py`/`ml.py`/CI config — files no domain router touches — so Member 1 can do
   that work in parallel with everyone else without blocking or colliding.

### Member 1 — Dashboard, task-time estimation & platform infra (_name: ____)
**Files:** `backend/app/data.py`, `backend/app/ml.py`,
`backend/app/routers/{dashboard,predictor}.py`,
`frontend/src/api/{dashboard,predictor}.ts`,
`frontend/src/components/{Dashboard,Predictor}.tsx`, CI config, `docker-compose.yml`.
- [ ] One-time: split `main.py` into `routers/`, scaffold empty router files for
      Members 2–4, split `api.ts` into `api/` the same way
- [ ] Cache `load_all()` (startup load or `lru_cache`/mtime check)
- [ ] Persist/train-at-startup the task-time model (`joblib` cache)
- [ ] `/api/dashboard/{operator_id}` or `?date=` filtering
- [ ] Input validation / error responses for unknown machine/operator IDs
- [ ] Confidence range on task-time predictions, shown in `Predictor.tsx`
- [ ] Real dashboard landing view: import and place summary components exported
      by Members 2–4 (their files, not touched by Member 1 directly)
- [ ] Smoke tests for every endpoint (`pytest`); `docker-compose`; CI (lint + test)

### Member 2 — Safety & coaching (_name: ____)
**Files:** `backend/app/routers/{safety,coaching}.py`,
`frontend/src/api/{safety,coaching}.ts`,
`frontend/src/components/{Safety,Coaching}.tsx` (Coaching is new).
- [ ] Seatbelt compliance + ranked proximity-hazards view
- [ ] Incident logging: `POST /api/incidents` + UI to create one
- [ ] Fatigue sub-feature: extend `telemetry.csv` generation with fatigue fields
      (`Fatigue Score`, `Eye Closure Duration`, `Alert Level`) inside their own
      `generate_safety()` function in `generate_data.py`; gauge in `Safety.tsx`
- [ ] `coaching_events.csv` schema + `/api/coaching` + `Coaching.tsx` feed panel
- [ ] Export `SafetySummary` / `CoachingSummary` components for Member 1 to import

### Member 3 — Ergonomics & environment (_name: ____)
**Files:** `backend/app/routers/{ergonomics,environment}.py`,
`frontend/src/api/{ergonomics,environment}.ts`,
`frontend/src/components/{Ergonomics,Environment}.tsx` (both new).
- [ ] `ergonomics.csv` schema (own `generate_ergonomics()` in `generate_data.py`)
      + `/api/ergonomics` + vibration chart panel
- [ ] `environment.csv` schema (own `generate_environment()`)
      + `/api/environment` + CO₂/HVAC status panel
- [ ] Export `ErgonomicsSummary` / `EnvironmentSummary` components for Member 1

### Member 4 — Training hub & anomaly detection (_name: ____)
**Files:** `backend/app/routers/{training,anomalies}.py`,
`frontend/src/api/{training,anomalies}.ts`,
`frontend/src/components/{Training,Anomalies}.tsx`.
- [ ] Training hub format (e-learning video catalog + quiz/simulation stub)
- [ ] Certification-expiry warnings surfaced prominently in `Training.tsx`
- [ ] Expand anomaly detection beyond idling/fuel z-scores (repeated safety
      alerts, RPM/load-cycle combos)
- [ ] Loading/error states for their own `fetch` calls in `api/{training,anomalies}.ts`
      (each member does this for their own API files — not a shared task)
- [ ] Export `AnomaliesSummary` component for Member 1 to place on the dashboard
- [ ] Responsive layout check for in-cab tablet-sized screens (applies globally,
      but implemented as each member checking their own component — not one
      person editing everyone else's files)
      