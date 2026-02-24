import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../state/AuthContext";

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const navLinkClass = (path: string) =>
    location.pathname.startsWith(path) ? "nav-link nav-link-active" : "nav-link";

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-header-left">
          <span className="app-title">Crewboard</span>
        </div>
        <nav className="app-nav">
          {isAuthenticated && (
            <>
              <Link to="/crew-members" className={navLinkClass("/crew-members")}>
                Crew
              </Link>
              <Link to="/flights" className={navLinkClass("/flights")}>
                Flights
              </Link>
              <Link to="/assignments" className={navLinkClass("/assignments")}>
                Assignments
              </Link>
            </>
          )}
        </nav>
        <div className="app-header-right">
          {isAuthenticated ? (
            <button className="btn btn-secondary" onClick={logout}>
              Logout
            </button>
          ) : (
            <Link to="/login" className="btn btn-primary">
              Login
            </Link>
          )}
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
};

