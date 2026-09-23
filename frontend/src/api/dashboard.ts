import { get, type Row } from "./client";

export const dashboardApi = {
  machines: () => get("/machines"),
  tasks: (opts?: { operatorId?: string; date?: string }) => {
    const params = new URLSearchParams();
    if (opts?.operatorId) params.set("operator_id", opts.operatorId);
    if (opts?.date) params.set("task_date", opts.date);
    const qs = params.toString();
    return get(qs ? `/tasks?${qs}` : "/tasks");
  },
};

export type { Row };
