# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository currently contains no code — only two reference images describing the
project brief and sample data. No application has been scaffolded yet, so there are no
build, lint, or test commands to document. Update this file once a project structure
(language, framework, package manager) is chosen.

## Project brief: Smart Operator Assistant for CAT machinery

**Background:** Construction equipment (excavators, loaders) is increasingly digitalized,
but operator-facing tools remain basic. The goal is an end-to-end intelligent assistant
that supports machine operators throughout their workday, improving efficiency, safety,
and training.

**Challenge:** Design and build a multi-functional operator interface for CAT machine
operators — not just a tool, but an intelligent companion.

**Expected outcomes:**
- **Daily task dashboard** — view scheduled tasks for the day.
- **Safety features** — real-time operator safety using available/assumed data:
  1. Seatbelt compliance
  2. Proximity hazards
  3. Incident logging
- **Operator training hub** — creative learning format (e-learning videos, instructor
  booking, or a simulation module).
- **Anomaly detection** — identify unusual machine usage patterns (e.g. excessive idling,
  unsafe operation patterns).
- **Task time estimation** — predict time to complete a task based on past data and
  environmental conditions.

### Sample data

Synthetic sample data lives in `data/` (generated, seeded, not real telemetry — replace
with real feeds before production use). Seven linked CSVs cover all expected outcomes:

- `machines.csv` — machine master data (ID, type, model, age, maintenance dates, engine hours, status)
- `operators.csv` — operator master data (ID, name, skill level, certifications, license expiry, shift)
- `tasks.csv` — daily schedule, joined to Machine ID + Operator ID (dashboard + task time estimation: Estimated Time vs Actual Time, Weather, Priority, Status)
- `telemetry.csv` — time-series sensor feed per machine/operator (Engine Hours, Fuel Used, Load Cycles, Idling Time, RPM, Speed, Seatbelt Status, Proximity Distance/Alert, Safety Alert Triggered) — source for safety features and anomaly detection
- `safety_incidents.csv` — incident log derived from flagged telemetry rows (Incident Type, Severity, Action Taken, Resolved)
- `training_modules.csv` — catalog of training content (Category, Format, Duration, Difficulty)
- `training_records.csv` — per-operator training progress, joined to Module ID (Status, Score, Certification Expiry)

Join keys: `Machine ID`, `Operator ID`, `Module ID` link the tables above. Regenerate the
CSVs with `python3 scripts/generate_data.py` (deterministic, seeded with `random.seed(42)`,
dates anchored to today). Edit that script to add rows/features; if you hand-edit the CSVs
directly instead, keep the join keys and column names stable.
