#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

SITE_NAME="${SITE_NAME:-embassy.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-change-admin-password}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-${MYSQL_ROOT_PASSWORD:-change-db-root-password}}"
DB_ROOT_USER="${DB_ROOT_USER:-root}"
DB_HOST="${DB_HOST:-mariadb}"
DB_PORT="${DB_PORT:-3306}"
SOCKETIO_PORT="${SOCKETIO_PORT:-9000}"

configure_bench_for_docker() {
  docker compose exec \
    -e SITE_NAME="${SITE_NAME}" \
    -e DB_HOST="${DB_HOST}" \
    -e DB_PORT="${DB_PORT}" \
    -e SOCKETIO_PORT="${SOCKETIO_PORT}" \
    backend bash -lc 'cd /home/frappe/frappe-bench && timestamp="$(date +%Y%m%d%H%M%S)" && mkdir -p assets sites && if [ -e sites/assets ] && [ ! -L sites/assets ]; then mv sites/assets "sites/assets.bak.${timestamp}"; fi && rm -f sites/assets && ln -s /home/frappe/frappe-bench/assets sites/assets && ls -1 apps > sites/apps.txt && for app in $(ls -1 apps); do public="apps/$app/$app/public"; if [ -d "$public" ]; then if [ -e "assets/$app" ] && [ ! -L "assets/$app" ]; then mv "assets/$app" "assets/$app.bak.${timestamp}"; fi; rm -f "assets/$app"; ln -s "../$public" "assets/$app"; fi; done && ./env/bin/python - <<'"'"'PY'"'"'
import json
import os
from pathlib import Path

values = {
    "db_host": os.environ["DB_HOST"],
    "db_port": int(os.environ["DB_PORT"]),
    "redis_cache": "redis://redis-cache:6379",
    "redis_queue": "redis://redis-queue:6379",
    "redis_socketio": "redis://redis-queue:6379",
    "socketio_port": int(os.environ["SOCKETIO_PORT"]),
}

def update(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if path.exists() and path.read_text().strip():
        data = json.loads(path.read_text())
    data.update(values)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")

update(Path("sites/common_site_config.json"))
site_config = Path("sites") / os.environ["SITE_NAME"] / "site_config.json"
if site_config.exists():
    update(site_config)
PY'
}

docker compose build backend
docker compose up -d mariadb redis-cache redis-queue configurator backend websocket queue-short queue-long scheduler frontend
configure_bench_for_docker

if docker compose exec backend bench --site "${SITE_NAME}" list-apps >/dev/null 2>&1; then
  echo "Site ${SITE_NAME} already exists."
else
  docker compose exec backend bench new-site "${SITE_NAME}" \
    --db-host "${DB_HOST}" \
    --db-port "${DB_PORT}" \
    --db-root-username "${DB_ROOT_USER}" \
    --db-root-password "${DB_ROOT_PASSWORD}" \
    --mariadb-user-host-login-scope='%' \
    --admin-password "${ADMIN_PASSWORD}" \
    --set-default
fi

configure_bench_for_docker

"${ROOT_DIR}/scripts/install-apps.sh"

echo "Site ${SITE_NAME} is ready at http://localhost:${HTTP_PUBLISH_PORT:-8080}"
