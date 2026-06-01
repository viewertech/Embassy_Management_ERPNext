#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"
DB_HOST="${DB_HOST:-mariadb}"
DB_PORT="${DB_PORT:-3306}"
SOCKETIO_PORT="${SOCKETIO_PORT:-9000}"
IFS=',' read -ra APPS <<< "${INSTALL_APPS:-erpnext,embassy_management}"

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

for path in (
    Path("sites/common_site_config.json"),
    Path("sites") / os.environ["SITE_NAME"] / "site_config.json",
):
    if not path.exists():
        continue
    data = json.loads(path.read_text()) if path.read_text().strip() else {}
    data.update(values)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
PY'

for app in "${APPS[@]}"; do
  app="$(echo "${app}" | xargs)"
  if docker compose exec backend bench --site "${SITE_NAME}" list-apps | grep -qx "${app}"; then
    echo "App ${app} is already installed on ${SITE_NAME}."
  else
    docker compose exec backend bench --site "${SITE_NAME}" install-app "${app}"
  fi
done

docker compose exec backend bench --site "${SITE_NAME}" migrate
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache

"${ROOT_DIR}/scripts/repair-assets.sh"
