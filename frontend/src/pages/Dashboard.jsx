import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiGet } from "../api.js";
import { useAuth } from "../auth.jsx";
import JobBoard from "../components/JobBoard.jsx";

export default function Dashboard() {
  const navigate = useNavigate();
  const { token, user, login, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState([]);
  const [jobsError, setJobsError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const meData = await apiGet("/api/auth/me", token);
        if (cancelled) return;
        login(token, meData.user);
        try {
          const jobsData = await apiGet("/api/jobs", token);
          if (!cancelled) {
            setJobs(jobsData.jobs ?? []);
            setJobsError("");
          }
        } catch (e) {
          if (!cancelled) {
            setJobs([]);
            setJobsError(e.message || "Could not load jobs");
          }
        }
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
      <div className="layout layout-dashboard">
        <p style={{ color: "var(--muted)", textAlign: "center" }}>Loading…</p>
      </div>
    );
  }

  const display = user;

  return (
    <div className="layout layout-dashboard">
      <div className="dashboard-topbar">
        <div className="dashboard-header dashboard-header--wide">
          <div>
            <div className="brand-badge" style={{ marginBottom: "0.35rem" }}>
              Prisha Company
            </div>
            <h1 className="brand-title dashboard-welcome">
              Welcome{display?.username ? `, ${display.username}` : ""}
            </h1>
          </div>
          <div className="dashboard-topbar-actions">
            <span className="pill">{display?.role === "hr" ? "HR" : "Applicant"}</span>
            <button
              type="button"
              className="btn btn-primary btn-signout"
              onClick={() => {
                logout();
                navigate("/", { replace: true });
              }}
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      {jobsError ? <div className="error-banner">{jobsError}</div> : null}

      <JobBoard jobs={jobs} role={display?.role} token={token} />

      <p className="footer-links">
        <Link to="/">Home</Link>
      </p>
    </div>
  );
}
