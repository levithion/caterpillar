import { useState } from "react";
import "./App.css";
import { Dashboard } from "./components/Dashboard";
import { Safety } from "./components/Safety";
import { Coaching } from "./components/Coaching";
import { Training } from "./components/Training";
import { Anomalies } from "./components/Anomalies";
import { Predictor } from "./components/Predictor";

const TABS = [
  { id: "dashboard", label: "Dashboard", component: Dashboard },
  { id: "safety", label: "Safety", component: Safety },
  { id: "coaching", label: "Coaching", component: Coaching },
  { id: "training", label: "Training", component: Training },
  { id: "anomalies", label: "Anomalies", component: Anomalies },
  { id: "predictor", label: "Task Time", component: Predictor },
] as const;

function App() {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]["id"]>("dashboard");
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
      </header>
      <main>
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;
