#!/usr/bin/env bash
# Wykonanie notebooka homework → dataset.parquet.
set -euo pipefail

HW="$(cd "$(dirname "$0")" && pwd)"
LAB03="$(cd "$HW/.." && pwd)"
cd "$LAB03"

NOTEBOOK="${NOTEBOOK:-homework/homework.ipynb}"
OUT_PARQUET="${OUT_PARQUET:-homework/dataset.parquet}"

echo "==> Execute $NOTEBOOK"
uv run jupyter nbconvert --to notebook --execute --inplace "$NOTEBOOK"

if [[ -f "$OUT_PARQUET" ]]; then
  size=$(stat -c%s "$OUT_PARQUET" 2>/dev/null || stat -f%z "$OUT_PARQUET")
  echo "==> $OUT_PARQUET (${size} B)"
else
  echo "Brak $OUT_PARQUET (sprawdź ścieżkę zapisu w notebooku)" >&2
  exit 1
fi