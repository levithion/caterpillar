const BASE_URL = "http://localhost:8000/api";

export type Row = Record<string, string | number | null>;

export interface SafetySummaryData {
  seatbelt_compliance: Row[];
  proximity_hazards: Row[];
  latest_fatigue: Row[];
}

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export async function getIncidents(): Promise<Row[]> {
  const res = await fetch(`${BASE_URL}/incidents`);
  if (!res.ok) throw new Error("Failed to load incidents");
  return res.json();
}

export async function createIncident(payload: {
  machine_id: string;
  operator_id: string;
  incident_type: string;
  severity: string;
  description?: string;
  action_taken?: string;
  location?: string;
}): Promise<Row> {
  const res = await fetch(`${BASE_URL}/incidents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create incident");
  return res.json();
}

export async function getSafetySummary(): Promise<SafetySummaryData> {
  const res = await fetch(`${BASE_URL}/safety/summary`);
  if (!res.ok) throw new Error("Failed to load safety summary");
  return res.json();
}
