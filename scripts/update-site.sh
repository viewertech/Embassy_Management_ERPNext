#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"

"${ROOT_DIR}/scripts/backup-site.sh"

docker compose pull
docker compose build backend
docker compose up -d
docker compose exec backend bench --site "${SITE_NAME}" migrate
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache
"${ROOT_DIR}/scripts/repair-assets.sh"

echo "Update completed for ${SITE_NAME}."
