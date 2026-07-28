import { Link, useParams } from "react-router-dom";

/** Setup page stub — Lovable should implement full admin setup UI */
export function SetupPage() {
  const { location = "", room = "" } = useParams();

  return (
    <div className="space-y-4 rounded-2xl border border-border bg-panel p-6">
      <h2 className="text-xl font-semibold">Room setup</h2>
      <p className="text-sm text-muted">
        {location} / {room} — connection, sources, layout, and templates.
      </p>
      <p className="text-sm text-muted">
        Use APIs:{" "}
        <code className="text-text">GET/PUT /api/displays/:id/config</code>,{" "}
        <code className="text-text">POST /api/displays/:id/discover</code>,{" "}
        <code className="text-text">GET /api/layout-templates</code>.
      </p>
      <Link
        to={`/d/${location}/${room}`}
        className="inline-flex rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white no-underline"
      >
        ← Back to remote
      </Link>
    </div>
  );
}
