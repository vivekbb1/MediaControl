#!/bin/bash
# Double-click in Finder to start the remote server (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PORT="${FLIP_PORT:-8080}"

pip3 install -q -r requirements-core.txt

if [[ ! -f frontend/dist/index.html ]]; then
  (cd frontend && npm install && npm run build)
fi

echo ""
echo "  MediaControl remote"
echo "  → http://localhost:${PORT}/app/"
echo "  → http://127.0.0.1:${PORT}/app/d/conares/billet?tab=channels"
echo "  Login: admin / changeme"
echo ""
echo "  Leave this window open. Press Ctrl+C to stop."
echo ""

exec python3 server.py "$PORT"
