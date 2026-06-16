#!/usr/bin/env bash
# Verify feature flags API against a deployed App Platform app (Postgres-backed).
#
# Usage:
#   APP_URL=https://your-app.ondigitalocean.app ./scripts/verify_do_postgres.sh
#
# Prerequisites:
# 1. App spec applied once in DO (databases + DATABASE_URL in .do/app.yaml)
# 2. Latest code deployed with psycopg and PostgresFlagStore

set -euo pipefail

APP_URL="${APP_URL:?Set APP_URL to your App Platform URL (no trailing slash)}"

DARK_MODE_JSON='{"name":"dark_mode","default_state":false,"segment_key":"region","segments":{"us-east":false,"us-west":true}}'

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

# Usage: api_call METHOD PATH EXPECTED_STATUSES "desc" [curl args...]
# EXPECTED_STATUSES is a pipe-separated list, e.g. "200" or "201|409"
api_call() {
  local method=$1
  local path=$2
  local expected=$3
  local desc=$4
  shift 4

  local tmp
  tmp=$(mktemp)
  local status
  status=$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" "$APP_URL$path" "$@")
  local body
  body=$(cat "$tmp")
  rm -f "$tmp"

  local IFS='|'
  local ok=0
  for code in $expected; do
    if [[ "$status" == "$code" ]]; then
      ok=1
      break
    fi
  done

  if [[ $ok -eq 0 ]]; then
    echo "$body" >&2
    fail "$desc → HTTP $status (expected one of: ${expected//|/, })"
  fi

  printf '%s' "$body"
}

echo "==> Health"
health=$(api_call GET /health 200 "GET /health")
echo "$health"

echo
echo "==> Create dark_mode"
create_response=$(api_call POST /flags "201|409" "POST /flags" \
  -H 'Content-Type: application/json' \
  -d "$DARK_MODE_JSON")
echo "$create_response"

echo
echo "==> List flags"
list_response=$(api_call GET /flags 200 "GET /flags")
echo "$list_response"
if [[ "$list_response" != *'"name":"dark_mode"'* && "$list_response" != *'"name": "dark_mode"'* ]]; then
  fail "dark_mode not found in GET /flags response"
fi

echo
echo "==> Evaluate us-west"
west_response=$(api_call GET '/flags/dark_mode/evaluate?region=us-west' 200 "GET evaluate us-west")
echo "$west_response"
if [[ "$west_response" != *'"enabled":true'* && "$west_response" != *'"enabled": true'* ]]; then
  fail "us-west evaluation did not return enabled: true"
fi

echo
echo "==> Evaluate us-east"
east_response=$(api_call GET '/flags/dark_mode/evaluate?region=us-east' 200 "GET evaluate us-east")
echo "$east_response"
if [[ "$east_response" != *'"enabled":false'* && "$east_response" != *'"enabled": false'* ]]; then
  fail "us-east evaluation did not return enabled: false"
fi

echo
echo "==> Evaluate eu-central"
default_response=$(api_call GET '/flags/dark_mode/evaluate?region=eu-central' 200 "GET evaluate eu-central")
echo "$default_response"
if [[ "$default_response" != *'"enabled":false'* && "$default_response" != *'"enabled": false'* ]]; then
  fail "eu-central evaluation did not return enabled: false"
fi
if [[ "$default_response" != *'"source":"default"'* && "$default_response" != *'"source": "default"'* ]]; then
  fail "eu-central evaluation did not return source: default"
fi

echo
echo "Done."
