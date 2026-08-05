import { useMemo, useState } from "react";

type Props = {
  busy: string | null;
  onSend: (command: string) => Promise<void> | void;
  onTune?: (digits: string) => Promise<void> | void;
  disabled?: boolean;
};

const PAD = [
  ["1", "2", "3"],
  ["4", "5", "6"],
  ["7", "8", "9"],
  ["CH−", "0", "CH+"],
] as const;

export function ChannelPad({ busy, onSend, onTune, disabled }: Props) {
  const [buffer, setBuffer] = useState("");

  const digits = useMemo(() => buffer.replace(/\D/g, "").slice(0, 4), [buffer]);

  async function press(label: string) {
    if (disabled) return;
    if (label === "CH+") return onSend("ch_up");
    if (label === "CH−") return onSend("ch_down");
    const d = label;
    const next = (digits + d).slice(0, 4);
    setBuffer(next);
    await onSend(`num_${d}`);
  }

  async function go() {
    if (!digits) return;
    if (onTune) await onTune(digits);
    else {
      for (const d of digits) {
        await onSend(`num_${d}`);
      }
    }
    setBuffer("");
  }

  return (
    <div className="space-y-3 rounded-2xl border border-border bg-panel p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-muted">Channel pad</h3>
        <div className="rounded-lg bg-panel-elevated px-3 py-1 font-mono text-lg tracking-widest">
          {digits || "····"}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {PAD.flat().map((label) => (
          <button
            key={label}
            type="button"
            disabled={disabled || Boolean(busy)}
            onClick={() => press(label)}
            className="min-h-12 rounded-xl border border-border bg-panel-elevated text-base font-semibold hover:border-accent disabled:opacity-50"
          >
            {label}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2">
        <button
          type="button"
          disabled={disabled || Boolean(busy)}
          onClick={() => onSend("last")}
          className="min-h-11 rounded-xl border border-border bg-panel-elevated text-sm disabled:opacity-50"
        >
          Last
        </button>
        <button
          type="button"
          disabled={disabled || !digits || Boolean(busy)}
          onClick={() => go()}
          className="min-h-11 rounded-xl bg-accent text-sm font-semibold text-white disabled:opacity-50"
        >
          Go
        </button>
        <button
          type="button"
          disabled={disabled || Boolean(busy)}
          onClick={() => onSend("guide")}
          className="min-h-11 rounded-xl border border-border bg-panel-elevated text-sm disabled:opacity-50"
        >
          Guide
        </button>
      </div>
    </div>
  );
}
