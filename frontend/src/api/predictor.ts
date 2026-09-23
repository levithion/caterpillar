import { BASE_URL } from "./client";

export type TaskTimePrediction = {
  predicted_minutes: number;
  lower_bound_minutes: number;
  upper_bound_minutes: number;
};

export const predictorApi = {
  predictTaskTime: async (payload: {
    task_type: string;
    weather: string;
    skill_level: string;
    machine_age: number;
  }): Promise<TaskTimePrediction> => {
    const res = await fetch(`${BASE_URL}/predict/task-time`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Prediction failed");
    return res.json() as Promise<TaskTimePrediction>;
  },
};
