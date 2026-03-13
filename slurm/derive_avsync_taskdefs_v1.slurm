#!/bin/bash
#SBATCH --job-name=derive_avsync_taskdefs
#SBATCH --output=logs/derive_avsync_taskdefs_%j.out
#SBATCH --error=logs/derive_avsync_taskdefs_%j.err
#SBATCH --time=00:15:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -euo pipefail

REPO_ROOT="/users/40432309/sharedscratch/fakeav_xception"
PYTHON_EXE="${PYTHON_EXE:-python}"

cd "$REPO_ROOT"

"$PYTHON_EXE" scripts/avsync_models/derive_avsync_taskdefs_v1.py \
  --infile data_avsync/features_avsync_v1/features_merged.jsonl.gz \
  --manifest manifests_v2/avsync_manifest_v2_with_paths.jsonl \
  --outdir results_preds_v2/avsync_target_aligned/taskdefs