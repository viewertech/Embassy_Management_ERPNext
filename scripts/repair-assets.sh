#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

SITE_NAME="${SITE_NAME:-embassy.localhost}"

docker compose exec backend bash -lc '
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
    if [ -e "assets/${app}" ] && [ ! -L "assets/${app}" ]; then
      mv "assets/${app}" "assets/${app}.bak.${timestamp}"
    fi
    rm -f "assets/${app}"
    ln -s "../${public}" "assets/${app}"
  fi
done

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


if manifest.exists():
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

echo "Asset links:"
ls -ld sites/assets assets/frappe assets/erpnext assets/embassy_management 2>/dev/null || true
if [ -f assets/assets.json ]; then
  echo "Current asset manifest:"
  grep -o "website.bundle.[A-Z0-9]*.css" assets/assets.json | head -1 || true
  grep -o "login.bundle.[A-Z0-9]*.css" assets/assets.json | head -1 || true
fi
'

docker compose exec redis-cache redis-cli FLUSHALL
docker compose exec backend bench --site "${SITE_NAME}" clear-cache
docker compose exec backend bench --site "${SITE_NAME}" clear-website-cache
docker compose restart backend frontend websocket queue-short queue-long scheduler
