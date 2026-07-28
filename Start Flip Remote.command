#!/bin/bash
# Double-click in Finder to start the remote server (macOS).
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PORT="${FLIP_PORT:-8080}"

pip3 install -q -r requirements.txt

echo ""
echo "  Samsung Flip Remote"
echo "  → http://localhost:${PORT}/"
echo "  → http://127.0.0.1:${PORT}/"
echo ""
echo "  Leave this window open. Press Ctrl+C to stop."
echo ""

exec python3 server.py "$PORT"
