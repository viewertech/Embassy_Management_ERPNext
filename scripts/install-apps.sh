#!/usr/bin/env bash
set -euo pipefail
source .env
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} install-app embassy_management || true"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} migrate && bench --site ${SITE_NAME} clear-cache"
