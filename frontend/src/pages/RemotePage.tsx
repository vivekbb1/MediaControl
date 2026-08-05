import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import type { DisplaySummary, DisplayStatus } from "@/lib/types";
import { ChannelPad } from "@/components/ChannelPad";
import { EPGGuide } from "@/components/EPGGuide";
import { BeaconPresence } from "@/components/BeaconPresence";

type Tab = "remote" | "channels" | "epg" | "presence";

type RoomFeatures = {
  broadlink?: {
    configured?: boolean;
    dry_run?: boolean;
    has_number_pad?: boolean;
  };
  epg?: { enabled?: boolean; channel_count?: number };
  beacons?: { enabled?: boolean };
};

export function RemotePage() {
  const { location = "", room = "" } = useParams();
  const [display, setDisplay] = useState<DisplaySummary | null>(null);
  const [status, setStatus] = useState<DisplayStatus | null>(null);
  const [features, setFeatures] = useState<RoomFeatures | null>(null);
  const [tab, setTab] = useState<Tab>("remote");
  const [busy, setBusy] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
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
        const f = (match as DisplaySummary & { features?: RoomFeatures }).features;
        if (f) setFeatures(f);
      })
      .catch((e) => setError(e.message));
  }, [location, room]);

  useEffect(() => {
    if (!display) return;
    api
      .roomFeatures(display.id)
      .then((f) => setFeatures(f))
      .catch(() => undefined);
  }, [display]);

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
    setToast(null);
    try {
      const useIr =
        features?.broadlink?.configured &&
        (command.startsWith("num_") ||
          ["ch_up", "ch_down", "last", "guide", "up", "down", "left", "right", "ok", "back", "menu", "exit", "info", "play", "pause", "stop", "rewind", "forward", "record"].includes(command));
      const result = useIr
        ? await api.sendIr(display.id, command)
        : await api.sendCommand(display.id, command);
      if (result && "dry_run" in result && result.dry_run) {
        setToast(`Dry-run: ${command}`);
      }
      if (!useIr) {
        const s = await api.displayStatus(display.id);
        setStatus(s);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Command failed");
    } finally {
      setBusy(null);
    }
  }

  async function tune(channel: string | number, ir_command?: string) {
    if (!display) return;
    setBusy(`tune:${channel}`);
    try {
      const result = await api.tuneChannel(display.id, {
        channel,
        ir_command,
      });
      setToast(
        result.dry_run
          ? `Dry-run tune ${channel}`
          : `Tuned to ${channel}`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Tune failed");
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
    label?: string;
    buttons?: Array<{ id?: string; title?: string; command?: string }>;
  }>;

  const tabs: Array<{ id: Tab; label: string; show: boolean }> = [
    { id: "remote", label: "Remote", show: true },
    {
      id: "channels",
      label: "Channels",
      show: Boolean(features?.broadlink?.configured),
    },
    { id: "epg", label: "EPG", show: Boolean(features?.epg?.enabled) },
    {
      id: "presence",
      label: "Presence",
      show: Boolean(features?.beacons?.enabled),
    },
  ];

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
          {features?.broadlink?.dry_run && (
            <p className="mt-1 text-xs text-amber-200">
              Broadlink dry-run mode (no hardware required)
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

      <div className="flex flex-wrap gap-2">
        {tabs
          .filter((t) => t.show)
          .map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={`rounded-xl border px-3 py-2 text-sm min-h-11 ${
                tab === t.id
                  ? "border-accent bg-accent text-white"
                  : "border-border bg-panel-elevated"
              }`}
            >
              {t.label}
            </button>
          ))}
      </div>

      {toast && (
        <p className="rounded-xl border border-border bg-panel px-3 py-2 text-sm text-muted">
          {toast}
        </p>
      )}
      {error && (
        <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">
          {error}
          <button
            type="button"
            className="ml-3 text-xs underline"
            onClick={() => setError(null)}
          >
            dismiss
          </button>
        </p>
      )}

      {tab === "channels" && (
        <ChannelPad
          busy={busy}
          onSend={send}
          onTune={(digits) => tune(digits)}
        />
      )}

      {tab === "epg" && (
        <EPGGuide
          displayId={display.id}
          onTune={(ch) =>
            tune(ch.channel_number ?? "", ch.ir_command || undefined)
          }
        />
      )}

      {tab === "presence" && <BeaconPresence displayId={display.id} />}

      {tab === "remote" &&
        (sections.length > 0 ? (
          sections.map((section) => (
            <section key={section.id ?? section.title} className="space-y-2">
              {(section.label || section.title) && (
                <h3 className="text-sm font-semibold text-muted">
                  {section.label ?? section.title}
                </h3>
              )}
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
                {(section.buttons ?? []).map((btn) => {
                  const cmd = btn.command ?? btn.id;
                  return (
                    <button
                      key={btn.id ?? cmd}
                      type="button"
                      disabled={!cmd || busy === cmd}
                      onClick={() => cmd && send(cmd)}
                      className="min-h-[52px] rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm font-medium hover:border-accent disabled:opacity-50"
                    >
                      {btn.title ?? btn.id ?? cmd}
                    </button>
                  );
                })}
              </div>
            </section>
          ))
        ) : (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {["POWER", "POWER_OFF", "VOLUME_UP", "VOLUME_DOWN", "MUTE"].map(
              (cmd) => (
                <button
                  key={cmd}
                  type="button"
                  disabled={busy === cmd}
                  onClick={() => send(cmd)}
                  className="min-h-[52px] rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm font-medium"
                >
                  {cmd.replace(/_/g, " ")}
                </button>
              ),
            )}
          </div>
        ))}
    </div>
  );
}
