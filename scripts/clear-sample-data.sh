#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"
YES="${1:-}"

if [[ "${YES}" != "--yes" ]]; then
  echo "This will remove only EMSDEMO/GEN-tagged sample data from ${SITE_NAME}."
  echo "Real pilot or production records should not be touched."
  read -r -p "Type CLEAR to continue: " CONFIRM
  if [[ "${CONFIRM}" != "CLEAR" ]]; then
    echo "Cancelled."
    exit 1
  fi
fi

docker compose exec backend bench --site "${SITE_NAME}" execute embassy_management.demo_data.clear_sample_data
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache

echo "EMSDEMO sample data cleared for ${SITE_NAME}."
