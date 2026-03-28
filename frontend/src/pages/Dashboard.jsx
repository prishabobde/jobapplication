import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiGet } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Dashboard() {
  const navigate = useNavigate();
  const { token, user, login, logout } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await apiGet("/api/auth/me", token);
        if (!cancelled) login(token, data.user);
      } catch {
        if (!cancelled) {
          logout();
          navigate("/", { replace: true });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, login, logout, navigate]);

  if (loading) {
    return (
      <div className="layout">
        <p style={{ color: "var(--muted)", textAlign: "center" }}>Loading…</p>
      </div>
    );
  }

  const display = user;

  return (
    <div className="layout">
      <div className="dashboard-header">
        <div>
          <div className="brand-badge" style={{ marginBottom: "0.35rem" }}>
            Prisha Company
          </div>
          <h1 className="brand-title" style={{ fontSize: "1.75rem" }}>
            Welcome{display?.username ? `, ${display.username}` : ""}
          </h1>
        </div>
        <span className="pill">{display?.role === "hr" ? "HR" : "Applicant"}</span>
      </div>

      <div className="panel" style={{ maxWidth: "100%" }}>
        <p style={{ margin: "0 0 1rem", color: "var(--muted)", lineHeight: 1.6 }}>
          You are signed in to the portal. This screen is a placeholder for job listings,
          applications, and HR tools as you build them out.
        </p>
        <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--muted)" }}>
          User ID: {display?.id ?? "—"} · Username: {display?.username ?? "—"}
        </p>
        <button
          type="button"
          className="btn btn-primary"
          style={{ marginTop: "1.5rem", maxWidth: "200px" }}
          onClick={() => {
            logout();
            navigate("/", { replace: true });
          }}
        >
          Sign out
        </button>
      </div>

      <p className="footer-links">
        <Link to="/">Home</Link>
      </p>
    </div>
  );
}
