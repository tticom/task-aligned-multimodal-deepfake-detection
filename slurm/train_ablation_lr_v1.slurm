#!/bin/bash
#SBATCH --job-name=ablation_lr
#SBATCH --output=logs/ablation_lr_%j.out
#SBATCH --error=logs/ablation_lr_%j.err
#SBATCH --time=00:20:00
#SBATCH --partition=short
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -euo pipefail

REPO_ROOT="/users/40432309/sharedscratch/fakeav_xception"
PYTHON_EXE="${PYTHON_EXE:-python}"
TASK="${TASK:?set TASK=mismatch or videoauth}"
MODE="${MODE:?set MODE=visual_only, sync_only, or visual_sync}"

cd "$REPO_ROOT"

case "$TASK" in
  mismatch)
    INFILE="results_preds_v2/ablation_v1/joined/joined_mismatch.jsonl.gz"
    ;;
  videoauth)
    INFILE="results_preds_v2/ablation_v1/joined/joined_videoauth.jsonl.gz"
    ;;
  *)
    echo "Unsupported TASK=$TASK" >&2
    exit 2
    ;;
esac

"$PYTHON_EXE" scripts/avsync_models/train_ablation_lr_v1.py \
  --infile "$INFILE" \
  --task "$TASK" \
  --mode "$MODE" \
  --outroot results_preds_v2/ablation_v1 \
  --seed 42
