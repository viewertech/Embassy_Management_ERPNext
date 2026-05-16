#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --database path/to/database.sql.gz [--public-files path] [--private-files path]"
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"
DATABASE=""
PUBLIC_FILES=""
PRIVATE_FILES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --database)
      DATABASE="$2"
      shift 2
      ;;
    --public-files)
      PUBLIC_FILES="$2"
      shift 2
      ;;
    --private-files)
      PRIVATE_FILES="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${DATABASE}" || ! -f "${DATABASE}" ]]; then
  usage
  exit 1
fi

docker compose cp "${DATABASE}" "backend:/tmp/ems-restore-database.sql.gz"

RESTORE_ARGS=(bench --site "${SITE_NAME}" restore /tmp/ems-restore-database.sql.gz --force)

if [[ -n "${PUBLIC_FILES}" ]]; then
  docker compose cp "${PUBLIC_FILES}" "backend:/tmp/ems-restore-public-files.tar"
  RESTORE_ARGS+=(--with-public-files /tmp/ems-restore-public-files.tar)
fi

if [[ -n "${PRIVATE_FILES}" ]]; then
  docker compose cp "${PRIVATE_FILES}" "backend:/tmp/ems-restore-private-files.tar"
  RESTORE_ARGS+=(--with-private-files /tmp/ems-restore-private-files.tar)
fi

docker compose exec backend "${RESTORE_ARGS[@]}"
docker compose exec backend bench --site "${SITE_NAME}" migrate
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache

echo "Restore completed for ${SITE_NAME}."
