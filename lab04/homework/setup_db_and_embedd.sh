#!/usr/bin/env bash
# Postgres (lab) + tabela images + CLIP embeddingi do homework.
set -euo pipefail

LAB04="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB04"

MAX_IMAGES="${MAX_IMAGES:-2000}"
BATCH_SIZE="${BATCH_SIZE:-8}"

echo "==> Postgres (vectorscale_db)"
(cd lab/vectorscale_db && docker compose up -d)

echo "==> SQLAlchemy: create table images"
uv run python homework/setup_db.py

echo "==> Vectorize (recreate table, then ingest ${MAX_IMAGES} images, batch=${BATCH_SIZE})"
uv run python homework/vectorize.py --recreate-table --max-images "${MAX_IMAGES}" --batch-size "${BATCH_SIZE}"

echo "==> Done."