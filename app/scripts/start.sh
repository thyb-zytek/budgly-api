#! /usr/bin/env bash

ENV=${ENV:-development}
echo "============= Starting app [$ENV] ============="

# Let the DB start
echo "============= Verifying DB ============="
python scripts/pool_db.py

# Run migrations
if [ $ENV == "development" ]
  then
    echo "============= Upgrading migrations ============="
    alembic upgrade head;
    echo "============= Starting development server ============="
  else
    echo "============= Starting production server ============="
    fastapi run --workers 4
fi
