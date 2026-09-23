# Operator Health Monitor — Ergonomics & Environment

Production-focused monitoring for CAT machine operators: **seat vibration / active suspension** and **cabin air quality / thermal health**.

## Features

- **Ergonomics** — chassis & seat acceleration, damping control, WBV exposure index, shock detection
- **Environment** — CO₂, PM2.5, cab temperature, facial temp, automatic HVAC override alerts
- **Shared machine context** — select a machine once; all panels follow automatically
- **ML-powered real-time stream** — Random Forest + Isolation Forest models trained on sensor history, inference every 1s
- Cached CSV data layer with mtime invalidation
- Health (`/health`) and readiness (`/ready`) endpoints
- Docker Compose for one-command deployment
- CI pipeline (tests + frontend build)

## Quick start

```bash
# 1. Install dependencies
make install

# 2. Generate synthetic sensor data
make seed

# 3. Start backend (terminal 1)
make backend

# 4. Start frontend (terminal 2)
make frontend
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Docker

```bash
make seed          # generate data first
make docker-up     # backend :8000, frontend :3000
```

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness check |
| `GET /ready` | Readiness (data files loaded) |
| `GET /api/live/stream?machine_id=` | **SSE** ML real-time predictions (1 tick/sec) |
| `GET /api/ml/status` | ML model training status & metadata |
| `POST /api/ml/train` | Retrain models from CSV history |
| `GET /api/machines` | All machines with capabilities flags |
| `GET /api/machines/{id}` | Single machine profile |
| `GET /api/ergonomics` | Current state + time series |
| `GET /api/ergonomics/machines` | Available machine IDs |
| `GET /api/environment` | Current state + time series |
| `GET /api/environment/machines` | Available machine IDs |

Query params: `machine_id`, `operator_id`, `limit` (max 1000).

## Configuration

Copy `.env.example` to `.env` and adjust thresholds:

- `CHASSIS_SHOCK_THRESHOLD` — g-force for shock alert (default 0.7)
- `CO2_WARNING_THRESHOLD` — ppm for HVAC override (default 1000)
- `FACIAL_TEMP_WARNING_THRESHOLD` — °C for rest warning (default 37.2)
- `VITE_POLL_INTERVAL_MS` — frontend refresh interval (default 5000)

## Tests

```bash
make test
```

## Project structure

```
backend/app/
  config.py          # Environment-based settings
  data.py            # Cached CSV loader
  main.py            # FastAPI app
  routers/           # API routes
  services/          # Business logic
frontend/src/
  api/               # Typed API clients
  components/        # Ergonomics & Environment panels
  hooks/usePolling.ts
scripts/generate_data.py
data/                # ergonomics.csv, environment.csv, machines.csv, operators.csv
```

## Data files

| File | Purpose |
|------|---------|
| `machines.csv` | Machine master (with active suspension flag) |
| `operators.csv` | Operator master |
| `ergonomics.csv` | 1 Hz vibration time-series |
| `environment.csv` | 1 Hz cabin sensor time-series |

Regenerate anytime: `make seed` or `SAMPLES_PER_MACHINE=600 make seed`
