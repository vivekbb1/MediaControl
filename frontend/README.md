# Flip Remote — Lovable UI (frontend)

React + Vite + Tailwind scaffold for the Lovable UI refresh. The Python backend is unchanged.

## Quick start

```bash
# Terminal 1 — backend
python3 server.py 8080

# Terminal 2 — frontend dev (proxies /api to :8080)
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173/app/** (dev) or build and use **http://127.0.0.1:8080/app/** (prod).

## Lovable import

1. Push repo to GitHub.
2. Lovable → Import → set directory to `frontend/`.
3. Prompt: *"Follow docs/LOVABLE_UI_SCOPE.md — redesign all pages, keep api.ts contracts."*

See also: `../docs/LOVABLE_UI_SCOPE.md`, `../lovable.json`.

## Production build

```bash
cd frontend
npm run build
```

`server.py` serves `frontend/dist` at `/app/` when present.

## Structure

```
src/
  lib/api.ts      # REST client (do not break for Lovable)
  lib/types.ts    # API types
  pages/          # Route pages (redesign targets)
  components/     # Shared shell
  hooks/useAuth   # Session context
```

## Env

| Variable | Default |
|----------|---------|
| `VITE_API_BASE` | `` (same origin / dev proxy) |
