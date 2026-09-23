from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_TABLES = {
    "machines": "machines.csv",
    "tasks": "tasks.csv",
    "telemetry": "telemetry.csv",
    "incidents": "safety_incidents.csv",
    "training_modules": "training_modules.csv",
    "training_records": "training_records.csv",
}

_cache: dict[str, pd.DataFrame] | None = None
_cache_mtime: float | None = None


def _data_mtime() -> float:
    return max((p.stat().st_mtime for p in DATA_DIR.glob("*.csv")), default=0.0)


def load_all() -> dict[str, pd.DataFrame]:
    """Load all CSVs, cached in memory. Reloads only if a CSV file changes on
    disk (e.g. after rerunning scripts/generate_data.py), so normal requests
    don't re-read the filesystem every time.

    Operator/user accounts live in the SQLite database (see app.db), not a
    CSV, since they're mutated by every signup rather than being part of the
    static synthetic dataset. They're fetched fresh on every call instead of
    going through this cache."""
    global _cache, _cache_mtime
    # Local import: avoids a circular import, since app.db imports DATA_DIR from here.
    from app import db

    current_mtime = _data_mtime()
    if _cache is None or _cache_mtime != current_mtime:
        _cache = {name: pd.read_csv(DATA_DIR / filename) for name, filename in _TABLES.items()}
        _cache_mtime = current_mtime
    return {**_cache, "operators": db.get_all()}
