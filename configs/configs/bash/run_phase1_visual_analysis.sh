#!/usr/bin/env bash
set -euo pipefail

# Local runner for Phase 1 visual analysis (no Slurm).
#
# Example:
#   PREDS_PATH="data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz" \
#   MANIFEST_PATH="manifests_v2/avsync_manifest_v2_with_paths.jsonl" \
#   RUNNER="poetry run python" \
#   bash configs/bash/run_phase1_visual_analysis.sh

RUNNER="${RUNNER:-poetry run python}"
PREDS_PATH="${PREDS_PATH:?PREDS_PATH is required}"
MANIFEST_PATH="${MANIFEST_PATH:-}"
RESULTS_DIR="${RESULTS_DIR:-results_preds_v2}"
SECOND_PREDS_PATH="${SECOND_PREDS_PATH:-}"
METHOD_TOKENS="${METHOD_TOKENS:-}"
AUTO_METHOD_TOKENS="${AUTO_METHOD_TOKENS:-0}"
DECISION_THRESHOLDS="${DECISION_THRESHOLDS:-0.5}"
ECE_BINS="${ECE_BINS:-15}"

export RUNNER PREDS_PATH MANIFEST_PATH RESULTS_DIR SECOND_PREDS_PATH METHOD_TOKENS AUTO_METHOD_TOKENS DECISION_THRESHOLDS ECE_BINS

bash slurm/phase1_visual_analysis.slurm
