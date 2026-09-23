import { useEffect, useState } from "react";
import { anomaliesApi } from "../api/anomalies";
import type { Row } from "../api/client";

export function Anomalies() {
  const [anomalies, setAnomalies] = useState<Row[]>([]);

  useEffect(() => {
    anomaliesApi.anomalies().then(setAnomalies);
  }, []);

  return (
    <div className="panel">
      <h2>Anomaly Detection</h2>
      <p>Telemetry readings that deviate significantly (|z-score| ≥ 2) from a machine's own average.</p>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Machine</th>
            <th>Operator</th>
            <th>Metric</th>
            <th>Value</th>
            <th>Machine Avg</th>
            <th>Z-score</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.map((a, i) => (
            <tr key={i}>
              <td>{a["timestamp"]}</td>
              <td>{a["machine_id"]}</td>
              <td>{a["operator_id"]}</td>
              <td>{a["metric"]}</td>
              <td>{a["value"]}</td>
              <td>{a["machine_mean"]}</td>
              <td>{a["z_score"]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
