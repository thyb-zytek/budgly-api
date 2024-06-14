#! /usr/bin/env bash

export USE_NEON_DB=true

if [ $# -lt 1 ]; then
  alembic upgrade head
else
  alembic upgrade $@
fi
