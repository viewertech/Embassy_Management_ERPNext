#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SOCKETIO_PORT="${SOCKETIO_PORT:-9000}"

echo "Validating Docker Compose configuration..."
docker compose config --quiet

echo "Checking backend connectivity to MariaDB and Redis..."
docker compose exec -T \
  -e SOCKETIO_PORT="${SOCKETIO_PORT}" \
  backend bash -lc 'python - <<PY
import socket

targets = [
    ("mariadb", 3306),
    ("redis-cache", 6379),
    ("redis-queue", 6379),
]

for host, port in targets:
    with socket.create_connection((host, port), timeout=5):
        print(f"OK backend -> {host}:{port}")
PY'

echo "Checking frontend connectivity to backend and websocket..."
docker compose exec -T \
  -e SOCKETIO_PORT="${SOCKETIO_PORT}" \
  frontend bash -lc 'python - <<PY
import os
import socket

targets = [
    ("backend", 8000),
    ("websocket", int(os.environ.get("SOCKETIO_PORT", "9000"))),
]

for host, port in targets:
    with socket.create_connection((host, port), timeout=5):
        print(f"OK frontend -> {host}:{port}")
PY'

echo "Docker service communication checks passed. Powered by Viewertech: https://viewertech.net"
