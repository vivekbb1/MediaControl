import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Settings</h2>
      <section className="rounded-2xl border border-border bg-panel p-5 space-y-2">
        <h3 className="font-semibold">Account</h3>
        <p className="text-sm text-muted">Signed in as {user?.username}</p>
        <p className="text-sm text-muted">
          Password change: <code>PUT /api/auth/admin-password</code>
        </p>
      </section>
      {user?.is_master && (
        <section className="rounded-2xl border border-border bg-panel p-5">
          <h3 className="font-semibold">Locations</h3>
          <Link to="/locations" className="mt-2 inline-block text-accent">
            Manage locations →
          </Link>
        </section>
      )}
      <section className="rounded-2xl border border-dashed border-border p-5 opacity-80">
        <h3 className="font-semibold">Plan &amp; billing</h3>
        <p className="text-sm text-muted">Coming soon — subscription tiers by location.</p>
      </section>
      <p className="text-xs text-muted">
        Full settings parity: see legacy <a href="/settings">/settings</a> until
        Lovable redesign is complete.
      </p>
    </div>
  );
}
