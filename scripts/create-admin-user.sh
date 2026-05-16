#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"
EMAIL="${1:-admin@example.org}"
FIRST_NAME="${2:-Embassy}"
LAST_NAME="${3:-Administrator}"
PASSWORD="${4:-ChangeMe123!}"

docker compose exec backend bench --site "${SITE_NAME}" execute embassy_management.setup.create_admin_user --kwargs "{\"email\":\"${EMAIL}\",\"first_name\":\"${FIRST_NAME}\",\"last_name\":\"${LAST_NAME}\",\"password\":\"${PASSWORD}\"}"
