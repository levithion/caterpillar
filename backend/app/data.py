from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "machines": _load("machines.csv"),
        "operators": _load("operators.csv"),
        "tasks": _load("tasks.csv"),
        "telemetry": _load("telemetry.csv"),
        "incidents": _load("safety_incidents.csv"),
        "training_modules": _load("training_modules.csv"),
        "training_records": _load("training_records.csv"),
    }
