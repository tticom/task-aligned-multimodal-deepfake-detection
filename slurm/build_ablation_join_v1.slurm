#!/bin/bash
#SBATCH --job-name=ablation_join
#SBATCH --output=logs/ablation_join_%j.out
#SBATCH --error=logs/ablation_join_%j.err
#SBATCH --time=00:15:00
#SBATCH --partition=short
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -euo pipefail

REPO_ROOT="/users/40432309/sharedscratch/fakeav_xception"
PYTHON_EXE="${PYTHON_EXE:-python}"

cd "$REPO_ROOT"

"$PYTHON_EXE" scripts/avsync_models/build_ablation_join_v1.py \
  --visual-preds data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz \
  --sync-preds-mismatch results_preds_v2/avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz \
  --sync-preds-videoauth results_preds_v2/avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz \
  --manifest manifests_v2/avsync_manifest_v2_with_paths.jsonl \
  --outdir results_preds_v2/ablation_v1/joined
