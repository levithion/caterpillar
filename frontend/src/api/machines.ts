import { apiGet } from "./client";

export type MachineCapabilities = {
  ergonomics: boolean;
  environment: boolean;
};

export type Machine = {
  id: string;
  type: string;
  model: string;
  status: string;
  has_active_suspension: boolean;
  capabilities: MachineCapabilities;
};

export async function fetchMachines(): Promise<Machine[]> {
  const data = await apiGet<{ machines: Machine[] }>("/machine-capabilities");
  return data.machines;
}

export async function fetchMachine(machineId: string): Promise<Machine> {
  return apiGet<Machine>(`/machine-capabilities/${encodeURIComponent(machineId)}`);
}
