#!/usr/bin/env bash

load_env_file() {
  local env_file="${1:-.env}"
  [[ -f "${env_file}" ]] || return 0

  local line key value
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    line="${line#"${line%%[![:space:]]*}"}"

    [[ -z "${line}" || "${line}" == \#* ]] && continue

    if [[ "${line}" =~ ^export[[:space:]]+(.+)$ ]]; then
      line="${BASH_REMATCH[1]}"
    fi

    if [[ "${line}" != *=* ]]; then
      echo "Skipping invalid dotenv line in ${env_file}: ${line}" >&2
      continue
    fi

    key="${line%%=*}"
    value="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"

    if [[ ! "${key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      echo "Skipping invalid dotenv key in ${env_file}: ${key}" >&2
      continue
    fi

    if [[ ${#value} -ge 2 && ( ( "${value}" == \"*\" && "${value}" == *\" ) || ( "${value}" == \'*\' && "${value}" == *\' ) ) ]]; then
      value="${value:1:${#value}-2}"
    fi

    export "${key}=${value}"
  done < "${env_file}"
}
