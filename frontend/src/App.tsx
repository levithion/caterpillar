import { useEffect, useState } from "react";
import "./App.css";
import { Dashboard } from "./components/Dashboard";
import { Safety } from "./components/Safety";
import { Coaching } from "./components/Coaching";
import { Training } from "./components/Training";
import { Anomalies } from "./components/Anomalies";
import { Predictor } from "./components/Predictor";
import { Login } from "./components/Login";
import { CatLogo } from "./components/CatLogo";
import { Ergonomics } from "./components/Ergonomics";
import { Environment } from "./components/Environment";
import { MachineBadge, MachineSelector } from "./components/MachineSelector";
import { MachineProvider, useMachine } from "./context/MachineContext";
import { LiveDataProvider, useLiveData } from "./context/LiveDataContext";
import type { Operator } from "./api/auth";

const TABS = [
  { id: "dashboard", label: "Dashboard", component: Dashboard },
  { id: "safety", label: "Safety", component: Safety },
  { id: "coaching", label: "Coaching", component: Coaching },
  { id: "training", label: "Training", component: Training },
  { id: "anomalies", label: "Anomalies", component: Anomalies },
  { id: "predictor", label: "Task Time", component: Predictor },
  { id: "operator-health", label: "Operator Health", component: OperatorHealth },
] as const;

const STORAGE_KEY = "soa_operator";

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

function OperatorHealth() {
  const { machineId, selectedMachine, loading } = useMachine();
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL?.replace("/api", "") ?? "http://localhost:8000";
    fetch(`${base}/health`)
      .then((r) => setApiStatus(r.ok ? "ok" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  if (loading) {
    return <p className="muted">Loading machine context…</p>;
  }

  if (!machineId || !selectedMachine) {
    return (
      <p className="muted">
        No machines available. Run <code>make seed</code> to generate data.
      </p>
    );
  }

  return (
    <>
      <div className="header-controls operator-health-controls">
        <MachineSelector />
        <span className={`status-dot ${apiStatus}`} title={`API ${apiStatus}`} />
      </div>
      <MachineBadge />
      <LiveStatusBar />
      <p className="context-hint muted">
        Sensors calculate readings every second for <strong>{machineId}</strong>. Graphs and metrics
        update automatically on the dashboard.
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
  );
}

function AppShell() {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]["id"]>("dashboard");
  const [operator, setOperator] = useState<Operator | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? (JSON.parse(stored) as Operator) : null;
    } catch {
      return null;
    }
  });

  const handleLogin = (op: Operator) => {
    setOperator(op);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(op));
    } catch {
      // ignore unavailable storage
    }
  };

  const handleLogout = () => {
    setOperator(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore unavailable storage
    }
  };

  if (!operator) return <Login onLogin={handleLogin} />;

  const ActiveComponent = TABS.find((t) => t.id === activeTab)!.component;

  return (
    <MachineProvider>
      <LiveDataProvider>
        <div className="app">
          <header>
            <CatLogo />
            <h1>Smart Operator Assistant</h1>
            <nav>
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  className={tab.id === activeTab ? "active" : ""}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
            <div className="session">
              <span>
                {operator.Name} · {operator["Skill Level"]} · {operator["Operator ID"]}
              </span>
              <button onClick={handleLogout}>Log out</button>
            </div>
          </header>
          <main>
            <ActiveComponent />
          </main>
        </div>
      </LiveDataProvider>
    </MachineProvider>
  );
}

export default AppShell;
