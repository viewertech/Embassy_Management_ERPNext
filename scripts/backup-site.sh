#!/usr/bin/env bash
set -euo pipefail
source .env
mkdir -p backups
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} backup --with-files"
docker compose cp "backend:/home/frappe/frappe-bench/sites/${SITE_NAME}/private/backups" "./backups/${SITE_NAME}-$(date +%Y%m%d-%H%M%S)" || true
echo "Backup completed under ./backups"
