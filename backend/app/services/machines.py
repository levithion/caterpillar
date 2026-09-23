from app.data import load_csv


def list_machines() -> list[dict]:
    machines = load_csv("machines.csv")
    ergo_ids = set(load_csv("ergonomics.csv")["Machine ID"].unique())
    env_ids = set(load_csv("environment.csv")["Machine ID"].unique())

    result = []
    for _, row in machines.iterrows():
        mid = row["Machine ID"]
        has_suspension = row.get("Has Active Suspension", "No") == "Yes"
        result.append({
            "id": mid,
            "type": row["Type"],
            "model": row["Model"],
            "status": row["Status"],
            "has_active_suspension": has_suspension,
            "capabilities": {
                "ergonomics": has_suspension and mid in ergo_ids,
                "environment": mid in env_ids,
            },
        })
    return result


def get_machine(machine_id: str) -> dict | None:
    return next((m for m in list_machines() if m["id"] == machine_id), None)
