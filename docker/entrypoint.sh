#!/usr/bin/env bash
set -e

if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
  until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    sleep 0.5
  done
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Starting: $*"
exec "$@"
