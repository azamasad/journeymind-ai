#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ "${1:-start}" = "stop" ]; then
  if [ -f backend/backend.pid ]; then
    kill "$(cat backend/backend.pid)" 2>/dev/null || true
    rm -f backend/backend.pid
  fi
  if [ -f frontend/frontend.pid ]; then
    kill "$(cat frontend/frontend.pid)" 2>/dev/null || true
    rm -f frontend/frontend.pid
  fi
  echo "JourneyMind AI stopped."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not found."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is required but not found."
  exit 1
fi

echo "Starting JourneyMind AI demo..."

# Backend
cd backend
if [ ! -d .venv ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
python3 -m pip install -q -r requirements.txt
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
echo $! > backend.pid
cd ..

# Frontend
cd frontend
if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  npm install
fi
nohup npm run dev -- --host 0.0.0.0 > frontend.log 2>&1 &
echo $! > frontend.pid
cd ..

echo ""
echo "JourneyMind AI is starting."
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Logs:     backend/backend.log, frontend/frontend.log"
echo "  Stop:     ./run_demo.sh stop"
