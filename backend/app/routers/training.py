from fastapi import APIRouter, HTTPException

from app.data import load_all
from app.utils import records

router = APIRouter(tags=["training"])


@router.get("/api/operators")
def get_operators():
    operators = load_all()["operators"].drop(columns=["Password Hash", "Password Salt"], errors="ignore")
    return records(operators)


@router.get("/api/training/modules")
def get_training_modules():
    return records(load_all()["training_modules"])


@router.get("/api/training/records")
def get_training_records(operator_id: str | None = None):
    records_df = load_all()["training_records"]
    if operator_id:
        if operator_id not in set(load_all()["operators"]["Operator ID"]):
            raise HTTPException(status_code=404, detail=f"Unknown operator_id: {operator_id}")
        records_df = records_df[records_df["Operator ID"] == operator_id]
    return records(records_df)
