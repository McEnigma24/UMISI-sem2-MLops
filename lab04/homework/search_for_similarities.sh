#!/usr/bin/env bash
# Kilka zapytań tekstowych → top-k obrazów (+ search_results_*.png w homework).
set -euo pipefail

HW="$(cd "$(dirname "$0")" && pwd)"
LAB04="$(cd "$HW/.." && pwd)"
cd "$HW"

K="${K:-5}"

slug() {
  echo "$1" | tr ' ' '_' | tr -cd '[:alnum:]_-' | cut -c1-40
}

QUERIES=(
  "laptop on desk"
  "red sports car"
  "wooden dining table"
  "running shoes"
  "coffee mug"
)

for query in "${QUERIES[@]}"; do
  echo ""
  echo "========================================"
  echo "Query: $query"
  out="search_results_$(slug "$query").png"
  (cd "$LAB04" && uv run python homework/search.py "$query" -k "$K" -o "$HW/$out")
done

echo ""
echo "Previews saved in $HW/search_results_*.png"