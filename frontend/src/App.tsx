import { useState } from "react";
import "./App.css";
import { Dashboard } from "./components/Dashboard";
import { Safety } from "./components/Safety";
import { Training } from "./components/Training";
import { Anomalies } from "./components/Anomalies";
import { Predictor } from "./components/Predictor";
import { Login } from "./components/Login";
import type { Operator } from "./api/auth";

const TABS = [
  { id: "dashboard", label: "Dashboard", component: Dashboard },
  { id: "safety", label: "Safety", component: Safety },
  { id: "training", label: "Training", component: Training },
  { id: "anomalies", label: "Anomalies", component: Anomalies },
  { id: "predictor", label: "Task Time", component: Predictor },
] as const;

const STORAGE_KEY = "soa_operator";

function App() {
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
    <div className="app">
      <header>
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
  );
}

export default App;
