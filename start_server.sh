#!/usr/bin/env bash
set -euo pipefail
# Start the FastAPI app from the repository root so the AIAgents package is importable.
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Activate venv if present
if [ -f "AIAgents/.venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "AIAgents/.venv/bin/activate"
fi

echo "Starting uvicorn from $ROOT_DIR (app: AIAgents.main:app)"
uvicorn AIAgents.main:app --reload --port 8000
