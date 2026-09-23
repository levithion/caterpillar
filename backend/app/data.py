import logging
from pathlib import Path

import pandas as pd

from app.config import get_settings

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[float, pd.DataFrame]] = {}


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def load_csv(name: str) -> pd.DataFrame:
    """Load a CSV with mtime-based cache invalidation."""
    settings = get_settings()
    path = settings.data_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")

    mtime = _mtime(path)
    cached = _cache.get(name)
    if cached and cached[0] == mtime:
        return cached[1]

    logger.info("Loading %s", path)
    df = pd.read_csv(path)
    _cache[name] = (mtime, df)
    return df


def preload() -> None:
    """Warm cache at startup."""
    for name in ("machines.csv", "operators.csv", "ergonomics.csv", "environment.csv"):
        try:
            load_csv(name)
        except FileNotFoundError:
            logger.warning("Skipping preload for missing file: %s", name)


def clear_cache() -> None:
    _cache.clear()


def records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notnull(df), None).to_dict(orient="records")
