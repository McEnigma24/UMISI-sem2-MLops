#!/usr/bin/env bash
# Jeden etap kumulatywny katalogu: 20 → [0,20%%), 40 → [20%%,40%%), … (inkrementalny insert, bez czyszczenia DB).
# Użycie: ./run_catalog_stage.sh 20
# Kontynuacja: ./run_catalog_stage.sh 40
# Od zera:     RESET=1 ./run_catalog_stage.sh 20
set -euo pipefail

STAGE_PCT="${1:-${STAGE_PCT:-}}"
if [[ -z "$STAGE_PCT" ]]; then
  echo "Usage: STAGE_PCT=20 $0   lub   $0 20" >&2
  exit 1
fi

HW="$(cd "$(dirname "$0")" && pwd)"
LAB04="$(cd "$HW/.." && pwd)"
cd "$LAB04"

BATCH_SIZE="${BATCH_SIZE:-32}"
PATHS_FILE="$HW/data/abo/valid_image_paths.txt"
CATALOG_TOTAL="$(wc -l < "$PATHS_FILE" | tr -d ' ')"
RUN_ROOT="${RUN_ROOT:-$HW/results/incremental_scaling}"
STATE="$RUN_ROOT/state.json"
mkdir -p "$HW/results" "$RUN_ROOT"

end=$(( CATALOG_TOTAL * STAGE_PCT / 100 ))
if [[ -n "${ABSOLUTE_CAP:-}" ]] && (( end > ABSOLUTE_CAP )); then
  end=$ABSOLUTE_CAP
fi

start=0
if [[ -f "$STATE" ]] && [[ "${RESET:-}" != "1" ]]; then
  start="$(uv run python -c "import json; print(json.load(open('$STATE'))['next_start_index'])")"
fi

if (( start >= end )); then
  echo "Catalog already ingested through index ${end} (stage ${STAGE_PCT}%). Next: higher STAGE_PCT." >&2
  exit 0
fi

run_dir="$RUN_ROOT/pct_catalog_${STAGE_PCT}_end_${end}"
search_dir="$run_dir/search"
mkdir -p "$search_dir"

echo "==> Postgres"
(cd lab/vectorscale_db && docker compose up -d)

SECONDS=0
echo "Stage ${STAGE_PCT}% cumulative | slice [${start}:${end}) of ${CATALOG_TOTAL}"

RECREATE_FLAG=()
if (( start == 0 )) || [[ "${RESET:-}" == "1" ]]; then
  RECREATE_FLAG=(--recreate-table)
fi

uv run python homework/vectorize.py \
  "${RECREATE_FLAG[@]}" \
  --start-index "$start" \
  --end-index "$end" \
  --batch-size "$BATCH_SIZE" \
  --stage-pct-of-catalog "$STAGE_PCT" \
  --meta-out "$run_dir/vectorize_meta.json"

elapsed=$SECONDS
echo "Vectorize wall time: ${elapsed}s ($(date -u -d "@$elapsed" +%H:%M:%S 2>/dev/null || echo ${elapsed}s))"

OUTPUT_DIR="$search_dir" K="${K:-5}" "$HW/search_for_similarities.sh"

uv run python -c "
import json, time
from pathlib import Path
state = {
    'next_start_index': $end,
    'last_stage_pct': $STAGE_PCT,
    'catalog_total': $CATALOG_TOTAL,
    'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'vectorize_wall_seconds': $elapsed,
}
Path('$STATE').write_text(json.dumps(state, indent=2) + '\n')
print('State:', json.dumps(state, indent=2))
"

echo "Results: $run_dir"