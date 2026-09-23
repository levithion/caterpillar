import type { EnvironmentCurrent, EnvironmentReading } from "../api/environment";
import { useMachine } from "../context/MachineContext";
import { useLiveData } from "../context/LiveDataContext";

function Co2Chart({ series, tick }: { series: EnvironmentReading[]; tick: number }) {
  if (series.length < 2) return <p className="muted">Waiting for live readings…</p>;

  const width = 480;
  const height = 140;
  const padding = 8;
  const values = series.map((r) => r["Cab CO2 (ppm)"]);
  const minVal = Math.min(...values) - 50;
  const maxVal = Math.max(...values, 1000) + 50;
  const range = maxVal - minVal || 1;
  const step = (width - padding * 2) / (series.length - 1);
  const thresholdY =
    height - padding - ((1000 - minVal) / range) * (height - padding * 2);

  const points = values
    .map((v, i) => {
      const x = padding + i * step;
      const y = height - padding - ((v - minVal) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg key={tick} viewBox={`0 0 ${width} ${height}`} className="chart live-chart" role="img" aria-label="Live CO2 trend chart">
      <line x1={padding} y1={thresholdY} x2={width - padding} y2={thresholdY} stroke="#ef4444" strokeDasharray="4 4" />
      <text x={width - padding - 80} y={thresholdY - 4} fill="#ef4444" fontSize="10">1000 ppm</text>
      <polyline fill="none" stroke="#3b82f6" strokeWidth="2" points={points} />
      <text x={padding} y={14} fill="#94a3b8" fontSize="11">Live — Cab CO₂ (ppm)</text>
    </svg>
  );
}

export function EnvironmentPanel({
  current,
  series,
  tick,
}: {
  current: EnvironmentCurrent | null;
  series: EnvironmentReading[];
  tick: number;
}) {
  if (!current) return <p className="muted">Waiting for live environment stream…</p>;

  const co2High = current.co2_ppm > 1000;
  const tempHigh = current.facial_temp_c > 37.2;

  return (
    <div className="environment-panel panel-card">
      <h3>Live Cabin Environment</h3>
      {current.warnings.length > 0 && (
        <div className="banner warning">
          {current.warnings.map((w) => <div key={w}>{w}</div>)}
        </div>
      )}
      {(co2High || tempHigh) && (
        <div className="banner critical">
          Hydration and rest break recommended — cabin conditions require intervention
        </div>
      )}
      <Co2Chart series={series} tick={tick} />
      <div className="metric-grid">
        <div className="metric">
          <span className="metric-label">CO₂</span>
          <span className={`metric-value live-value ${co2High ? "text-warning" : ""}`}>
            {current.co2_ppm.toFixed(0)} ppm
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Facial Temp</span>
          <span className={`metric-value live-value ${tempHigh ? "text-warning" : ""}`}>
            {current.facial_temp_c.toFixed(1)}°C
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Cab Temp</span>
          <span className="metric-value live-value">{current.cab_temp_c.toFixed(1)}°C</span>
        </div>
        <div className="metric">
          <span className="metric-label">HVAC</span>
          <span className={`metric-value badge ${current.hvac_override_active ? "hvac-active" : ""}`}>
            {current.hvac_override_active ? "Override ON" : "Normal"}
          </span>
        </div>
      </div>
      {current.prediction_source === "ml" && (
        <div className="ml-meta muted">
          ML · HVAC risk {((current.hvac_probability ?? 0) * 100).toFixed(0)}%
          · Anomaly score {current.anomaly_score?.toFixed(2) ?? "—"}
        </div>
      )}
      <div className="status-row">
        <span className={current.fresh_air_flush_active ? "status-on" : "status-off"}>
          Fresh Air Flush: {current.fresh_air_flush_active ? "Active" : "Off"}
        </span>
        <span className="muted">
          PM2.5: {current.pm25_ug_m3.toFixed(1)} µg/m³ · Humidity: {current.cab_humidity_pct}%
        </span>
      </div>
    </div>
  );
}

export function Environment() {
  const { machineId, selectedMachine } = useMachine();
  const { environmentCurrent, environmentSeries, connected, error, tickCount } = useLiveData();

  if (!machineId) return <p className="muted">Select a machine to view environment data.</p>;
  if (selectedMachine && !selectedMachine.capabilities.environment) {
    return <p className="muted">Environment monitoring is not available for {machineId}.</p>;
  }
  if (error) return <p className="error">{error}</p>;
  if (!connected && !environmentCurrent) return <p className="muted">Connecting to live sensor stream…</p>;

  return <EnvironmentPanel current={environmentCurrent} series={environmentSeries} tick={tickCount} />;
}
