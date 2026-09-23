import logging
from pathlib import Path

import pandas as pd

from app import db
from app.config import get_settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_TABLES = {
    "machines": "machines.csv",
    "tasks": "tasks.csv",
    "telemetry": "telemetry.csv",
    "incidents": "safety_incidents.csv",
    "coaching_events": "coaching_events.csv",
    "fatigue_events": "fatigue_events.csv",
    "training_modules": "training_modules.csv",
    "training_records": "training_records.csv",
}

_ERGONOMICS_RENAMES = {
    "Chassis Accel X (g)": "Chassis Accel X",
    "Chassis Accel Y (g)": "Chassis Accel Y",
    "Chassis Accel Z (g)": "Chassis Accel Z",
    "Seat Accel X (g)": "Seat Accel X",
    "Seat Accel Y (g)": "Seat Accel Y",
    "Seat Accel Z (g)": "Seat Accel Z",
}

_ENVIRONMENT_RENAMES = {
    "Cab PM2.5 (ug/m3)": "Cab PM2.5 (µg/m³)",
}

_load_all_cache: dict[str, pd.DataFrame] | None = None
_load_all_mtime: float | None = None
_file_cache: dict[str, tuple[float, pd.DataFrame]] = {}


def _data_dir() -> Path:
    return get_settings().data_dir


def _data_mtime(data_dir: Path) -> float:
    return max((p.stat().st_mtime for p in data_dir.glob("*.csv")), default=0.0)


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def _normalize_columns(filename: str, df: pd.DataFrame) -> pd.DataFrame:
    if filename == "ergonomics.csv":
        df = df.rename(columns={k: v for k, v in _ERGONOMICS_RENAMES.items() if k in df.columns})
        if "Damping Setting" in df.columns:
            df["Damping Setting"] = df["Damping Setting"].astype(str).str.lower()
    elif filename == "environment.csv":
        df = df.rename(columns={k: v for k, v in _ENVIRONMENT_RENAMES.items() if k in df.columns})
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Load platform CSV tables, cached until any data file changes.

    Operator/user accounts live in the SQLite database (see app.db), not a
    CSV, since they're mutated by every signup rather than being part of the
    static synthetic dataset. They're fetched fresh on every call instead of
    going through this cache."""
    global _load_all_cache, _load_all_mtime
    data_dir = _data_dir()
    current_mtime = _data_mtime(data_dir)
    if _load_all_cache is None or _load_all_mtime != current_mtime:
        _load_all_cache = {
            name: pd.read_csv(data_dir / filename)
            for name, filename in _TABLES.items()
            if (data_dir / filename).exists()
        }
        _load_all_mtime = current_mtime
        _file_cache.clear()
    return {**_load_all_cache, "operators": db.get_all()}


def load_csv(name: str) -> pd.DataFrame:
    """Load a single CSV with mtime-based cache invalidation."""
    data_dir = _data_dir()
    path = data_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")

    mtime = _mtime(path)
    cached = _file_cache.get(name)
    if cached and cached[0] == mtime:
        return cached[1]

    logger.info("Loading %s", path)
    df = _normalize_columns(name, pd.read_csv(path))
    _file_cache[name] = (mtime, df)
    return df


def preload() -> None:
    """Warm caches at startup."""
    try:
        load_all()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Platform data preload skipped: %s", exc)
    for name in ("machines.csv", "ergonomics.csv", "environment.csv"):
        try:
            load_csv(name)
        except FileNotFoundError:
            logger.warning("Skipping preload for missing file: %s", name)


def clear_cache() -> None:
    global _load_all_cache, _load_all_mtime
    _load_all_cache = None
    _load_all_mtime = None
    _file_cache.clear()
