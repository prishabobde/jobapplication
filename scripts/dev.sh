#!/usr/bin/env bash
# Start backend (FastAPI) and frontend (Vite) together for local development.
# Prerequisites: backend venv + pip install; frontend npm install.
# Usage: from repo root —  ./scripts/dev.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup INT TERM EXIT

PIDS=()

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  echo "Missing backend/.venv — create it first:" >&2
  echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo "Missing frontend/node_modules — run: cd frontend && npm install" >&2
  exit 1
fi

(
  cd "$ROOT/backend"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --host 127.0.0.1 --port 3001
) &
PIDS+=("$!")

(
  cd "$ROOT/frontend"
  exec npm run dev
) &
PIDS+=("$!")

echo "Backend:  http://127.0.0.1:3001  (API docs: /docs)"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."
wait
