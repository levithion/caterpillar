import { get, getOne, BASE_URL, type Row } from "./client";

export type { Row };

export interface SafetySummaryData {
  seatbelt_compliance: Row[];
  proximity_hazards: Row[];
  latest_fatigue: Row[];
}

export async function getIncidents(): Promise<Row[]> {
  return get("/incidents");
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
  return getOne<SafetySummaryData>("/safety/summary");
}
