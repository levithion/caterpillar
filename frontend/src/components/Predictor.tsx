import { useState } from "react";
import { api } from "../api";

const TASK_TYPES = ["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition", "Compaction", "Hauling"];
const WEATHERS = ["Sunny", "Rainy", "Cloudy", "Windy", "Foggy"];
const SKILLS = ["Beginner", "Intermediate", "Expert"];

export function Predictor() {
  const [taskType, setTaskType] = useState(TASK_TYPES[0]);
  const [weather, setWeather] = useState(WEATHERS[0]);
  const [skill, setSkill] = useState(SKILLS[0]);
  const [machineAge, setMachineAge] = useState(3);
  const [result, setResult] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    try {
      const res = await api.predictTaskTime({
        task_type: taskType,
        weather,
        skill_level: skill,
        machine_age: machineAge,
      });
      setResult(res.predicted_minutes);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Task Time Estimation</h2>
      <div className="form">
        <label>
          Task Type
          <select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
            {TASK_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </label>
        <label>
          Weather
          <select value={weather} onChange={(e) => setWeather(e.target.value)}>
            {WEATHERS.map((w) => (
              <option key={w}>{w}</option>
            ))}
          </select>
        </label>
        <label>
          Operator Skill
          <select value={skill} onChange={(e) => setSkill(e.target.value)}>
            {SKILLS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
        <label>
          Machine Age (yrs)
          <input
            type="number"
            min={0}
            max={20}
            value={machineAge}
            onChange={(e) => setMachineAge(Number(e.target.value))}
          />
        </label>
        <button onClick={predict} disabled={loading}>
          {loading ? "Predicting…" : "Predict"}
        </button>
      </div>
      {result !== null && (
        <div className="result">
          Estimated time: <strong>{result} min</strong>
        </div>
      )}
    </div>
  );
}
