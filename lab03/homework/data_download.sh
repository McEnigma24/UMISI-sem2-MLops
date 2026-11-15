#!/usr/bin/env bash
# Brakujące parquety 2024 + taxi_zone_lookup.csv do lab03/data.
set -euo pipefail

HW="$(cd "$(dirname "$0")" && pwd)"
LAB03="$(cd "$HW/.." && pwd)"
DATA="$LAB03/data"
mkdir -p "$DATA"

BASE="https://d37ci6vzurychx.cloudfront.net/trip-data"
for month in $(seq 1 12); do
  out="$DATA/${month}.parquet"
  if [[ -f "$out" ]]; then
    continue
  fi
  echo "==> yellow_tripdata_2024-$(printf '%02d' "$month").parquet"
  curl -L --progress-bar -o "$out" "${BASE}/yellow_tripdata_2024-$(printf '%02d' "$month").parquet"
done

lookup="$DATA/taxi_zone_lookup.csv"
if [[ ! -f "$lookup" ]]; then
  echo "==> taxi_zone_lookup.csv"
  curl -L --progress-bar -o "$lookup" \
    "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
fi

echo "==> Gotowe: $DATA"