const BASE_URL = "http://localhost:8000/api";

export type Row = Record<string, string | number | null>;

export async function getCoachingEvents(machineId?: string, severity?: string): Promise<Row[]> {
  const params = new URLSearchParams();
  if (machineId) params.set("machine_id", machineId);
  if (severity) params.set("severity", severity);
  const query = params.toString();
  const res = await fetch(`${BASE_URL}/coaching${query ? `?${query}` : ""}`);
  if (!res.ok) throw new Error("Failed to load coaching events");
  return res.json();
}
