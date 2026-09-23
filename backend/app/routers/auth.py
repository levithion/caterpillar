import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data import DATA_DIR, load_all
from app.utils import records

router = APIRouter(tags=["auth"])

SKILL_LEVELS = ["Beginner", "Intermediate", "Expert"]
SHIFTS = ["Day", "Night"]


class SignupRequest(BaseModel):
    name: str
    skill_level: str
    shift: str


class LoginRequest(BaseModel):
    operator_id: str


def _next_operator_id(operators: pd.DataFrame) -> str:
    numbers = operators["Operator ID"].str.extract(r"OP(\d+)")[0].dropna().astype(int)
    next_number = (numbers.max() + 1) if not numbers.empty else 1001
    return f"OP{next_number}"


@router.post("/api/operators/signup")
def signup(request: SignupRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="name is required")
    if request.skill_level not in SKILL_LEVELS:
        raise HTTPException(status_code=400, detail=f"skill_level must be one of {SKILL_LEVELS}")
    if request.shift not in SHIFTS:
        raise HTTPException(status_code=400, detail=f"shift must be one of {SHIFTS}")

    operators = load_all()["operators"]
    new_row = {
        "Operator ID": _next_operator_id(operators),
        "Name": request.name.strip(),
        "Skill Level": request.skill_level,
        "Certifications": "None",
        "License Expiry": "",
        "Date of Joining": pd.Timestamp.now().date().isoformat(),
        "Shift": request.shift,
        "Contact": "",
        "Typical Fatigue Risk": "Low",
        "Weight Class": "Medium",
    }
    updated = pd.concat([operators, pd.DataFrame([new_row])], ignore_index=True)
    updated.to_csv(DATA_DIR / "operators.csv", index=False)
    return new_row


@router.post("/api/operators/login")
def login(request: LoginRequest):
    operators = load_all()["operators"]
    match = operators[operators["Operator ID"] == request.operator_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Operator not found")
    return records(match)[0]
