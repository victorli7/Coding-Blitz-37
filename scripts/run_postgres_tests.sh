#!/usr/bin/env bash
# Run Postgres integration tests when a database URL is available.
#
# Local example (requires Postgres listening):
#   export TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:5432/flags_test"
#   ./scripts/run_postgres_tests.sh
#
# DigitalOcean dev DB example (from App → db → Connection String):
#   export TEST_DATABASE_URL="postgresql://..."
#   ./scripts/run_postgres_tests.sh

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -z "${TEST_DATABASE_URL:-}" ]]; then
  echo "TEST_DATABASE_URL is not set. Skipping Postgres integration tests."
  echo "SQLite tests still run via: .venv/bin/pytest"
  exit 0
fi

.venv/bin/pytest -v tests/test_postgres_store.py
