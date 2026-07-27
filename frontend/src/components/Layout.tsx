import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { Badge } from "./Badge";

const NAV_ITEMS = [
  { to: "/documents", label: "Documents" },
  { to: "/ask", label: "Ask a Question" },
  { to: "/audit-log", label: "Audit Log" },
  { to: "/settings", label: "Settings" },
];

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm ${
    isActive
      ? "bg-surface-container-high text-on-surface"
      : "text-on-surface-muted hover:text-on-surface"
  }`;

export function Layout() {
  const { tenantName, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="flex shrink-0 flex-col justify-between border-surface-border bg-surface-container-high p-4 md:w-60 md:border-r">
        <div>
          <p className="mb-4 font-semibold">SecureRAG</p>
          <nav className="flex flex-row gap-1 overflow-x-auto md:flex-col md:overflow-visible">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <button
          onClick={logout}
          className="mt-4 text-left text-sm text-on-surface-muted hover:text-on-surface"
        >
          Sign out
        </button>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-surface-border px-4 py-3 md:px-6">
          <span className="text-sm text-on-surface-muted">Scoped to your organization</span>
          {tenantName && <Badge variant="success">{tenantName}</Badge>}
        </header>
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
