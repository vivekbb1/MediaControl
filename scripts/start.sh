#!/bin/bash
# Run Flip Pro remote (bind all interfaces on PORT, default 8080)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${1:-8080}"
pip3 install -q -r requirements.txt
exec python3 server.py "$PORT"
