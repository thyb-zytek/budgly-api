#! /usr/bin/env bash

if [ -z `docker-compose ps --services --filter "status=running" | grep api` ]; then
  echo "Env is not running, so we start it.";
  docker compose up -d;
fi

echo "- Run mypy check";
docker compose exec api mypy .;
echo "- Run ruff check";
docker compose exec api ruff check . --fix;
echo "- Run ruff format";
docker compose exec api ruff format .;
