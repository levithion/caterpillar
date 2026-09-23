import { useEffect, useRef, useState } from "react";
import { predictorApi, type TaskTimePrediction } from "../api/predictor";

const TASK_TYPES = ["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition", "Compaction", "Hauling"];
const WEATHERS = ["Sunny", "Rainy", "Cloudy", "Windy", "Foggy"];
const SKILLS = ["Beginner", "Intermediate", "Expert"];
const STREAM_INTERVAL_MS = 4000;
const MAX_FEED = 8;

type StreamEntry = {
  id: number;
  taskType: string;
  weather: string;
  skill: string;
  machineAge: number;
  prediction: TaskTimePrediction;
};

function randomOf<T>(options: T[]): T {
  return options[Math.floor(Math.random() * options.length)];
}

export function Predictor() {
  const [feed, setFeed] = useState<StreamEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const nextId = useRef(0);

  useEffect(() => {
    let cancelled = false;

    const tick = async () => {
      const taskType = randomOf(TASK_TYPES);
      const weather = randomOf(WEATHERS);
      const skill = randomOf(SKILLS);
      const machineAge = Math.round(Math.random() * 20);
      try {
        const prediction = await predictorApi.predictTaskTime({
          task_type: taskType,
          weather,
          skill_level: skill,
          machine_age: machineAge,
        });
        if (cancelled) return;
        setError(null);
        nextId.current += 1;
        setFeed((prev) => [
          { id: nextId.current, taskType, weather, skill, machineAge, prediction },
          ...prev,
        ].slice(0, MAX_FEED));
      } catch {
        if (!cancelled) setError("Prediction stream interrupted. Is the backend running?");
      }
    };

    tick();
    const interval = setInterval(tick, STREAM_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const latest = feed[0];
  const history = feed.slice(1);

  return (
    <div className="panel">
      <h2>Task Time Estimation</h2>
      <p>
        Simulates a live stream of incoming tasks (random type, weather, operator skill, machine age) and predicts
        each one's completion time with a confidence range as it arrives.
      </p>

      {error && <p className="error">{error}</p>}

      {latest ? (
        <div className="result">
          <span className="badge">● live</span>
          <div>
            <strong>{latest.taskType}</strong> · {latest.weather} · {latest.skill} · Machine age{" "}
            {latest.machineAge} yrs
          </div>
          <div>
            Estimated time: <strong>{latest.prediction.predicted_minutes} min</strong>
          </div>
          <div>
            Confidence range: {latest.prediction.lower_bound_minutes}–{latest.prediction.upper_bound_minutes} min
          </div>
        </div>
      ) : (
        !error && <p>Waiting for the first task…</p>
      )}

      {history.length > 0 && (
        <>
          <h3>Recent Stream</h3>
          <table>
            <thead>
              <tr>
                <th>Task Type</th>
                <th>Weather</th>
                <th>Skill</th>
                <th>Machine Age</th>
                <th>Predicted (min)</th>
                <th>Range (min)</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.taskType}</td>
                  <td>{entry.weather}</td>
                  <td>{entry.skill}</td>
                  <td>{entry.machineAge}</td>
                  <td>{entry.prediction.predicted_minutes}</td>
                  <td>
                    {entry.prediction.lower_bound_minutes}–{entry.prediction.upper_bound_minutes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
