import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, roomAppPath } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { DisplaySummary, Location } from "@/lib/types";

export function HomePage() {
  const { user } = useAuth();
  const [displays, setDisplays] = useState<DisplaySummary[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [site, setSite] = useState<{
    homepage_title?: string;
    homepage_lead?: string;
    show_default_remote?: boolean;
  }>({});
  const [defaultRemoteUrl, setDefaultRemoteUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .displays()
      .then((data) => {
        setDisplays(data.displays);
        setLocations(data.locations);
        setSite(data.site);
        setDefaultRemoteUrl(data.default_remote_url ?? null);
      })
      .catch((e) => setError(e.message));
  }, []);

  const byLocation = useMemo(() => {
    const map = new Map<string, DisplaySummary[]>();
    for (const d of displays) {
      const key = d.location || "default";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(d);
    }
    return map;
  }, [displays]);

  const title = site.homepage_title || "TV Remotes";
  const lead =
    site.homepage_lead ||
    "New app UI. Classic remotes (often clearer) live at / on the same server.";

  const defaultRemotePath = defaultRemoteUrl?.startsWith("/d/")
    ? defaultRemoteUrl
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">{title}</h2>
        <p className="mt-2 text-sm text-muted">{lead}</p>
      </div>

      <div className="rounded-2xl border border-border bg-panel p-4 text-sm leading-relaxed">
        <strong>Three layers (same server)</strong>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-muted">
          <li>
            <a href="/" className="font-semibold text-accent">
              Classic remote
            </a>{" "}
            — default day-to-day UI. Open a room and use the Channels pad.
          </li>
          <li>
            <strong className="text-text">This /app UI</strong> — React remotes
            with Channels / EPG / Presence tabs (demo room: Billet).
          </li>
          <li>
            <Link to="/features" className="font-semibold text-accent">
              Features catalog
            </Link>{" "}
            — status/docs for IR gateways, hospitality, access, etc. Not every
            module has a full control screen yet.
          </li>
        </ol>
        <div className="mt-3 flex flex-wrap gap-2">
          <a
            href="/"
            className="inline-flex min-h-11 items-center rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white no-underline"
          >
            Open classic home
          </a>
          <Link
            to="/d/conares/billet?tab=channels"
            className="inline-flex min-h-11 items-center rounded-xl border border-border bg-panel-elevated px-4 py-2.5 text-sm font-semibold no-underline"
          >
            App: Billet Channels
          </Link>
          <a
            href="/d/conares/billet?section=channels"
            className="inline-flex min-h-11 items-center rounded-xl border border-border bg-panel-elevated px-4 py-2.5 text-sm font-semibold no-underline"
          >
            Classic: Billet Channels
          </a>
        </div>
      </div>

      {site.show_default_remote !== false && defaultRemotePath && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-panel p-4">
          <div>
            <strong>Default remote</strong>
            <p className="text-sm text-muted">Open your primary room remote.</p>
          </div>
          <a
            href={defaultRemotePath}
            className="inline-flex min-h-11 items-center rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white no-underline"
          >
            Classic remote
          </a>
        </div>
      )}

      {error && (
        <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}

      {locations.map((loc) => {
        const rooms = byLocation.get(loc.id) ?? [];
        if (!rooms.length) return null;
        return (
          <section key={loc.id} className="space-y-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-base font-bold">{loc.title || loc.id}</h3>
              <span className="text-xs text-muted">{loc.id}</span>
            </div>
            <div className="grid gap-3">
              {rooms.map((room) => {
                const hasBl = Boolean(
                  (room.features as { broadlink?: { configured?: boolean } } | undefined)
                    ?.broadlink?.configured,
                );
                return (
                  <article
                    key={room.id}
                    className="flex flex-col gap-3 rounded-2xl border border-border bg-panel p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <h4 className="font-semibold">{room.title}</h4>
                      <p className="text-xs text-muted">
                        {room.ip ? `${room.ip}:${room.port ?? 1515}` : room.id}
                        {hasBl ? " · Broadlink / Channels" : ""}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <a
                        href={`/d/${room.location}/${room.id}${hasBl ? "?section=channels" : ""}`}
                        className="inline-flex min-h-11 items-center rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white no-underline"
                      >
                        Classic
                      </a>
                      <Link
                        to={
                          hasBl
                            ? `${roomAppPath(room.location, room.id)}?tab=channels`
                            : roomAppPath(room.location, room.id)
                        }
                        className="inline-flex min-h-11 items-center rounded-xl border border-border bg-panel-elevated px-4 py-2.5 text-sm font-semibold no-underline"
                      >
                        App remote
                      </Link>
                      {(user?.is_master || user?.role === "location_admin") && (
                        <a
                          href={`/d/${room.location}/${room.id}/setup`}
                          className="inline-flex min-h-11 items-center rounded-xl border border-border bg-panel-elevated px-4 py-2.5 text-sm font-semibold no-underline"
                        >
                          Setup
                        </a>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        );
      })}

      {!displays.length && !error && (
        <p className="rounded-2xl border border-dashed border-border py-12 text-center text-muted">
          No rooms yet.{" "}
          {(user?.is_master || user?.role === "location_admin") && (
            <a href="/add" className="text-accent">
              Add a room
            </a>
          )}
        </p>
      )}
    </div>
  );
}
