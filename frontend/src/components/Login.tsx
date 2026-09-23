import { useState } from "react";
import { authApi, type Operator } from "../api/auth";
import { COUNTRY_CODES } from "../countryCodes";

const SKILL_LEVELS = ["Beginner", "Intermediate", "Expert"];
const SHIFTS = ["Day", "Night"];
const DEFAULT_COUNTRY = COUNTRY_CODES.find((c) => c.iso2 === "US") ?? COUNTRY_CODES[0];

export function Login({ onLogin }: { onLogin: (operator: Operator) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");

  // Login fields
  const [identifier, setIdentifier] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup fields
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [countryCode, setCountryCode] = useState(DEFAULT_COUNTRY.dial);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [skillLevel, setSkillLevel] = useState(SKILL_LEVELS[0]);
  const [shift, setShift] = useState(SHIFTS[0]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      onLogin(await authApi.login({ identifier: identifier.trim(), password: loginPassword }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const submitSignup = async () => {
    if (signupPassword !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      onLogin(
        await authApi.signup({
          name: name.trim(),
          email: email.trim(),
          country_code: countryCode,
          phone_number: phoneNumber.trim(),
          password: signupPassword,
          skill_level: skillLevel,
          shift,
        }),
      );
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
              Email or Operator ID
              <input
                type="text"
                placeholder="e.g. you@example.com or OP1001"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
              />
            </label>
            <label>
              Password
              <input type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} />
            </label>
            <button onClick={submitLogin} disabled={loading || !identifier.trim() || !loginPassword}>
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
              Email
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            <label>
              Phone
              <div className="phone-row">
                <select value={countryCode} onChange={(e) => setCountryCode(e.target.value)}>
                  {COUNTRY_CODES.map((c) => (
                    <option key={c.iso2} value={c.dial}>
                      {c.name} ({c.dial})
                    </option>
                  ))}
                </select>
                <input
                  type="tel"
                  placeholder="Phone number"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                />
              </div>
            </label>
            <label>
              Password
              <input
                type="password"
                value={signupPassword}
                onChange={(e) => setSignupPassword(e.target.value)}
              />
            </label>
            <label>
              Confirm Password
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
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
            <p className="hint">Your Operator ID is assigned automatically after signup.</p>
            <button
              onClick={submitSignup}
              disabled={
                loading ||
                !name.trim() ||
                !email.trim() ||
                !phoneNumber.trim() ||
                !signupPassword ||
                !confirmPassword
              }
            >
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
            Already have an account?{" "}
            <button className="link" onClick={() => setMode("login")}>
              Log in
            </button>
          </>
        )}
      </p>
    </div>
  );
}
