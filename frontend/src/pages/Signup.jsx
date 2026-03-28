import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiPost } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Signup() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await apiPost("/api/auth/register", {
        username,
        password,
        role: "applicant",
      });
      login(data.token, data.user);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Could not create account");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      <Link className="nav-back" to="/login/applicant">
        ← Applicant login
      </Link>
      <div className="panel">
        <h1>Create applicant account</h1>
        <p className="hint">Pick any username and password. No email verification.</p>
        {error ? <div className="error-banner">{error}</div> : null}
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="su-user">Username</label>
            <input
              id="su-user"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={1}
            />
          </div>
          <div className="field">
            <label htmlFor="su-pass">Password</label>
            <input
              id="su-pass"
              name="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={1}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Creating…" : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
