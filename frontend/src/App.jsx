import { Navigate, Route, Routes } from "react-router-dom";
import ThemeToggle from "./components/ThemeToggle.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import { useAuth } from "./auth.jsx";

function Protected({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <>
      <div className="theme-toggle-fixed">
        <ThemeToggle />
      </div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login/hr" element={<Login role="hr" />} />
        <Route path="/login/applicant" element={<Login role="applicant" />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/dashboard"
          element={
            <Protected>
              <Dashboard />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
