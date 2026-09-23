import { useEffect, useState } from "react";
import { anomaliesApi, type ModelAnomaly } from "../api/anomalies";
import type { Row } from "../api/client";

type Source = "model" | "rule";

const driverLabels: Record<string, string> = {
  "Engine RPM": "RPM",
  "Speed (km/h)": "speed",
  "Hydraulic Pressure (bar)": "hydraulic pressure",
  "Load Cycles": "load cycles",
  "Idling Time (min)": "idling",
  "Fuel Used (L)": "fuel",
  "Slippage Events": "slippage",
};

export function Anomalies() {
  const [source, setSource] = useState<Source>("model");
  const [ruleRows, setRuleRows] = useState<Row[]>([]);
  const [modelRows, setModelRows] = useState<ModelAnomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    if (source === "model") {
      anomaliesApi
        .modelAnomalies()
        .then(setModelRows)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    } else {
      anomaliesApi
        .anomalies()
        .then(setRuleRows)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [source]);

  return (
    <div className="panel">
      <h2>Anomaly Detection</h2>

      <div className="source-toggle">
        <button
          className={source === "model" ? "active" : ""}
          onClick={() => setSource("model")}
        >
          🤖 Trained model
        </button>
        <button
          className={source === "rule" ? "active" : ""}
          onClick={() => setSource("rule")}
        >
          📏 Rule z-scores
        </button>
      </div>

      {source === "model" ? (
        <p>
          An IsolationForest, normalized against each machine's own history, flags
          readings that are <em>jointly</em> unusual across all signals — not just
          one big number.
        </p>
      ) : (
        <p>
          Baseline: readings with |z-score| ≥ 2 vs. a machine's own average on
          idling time and fuel use.
        </p>
      )}

      {loading && <p>Loading anomalies…</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && source === "model" && (
        <>
          <div className="chips-row">
            <span className="chip chip-red">{modelRows.length} flagged sessions</span>
            <span className="chip">learned per-machine norm</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Machine</th>
                <th>Operator</th>
                <th>Anomaly score</th>
                <th>What stands out</th>
              </tr>
            </thead>
            <tbody>
              {modelRows.slice(0, 15).map((a) => (
                <tr key={`${a.timestamp}-${a.machine_id}-${a.operator_id}`}>
                  <td>{a.timestamp}</td>
                  <td>{a.machine_id}</td>
                  <td>{a.operator_id}</td>
                  <td>
                    <span className="badge severity-high">{a.anomaly_score.toFixed(3)}</span>
                  </td>
                  <td className="drivers-cell">
                    {(a.top_drivers ?? []).map((d) => driverLabels[d] ?? d).join(" · ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {modelRows.length > 15 && (
            <p className="more-note">Showing top 15 of {modelRows.length}</p>
          )}
        </>
      )}

      {!loading && !error && source === "rule" && (
        <>
          <div className="chips-row">
            <span className="chip chip-amber">{ruleRows.length} z-score flags</span>
            <span className="chip">idling + fuel only</span>
          </div>
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
              {ruleRows.slice(0, 15).map((a, i) => (
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
          {ruleRows.length > 15 && (
            <p className="more-note">Showing top 15 of {ruleRows.length}</p>
          )}
        </>
      )}
    </div>
  );
}

export function AnomaliesSummary() {
  const [rows, setRows] = useState<ModelAnomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    anomaliesApi
      .modelAnomalies()
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="summary-card">Loading anomalies…</div>;

  return (
    <div className={`summary-card ${rows.length ? "summary-alert" : ""}`}>
      <h4>Anomalies</h4>
      <div className="summary-counts">
        <div className="glance-value glance-red">{rows.length}</div>
        <div className="glance-label">unusual sessions (model)</div>
      </div>
      {rows[0] && (
        <div className="latest-tip">
          Worst: <em>{rows[0].machine_id} at score {rows[0].anomaly_score}</em>
        </div>
      )}
    </div>
  );
}
