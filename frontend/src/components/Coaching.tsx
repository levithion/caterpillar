import { useEffect, useState } from "react";
import { getCoachingEvents, type Row } from "../api/coaching";

const SEVERITIES = ["all", "critical", "warning", "info"];

function useCoachingEvents(filterSeverity: string) {
  const [events, setEvents] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getCoachingEvents(undefined, filterSeverity === "all" ? undefined : filterSeverity)
      .then(setEvents)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filterSeverity]);

  return { events, loading, error };
}

function CoachingCard({ event }: { event: Row }) {
  const severity = String(event["Severity"]).toLowerCase();
  const typeToIcon: Record<string, string> = {
    hoist_while_tramming: "⬆️",
    high_pressure_low_rpm: "⚙️",
    repeated_slippage: "🔄",
    hard_braking: "🛑",
  };

  return (
    <div className={`card coaching-card severity-${severity}`}>
      <div className="coaching-header">
        <span className="coaching-icon">{typeToIcon[String(event["Event Type"])] || "💡"}</span>
        <strong>{event["Event Type"]}</strong>
        <span className={`badge severity-${severity}`}>{event["Severity"]}</span>
      </div>
      <div className="coaching-message">{event["Message"]}</div>
      <div className="coaching-action">👉 {event["Recommended Action"]}</div>
      <div className="coaching-meta">
        {event["Machine ID"]} · {event["Operator ID"]} · {event["Timestamp"]}
      </div>
    </div>
  );
}

export function Coaching() {
  const [severity, setSeverity] = useState("all");
  const { events, loading, error } = useCoachingEvents(severity);

  return (
    <div className="panel">
      <h2>Real-Time Coaching</h2>
      <p>CAN-bus-style rules detect inefficient or damaging operator moves as they happen.</p>

      <div className="filter-bar">
        <label>
          Filter:
          <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <p>Loading coaching events…</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <div className="cards coaching-feed">
          {events.length === 0 ? (
            <p>No coaching events for the selected filter.</p>
          ) : (
            events.map((e) => <CoachingCard event={e} key={e["Event ID"] as string} />)
          )}
        </div>
      )}
    </div>
  );
}

export function CoachingSummary() {
  const [events, setEvents] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCoachingEvents()
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="summary-card">Loading coaching…</div>;

  const latest = events[0];
  const warnings = events.filter((e) => String(e["Severity"]).toLowerCase() === "warning").length;

  return (
    <div className="summary-card">
      <h4>Coaching</h4>
      <div className="summary-counts">
        <div>
          <strong>{events.length}</strong> total tips
        </div>
        <div>
          <strong className={warnings ? "text-warning" : ""}>{warnings}</strong> warnings
        </div>
      </div>
      {latest && (
        <div className="latest-tip">
          Latest: <em>{latest["Message"]}</em>
        </div>
      )}
    </div>
  );
}
