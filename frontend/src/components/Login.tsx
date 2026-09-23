import { useState } from "react";
import { authApi, type Operator } from "../api/auth";

const SKILL_LEVELS = ["Beginner", "Intermediate", "Expert"];
const SHIFTS = ["Day", "Night"];

export function Login({ onLogin }: { onLogin: (operator: Operator) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");

  const [operatorId, setOperatorId] = useState("");
  const [name, setName] = useState("");
  const [skillLevel, setSkillLevel] = useState(SKILL_LEVELS[0]);
  const [shift, setShift] = useState(SHIFTS[0]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      onLogin(await authApi.login(operatorId.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const submitSignup = async () => {
    setLoading(true);
    setError(null);
    try {
      onLogin(await authApi.signup({ name: name.trim(), skill_level: skillLevel, shift }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel login-panel">
      <h2>Smart Operator Assistant</h2>
      <div className="form">
        {mode === "login" ? (
          <>
            <label>
              Operator ID
              <input
                type="text"
                placeholder="e.g. OP1001"
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
              />
            </label>
            <button onClick={submitLogin} disabled={loading || !operatorId.trim()}>
              {loading ? "Logging in…" : "Log in"}
            </button>
          </>
        ) : (
          <>
            <label>
              Name
              <input type="text" placeholder="Your name" value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label>
              Operator Skill
              <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)}>
                {SKILL_LEVELS.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <label>
              Shift
              <select value={shift} onChange={(e) => setShift(e.target.value)}>
                {SHIFTS.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <button onClick={submitSignup} disabled={loading || !name.trim()}>
              {loading ? "Signing up…" : "Sign up"}
            </button>
          </>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      <p className="switch-mode">
        {mode === "login" ? (
          <>
            New operator?{" "}
            <button className="link" onClick={() => setMode("signup")}>
              Sign up
            </button>
          </>
        ) : (
          <>
            Already have an ID?{" "}
            <button className="link" onClick={() => setMode("login")}>
              Log in
            </button>
          </>
        )}
      </p>
    </div>
  );
}
