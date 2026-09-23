import { get, type Row } from "./client";

export type { Row };

export async function getCoachingEvents(machineId?: string, severity?: string): Promise<Row[]> {
  const params = new URLSearchParams();
  if (machineId) params.set("machine_id", machineId);
  if (severity) params.set("severity", severity);
  const query = params.toString();
  return get(`/coaching${query ? `?${query}` : ""}`);
}
