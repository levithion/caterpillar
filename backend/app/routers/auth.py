import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from app.data import DATA_DIR, load_all
from app.security import hash_password, verify_password
from app.utils import clean_value

router = APIRouter(tags=["auth"])

SKILL_LEVELS = ["Beginner", "Intermediate", "Expert"]
SHIFTS = ["Day", "Night"]
_SENSITIVE_FIELDS = {"Password Hash", "Password Salt"}


class SignupRequest(BaseModel):
    name: str
    email: str
    country_code: str
    phone_number: str
    password: str
    skill_level: str
    shift: str


class LoginRequest(BaseModel):
    identifier: str  # email or Operator ID
    password: str


def _public(row: dict) -> dict:
    return {k: clean_value(v) for k, v in row.items() if k not in _SENSITIVE_FIELDS}


def _next_operator_id(operators: pd.DataFrame) -> str:
    numbers = operators["Operator ID"].str.extract(r"OP(\d+)")[0].dropna().astype(int)
    next_number = (numbers.max() + 1) if not numbers.empty else 1001
    return f"OP{next_number}"


@router.post("/api/operators/signup")
def signup(request: SignupRequest):
    name = request.name.strip()
    email = request.email.strip()
    country_code = request.country_code.strip()
    phone_number = request.phone_number.strip()

    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="a valid email is required")
    if not country_code or not phone_number:
        raise HTTPException(status_code=400, detail="country_code and phone_number are required")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="password must be at least 6 characters")
    if request.skill_level not in SKILL_LEVELS:
        raise HTTPException(status_code=400, detail=f"skill_level must be one of {SKILL_LEVELS}")
    if request.shift not in SHIFTS:
        raise HTTPException(status_code=400, detail=f"shift must be one of {SHIFTS}")

    operators = load_all()["operators"]
    if (operators["Email"].astype(str).str.lower() == email.lower()).any():
        raise HTTPException(status_code=400, detail="An operator with this email already exists")

    password_hash, salt = hash_password(request.password)
    new_row = {
        "Operator ID": _next_operator_id(operators),
        "Name": name,
        "Skill Level": request.skill_level,
        "Certifications": "None",
        "License Expiry": "",
        "Date of Joining": datetime.now(tz=timezone.utc).date().isoformat(),
        "Shift": request.shift,
        "Email": email,
        "Phone": f"{country_code} {phone_number}",
        "Password Hash": password_hash,
        "Password Salt": salt,
        "Typical Fatigue Risk": "Low",
        "Weight Class": "Medium",
    }
    updated = pd.concat([operators, pd.DataFrame([new_row])], ignore_index=True)
    updated.to_csv(DATA_DIR / "operators.csv", index=False)
    return _public(new_row)


@router.post("/api/operators/login")
def login(request: LoginRequest):
    operators = load_all()["operators"]
    identifier = request.identifier.strip()
    match = operators[
        (operators["Operator ID"] == identifier)
        | (operators["Email"].astype(str).str.lower() == identifier.lower())
    ]
    if match.empty:
        raise HTTPException(status_code=404, detail="Operator not found")

    row = match.iloc[0].to_dict()
    if not verify_password(request.password, str(row.get("Password Salt", "")), str(row.get("Password Hash", ""))):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return _public(row)
