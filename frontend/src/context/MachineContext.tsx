import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { fetchMachines, type Machine } from "../api/machines";

const STORAGE_KEY = "selectedMachineId";

type MachineContextValue = {
  machines: Machine[];
  machineId: string | null;
  selectedMachine: Machine | null;
  setMachineId: (id: string) => void;
  loading: boolean;
  error: string | null;
};

const MachineContext = createContext<MachineContextValue | null>(null);

function readStoredMachineId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function storeMachineId(id: string) {
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {
    /* ignore quota / private mode */
  }
}

export function MachineProvider({ children }: { children: ReactNode }) {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [machineId, setMachineIdState] = useState<string | null>(readStoredMachineId());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMachines()
      .then((list) => {
        setMachines(list);
        const stored = readStoredMachineId();
        const validStored = stored && list.some((m) => m.id === stored);
        const initial = validStored ? stored : list[0]?.id ?? null;
        setMachineIdState(initial);
        if (initial) storeMachineId(initial);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load machines"))
      .finally(() => setLoading(false));
  }, []);

  const setMachineId = useCallback((id: string) => {
    setMachineIdState(id);
    storeMachineId(id);
  }, []);

  const selectedMachine = useMemo(
    () => machines.find((m) => m.id === machineId) ?? null,
    [machines, machineId],
  );

  const value = useMemo(
    () => ({
      machines,
      machineId,
      selectedMachine,
      setMachineId,
      loading,
      error,
    }),
    [machines, machineId, selectedMachine, setMachineId, loading, error],
  );

  return <MachineContext.Provider value={value}>{children}</MachineContext.Provider>;
}

/** Shared machine selection — use in any feature panel or dashboard. */
export function useMachine() {
  const ctx = useContext(MachineContext);
  if (!ctx) {
    throw new Error("useMachine must be used within MachineProvider");
  }
  return ctx;
}
