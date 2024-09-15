#! /usr/bin/env bash

echo "============= TYPECHECK ============="
docker compose exec api mypy .
echo "============= LINT ============="
docker compose exec api ruff check . --fix
echo "============= FORMAT ============="
docker compose exec api ruff format .
