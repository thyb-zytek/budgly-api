#! /usr/bin/env bash

# Let the DB start
python scripts/pool_db.py

# Run migrations
if [ $ENV == "development" ]
  then
    alembic upgrade head
fi
