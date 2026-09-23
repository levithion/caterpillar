import { API_BASE_URL } from "../config";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const BASE_URL = API_BASE_URL;

export type Row = Record<string, string | number | null>;

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new ApiError(detail || `Request failed: ${path}`, res.status);
  }
  return res.json() as Promise<T>;
}

export async function get(path: string): Promise<Row[]> {
  return apiGet<Row[]>(path);
}

export async function getOne<T>(path: string): Promise<T> {
  return apiGet<T>(path);
}
