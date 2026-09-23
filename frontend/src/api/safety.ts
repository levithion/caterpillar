import { get, type Row } from "./client";

export const safetyApi = {
  telemetry: (machineId?: string) =>
    get(machineId ? `/telemetry?machine_id=${encodeURIComponent(machineId)}` : "/telemetry"),
  incidents: () => get("/incidents"),
};

export type { Row };

// TODO (Member 2): fatigue() + coaching() calls once /api/fatigue and
// /api/coaching exist (this file is scaffolded, not owned by Member 1).
