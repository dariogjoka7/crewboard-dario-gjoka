#!/usr/bin/env bash
set -e

# Default Postgres settings
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=crewboard}"
: "${POSTGRES_USER:=crewboard}"
: "${POSTGRES_PASSWORD:=crewboard}"

echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."

# Wait until Postgres is ready using pg_isready
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    echo "Postgres is unavailable - sleeping 1s"
    sleep 1
done

echo "Postgres is up - running migrations"

# Run Alembic migrations
alembic upgrade head

# Optionally seed the DB
python db/seed.py

echo "Starting FastAPI"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload