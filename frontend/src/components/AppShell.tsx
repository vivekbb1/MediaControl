import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export function AppShell() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-full bg-[radial-gradient(1200px_600px_at_10%_-10%,#1a2744_0%,var(--color-bg)_55%)]">
      <header className="mx-auto flex max-w-4xl flex-wrap items-center gap-3 px-4 pb-2 pt-[max(1rem,env(safe-area-inset-top))]">
        <h1 className="flex-1 text-xl font-semibold tracking-tight sm:text-2xl">
          Flip Remote
        </h1>
        {user && (
          <span className="rounded-full bg-[#2a3550] px-2.5 py-1 text-xs text-accent">
            {user.is_master ? "Master" : user.role.replace("_", " ")}
          </span>
        )}
        <nav className="flex items-center gap-2">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `rounded-xl border px-3 py-2 text-sm font-medium min-h-11 inline-flex items-center ${
                isActive
                  ? "border-accent bg-accent text-white"
                  : "border-border bg-panel-elevated text-text hover:bg-panel"
              }`
            }
          >
            Rooms
          </NavLink>
          {(user?.is_master || user?.role === "location_admin") && (
            <NavLink
              to="/settings"
              className="rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm font-medium min-h-11 inline-flex items-center hover:bg-panel"
            >
              Settings
            </NavLink>
          )}
          <button
            type="button"
            onClick={() => logout()}
            className="rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm min-h-11 hover:bg-panel"
          >
            Sign out
          </button>
        </nav>
      </header>
      <main className="mx-auto max-w-4xl px-4 pb-8">
        <Outlet />
      </main>
    </div>
  );
}
