import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Occupant = {
  user_id?: string;
  name?: string;
  zone?: string;
  distance_meters?: number;
  entered_at?: string;
  demo?: boolean;
};

type Props = {
  displayId: string;
};

export function BeaconPresence({ displayId }: Props) {
  const [data, setData] = useState<{
    occupied?: boolean;
    occupants?: Occupant[];
    beacon_id?: string;
    enabled?: boolean;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      const res = await api.roomBeacons(displayId);
      setData(res);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load presence");
    }
  }

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 8000);
    return () => window.clearInterval(id);
  }, [displayId]);

  async function simulate(zone: string) {
    setBusy(true);
    try {
      await api.reportBeacon(displayId, {
        user_id: "demo_phone",
        name: "Demo Phone",
        zone,
        rssi: zone === "immediate" ? -50 : zone === "near" ? -65 : -80,
      });
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setBusy(false);
    }
  }

  if (error && !data) {
    return <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">{error}</p>;
  }

  const occupants = data?.occupants ?? [];

  return (
    <div className="space-y-3 rounded-2xl border border-border bg-panel p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-muted">Presence</h3>
          <p className="text-xs text-muted">{data?.beacon_id || "beacon"}</p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
            data?.occupied
              ? "bg-emerald-500/20 text-emerald-300"
              : "bg-panel-elevated text-muted"
          }`}
        >
          {data?.occupied ? "Occupied" : "Vacant"}
        </span>
      </div>

      {occupants.length === 0 ? (
        <p className="text-sm text-muted">No occupants detected.</p>
      ) : (
        <ul className="space-y-2">
          {occupants.map((o) => (
            <li
              key={o.user_id}
              className="flex items-center justify-between rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm"
            >
              <span>
                {o.name || o.user_id}
                {o.demo ? " (demo)" : ""}
              </span>
              <span className="text-xs text-muted">{o.zone}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="flex flex-wrap gap-2">
        {(["immediate", "near", "far", "unknown"] as const).map((zone) => (
          <button
            key={zone}
            type="button"
            disabled={busy}
            onClick={() => simulate(zone)}
            className="rounded-xl border border-border px-3 py-2 text-xs capitalize hover:border-accent disabled:opacity-50"
          >
            Scan {zone}
          </button>
        ))}
      </div>
    </div>
  );
}
