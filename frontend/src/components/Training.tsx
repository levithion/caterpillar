import { useEffect, useState } from "react";
import { trainingApi } from "../api/training";
import type { Row } from "../api/client";

export function Training() {
  const [modules, setModules] = useState<Row[]>([]);
  const [records, setRecords] = useState<Row[]>([]);
  const [operators, setOperators] = useState<Row[]>([]);
  const [selectedOperator, setSelectedOperator] = useState<string>("");

  useEffect(() => {
    trainingApi.trainingModules().then(setModules);
    trainingApi.operators().then(setOperators);
  }, []);

  useEffect(() => {
    trainingApi.trainingRecords(selectedOperator || undefined).then(setRecords);
  }, [selectedOperator]);

  const moduleById: Record<string, Row> = Object.fromEntries(modules.map((m) => [m["Module ID"], m]));

  return (
    <div className="panel">
      <h2>Operator Training Hub</h2>

      <h3>Modules</h3>
      <div className="cards">
        {modules.map((m) => (
          <div className="card" key={m["Module ID"] as string}>
            <strong>{m["Title"]}</strong>
            <div>{m["Category"]} · {m["Format"]} · {m["Duration (min)"]} min</div>
            <span className="badge">{m["Difficulty"]}</span>
          </div>
        ))}
      </div>

      <h3>Progress</h3>
      <label>
        Operator:{" "}
        <select value={selectedOperator} onChange={(e) => setSelectedOperator(e.target.value)}>
          <option value="">All</option>
          {operators.map((o) => (
            <option key={o["Operator ID"] as string} value={o["Operator ID"] as string}>
              {o["Name"]}
            </option>
          ))}
        </select>
      </label>
      <table>
        <thead>
          <tr>
            <th>Operator</th>
            <th>Module</th>
            <th>Status</th>
            <th>Score</th>
            <th>Certification Expiry</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r["Record ID"] as string}>
              <td>{r["Operator ID"]}</td>
              <td>{moduleById[r["Module ID"] as string]?.["Title"] ?? r["Module ID"]}</td>
              <td>
                <span className={`badge status-${String(r["Status"]).toLowerCase().replace(" ", "-")}`}>
                  {r["Status"]}
                </span>
              </td>
              <td>{r["Score"] || "—"}</td>
              <td>{r["Certification Expiry"] || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
