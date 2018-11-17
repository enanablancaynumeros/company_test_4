#!/usr/bin/env bash

set -e
set -x

bash wait-for-it.sh --timeout=10 ${POSTGRES_HOST}:${POSTGRES_PORT}
bash wait-for-it.sh --timeout=10 ${INVENTORY_API_HOST}:${INVENTORY_API_PORT}

behave /src/tests/ --no-capture --stop --summary --show-timings --no-skipped
