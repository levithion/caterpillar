import { API_BASE_URL } from "../config";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new ApiError(detail || `Request failed: ${path}`, res.status);
  }
  return res.json() as Promise<T>;
}
