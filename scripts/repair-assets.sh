#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck source=scripts/lib/env.sh
source "${ROOT_DIR}/scripts/lib/env.sh"
load_env_file ".env"

SITE_NAME="${SITE_NAME:-embassy.localhost}"

sync_container_assets() {
  local service="$1"

  echo "Repairing asset links in ${service}..."
  docker compose exec -T "${service}" bash -lc '
set -euo pipefail
cd /home/frappe/frappe-bench

timestamp="$(date +%Y%m%d%H%M%S)"
mkdir -p assets sites

if [ -e sites/assets ] && [ ! -L sites/assets ]; then
  mv sites/assets "sites/assets.bak.${timestamp}"
fi
rm -f sites/assets
ln -s /home/frappe/frappe-bench/assets sites/assets

ls -1 apps > sites/apps.txt
for app in $(ls -1 apps); do
  public="apps/${app}/${app}/public"
  if [ -d "${public}" ]; then
    if [ -L "assets/${app}" ] || [ -f "assets/${app}" ]; then
      rm -f "assets/${app}"
    elif [ -d "assets/${app}" ]; then
      mv "assets/${app}" "assets/${app}.bak.${timestamp}"
    fi
    ln -s "../${public}" "assets/${app}"
  fi
done

if [ ! -f assets/embassy_management/js/embassy.js ]; then
  echo "Missing EMS JS asset in ${HOSTNAME}: assets/embassy_management/js/embassy.js" >&2
  exit 1
fi

if [ ! -f assets/embassy_management/css/embassy.css ]; then
  echo "Missing EMS CSS asset in ${HOSTNAME}: assets/embassy_management/css/embassy.css" >&2
  exit 1
fi

if [ ! -f assets/embassy_management/img/app_icon.png ]; then
  echo "Missing EMS icon asset in ${HOSTNAME}: assets/embassy_management/img/app_icon.png" >&2
  exit 1
fi

echo "Asset links:"
ls -ld sites/assets assets/frappe assets/erpnext assets/embassy_management 2>/dev/null || true
'
}

repair_manifest() {
  local service="$1"

  echo "Repairing asset manifest in ${service}..."
  docker compose exec -T "${service}" bash -lc '
set -euo pipefail
cd /home/frappe/frappe-bench

./env/bin/python - <<PY
import json
import os
import re
import shutil
from pathlib import Path


assets_root = Path("assets")
manifest = assets_root / "assets.json"
hash_pattern = re.compile(r"^(?P<prefix>.+\.bundle)\.[^.]+(?P<suffix>\.(?:css|js))$")


def asset_path(value):
    clean_value = value.split("?", 1)[0]
    if clean_value.startswith("/assets/"):
        return assets_root / clean_value[len("/assets/") :], "/assets/"
    if clean_value.startswith("assets/"):
        return Path(clean_value), "assets/"
    return assets_root / clean_value.lstrip("/"), ""


def asset_value(path, prefix):
    rel = path.relative_to(assets_root).as_posix()
    if prefix == "/assets/":
        return f"/assets/{rel}"
    if prefix == "assets/":
        return f"assets/{rel}"
    return rel


def link_compatibility_name(missing_path, target_path):
    if missing_path.exists():
        return False
    try:
        os.symlink(target_path.name, missing_path)
    except OSError:
        shutil.copy2(target_path, missing_path)
    return True


if not manifest.exists():
    print("Asset manifest not found; skipped.")
    raise SystemExit

data = json.loads(manifest.read_text())
updated = 0
linked = 0

for key, value in list(data.items()):
    if not isinstance(value, str):
        continue

    missing_path, prefix = asset_path(value)
    if missing_path.exists():
        continue

    match = hash_pattern.match(missing_path.name)
    if not match or not missing_path.parent.exists():
        continue

    bundle_prefix = match.group("prefix")
    bundle_suffix = match.group("suffix")
    candidates = [
        candidate
        for candidate in missing_path.parent.glob(f"{bundle_prefix}.*{bundle_suffix}")
        if candidate.name != missing_path.name and candidate.is_file() and not candidate.name.endswith(".map")
    ]
    if not candidates:
        continue

    replacement = sorted(candidates, key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[0]
    data[key] = asset_value(replacement, prefix)
    updated += 1
    if link_compatibility_name(missing_path, replacement):
        linked += 1

if updated:
    manifest.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
print(f"Asset manifest repaired: {updated} stale entries updated, {linked} compatibility links created.")
PY
'
}

sync_container_assets backend
sync_container_assets frontend
repair_manifest frontend

docker compose exec -T redis-cache redis-cli FLUSHALL
docker compose exec -T backend bench --site "${SITE_NAME}" clear-cache
docker compose exec -T backend bench --site "${SITE_NAME}" clear-website-cache
docker compose restart backend frontend websocket queue-short queue-long scheduler

echo "Checking EMS asset URLs through the published frontend..."
HTTP_PUBLISH_PORT="${HTTP_PUBLISH_PORT:-8091}"
for asset in \
  /assets/embassy_management/js/embassy.js \
  /assets/embassy_management/css/embassy.css \
  /assets/embassy_management/img/app_icon.png
do
  for attempt in $(seq 1 30); do
    if curl -fsSI "http://127.0.0.1:${HTTP_PUBLISH_PORT}${asset}" >/dev/null; then
      echo "OK ${asset}"
      break
    fi
    if [ "${attempt}" -eq 30 ]; then
      echo "Asset URL still unavailable: ${asset}" >&2
      exit 1
    fi
    sleep 2
  done
done
