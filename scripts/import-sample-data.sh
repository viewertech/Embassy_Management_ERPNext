#!/usr/bin/env bash
set -euo pipefail
source .env
docker compose run --rm backend bash -lc "bench --site ${SITE_NAME} execute embassy_management.setup.import_sample_data"
echo "Generic sample data imported. Review before production use."
