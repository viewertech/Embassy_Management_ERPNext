#!/usr/bin/env bash
set -euo pipefail
source .env
docker compose up -d mariadb redis-cache redis-queue configurator
docker compose run --rm backend bash -lc "bench new-site ${SITE_NAME} --mariadb-root-password ${DB_ROOT_PASSWORD} --admin-password ${ADMIN_PASSWORD} --set-default --force"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} install-app erpnext"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} install-app embassy_management"
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} set-config developer_mode 0 && bench --site ${SITE_NAME} clear-cache"
echo "Site ${SITE_NAME} created with ERPNext and embassy_management."
