import {
  FileText,
  LogOut,
  MessageSquareText,
  ScrollText,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { Badge } from "./Badge";
import { ThemeToggle } from "./ThemeToggle";

const ADMIN_NAV_ITEMS = [
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/ask", label: "Ask a Question", icon: MessageSquareText },
  { to: "/audit-log", label: "Audit Log", icon: ScrollText },
  { to: "/org/members", label: "Members", icon: Users },
  { to: "/settings", label: "Settings", icon: Settings },
];

// Members can only query — no document management, no settings, no member management.
const MEMBER_NAV_ITEMS = [
  { to: "/ask", label: "Ask a Question", icon: MessageSquareText },
];

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 rounded-md px-3 py-2 text-sm ${
    isActive
      ? "bg-surface-container-high text-on-surface"
      : "text-on-surface-muted hover:text-on-surface"
  }`;

export function Layout() {
  const { tenantName, role, name, email, logout } = useAuth();
  const navItems = role === "admin" ? ADMIN_NAV_ITEMS : MEMBER_NAV_ITEMS;

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="flex shrink-0 flex-col justify-between border-surface-border bg-surface-container-high p-4 md:w-60 md:border-r">
        <div>
          <p className="mb-4 flex items-center gap-2 font-semibold">
            <ShieldCheck size={18} className="text-accent" />
            SecureRAG
          </p>
          <nav className="flex flex-row gap-1 overflow-x-auto md:flex-col md:overflow-visible">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                <item.icon size={16} />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <button
          type="button"
          onClick={logout}
          className="mt-4 flex items-center gap-2 text-left text-sm text-on-surface-muted hover:text-on-surface"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-surface-border px-4 py-3 md:px-6">
          <span className="text-sm text-on-surface-muted">Scoped to your organization</span>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {tenantName && <Badge variant="success">{tenantName}</Badge>}
            {/* Admins ARE the org, effectively — only show a member's own
                name/email alongside the org badge so they can tell whose
                account they're signed in as. */}
            {role === "member" && (name || email) && (
              <Badge variant="neutral">{name || email}</Badge>
            )}
          </div>
        </header>
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

