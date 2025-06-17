#!/usr/bin/env bash
set -euo pipefail

psql --username "$PG_USER" --dbname "$PG_NAME" <<-EOSQL
  CREATE SCHEMA IF NOT EXISTS content;
  ALTER SCHEMA content OWNER TO "$PG_USER";
EOSQL

psql \
  --username "$PG_USER" \
  --dbname   "$PG_NAME" \
  -f /postgres_dump/01-dump.sql