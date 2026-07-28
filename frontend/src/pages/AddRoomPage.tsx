import { Link } from "react-router-dom";

export function AddRoomPage() {
  return (
    <div className="space-y-4 rounded-2xl border border-border bg-panel p-6">
      <h2 className="text-xl font-semibold">Add room</h2>
      <p className="text-sm text-muted">
        Room wizard stub — POST <code className="text-text">/api/displays</code>
      </p>
      <a href="/add" className="text-accent text-sm">
        Use legacy add room form →
      </a>
      <div>
        <Link to="/" className="text-sm text-muted">
          ← Home
        </Link>
      </div>
    </div>
  );
}
