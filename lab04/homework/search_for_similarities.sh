#!/usr/bin/env bash
# Zapytania tekstowe → top-k obrazów (+ search_results_<grupa>_*.png).
set -euo pipefail

HW="$(cd "$(dirname "$0")" && pwd)"
LAB04="$(cd "$HW/.." && pwd)"
cd "$HW"

K="${K:-5}"
OUTPUT_DIR="${OUTPUT_DIR:-$HW}"
mkdir -p "$OUTPUT_DIR"

slug() {
  echo "$1" | tr ' ' '_' | tr -cd '[:alnum:]_-' | cut -c1-48
}

# 5 prostych — typowe produkty / obiekty z katalogu e-commerce
QUERIES_SIMPLE=(
  "laptop on desk"
  "coffee mug"
  "running shoes"
  "wooden chair"
  "backpack"
)

# 5 średnich — bardziej szczegółowy opis
QUERIES_MEDIUM=(
  "vintage leather armchair"
  "stainless steel water bottle"
  "colorful children's building blocks"
  "ceramic pot with green plant"
  "wireless ergonomic computer mouse"
)

# 5 poza katalogiem — szukamy najbliższego semantycznego trafienia
QUERIES_UNLIKELY=(
  "bomba atomowa"
  "proton"
  "grad"
  "gradient"
  "bałwan w czapce"
  "Jensen Huang"
)

run_queries() {
  local group_label="$1"
  shift
  local -a queries=("$@")

  echo ""
  echo "######## ${group_label} ########"

  for query in "${queries[@]}"; do
    echo ""
    echo "========================================"
    echo "[${group_label}] Query: $query"
    out="$OUTPUT_DIR/search_results_${group_label}_$(slug "$query").png"
    (cd "$LAB04" && uv run python homework/search.py "$query" -k "$K" -o "$out")
  done
}

run_queries "simple" "${QUERIES_SIMPLE[@]}"
run_queries "medium" "${QUERIES_MEDIUM[@]}"
run_queries "unlikely" "${QUERIES_UNLIKELY[@]}"

echo ""
echo "Previews saved in $OUTPUT_DIR/search_results_*.png"