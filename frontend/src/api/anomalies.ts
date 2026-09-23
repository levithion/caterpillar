import { apiGet, get, type Row } from "../api/client";

export type ModelAnomaly = {
  timestamp: string;
  machine_id: string;
  operator_id: string;
  anomaly_score: number;
  severity: string;
  top_drivers: string[];
};

export type FatigueCompareRow = {
  timestamp: string;
  machine_id: string;
  operator_id: string;
  fatigue_score: number;
  eye_closure_seconds: number;
  rule_alert_level: string;
  model_alert_level: string;
  model_probability: number;
  agreement: boolean;
};

export const anomaliesApi = {
  anomalies: () => get("/anomalies"),
  modelAnomalies: (limit = 20) =>
    apiGet<ModelAnomaly[]>(`/ml/telemetry-anomalies?limit=${limit}`),
};

export type { Row };
