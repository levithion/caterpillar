import { useEffect, useState } from "react";
import { api, type Row } from "../api";

export function Dashboard() {
  const [tasks, setTasks] = useState<Row[]>([]);
  const [machines, setMachines] = useState<Row[]>([]);

  useEffect(() => {
    api.tasks().then(setTasks);
    api.machines().then(setMachines);
  }, []);

  const machineById: Record<string, Row> = Object.fromEntries(machines.map((m) => [m["Machine ID"], m]));

  return (
    <div className="panel">
      <h2>Daily Task Dashboard</h2>
      <table>
        <thead>
          <tr>
            <th>Task</th>
            <th>Type</th>
            <th>Machine</th>
            <th>Weather</th>
            <th>Priority</th>
            <th>Est. (min)</th>
            <th>Actual (min)</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t["Task ID"] as string}>
              <td>{t["Task ID"]}</td>
              <td>{t["Task Type"]}</td>
              <td>{t["Machine ID"]}</td>
              <td>{t["Weather"]}</td>
              <td>
                <span className={`badge priority-${String(t["Priority"]).toLowerCase()}`}>
                  {t["Priority"]}
                </span>
              </td>
              <td>{t["Estimated Time (min)"]}</td>
              <td>{t["Actual Time (min)"] ?? "—"}</td>
              <td>
                <span className={`badge status-${String(t["Status"]).toLowerCase().replace(" ", "-")}`}>
                  {t["Status"]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Machine Health</h3>
      <div className="cards">
        {Object.values(machineById).map((m) => (
          <div className="card" key={m["Machine ID"] as string}>
            <strong>{m["Machine ID"]}</strong> — {m["Type"]}
            <div>Engine Hours: {m["Total Engine Hours"]}</div>
            <div>Next Maintenance: {m["Next Maintenance Due"]}</div>
            <span className={`badge status-${String(m["Status"]).toLowerCase()}`}>{m["Status"]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
