import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiPost } from "../api.js";
import { useAuth } from "../auth.jsx";

const demoHint =
  "HR demo: prisha / prisha (or hr / hr). Applicant: applicant / applicant.";

export default function Login({ role }) {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const title = role === "hr" ? "HR sign in" : "Applicant sign in";

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await apiPost("/api/auth/login", { username, password, role });
      login(data.token, data.user);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      <Link className="nav-back" to="/">
        ← Back to home
      </Link>
      <div className="panel">
        <h1>{title}</h1>
        <p className="hint">{demoHint}</p>
        {error ? <div className="error-banner">{error}</div> : null}
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        {role === "applicant" ? (
          <p className="footer-links" style={{ marginTop: "1.25rem" }}>
            New here? <Link to="/signup">Create an applicant account</Link>
          </p>
        ) : null}
      </div>
    </div>
  );
}
