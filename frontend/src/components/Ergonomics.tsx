import type { ErgonomicsCurrent, ErgonomicsReading } from "../api/ergonomics";
import { useMachine } from "../context/MachineContext";
import { useLiveData } from "../context/LiveDataContext";

function VibrationChart({ series, tick }: { series: ErgonomicsReading[]; tick: number }) {
  if (series.length < 2) return <p className="muted">Waiting for live readings…</p>;

  const width = 480;
  const height = 140;
  const padding = 8;
  const chassis = series.map((r) => r["Chassis Accel Z"]);
  const seat = series.map((r) => r["Seat Accel Z"]);
  const maxVal = Math.max(...chassis, ...seat, 0.5);
  const step = (width - padding * 2) / (series.length - 1);

  const toPoints = (values: number[]) =>
    values
      .map((v, i) => {
        const x = padding + i * step;
        const y = height - padding - (v / maxVal) * (height - padding * 2);
        return `${x},${y}`;
      })
      .join(" ");

  return (
    <svg key={tick} viewBox={`0 0 ${width} ${height}`} className="chart live-chart" role="img" aria-label="Live vibration chart">
      <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#334155" />
      <line
        x1={padding}
        y1={height - padding - ((0.7 / maxVal) * (height - padding * 2))}
        x2={width - padding}
        y2={height - padding - ((0.7 / maxVal) * (height - padding * 2))}
        stroke="#ef4444"
        strokeDasharray="4 4"
      />
      <polyline fill="none" stroke="#f59e0b" strokeWidth="2" points={toPoints(chassis)} />
      <polyline fill="none" stroke="#22c55e" strokeWidth="2" points={toPoints(seat)} />
      <text x={padding} y={14} fill="#94a3b8" fontSize="11">Live — Chassis (amber) · Seat (green)</text>
    </svg>
  );
}

export function ErgonomicsPanel({
  current,
  series,
  tick,
}: {
  current: ErgonomicsCurrent | null;
  series: ErgonomicsReading[];
  tick: number;
}) {
  if (!current) return <p className="muted">Waiting for live ergonomics stream…</p>;

  const dampingClass = `damping-${current.damping_setting}`;

  return (
    <div className="ergonomics-panel panel-card">
      <h3>Live Vibration &amp; Suspension</h3>
      {current.shock_detected && (
        <div className="banner warning">Chassis shock detected — damping adjusted to firm</div>
      )}
      <VibrationChart series={series} tick={tick} />
      <div className="metric-grid">
        <div className="metric">
          <span className="metric-label">Chassis Z</span>
          <span className="metric-value live-value">{current.chassis_accel_z.toFixed(2)}g</span>
        </div>
        <div className="metric">
          <span className="metric-label">Seat Z</span>
          <span className="metric-value live-value">{current.seat_accel_z.toFixed(2)}g</span>
        </div>
        <div className="metric">
          <span className="metric-label">Damping</span>
          <span className={`metric-value badge ${dampingClass}`}>{current.damping_setting}</span>
        </div>
        <div className="metric">
          <span className="metric-label">WBV Index</span>
          <span className="metric-value live-value">{current.wbv_exposure_index.toFixed(1)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Seat Pressure</span>
          <span className="metric-value">{current.seat_air_pressure_kpa.toFixed(0)} kPa</span>
        </div>
        <div className="metric">
          <span className="metric-label">Pressure Center</span>
          <span className="metric-value">
            {current.seat_pressure_center_x.toFixed(2)}, {current.seat_pressure_center_y.toFixed(2)}
          </span>
        </div>
      </div>
      {current.prediction_source === "ml" && (
        <div className="ml-meta muted">
          ML · Shock risk {((current.shock_probability ?? 0) * 100).toFixed(0)}%
          · Anomaly score {current.anomaly_score?.toFixed(2) ?? "—"}
        </div>
      )}
      <p className="muted recommendation">{current.recommendation}</p>
    </div>
  );
}

export function Ergonomics() {
  const { machineId, selectedMachine } = useMachine();
  const { ergonomicsCurrent, ergonomicsSeries, connected, error, tickCount } = useLiveData();

  if (!machineId) return <p className="muted">Select a machine to view ergonomics.</p>;
  if (selectedMachine && !selectedMachine.capabilities.ergonomics) {
    return (
      <p className="muted">
        {machineId} has no active suspension — ergonomics monitoring is not available for this machine.
      </p>
    );
  }
  if (error) return <p className="error">{error}</p>;
  if (!connected && !ergonomicsCurrent) return <p className="muted">Connecting to live sensor stream…</p>;

  return <ErgonomicsPanel current={ergonomicsCurrent} series={ergonomicsSeries} tick={tickCount} />;
}
