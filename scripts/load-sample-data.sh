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
  echo "This will load EMSDEMO generic presentation data into ${SITE_NAME}."
  echo "It first removes existing EMSDEMO/GEN sample data, then creates fresh EMS and ERPNext demo records."
  read -r -p "Type LOAD to continue: " CONFIRM
  if [[ "${CONFIRM}" != "LOAD" ]]; then
    echo "Cancelled."
    exit 1
  fi
fi

docker compose exec backend bench --site "${SITE_NAME}" execute embassy_management.demo_data.load_sample_data
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache

echo "EMSDEMO EMS and ERPNext presentation data loaded for ${SITE_NAME}."
