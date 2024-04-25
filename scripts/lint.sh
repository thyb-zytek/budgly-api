#! /usr/bin/env bash

docker compose run -T api mypy .
docker compose run -T api ruff check . --fix
docker compose run -T api ruff format .
