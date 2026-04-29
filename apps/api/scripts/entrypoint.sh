#!/usr/bin/env sh
set -e

if [ "${DATABASE_URL:-}" != "" ]; then
  echo "Waiting for database..."
  # Docker Compose healthchecks normally handle this. This is extra safety.
  sleep 1
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
fi

exec "$@"
