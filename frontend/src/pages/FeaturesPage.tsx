import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "@/lib/api";

type FeatureItem = {
  id: string;
  name: string;
  category: string;
  description: string;
  available: boolean;
  error?: string | null;
  docs?: string | null;
  docs_exists?: boolean;
  ui_path?: string;
};

type FeaturesResponse = {
  ok: boolean;
  summary: { total: number; available: number; unavailable: number };
  features: FeatureItem[];
  version?: string;
};

type DetailPayload = Record<string, unknown>;

const DETAIL_KEYS = [
  "broadlink",
  "epg",
  "beacons",
  "hospitality",
  "access",
  "sources",
  "smarthome",
] as const;

export function FeaturesPage() {
  const { section } = useParams<{ section?: string }>();
  const [data, setData] = useState<FeaturesResponse | null>(null);
  const [detail, setDetail] = useState<DetailPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .featuresCatalog()
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!section || !DETAIL_KEYS.includes(section as (typeof DETAIL_KEYS)[number])) {
      setDetail(null);
      return;
    }
    api
      .featureDetail(section)
      .then(setDetail)
      .catch((e: Error) => setError(e.message));
  }, [section]);

  const byCategory = useMemo(() => {
    const map = new Map<string, FeatureItem[]>();
    for (const f of data?.features ?? []) {
      if (!map.has(f.category)) map.set(f.category, []);
      map.get(f.category)!.push(f);
    }
    return map;
  }, [data]);

  if (section && DETAIL_KEYS.includes(section as (typeof DETAIL_KEYS)[number])) {
    return (
      <div className="space-y-4">
        <Link to="/features" className="text-sm text-accent no-underline hover:underline">
          ← All features
        </Link>
        <h2 className="text-2xl font-semibold capitalize">{section.replace("-", " ")}</h2>
        {error && (
          <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">{error}</p>
        )}
        {detail ? (
          <pre className="overflow-x-auto rounded-2xl border border-border bg-panel p-4 text-xs leading-relaxed text-muted">
            {JSON.stringify(detail, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-muted">Loading…</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Features catalog</h2>
        <p className="mt-2 text-sm text-muted">
          This is a <strong className="text-text">status / docs catalog</strong>,
          not a second remote. Day-to-day control stays on the{" "}
          <a href="/" className="text-accent">
            classic UI
          </a>{" "}
          or{" "}
          <Link to="/" className="text-accent">
            app remotes
          </Link>
          . Green = Python module imports; many items still need hardware config
          and do not have full control screens yet.
        </p>
      </div>

      {error && (
        <p className="rounded-xl bg-danger/15 px-4 py-3 text-sm text-danger">{error}</p>
      )}

      {data && (
        <div className="grid grid-cols-3 gap-3">
          <Stat label="Total" value={data.summary.total} />
          <Stat label="Available" value={data.summary.available} accent />
          <Stat label="Unavailable" value={data.summary.unavailable} />
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {DETAIL_KEYS.map((key) => (
          <Link
            key={key}
            to={`/features/${key}`}
            className="rounded-xl border border-border bg-panel-elevated px-3 py-2 text-sm capitalize no-underline hover:bg-panel"
          >
            {key}
          </Link>
        ))}
      </div>

      {[...byCategory.entries()].map(([category, items]) => (
        <section key={category} className="space-y-3">
          <h3 className="text-lg font-medium text-muted">{category}</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {items.map((f) => (
              <article
                key={f.id}
                className="rounded-2xl border border-border bg-panel p-4"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold">{f.name}</h4>
                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium ${
                      f.available
                        ? "bg-emerald-500/20 text-emerald-300"
                        : "bg-amber-500/20 text-amber-200"
                    }`}
                  >
                    {f.available ? "Ready" : "Setup needed"}
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted">{f.description}</p>
                {f.error && (
                  <p className="mt-2 text-xs text-amber-200/90">{f.error}</p>
                )}
                {f.ui_path && f.ui_path.startsWith("/features/") && (
                  <Link
                    to={f.ui_path}
                    className="mt-3 inline-flex text-sm text-accent no-underline hover:underline"
                  >
                    Open details →
                  </Link>
                )}
              </article>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-border bg-panel p-3 text-center">
      <div
        className={`text-2xl font-semibold ${accent ? "text-accent" : ""}`}
      >
        {value}
      </div>
      <div className="text-xs text-muted">{label}</div>
    </div>
  );
}
