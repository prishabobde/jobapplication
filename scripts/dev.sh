#!/usr/bin/env bash
# Start backend (FastAPI) + frontend (Vite), verify they respond, then open the app in your browser.
# Prerequisites: backend/.venv + pip install; frontend npm install
#
# Usage:
#   ./scripts/dev.sh           # open http://localhost:5173 when ready
#   ./scripts/dev.sh --no-open # same, but do not launch a browser

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

NO_OPEN=false
for arg in "$@"; do
  if [[ "$arg" == "--no-open" ]]; then
    NO_OPEN=true
  fi
done

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup INT TERM EXIT

PIDS=()

wait_for_http() {
  local url=$1
  local label=$2
  local max_attempts=${3:-60}
  local i
  for ((i = 1; i <= max_attempts; i++)); do
    if curl -sf --connect-timeout 1 --max-time 3 "$url" >/dev/null; then
      echo "OK: $label ($url)"
      return 0
    fi
    sleep 0.5
  done
  echo "Timeout: $label did not respond at $url" >&2
  return 1
}

open_browser() {
  local url=$1
  if [[ "$NO_OPEN" == true ]]; then
    return 0
  fi
  if command -v open >/dev/null 2>&1; then
    open "$url"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 &
  elif command -v explorer.exe >/dev/null 2>&1; then
    explorer.exe "$url" >/dev/null 2>&1 &
  else
    echo "Open manually: $url" >&2
  fi
}

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  echo "Missing backend/.venv — create it first:" >&2
  echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo "Missing frontend/node_modules — run: cd frontend && npm install" >&2
  exit 1
fi

echo "Starting backend on http://127.0.0.1:3001 …"
(
  cd "$ROOT/backend"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --host 127.0.0.1 --port 3001
) &
PIDS+=("$!")

wait_for_http "http://127.0.0.1:3001/api/health" "Backend API" || exit 1
curl -sf "http://127.0.0.1:3001/api/health" | cat
echo

echo "Starting frontend on http://localhost:5173 …"
(
  cd "$ROOT/frontend"
  exec npm run dev
) &
PIDS+=("$!")

wait_for_http "http://127.0.0.1:5173/" "Vite dev server" || exit 1

echo ""
echo "Local URLs:"
echo "  App (browser): http://localhost:5173"
echo "  API health:    http://127.0.0.1:3001/api/health"
echo "  API docs:      http://127.0.0.1:3001/docs"
echo ""
if [[ "$NO_OPEN" == false ]]; then
  echo "Opening app in your default browser…"
  open_browser "http://localhost:5173"
fi
echo "Press Ctrl+C to stop backend and frontend."
echo ""

wait
