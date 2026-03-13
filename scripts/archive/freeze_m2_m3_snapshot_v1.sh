#!/usr/bin/env bash
set -euo pipefail

SNAPSHOT_NAME="${1:-frozen_snapshot_2026-03-11_m2_m3}"
SNAPSHOT_ROOT="results_registry/${SNAPSHOT_NAME}"

if [[ -e "${SNAPSHOT_ROOT}" ]]; then
  echo "Refusing to overwrite existing snapshot: ${SNAPSHOT_ROOT}" >&2
  echo "Choose a new snapshot name or remove the existing directory first." >&2
  exit 1
fi

need() {
  if [[ ! -e "$1" ]]; then
    echo "Missing required path: $1" >&2
    exit 1
  fi
}

copy_dir() {
  local src="$1"
  local dst="$2"
  need "$src"
  mkdir -p "$dst"
  rsync -a "$src"/ "$dst"/
  printf "DIR\t%s\t%s\n" "$src" "$dst" >> "${SNAPSHOT_ROOT}/COPY_MAP.tsv"
}

copy_file() {
  local src="$1"
  local dst="$2"
  need "$src"
  mkdir -p "$(dirname "$dst")"
  install -m 0644 "$src" "$dst"
  printf "FILE\t%s\t%s\n" "$src" "$dst" >> "${SNAPSHOT_ROOT}/COPY_MAP.tsv"
}

copy_file_optional() {
  local src="$1"
  local dst="$2"
  if [[ -e "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    install -m 0644 "$src" "$dst"
    printf "FILE\t%s\t%s\n" "$src" "$dst" >> "${SNAPSHOT_ROOT}/COPY_MAP.tsv"
  else
    printf "MISSING_OPTIONAL\t%s\t%s\n" "$src" "$dst" >> "${SNAPSHOT_ROOT}/COPY_MAP.tsv"
  fi
}

mkdir -p "${SNAPSHOT_ROOT}"
{
  printf "TYPE\tSOURCE\tDESTINATION\n"
} > "${SNAPSHOT_ROOT}/COPY_MAP.tsv"

# Core Milestone 2 outputs
copy_dir "results_preds_v2/avsync_target_aligned" \
         "${SNAPSHOT_ROOT}/avsync_target_aligned"

# Core Milestone 3 outputs
copy_dir "results_preds_v2/ablation_v1" \
         "${SNAPSHOT_ROOT}/ablation_v1"

# Manifest used by the derivation/join stages
copy_file "manifests_v2/avsync_manifest_v2_with_paths.jsonl" \
          "${SNAPSHOT_ROOT}/manifests/avsync_manifest_v2_with_paths.jsonl"

# Scripts used for Milestone 2
copy_file "scripts/avsync_models/derive_avsync_taskdefs_v1.py" \
          "${SNAPSHOT_ROOT}/scripts/avsync_models/derive_avsync_taskdefs_v1.py"
copy_file "scripts/avsync_models/train_avsync_lr_v1.py" \
          "${SNAPSHOT_ROOT}/scripts/avsync_models/train_avsync_lr_v1.py"
copy_file_optional "scripts/avsync_models/write_avsync_target_aligned_readme_v1.py" \
                   "${SNAPSHOT_ROOT}/scripts/avsync_models/write_avsync_target_aligned_readme_v1.py"

# Scripts used for Milestone 3
copy_file "scripts/avsync_models/build_ablation_join_v1.py" \
          "${SNAPSHOT_ROOT}/scripts/avsync_models/build_ablation_join_v1.py"
copy_file "scripts/avsync_models/train_ablation_lr_v1.py" \
          "${SNAPSHOT_ROOT}/scripts/avsync_models/train_ablation_lr_v1.py"

# Slurm wrappers
copy_file_optional "slurm/derive_avsync_taskdefs_v1.slurm" \
                   "${SNAPSHOT_ROOT}/slurm/derive_avsync_taskdefs_v1.slurm"
copy_file_optional "slurm/build_ablation_join_v1.slurm" \
                   "${SNAPSHOT_ROOT}/slurm/build_ablation_join_v1.slurm"
copy_file_optional "slurm/train_ablation_lr_v1.slurm" \
                   "${SNAPSHOT_ROOT}/slurm/train_ablation_lr_v1.slurm"

# Environment export if you want it inside the new snapshot docs
copy_file_optional "results_registry/frozen_snapshot_2026-03-10/docs/environment/conda_env_export.yml" \
                   "${SNAPSHOT_ROOT}/docs/environment/conda_env_export.yml"

# Minimal top-level README if one does not already exist
cat > "${SNAPSHOT_ROOT}/README.md" <<EOF
# ${SNAPSHOT_NAME}

This snapshot freezes the post-Milestone 2 and Milestone 3 artefacts.

## Included areas
- avsync_target_aligned/
- ablation_v1/
- manifests/
- scripts/
- slurm/
- docs/environment/

## Provenance
See:
- COPY_MAP.tsv

## Notes
- This snapshot intentionally leaves frozen_snapshot_2026-03-10 unchanged.
- Checksums and file inventory should be generated after the copy step.
EOF

echo "Created snapshot root: ${SNAPSHOT_ROOT}"
echo "Next step: generate SHA256SUMS.txt, SHA256SUMS.csv, and file_inventory.csv"