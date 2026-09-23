import { apiGet } from "./client";
import { SERIES_LIMIT } from "../config";

export type EnvironmentReading = {
  Timestamp: string;
  "Operator ID": string;
  "Machine ID": string;
  "Cab CO2 (ppm)": number;
  "Cab PM2.5 (µg/m³)": number;
  "Cab Temp (C)": number;
  "Cab Humidity (%)": number;
  "Operator Facial Temp (C)": number;
  "HVAC Override Active": string;
  "Fresh Air Flush Active": string;
};

export type EnvironmentCurrent = {
  timestamp: string;
  operator_id: string;
  machine_id: string;
  co2_ppm: number;
  pm25_ug_m3: number;
  cab_temp_c: number;
  cab_humidity_pct: number;
  facial_temp_c: number;
  hvac_override_active: boolean;
  fresh_air_flush_active: boolean;
  hvac_probability?: number;
  anomaly_score?: number;
  prediction_source?: string;
  warnings: string[];
};

export type EnvironmentResponse = {
  current: EnvironmentCurrent | null;
  series: EnvironmentReading[];
};

export async function fetchEnvironmentMachines(): Promise<string[]> {
  const data = await apiGet<{ machines: string[] }>("/environment/machines");
  return data.machines;
}

export async function fetchEnvironment(
  machineId?: string,
  limit = SERIES_LIMIT,
): Promise<EnvironmentResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (machineId) params.set("machine_id", machineId);
  return apiGet<EnvironmentResponse>(`/environment?${params}`);
}
