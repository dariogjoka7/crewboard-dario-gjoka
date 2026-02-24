import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./state/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { CrewMembersPage } from "./pages/CrewMembersPage";
import { FlightsPage } from "./pages/FlightsPage";
import { AssignmentsPage } from "./pages/AssignmentsPage";
import { Layout } from "./components/Layout";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/crew-members"
          element={
            <PrivateRoute>
              <CrewMembersPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/flights"
          element={
            <PrivateRoute>
              <FlightsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/assignments"
          element={
            <PrivateRoute>
              <AssignmentsPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/crew-members" replace />} />
      </Routes>
    </Layout>
  );
}

