import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { API_BASE_URL, STREAM_SERIES_WINDOW } from "../config";
import type { ErgonomicsCurrent, ErgonomicsReading } from "../api/ergonomics";
import type { EnvironmentCurrent, EnvironmentReading } from "../api/environment";
import { useMachine } from "./MachineContext";

export type LiveStreamPayload = {
  timestamp: string;
  machine_id: string;
  operator_id: string;
  engine?: string;
  ergonomics: {
    current: ErgonomicsCurrent;
    reading: ErgonomicsReading;
  } | null;
  environment: {
    current: EnvironmentCurrent;
    reading: EnvironmentReading;
  };
};

type LiveDataState = {
  connected: boolean;
  ergonomicsCurrent: ErgonomicsCurrent | null;
  environmentCurrent: EnvironmentCurrent | null;
  ergonomicsSeries: ErgonomicsReading[];
  environmentSeries: EnvironmentReading[];
  lastTick: Date | null;
  tickCount: number;
  engine: string;
  error: string | null;
  reconnect: () => void;
};

const LiveDataContext = createContext<LiveDataState | null>(null);

export function LiveDataProvider({ children }: { children: ReactNode }) {
  const { machineId, selectedMachine } = useMachine();
  const [connected, setConnected] = useState(false);
  const [ergonomicsCurrent, setErgonomicsCurrent] = useState<ErgonomicsCurrent | null>(null);
  const [environmentCurrent, setEnvironmentCurrent] = useState<EnvironmentCurrent | null>(null);
  const [ergonomicsSeries, setErgonomicsSeries] = useState<ErgonomicsReading[]>([]);
  const [environmentSeries, setEnvironmentSeries] = useState<EnvironmentReading[]>([]);
  const [lastTick, setLastTick] = useState<Date | null>(null);
  const [tickCount, setTickCount] = useState(0);
  const [engine, setEngine] = useState("connecting");
  const [error, setError] = useState<string | null>(null);
  const sourceRef = useRef<EventSource | null>(null);
  const mountedRef = useRef(true);

  const appendPoint = useCallback(<T,>(prev: T[], point: T): T[] => {
    const next = [...prev, point];
    return next.length > STREAM_SERIES_WINDOW ? next.slice(-STREAM_SERIES_WINDOW) : next;
  }, []);

  const connect = useCallback(() => {
    if (!machineId) return;

    sourceRef.current?.close();
    setConnected(false);
    setError(null);
    setErgonomicsSeries([]);
    setEnvironmentSeries([]);
    setErgonomicsCurrent(null);
    setEnvironmentCurrent(null);
    setTickCount(0);

    const url = `${API_BASE_URL}/live/stream?machine_id=${encodeURIComponent(machineId)}`;
    const es = new EventSource(url);
    sourceRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as LiveStreamPayload;
        if (data.engine) setEngine(data.engine);
        if (data.ergonomics) {
          setErgonomicsCurrent(data.ergonomics.current);
          setErgonomicsSeries((s) => appendPoint(s, data.ergonomics!.reading));
        }
        if (data.environment) {
          setEnvironmentCurrent(data.environment.current);
          setEnvironmentSeries((s) => appendPoint(s, data.environment.reading));
        }
        setLastTick(new Date());
        setTickCount((c) => c + 1);
      } catch {
        setError("Failed to parse live stream");
      }
    };

    es.onerror = () => {
      setConnected(false);
      setError("Live stream disconnected — reconnecting…");
      es.close();
      setTimeout(() => {
        if (mountedRef.current) connect();
      }, 2000);
    };
  }, [machineId, appendPoint]);

  const reconnect = useCallback(() => {
    connect();
  }, [connect]);

  useEffect(() => {
    mountedRef.current = true;
    if (!machineId || !selectedMachine) {
      sourceRef.current?.close();
      setConnected(false);
      return;
    }
    connect();
    return () => {
      mountedRef.current = false;
      sourceRef.current?.close();
      setConnected(false);
    };
  }, [machineId, selectedMachine, connect]);

  const value = useMemo(
    () => ({
      connected,
      ergonomicsCurrent,
      environmentCurrent,
      ergonomicsSeries,
      environmentSeries,
      lastTick,
      tickCount,
      engine,
      error,
      reconnect,
    }),
    [
      connected,
      ergonomicsCurrent,
      environmentCurrent,
      ergonomicsSeries,
      environmentSeries,
      lastTick,
      tickCount,
      engine,
      error,
      reconnect,
    ],
  );

  return <LiveDataContext.Provider value={value}>{children}</LiveDataContext.Provider>;
}

export function useLiveData() {
  const ctx = useContext(LiveDataContext);
  if (!ctx) {
    throw new Error("useLiveData must be used within LiveDataProvider");
  }
  return ctx;
}
