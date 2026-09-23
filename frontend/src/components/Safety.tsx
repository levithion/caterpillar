import { useEffect, useState } from "react";
import {
  createIncident,
  getIncidents,
  getSafetySummary,
  type Row,
  type SafetySummaryData,
} from "../api/safety";

function useSafetySummary() {
  const [summary, setSummary] = useState<SafetySummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSafetySummary()
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { summary, loading, error };
}

function useIncidents() {
  const [incidents, setIncidents] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    setLoading(true);
    setError(null);
    getIncidents()
      .then(setIncidents)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
  }, []);

  return { incidents, loading, error, refresh };
}

function FatigueGauge({
  score,
  alertLevel,
  eyeClosure,
  haptic,
}: {
  score: number;
  alertLevel: string;
  eyeClosure: number;
  haptic: string;
}) {
  const level = String(alertLevel).toLowerCase();
  const color =
    level === "critical" ? "#ef4444" : level === "caution" ? "#f59e0b" : "#22c55e";

  return (
    <div className="fatigue-gauge">
      <div className="gauge-bar-bg">
        <div
          className="gauge-bar-fill"
          style={{ width: `${Math.min(score, 100)}%`, background: color }}
        />
      </div>
      <div className="gauge-meta">
        <strong>Score: {score}</strong>
        <span className={`badge alert-${level}`}>{alertLevel}</span>
        {eyeClosure > 1.5 && <span className="badge alert-critical">Eye closure {eyeClosure}s</span>}
        {haptic === "Yes" && <span className="badge alert-critical">Haptic fired</span>}
      </div>
    </div>
  );
}

export function Safety() {
  const { summary, loading: summaryLoading, error: summaryError } = useSafetySummary();
  const { incidents, loading: incidentsLoading, error: incidentsError, refresh } = useIncidents();
  const [operators, setOperators] = useState<Row[]>([]);
  const [machines, setMachines] = useState<Row[]>([]);

  const [form, setForm] = useState({
    machine_id: "",
    operator_id: "",
    incident_type: "Seatbelt Violation",
    severity: "Medium",
    description: "",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [formSubmitting, setFormSubmitting] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/operators")
      .then((r) => r.json())
      .then(setOperators)
      .catch(() => setOperators([]));
    fetch("http://localhost:8000/api/machines")
      .then((r) => r.json())
      .then(setMachines)
      .catch(() => setMachines([]));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSubmitting(true);
    try {
      await createIncident(form);
      setForm({ ...form, description: "" });
      refresh();
    } catch (err: any) {
      setFormError(err.message);
    } finally {
      setFormSubmitting(false);
    }
  };

  const isLoading = summaryLoading || incidentsLoading;
  const error = summaryError || incidentsError;

  return (
    <div className="panel">
      <h2>Safety & Fatigue</h2>

      {isLoading && <p>Loading safety data…</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && !error && summary && (
        <>
          <section className="safety-section">
            <h3>Fatigue Snapshot</h3>
            <div className="cards">
              {summary.latest_fatigue.map((f) => (
                <div className="card" key={`${f["Machine ID"]}-${f["Operator ID"]}`}>
                  <div>
                    <strong>{f["Operator ID"]}</strong> · {f["Machine ID"]}
                  </div>
                  <FatigueGauge
                    score={Number(f["fatigue_score"])}
                    alertLevel={String(f["alert_level"])}
                    eyeClosure={Number(f["eye_closure_seconds"])}
                    haptic={String(f["haptic_triggered"])}
                  />
                </div>
              ))}
            </div>
          </section>

          <section className="safety-section">
            <h3>Seatbelt Compliance</h3>
            <table>
              <thead>
                <tr>
                  <th>Machine</th>
                  <th>Operator</th>
                  <th>Status</th>
                  <th>Compliant</th>
                </tr>
              </thead>
              <tbody>
                {summary.seatbelt_compliance.map((row) => (
                  <tr key={`${row["Machine ID"]}-${row["Operator ID"]}`}>
                    <td>{row["Machine ID"]}</td>
                    <td>{row["Operator ID"]}</td>
                    <td>{row["seatbelt_status"]}</td>
                    <td>
                      {row["compliant"] ? (
                        <span className="badge status-completed">Yes</span>
                      ) : (
                        <span className="badge severity-high">No</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="safety-section">
            <h3>Proximity Hazards (Ranked)</h3>
            {summary.proximity_hazards.length === 0 ? (
              <p>No active proximity hazards.</p>
            ) : (
              <div className="cards">
                {summary.proximity_hazards.map((h) => (
                  <div className="card alert" key={`${h["Machine ID"]}-${h["Operator ID"]}`}>
                    <strong>{h["Machine ID"]}</strong> · {h["Operator ID"]}
                    <div>Distance: {h["distance_m"]} m</div>
                    <div className="timestamp">{h["Timestamp"]}</div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="safety-section">
            <h3>Log New Incident</h3>
            <form className="form" onSubmit={handleSubmit}>
              <label>
                Machine
                <select
                  value={form.machine_id}
                  onChange={(e) => setForm({ ...form, machine_id: e.target.value })}
                  required
                >
                  <option value="">Select…</option>
                  {machines.map((m) => (
                    <option key={m["Machine ID"] as string} value={m["Machine ID"] as string}>
                      {m["Machine ID"]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Operator
                <select
                  value={form.operator_id}
                  onChange={(e) => setForm({ ...form, operator_id: e.target.value })}
                  required
                >
                  <option value="">Select…</option>
                  {operators.map((o) => (
                    <option key={o["Operator ID"] as string} value={o["Operator ID"] as string}>
                      {o["Name"]} ({o["Operator ID"]})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Type
                <select
                  value={form.incident_type}
                  onChange={(e) => setForm({ ...form, incident_type: e.target.value })}
                >
                  <option>Seatbelt Violation</option>
                  <option>Proximity Breach</option>
                  <option>Excessive Idling</option>
                  <option>Fatigue Alert</option>
                  <option>Other</option>
                </select>
              </label>
              <label>
                Severity
                <select
                  value={form.severity}
                  onChange={(e) => setForm({ ...form, severity: e.target.value })}
                >
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                </select>
              </label>
              <label>
                Description
                <input
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="What happened?"
                />
              </label>
              <button type="submit" disabled={formSubmitting}>
                {formSubmitting ? "Saving…" : "Log Incident"}
              </button>
            </form>
            {formError && <p className="error">{formError}</p>}
          </section>

          <section className="safety-section">
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
                  <th>Resolved</th>
                </tr>
              </thead>
              <tbody>
                {incidents.slice(0, 50).map((inc) => (
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
                    <td>{inc["Resolved"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}

export function SafetySummary() {
  const { summary, loading, error } = useSafetySummary();

  if (loading) return <div className="summary-card">Loading safety…</div>;
  if (error || !summary) return <div className="summary-card error">Safety unavailable</div>;

  const criticalFatigue = summary.latest_fatigue.filter(
    (f) => String(f["alert_level"]).toLowerCase() === "critical"
  ).length;
  const hazards = summary.proximity_hazards.length;
  const nonCompliant = summary.seatbelt_compliance.filter((r) => !r["compliant"]).length;

  return (
    <div className="summary-card">
      <h4>Safety</h4>
      <div className="summary-counts">
        <div>
          <strong>{hazards}</strong> proximity hazards
        </div>
        <div>
          <strong className={nonCompliant ? "text-danger" : ""}>{nonCompliant}</strong> seatbelt issues
        </div>
        <div>
          <strong className={criticalFatigue ? "text-danger" : ""}>{criticalFatigue}</strong> fatigue critical
        </div>
      </div>
    </div>
  );
}
