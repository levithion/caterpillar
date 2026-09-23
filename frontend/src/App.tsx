import { useEffect, useState } from "react";
import "./App.css";
import { MachineProvider, useMachine } from "./context/MachineContext";
import { LiveDataProvider, useLiveData } from "./context/LiveDataContext";
import { MachineBadge, MachineSelector } from "./components/MachineSelector";
import { Ergonomics } from "./components/Ergonomics";
import { Environment } from "./components/Environment";

function LiveStatusBar() {
  const { machineId } = useMachine();
  const { connected, lastTick, tickCount, engine, error, reconnect } = useLiveData();

  return (
    <div className="live-status-bar">
      <span className={`live-pill ${connected ? "on" : "off"}`}>
        {connected ? "● LIVE" : "○ OFFLINE"}
      </span>
      <span className={`engine-pill engine-${engine}`}>
        {engine === "ml" ? "ML Engine" : engine === "rules" ? "Rule Fallback" : "Connecting"}
      </span>
      {machineId && <span className="muted">Streaming {machineId}</span>}
      {lastTick && (
        <span className="muted">
          Last tick: {lastTick.toLocaleTimeString()} ({tickCount} readings)
        </span>
      )}
      {error && (
        <button type="button" className="reconnect-btn" onClick={reconnect}>
          Reconnect
        </button>
      )}
    </div>
  );
}

function Dashboard() {
  const { machineId, selectedMachine, loading } = useMachine();
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL?.replace("/api", "") ?? "http://localhost:8000";
    fetch(`${base}/health`)
      .then((r) => setApiStatus(r.ok ? "ok" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="app">
      <header>
        <div className="header-brand">
          <h1>Operator Health Monitor</h1>
          <p className="subtitle">Real-time ergonomics &amp; environment automation</p>
        </div>
        <div className="header-controls">
          <MachineSelector />
          <span className={`status-dot ${apiStatus}`} title={`API ${apiStatus}`} />
        </div>
      </header>

      <main>
        {loading ? (
          <p className="muted">Loading machine context…</p>
        ) : !machineId || !selectedMachine ? (
          <p className="muted">No machines available. Run <code>make seed</code> to generate data.</p>
        ) : (
          <>
            <MachineBadge />
            <LiveStatusBar />
            <p className="context-hint muted">
              Sensors calculate readings every second for <strong>{machineId}</strong>.
              Graphs and metrics update automatically on the dashboard.
            </p>
            <div className="dashboard-grid">
              <section aria-label="Ergonomics monitoring">
                <h2>Ergonomics</h2>
                <Ergonomics />
              </section>
              <section aria-label="Environment monitoring">
                <h2>Environment</h2>
                <Environment />
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <MachineProvider>
      <LiveDataProvider>
        <Dashboard />
      </LiveDataProvider>
    </MachineProvider>
  );
}

export default App;
