import { useEffect, useState } from "react";
import { safetyApi } from "../api/safety";
import type { Row } from "../api/client";

export function Safety() {
  const [telemetry, setTelemetry] = useState<Row[]>([]);
  const [incidents, setIncidents] = useState<Row[]>([]);

  useEffect(() => {
    safetyApi.telemetry().then(setTelemetry);
    safetyApi.incidents().then(setIncidents);
  }, []);

  const alerts = telemetry.filter((t) => t["Safety Alert Triggered"] === "Yes").slice(-10).reverse();

  return (
    <div className="panel">
      <h2>Safety</h2>

      <h3>Recent Alerts</h3>
      <div className="cards">
        {alerts.map((a, i) => (
          <div className="card alert" key={i}>
            <strong>{a["Machine ID"]}</strong> — {a["Timestamp"]}
            <div>Seatbelt: {a["Seatbelt Status"]}</div>
            <div>Proximity: {a["Proximity Distance (m)"]} m ({a["Proximity Alert"]})</div>
          </div>
        ))}
        {alerts.length === 0 && <p>No active alerts.</p>}
      </div>

      <h3>Incident Log</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Timestamp</th>
            <th>Machine</th>
            <th>Operator</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Action Taken</th>
            <th>Resolved</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((inc) => (
            <tr key={inc["Incident ID"] as string}>
              <td>{inc["Incident ID"]}</td>
              <td>{inc["Timestamp"]}</td>
              <td>{inc["Machine ID"]}</td>
              <td>{inc["Operator ID"]}</td>
              <td>{inc["Incident Type"]}</td>
              <td>
                <span className={`badge severity-${String(inc["Severity"]).toLowerCase()}`}>
                  {inc["Severity"]}
                </span>
              </td>
              <td>{inc["Action Taken"]}</td>
              <td>{inc["Resolved"]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
