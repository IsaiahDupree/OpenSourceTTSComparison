#!/usr/bin/env bash
set -euo pipefail

# Default port 8811 if API_PORT is not set
PORT="${API_PORT:-8811}"

exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
