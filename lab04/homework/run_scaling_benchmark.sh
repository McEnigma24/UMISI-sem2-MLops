#!/usr/bin/env bash
# Etapy 5→100%% katalogu: pierwszy z recreate, reszta inkrementalnie (state.json).
set -euo pipefail

HW="$(cd "$(dirname "$0")" && pwd)"
export RUN_ROOT="${RUN_ROOT:-$HW/results/incremental_scaling}"

STAGES=(5 10 15 20 40 60 80 100)

RESET=1 "$HW/run_catalog_stage.sh" "${STAGES[0]}"
for pct in "${STAGES[@]:1}"; do
  RESET=0 "$HW/run_catalog_stage.sh" "$pct"
done