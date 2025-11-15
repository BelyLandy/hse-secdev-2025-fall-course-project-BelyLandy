#!/bin/sh
set -e

DB_PATH="${APP_DB_PATH:-/data/app.db}"
DB_DIR="$(dirname "$DB_PATH")"

chmod 1777 /tmp || true
mkdir -p /run && chmod 0755 /run || true

if [ "$(id -u)" = "0" ]; then
  mkdir -p "$DB_DIR" || true
  chown -R app:app "$DB_DIR" || true
  chmod 0775 "$DB_DIR" || true

  exec su -s /bin/sh -c "$*" app
fi

exec "$@"
