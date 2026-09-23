import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.data import load_all

_FEATURES = ["Task Type", "Weather", "Skill Level", "Age (yrs)"]


def _training_frame() -> pd.DataFrame:
    data = load_all()
    tasks = data["tasks"]
    operators = data["operators"][["Operator ID", "Skill Level"]]
    machines = data["machines"][["Machine ID", "Age (yrs)"]]

    completed = tasks[tasks["Status"] == "Completed"].copy()
    completed = completed.merge(operators, on="Operator ID", how="left")
    completed = completed.merge(machines, on="Machine ID", how="left")
    return completed.dropna(subset=["Actual Time (min)"])


def train_task_time_model() -> Pipeline:
    df = _training_frame()
    X = df[_FEATURES]
    y = df["Actual Time (min)"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["Task Type", "Weather", "Skill Level"]),
        ],
        remainder="passthrough",
    )
    model = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=200, random_state=42)),
    ])
    model.fit(X, y)
    return model


def predict_task_time(model: Pipeline, task_type: str, weather: str, skill_level: str, machine_age: float) -> float:
    row = pd.DataFrame([{
        "Task Type": task_type,
        "Weather": weather,
        "Skill Level": skill_level,
        "Age (yrs)": machine_age,
    }])
    return float(model.predict(row)[0])


def detect_anomalies(z_threshold: float = 2.0) -> list[dict]:
    data = load_all()
    telemetry = data["telemetry"].copy()
    anomalies = []

    for machine_id, group in telemetry.groupby("Machine ID"):
        for column in ["Idling Time (min)", "Fuel Used (L)"]:
            mean = group[column].mean()
            std = group[column].std(ddof=0)
            if not std:
                continue
            z_scores = (group[column] - mean) / std
            flagged = group[z_scores.abs() >= z_threshold]
            for _, row in flagged.iterrows():
                anomalies.append({
                    "timestamp": row["Timestamp"],
                    "machine_id": machine_id,
                    "operator_id": row["Operator ID"],
                    "metric": column,
                    "value": row[column],
                    "machine_mean": round(mean, 2),
                    "z_score": round(float((row[column] - mean) / std), 2),
                })

    anomalies.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return anomalies
