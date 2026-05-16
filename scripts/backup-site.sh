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
BACKUP_DIR="${BACKUP_DIR:-./backups}"
STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET_DIR="${BACKUP_DIR}/${SITE_NAME}-${STAMP}"

mkdir -p "${TARGET_DIR}"

docker compose exec backend bench --site "${SITE_NAME}" backup --with-files
docker compose cp "backend:/home/frappe/frappe-bench/sites/${SITE_NAME}/private/backups/." "${TARGET_DIR}/"

find "${BACKUP_DIR}" -mindepth 1 -maxdepth 1 -type d -mtime +"${BACKUP_RETENTION_DAYS:-14}" -print -exec rm -rf {} \;

echo "Backup copied to ${TARGET_DIR}"
