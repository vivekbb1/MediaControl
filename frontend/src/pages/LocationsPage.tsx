import { Link } from "react-router-dom";

export function LocationsPage() {
  return (
    <div className="space-y-4 rounded-2xl border border-border bg-panel p-6">
      <h2 className="text-xl font-semibold">Locations</h2>
      <p className="text-sm text-muted">Master-only location CRUD.</p>
      <p className="text-sm text-muted">
        APIs: <code className="text-text">GET/POST /api/locations</code>,{" "}
        <code className="text-text">PUT /api/locations/:id</code>
      </p>
      <a href="/locations" className="text-accent text-sm">
        Use legacy locations UI →
      </a>
      <div>
        <Link to="/" className="text-sm text-muted">
          ← Home
        </Link>
      </div>
    </div>
  );
}
