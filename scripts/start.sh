#!/bin/bash
# Run MediaControl / Flip remote locally (bind 0.0.0.0, default port 8080)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${1:-8080}"

echo "Installing core Python deps..."
pip3 install -q -r requirements-core.txt

if [[ ! -f frontend/dist/index.html ]]; then
  echo "Building frontend..."
  (cd frontend && npm install && npm run build)
fi

echo ""
echo "  MediaControl remote"
echo "  → http://localhost:${PORT}/app/"
echo "  → http://127.0.0.1:${PORT}/app/d/conares/billet?tab=channels"
echo "  Login: admin / changeme"
echo ""
echo "  Leave this terminal open. Ctrl+C to stop."
echo ""

exec python3 server.py "$PORT"
