import { BASE_URL } from "./client";

export type Operator = {
  "Operator ID": string;
  Name: string;
  "Skill Level": string;
  Shift: string;
  Email: string;
  Phone: string;
  [key: string]: string | number | null;
};

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const authApi = {
  signup: (payload: {
    name: string;
    email: string;
    country_code: string;
    phone_number: string;
    password: string;
    skill_level: string;
    shift: string;
  }) => post<Operator>("/operators/signup", payload),
  login: (payload: { identifier: string; password: string }) => post<Operator>("/operators/login", payload),
};
