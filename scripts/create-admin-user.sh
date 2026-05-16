#!/usr/bin/env bash
set -euo pipefail
source .env
EMAIL="${1:-admin@example.org}"
FIRST_NAME="${2:-Embassy}"
LAST_NAME="${3:-Administrator}"
PASSWORD="${4:-ChangeMe123!}"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} execute embassy_management.setup.create_admin_user --kwargs '{\"email\":\"${EMAIL}\",\"first_name\":\"${FIRST_NAME}\",\"last_name\":\"${LAST_NAME}\",\"password\":\"${PASSWORD}\"}'"
