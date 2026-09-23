import { useMachine } from "../context/MachineContext";

/** Reusable machine picker — place once on dashboard/header; all features follow selection. */
export function MachineSelector() {
  const { machines, machineId, setMachineId, loading, error } = useMachine();

  if (loading) return <span className="muted">Loading machines…</span>;
  if (error) return <span className="error">{error}</span>;

  return (
    <label className="machine-select">
      Active Machine
      <select
        value={machineId ?? ""}
        onChange={(e) => setMachineId(e.target.value)}
        disabled={!machines.length}
        aria-label="Select active machine"
      >
        {machines.map((m) => (
          <option key={m.id} value={m.id}>
            {m.id} — {m.type} ({m.model})
          </option>
        ))}
      </select>
    </label>
  );
}

/** Compact read-only badge showing the currently selected machine. */
export function MachineBadge() {
  const { selectedMachine, machineId } = useMachine();
  if (!selectedMachine || !machineId) return null;

  return (
    <div className="machine-badge" title="All panels use this machine">
      <span className="machine-badge-id">{machineId}</span>
      <span className="machine-badge-meta">
        {selectedMachine.type} · {selectedMachine.model}
      </span>
      <span className={`machine-badge-status status-${selectedMachine.status.toLowerCase().replace(" ", "-")}`}>
        {selectedMachine.status}
      </span>
    </div>
  );
}
