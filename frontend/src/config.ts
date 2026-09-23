export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "/api" : "http://localhost:8000/api");
export const SERIES_LIMIT = Number(import.meta.env.VITE_SERIES_LIMIT ?? 120);
export const STREAM_SERIES_WINDOW = Number(import.meta.env.VITE_STREAM_SERIES_WINDOW ?? 120);
