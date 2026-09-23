const BASE_URL = "http://localhost:8000/api";

export type Row = Record<string, string | number | null>;

export async function get(path: string): Promise<Row[]> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${path}`);
  return res.json();
}

export async function getOne<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${path}`);
  return res.json() as Promise<T>;
}

export { BASE_URL };
