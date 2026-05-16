#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: ./scripts/restore-site.sh /path/to/database.sql.gz [public-files.tar] [private-files.tar]"
  exit 1
fi
source .env
DB_BACKUP="$1"
PUBLIC_FILES="${2:-}"
PRIVATE_FILES="${3:-}"
docker compose cp "${DB_BACKUP}" "backend:/tmp/restore.sql.gz"
if [ -n "${PUBLIC_FILES}" ]; then docker compose cp "${PUBLIC_FILES}" "backend:/tmp/public-files.tar"; fi
if [ -n "${PRIVATE_FILES}" ]; then docker compose cp "${PRIVATE_FILES}" "backend:/tmp/private-files.tar"; fi
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} restore /tmp/restore.sql.gz --mariadb-root-password ${DB_ROOT_PASSWORD} --force"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} migrate && bench --site ${SITE_NAME} clear-cache"
