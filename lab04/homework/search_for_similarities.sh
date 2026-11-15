#!/usr/bin/env bash
# Zapytania tekstowe → top-k obrazów (01_…png, 02_…png, kolejność jak poniżej).
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

# 5 średnich — kilka cech naraz, nisze produktowe (nadal typowy katalog)
QUERIES_MEDIUM=(
  "mid-century modern walnut sideboard with brass handles"
  "waterproof hiking boots with bright orange laces"
  "set of six matte black ceramic dinner plates"
  "foldable pet stroller for small dogs in grey fabric"
  "rechargeable LED desk lamp with built-in USB charger"
)

# 5 trudnych — sceny, relacje, styl zdjęcia; słabe dopasowanie pojedynczym słowem
QUERIES_HARD=(
  "home office dual monitor standing desk cable management tidy"
  "kitchen marble countertop espresso machine morning sunlight"
  "gift box with red satin ribbon product unboxing flat lay"
  "jewelry display velvet tray gold necklace and pearl earrings"
  "toddler safely playing on soft foam indoor climbing blocks"
)

# poza katalogiem — szukamy najbliższego semantycznego trafienia
QUERIES_UNLIKELY=(
  "atomic bomb"
  "infinity stones"
  "Iron Man"
  "Mark Zuckerberg"
  "Aliens building the pyramids"
  "GPU card"
  "Nvidia"
  "Jensen Huang"
)

query_index=0

run_queries() {
  local group_label="$1"
  shift
  local -a queries=("$@")

  echo ""
  echo "######## ${group_label} ########"

  for query in "${queries[@]}"; do
    query_index=$((query_index + 1))
    num=$(printf '%02d' "$query_index")
    echo ""
    echo "========================================"
    echo "${num} [${group_label}] Query: $query"
    out="$OUTPUT_DIR/${num}_$(slug "$query").png"
    (cd "$LAB04" && uv run python homework/search.py "$query" -k "$K" -o "$out")
  done
}

run_queries "simple" "${QUERIES_SIMPLE[@]}"
run_queries "medium" "${QUERIES_MEDIUM[@]}"
run_queries "hard" "${QUERIES_HARD[@]}"
run_queries "unlikely" "${QUERIES_UNLIKELY[@]}"

echo ""
echo "Previews saved in $OUTPUT_DIR/01_*.png … $(printf '%02d' "$query_index")_*.png"