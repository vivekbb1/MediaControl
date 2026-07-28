# Lovable UI Refresh — Scope Document

**Project:** Samsung Flip / Multimedia Room Remote  
**Backend:** Python `server.py` (REST + session cookies) — **unchanged**  
**Target UI:** React 18 + TypeScript + Vite + Tailwind CSS v4 (Lovable-compatible)  
**Location in repo:** `frontend/`  
**Preview URL (local):** http://127.0.0.1:5173/app/ (dev) · http://127.0.0.1:8080/app/ (production build)

---

## 1. Product intent

Roll out a **subscription-ready**, **multi-location** remote control for Samsung Flip Pro (and similar MDC displays) in small offices and residential multimedia setups.

| Actor | Goal |
|-------|------|
| **Master admin** | All locations, billing tier, templates, location admins |
| **Location admin** | One site — rooms, setup, room credentials |
| **Room user** | Single-room remote only |
| **Guest (future)** | Read-only or limited presets |

**Business model (future):** Cloud-hosted SaaS priced by **locations × rooms**. This UI refresh must feel product-grade, not internal-tool grade.

---

## 2. What Lovable should redesign

### Pages (must ship)

| Route | Current file | Purpose |
|-------|--------------|---------|
| `/app/` | `HomePage` | Location-grouped room list, default remote shortcut, Add/Settings menus |
| `/app/login` | `LoginPage` | Admin / location admin / room login |
| `/app/d/:location/:room` | `RemotePage` | Touch-friendly TV remote (grids, icons, status bar) |
| `/app/d/:location/:room/setup` | `SetupPage` | Admin setup — connection, layout, sources, templates |
| `/app/settings` | `SettingsPage` | Account, homepage UI, location admins, templates |
| `/app/locations` | `LocationsPage` | CRUD locations (master only) |
| `/app/add` | `AddRoomPage` | New room wizard |

### Legacy URLs (redirect only — do not rebuild routing logic)

- `/d/:location/:room` → served by Python until cutover; new app uses same path under `/app`
- Old `/d/:room` → server redirects to canonical location path

---

## 3. Design direction

### Visual baseline (current tokens — refine, don’t discard)

```
background:   #0f1117
panel:        #1a1d27
panel-elevated:#232735
border:       #2e3344
text:         #e8ecf4
muted:        #8b93a7
accent:       #4f8cff
danger:       #f2555a
success:      #3dd68c
```

### UX principles

1. **Dark-first**, high contrast for AV environments (dim rooms, wall mounts).
2. **Touch targets ≥ 44px** on remote and home actions.
3. **Icon-first** source grids with brand PNGs/SVGs from `/assets/*`.
4. **Progressive disclosure** — Settings/Add as menus, not cluttered headers.
5. **Mobile + tablet + desktop** — remote usable on phone in portrait.
6. **Accessible** — focus rings, aria labels on icon buttons, live status region.

### Lovable creative latitude

- Typography scale, spacing rhythm, micro-interactions, empty states
- Component library polish (cards, dropdowns, forms, toasts)
- Optional light theme (low priority)
- Dashboard-style home for multi-location admins

### Out of design scope

- Backend/API changes
- MDC protocol, TV discovery logic
- Payment/subscription UI (placeholder card only)

---

## 4. API contract (frontend consumes as-is)

Base URL: same origin in prod; dev proxy → `http://127.0.0.1:8080`

All requests: `credentials: 'include'` (session cookie `flip_session`).

### Auth

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/auth/login` | `{ username, password }` |
| POST | `/api/auth/logout` | |
| GET | `/api/auth/me` | `{ user: { role, username, is_master, location_id?, remote_url? } }` |
| PUT | `/api/auth/admin-password` | Master password change |

**Roles:** `admin` (master), `location_admin`, `room`

### Data

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/displays` | `displays[], locations[], site{}, default_remote_url` |
| POST | `/api/displays` | Create room |
| GET/PUT | `/api/displays/:id/config` | Room config |
| GET | `/api/displays/:id/status` | Power, input, volume |
| POST | `/api/displays/:id/send` | `{ command }` |
| GET/PUT | `/api/site-settings` | Homepage title, default room |
| GET/PUT | `/api/locations` | Master only for writes |
| GET | `/api/layout-templates` | Template list |

Static assets: `/assets/*`, `/brand_icons.js`, `/button_svgs.js`

Full handler reference: `server.py`

---

## 5. Lovable workflow

### Option A — Import this repo (recommended)

1. Push repo to GitHub.
2. Lovable → **New project → Import from GitHub**.
3. Set root to `frontend/` (or import whole repo and set working directory).
4. Ensure **Vite boots** (`npm install && npm run dev`).
5. First prompt: *“Read `docs/LOVABLE_UI_SCOPE.md` and `frontend/src/lib/api.ts`. Redesign all pages to a polished product UI while keeping API calls unchanged.”*

### Option B — Greenfield in Lovable, merge later

1. Create new Lovable project with React + Vite + Tailwind.
2. Copy `frontend/src/lib/api.ts` and `types.ts` into Lovable export.
3. Sync via GitHub to `frontend/` branch `lovable-ui`.

### Environment

| Variable | Dev | Prod |
|----------|-----|------|
| `VITE_API_BASE` | `` (proxy) | `` (same origin) |

No Supabase required — backend is Python.

---

## 6. Acceptance criteria

- [ ] All pages in §2 implemented with responsive layouts
- [ ] Session auth works (login, logout, role-based redirects)
- [ ] Room remote sends commands and polls status
- [ ] URLs use `/d/:location/:room` pattern
- [ ] Brand icons load from existing `/assets` paths
- [ ] Master vs location admin permissions respected in UI
- [ ] `npm run build` produces `frontend/dist` servable at `/app/`
- [ ] Lighthouse accessibility ≥ 90 on home + remote
- [ ] No regression in TV control flows (manual QA checklist)

---

## 7. Cutover plan

1. **Phase 1:** Lovable redesign in `frontend/`; legacy HTML remains at `/`
2. **Phase 2:** Link on legacy home → “Preview new UI” → `/app/`
3. **Phase 3:** Default to `/app/` when `frontend/dist` exists (server flag)
4. **Phase 4:** Remove legacy `*.html` after parity sign-off

---

## 8. Subscription placeholder (future sprint)

Settings → **Plan & billing** (disabled): show tier limits (locations, rooms). Backend TBD — UI only stores read-only limits from future `/api/subscription`.

---

## 9. References

- `frontend/README.md` — dev commands
- `lovable.json` — machine-readable scope summary for Lovable agent
- `displays.yaml` — sample data shape
- `auth.yaml` — roles (do not commit secrets)

---

*Document version: 1.0 · July 2026*
