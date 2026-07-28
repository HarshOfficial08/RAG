import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./useAuth";

// Guards /login and /signup: landing here while a valid session already
// exists (e.g. via browser back navigation) should go straight into the app,
// not show the login form again.
export function RedirectIfAuthenticated() {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) return <Navigate to="/documents" replace />;
  return <Outlet />;
}
