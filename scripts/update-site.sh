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

"${ROOT_DIR}/scripts/backup-site.sh"

docker compose pull
docker compose build backend
docker compose up -d
docker compose exec backend bench --site "${SITE_NAME}" migrate
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache

echo "Update completed for ${SITE_NAME}."
