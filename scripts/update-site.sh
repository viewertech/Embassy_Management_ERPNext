#!/usr/bin/env bash
set -euo pipefail
source .env
docker compose build --pull
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} migrate && bench --site ${SITE_NAME} clear-cache"
docker compose up -d
