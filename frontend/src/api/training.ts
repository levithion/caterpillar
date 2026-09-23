import { get, type Row } from "./client";

export const trainingApi = {
  operators: () => get("/operators"),
  trainingModules: () => get("/training/modules"),
  trainingRecords: (operatorId?: string) =>
    get(operatorId ? `/training/records?operator_id=${encodeURIComponent(operatorId)}` : "/training/records"),
};

export type { Row };
