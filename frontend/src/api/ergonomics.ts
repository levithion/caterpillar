import { apiGet } from "./client";
import { SERIES_LIMIT } from "../config";

export type ErgonomicsReading = {
  Timestamp: string;
  "Operator ID": string;
  "Machine ID": string;
  "Chassis Accel X": number;
  "Chassis Accel Y": number;
  "Chassis Accel Z": number;
  "Seat Accel X": number;
  "Seat Accel Y": number;
  "Seat Accel Z": number;
  "Seat Pressure Center X": number;
  "Seat Pressure Center Y": number;
  "Seat Air Pressure (kPa)": number;
  "Damping Setting": string;
  "WBV Exposure Index": number;
};

export type ErgonomicsCurrent = {
  timestamp: string;
  operator_id: string;
  machine_id: string;
  chassis_accel_x: number;
  chassis_accel_y: number;
  chassis_accel_z: number;
  seat_accel_x: number;
  seat_accel_y: number;
  seat_accel_z: number;
  seat_pressure_center_x: number;
  seat_pressure_center_y: number;
  seat_air_pressure_kpa: number;
  damping_setting: string;
  wbv_exposure_index: number;
  shock_detected: boolean;
  shock_probability?: number;
  anomaly_score?: number;
  prediction_source?: string;
  recommendation: string;
};

export type ErgonomicsResponse = {
  current: ErgonomicsCurrent | null;
  series: ErgonomicsReading[];
};

export async function fetchErgonomicsMachines(): Promise<string[]> {
  const data = await apiGet<{ machines: string[] }>("/ergonomics/machines");
  return data.machines;
}

export async function fetchErgonomics(
  machineId?: string,
  limit = SERIES_LIMIT,
): Promise<ErgonomicsResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (machineId) params.set("machine_id", machineId);
  return apiGet<ErgonomicsResponse>(`/ergonomics?${params}`);
}
