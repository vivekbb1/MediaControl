import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Programme = {
  channel?: string;
  channel_name?: string;
  channel_number?: number | string;
  title?: string;
  desc?: string;
  start?: string;
  stop?: string;
  is_live?: boolean;
  ir_command?: string;
  demo?: boolean;
};

type Channel = {
  name?: string;
  epg_id?: string;
  channel_number?: number | string;
  ir_command?: string;
};

type Props = {
  displayId: string;
  onTune: (channel: Channel) => Promise<void> | void;
};

function fmt(iso?: string) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}

export function EPGGuide({ displayId, onTune }: Props) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<string>("");
  const [now, setNow] = useState<Programme[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [programmes, setProgrammes] = useState<Programme[]>([]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .roomEpg(displayId)
      .then((data) => {
        if (cancelled) return;
        setMode(String(data.mode ?? ""));
        setNow((data.now as Programme[]) ?? []);
        setChannels((data.channels as Channel[]) ?? []);
        setProgrammes((data.programmes as Programme[]) ?? []);
        setError(null);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [displayId]);

  if (loading) return <p className="text-sm text-muted">Loading TV guide…</p>;
  if (error) {
    return <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">{error}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-muted">TV Guide</h3>
        <span className="rounded-full bg-panel-elevated px-2 py-0.5 text-[11px] text-muted">
          {mode || "epg"}
        </span>
      </div>

      {now.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs uppercase tracking-wide text-muted">Now playing</h4>
          <div className="grid gap-2 sm:grid-cols-2">
            {now.slice(0, 6).map((p) => (
              <button
                key={`${p.channel}-${p.start}`}
                type="button"
                onClick={() =>
                  onTune({
                    name: p.channel_name,
                    epg_id: p.channel,
                    channel_number: p.channel_number,
                    ir_command: p.ir_command,
                  })
                }
                className="rounded-xl border border-accent/40 bg-panel p-3 text-left hover:border-accent"
              >
                <div className="text-xs text-accent">
                  {p.channel_name || p.channel} · {fmt(p.start)}–{fmt(p.stop)}
                </div>
                <div className="mt-1 font-medium">{p.title}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <h4 className="text-xs uppercase tracking-wide text-muted">Channels</h4>
        <div className="grid gap-2 sm:grid-cols-2">
          {channels.map((ch) => (
            <button
              key={ch.epg_id || ch.name}
              type="button"
              onClick={() => onTune(ch)}
              className="flex items-center justify-between rounded-xl border border-border bg-panel-elevated px-3 py-3 text-left hover:border-accent"
            >
              <span>
                <span className="font-semibold">{ch.name}</span>
                <span className="ml-2 text-xs text-muted">#{ch.channel_number}</span>
              </span>
              <span className="text-xs text-accent">Tune</span>
            </button>
          ))}
        </div>
      </div>

      {programmes.length > 0 && (
        <div className="max-h-64 overflow-y-auto rounded-xl border border-border">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-panel-elevated text-muted">
              <tr>
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Channel</th>
                <th className="px-3 py-2">Show</th>
              </tr>
            </thead>
            <tbody>
              {programmes.slice(0, 40).map((p, i) => (
                <tr key={`${p.channel}-${p.start}-${i}`} className="border-t border-border/60">
                  <td className="px-3 py-2 whitespace-nowrap">
                    {fmt(p.start)}
                    {p.is_live ? " ●" : ""}
                  </td>
                  <td className="px-3 py-2">{p.channel_name || p.channel}</td>
                  <td className="px-3 py-2">{p.title}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
