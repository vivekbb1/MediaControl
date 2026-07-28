/** Shared types for Flip Remote API responses */

export type UserRole = "admin" | "location_admin" | "room";

export interface AuthUser {
  role: UserRole;
  username?: string;
  scope?: string;
  is_master?: boolean;
  display_id?: string;
  location_id?: string;
  remote_url?: string;
}

export interface Location {
  id: string;
  title?: string;
  remote_host?: string;
  remote_port?: number;
}

export interface SiteSettings {
  homepage_title?: string;
  homepage_lead?: string;
  default_location?: string;
  default_room?: string;
  show_default_remote?: boolean;
}

export interface RemoteSource {
  id: string;
  code: string;
  title: string;
  category: string;
  order?: number;
  provision?: boolean;
  unstable?: boolean;
}

export interface DisplaySummary {
  id: string;
  title: string;
  location: string;
  location_title?: string;
  ip?: string;
  port?: number;
  remote_url: string;
  setup_url: string;
  sources?: RemoteSource[];
  remote_sections?: unknown[];
  icon_catalog?: unknown[];
}

export interface DisplaysResponse {
  ok: boolean;
  displays: DisplaySummary[];
  order: string[];
  locations: Location[];
  site: SiteSettings;
  default_remote_url?: string | null;
}

export interface AuthMeResponse {
  ok: boolean;
  user: AuthUser | null;
}

export interface LoginResponse {
  ok: boolean;
  user?: AuthUser;
  error?: string;
}

export interface DisplayStatus {
  ok: boolean;
  power?: string;
  input?: string;
  volume?: number;
  muted?: boolean;
  error?: string;
}
