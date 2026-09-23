import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from app.data import DATA_DIR

# Overridable so tests can point at an isolated, throwaway database instead
# of the developer's real operator accounts.
DB_PATH = Path(os.environ.get("OPERATORS_DB_PATH", DATA_DIR / "operators.db"))

_COLUMNS = [
    "Operator ID",
    "Name",
    "Skill Level",
    "Certifications",
    "License Expiry",
    "Date of Joining",
    "Shift",
    "Email",
    "Phone",
    "Password Hash",
    "Password Salt",
    "Typical Fatigue Risk",
    "Weight Class",
]

_QUOTED_COLUMNS = [f'"{c}"' for c in _COLUMNS]
_OTHER_COLUMNS_SQL = ", ".join(f'"{c}" TEXT' for c in _COLUMNS if c != "Operator ID")
_SELECT_COLUMNS_SQL = ", ".join(_QUOTED_COLUMNS)
_INSERT_SQL = (
    f"INSERT INTO users ({_SELECT_COLUMNS_SQL}) VALUES ({', '.join('?' for _ in _COLUMNS)})"
)


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the users table if needed, seeding it once from the synthetic
    operators.csv snapshot so existing dashboard/ML/training code (which
    joins on Operator ID) keeps working. Signups after this point are only
    ever written to the database, not back to the CSV, so operators.csv
    stays a clean, reproducible seed that scripts/generate_data.py can
    safely regenerate."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(f'CREATE TABLE IF NOT EXISTS users ("Operator ID" TEXT PRIMARY KEY, {_OTHER_COLUMNS_SQL})')
        (count,) = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if count == 0:
            seed_path = DATA_DIR / "operators.csv"
            if seed_path.exists():
                seed = pd.read_csv(seed_path)
                for column in _COLUMNS:
                    if column not in seed.columns:
                        seed[column] = None
                rows = seed[_COLUMNS].where(pd.notnull(seed[_COLUMNS]), None).values.tolist()
                conn.executemany(_INSERT_SQL, rows)


def get_all() -> pd.DataFrame:
    with _connect() as conn:
        rows = conn.execute(f"SELECT {_SELECT_COLUMNS_SQL} FROM users").fetchall()
    return pd.DataFrame([dict(row) for row in rows], columns=_COLUMNS)


def get_by_identifier(identifier: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            'SELECT * FROM users WHERE "Operator ID" = ? OR lower("Email") = lower(?)',
            (identifier, identifier),
        ).fetchone()
    return dict(row) if row else None


def email_exists(email: str) -> bool:
    with _connect() as conn:
        row = conn.execute('SELECT 1 FROM users WHERE lower("Email") = lower(?)', (email,)).fetchone()
    return row is not None


def next_operator_id() -> str:
    with _connect() as conn:
        ids = [row[0] for row in conn.execute('SELECT "Operator ID" FROM users').fetchall()]
    numbers = [int(i[2:]) for i in ids if i.startswith("OP") and i[2:].isdigit()]
    next_number = (max(numbers) + 1) if numbers else 1001
    return f"OP{next_number}"


def insert(row: dict) -> None:
    with _connect() as conn:
        conn.execute(_INSERT_SQL, [row.get(c) for c in _COLUMNS])
