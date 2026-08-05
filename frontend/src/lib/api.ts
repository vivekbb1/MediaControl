import type {
  AuthMeResponse,
  DisplaysResponse,
  DisplayStatus,
  LoginResponse,
  SiteSettings,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers: HeadersInit = {
    Accept: "application/json",
    ...(init.body ? { "Content-Type": "application/json" } : {}),
    ...init.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers,
  });

  const data = (await res.json().catch(() => ({}))) as T & {
    ok?: boolean;
    error?: string;
  };

  if (!res.ok) {
    throw new Error(
      (data as { error?: string }).error ?? `Request failed (${res.status})`,
    );
  }

  return data;
}

export const api = {
  me: () => request<AuthMeResponse>("/api/auth/me"),

  login: (username: string, password: string) =>
    request<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  logout: () =>
    request<{ ok: boolean }>("/api/auth/logout", { method: "POST" }),

  displays: () => request<DisplaysResponse>("/api/displays"),

  displayStatus: (id: string) =>
    request<DisplayStatus>(`/api/displays/${encodeURIComponent(id)}/status`),

  sendCommand: (id: string, command: string) =>
    request<{ ok: boolean }>(`/api/displays/${encodeURIComponent(id)}/send`, {
      method: "POST",
      body: JSON.stringify({ command }),
    }),

  siteSettings: () =>
    request<{ ok: boolean; settings: SiteSettings }>("/api/site-settings"),

  updateSiteSettings: (settings: Partial<SiteSettings>) =>
    request<{ ok: boolean; settings: SiteSettings }>("/api/site-settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),

  featuresCatalog: () =>
    request<{
      ok: boolean;
      summary: { total: number; available: number; unavailable: number };
      features: Array<{
        id: string;
        name: string;
        category: string;
        description: string;
        available: boolean;
        error?: string | null;
        docs?: string | null;
        docs_exists?: boolean;
        ui_path?: string;
      }>;
      version?: string;
    }>("/api/features/catalog"),

  featureDetail: (section: string) =>
    request<Record<string, unknown>>(
      `/api/features/${encodeURIComponent(section)}`,
    ),
};

/** Map legacy /d/... paths to React Router paths under /app */
export function legacyPathToApp(path: string): string {
  if (path.startsWith("/app")) return path;
  if (path.startsWith("/d/")) return `/app${path}`;
  if (path === "/settings") return "/app/settings";
  if (path === "/add") return "/app/add";
  if (path === "/locations") return "/app/locations";
  return `/app${path.startsWith("/") ? path : `/${path}`}`;
}

/** In-app route (BrowserRouter basename is /app) */
export function roomAppPath(location: string, room: string, setup = false): string {
  const base = `/d/${location}/${room}`;
  return setup ? `${base}/setup` : base;
}
