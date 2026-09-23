import { get, type Row } from "./client";

export const anomaliesApi = {
  anomalies: () => get("/anomalies"),
};

export type { Row };
