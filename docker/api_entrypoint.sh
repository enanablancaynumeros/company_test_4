#!/usr/bin/env bash

set -e

: "${POSTGRES_HOST:?Need to set POSTGRES}"
: "${POSTGRES_PORT:?Need to set POSTGRES_PORT}"

bash wait-for-it.sh --timeout=10 ${POSTGRES_HOST}:${POSTGRES_PORT}

mkdir -p ${LOGS_DESTINATION_FOLDER}${LOGGER_SERVICE_NAME}/
cd /src/api/inventory_api

if [[ "$@" == *--migrations* ]]; then
    flask create_database_and_upgrade
    flask alembic_checks
elif [[ "$@" == *--api* ]]; then
    uwsgi --socket 0.0.0.0:${INVENTORY_API_PORT} --yaml /src/api/uwsgi.yaml
fi
