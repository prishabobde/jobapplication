import { Link } from "react-router-dom";
import HeroGraphic from "../components/HeroGraphic.jsx";
import { useAuth } from "../auth.jsx";

export default function Home() {
  const { token } = useAuth();

  return (
    <div className="layout">
      <HeroGraphic />
      <header className="brand">
        <div className="brand-badge">Careers &amp; talent</div>
        <h1 className="brand-title">Prisha Company</h1>
        <p className="brand-sub">Application portal — sign in as HR or as an applicant.</p>
      </header>

      <div className="card-grid">
        <Link className="role-card" to="/login/hr">
          <h2>HR login</h2>
          <p>For company recruiters and hiring managers. Review applications and manage roles.</p>
          <div className="cta">Continue as HR →</div>
        </Link>
        <Link className="role-card" to="/login/applicant">
          <h2>Applicant login</h2>
          <p>For candidates outside the company. Apply to roles and track your submissions.</p>
          <div className="cta">Continue as applicant →</div>
        </Link>
      </div>

      {token && (
        <p className="footer-links" style={{ marginTop: "2.5rem" }}>
          You have an active session.{" "}
          <Link to="/dashboard">Open dashboard</Link>
        </p>
      )}
    </div>
  );
}
