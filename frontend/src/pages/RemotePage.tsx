import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import type { DisplaySummary, DisplayStatus } from "@/lib/types";

export function RemotePage() {
  const { location = "", room = "" } = useParams();
  const [display, setDisplay] = useState<DisplaySummary | null>(null);
  const [status, setStatus] = useState<DisplayStatus | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .displays()
      .then((data) => {
        const match = data.displays.find(
          (d) => d.id === room && d.location === location,
        );
        if (!match) throw new Error("Room not found");
        setDisplay(match);
      })
      .catch((e) => setError(e.message));
  }, [location, room]);

  useEffect(() => {
    if (!display) return;
    let cancelled = false;
    const poll = () => {
      api
        .displayStatus(display.id)
        .then((s) => {
          if (!cancelled) setStatus(s);
        })
        .catch(() => undefined);
    };
    poll();
    const id = window.setInterval(poll, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [display]);

  async function send(command: string) {
    if (!display) return;
    setBusy(command);
    try {
      await api.sendCommand(display.id, command);
      const s = await api.displayStatus(display.id);
      setStatus(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Command failed");
    } finally {
      setBusy(null);
    }
  }

  if (error && !display) {
    return (
      <p className="rounded-xl bg-danger/15 px-4 py-3 text-danger">{error}</p>
    );
  }

  if (!display) {
    return <p className="text-muted">Loading remote…</p>;
  }

  const sections = (display.remote_sections ?? []) as Array<{
    id?: string;
    title?: string;
    buttons?: Array<{ id?: string; title?: string; command?: string }>;
  }>;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted">
            {display.location_title || location}
          </p>
          <h2 className="text-xl font-semibold">{display.title}</h2>
          {status && (
            <p className="mt-1 text-sm text-muted">
              Power: {status.power ?? "—"} · Input: {status.input ?? "—"}
              {status.volume != null && ` · Vol ${status.volume}`}
            </p>
          )}
        </div>
        <Link
          to={`/d/${location}/${room}/setup`}
          className="rounded-xl border border-border px-3 py-2 text-sm no-underline"
        >
          Setup
        </Link>
      </div>

      {sections.length > 0 ? (
        sections.map((section) => (
          <section key={section.id ?? section.title} className="space-y-2">
            {section.title && (
              <h3 className="text-sm font-semibold text-muted">{section.title}</h3>
            )}
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
              {(section.buttons ?? []).map((btn) => (
                <button
                  key={btn.id ?? btn.command}
                  type="button"
                  disabled={!btn.command || busy === btn.command}
                  onClick={() => btn.command && send(btn.command)}
                  className="min-h-[52px] rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm font-medium hover:border-accent disabled:opacity-50"
                >
                  {btn.title ?? btn.id ?? btn.command}
                </button>
              ))}
            </div>
          </section>
        ))
      ) : (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {["POWER", "POWER_OFF", "VOLUME_UP", "VOLUME_DOWN", "MUTE"].map((cmd) => (
            <button
              key={cmd}
              type="button"
              disabled={busy === cmd}
              onClick={() => send(cmd)}
              className="min-h-[52px] rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm font-medium"
            >
              {cmd.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      )}

      <p className="text-xs text-muted">
        Lovable: replace this page with a polished touch remote using{" "}
        <code>display.remote_sections</code> and brand icons from{" "}
        <code>/assets/*</code>.
      </p>
    </div>
  );
}
