import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./useAuth";

/**
 * Protects routes that require the admin role.
 * Members are silently redirected to /ask rather than shown an error page,
 * since they should never see the link in the first place (it's hidden in nav).
 */
export function RequireAdmin() {
  const { role } = useAuth();

  if (role !== "admin") {
    return <Navigate to="/ask" replace />;
  }

  return <Outlet />;
}
