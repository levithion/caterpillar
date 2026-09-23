const BASE_URL = "http://localhost:8000/api";

export type Row = Record<string, string | number | null>;

async function get(path: string): Promise<Row[]> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${path}`);
  return res.json();
}

export const api = {
  machines: () => get("/machines"),
  operators: () => get("/operators"),
  tasks: () => get("/tasks"),
  telemetry: (machineId?: string) =>
    get(machineId ? `/telemetry?machine_id=${encodeURIComponent(machineId)}` : "/telemetry"),
  incidents: () => get("/incidents"),
  trainingModules: () => get("/training/modules"),
  trainingRecords: (operatorId?: string) =>
    get(operatorId ? `/training/records?operator_id=${encodeURIComponent(operatorId)}` : "/training/records"),
  anomalies: () => get("/anomalies"),
  predictTaskTime: async (payload: {
    task_type: string;
    weather: string;
    skill_level: string;
    machine_age: number;
  }) => {
    const res = await fetch(`${BASE_URL}/predict/task-time`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Prediction failed");
    return res.json() as Promise<{ predicted_minutes: number }>;
  },
};
