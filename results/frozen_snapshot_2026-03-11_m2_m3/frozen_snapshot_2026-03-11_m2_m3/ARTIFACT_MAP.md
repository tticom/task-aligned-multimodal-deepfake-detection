# Artifact map: frozen_snapshot_2026-03-11_m2_m3

## Overview

- snapshot root: `/mnt/scratch/users/40432309/fakeav_xception/results_registry/frozen_snapshot_2026-03-11_m2_m3`
- total files: 61

This snapshot preserves the post-Milestone 2 and Milestone 3 artefacts without modifying the earlier frozen snapshot.

## Top-level registry files

- `COPY_MAP.tsv` (384 bytes)

## Milestone 2: target-aligned AV-sync

- `avsync_target_aligned/README.md` (11951 bytes)
- `avsync_target_aligned/taskdefs/avsync_features_mismatch.jsonl.gz` (3106835 bytes)
- `avsync_target_aligned/taskdefs/avsync_features_videoauth.jsonl.gz` (3096785 bytes)
- `avsync_target_aligned/taskdefs/derive_avsync_taskdefs_summary.json` (3042 bytes)
- `avsync_target_aligned/metrics/metrics_avsync_mismatch_thr05.json` (1861 bytes)
- `avsync_target_aligned/metrics/metrics_avsync_videoauth_thr05.json` (1739 bytes)
- `avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_f1.json` (1077 bytes)
- `avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_fpr01.json` (1253 bytes)
- `avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_f1.json` (1060 bytes)
- `avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_fpr01.json` (1203 bytes)
- `avsync_target_aligned/models/mismatch/avsync_lr_model.json` (4067 bytes)
- `avsync_target_aligned/models/videoauth/avsync_lr_model.json` (4065 bytes)
- `avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz` (737633 bytes)
- `avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz` (702333 bytes)

## Milestone 3: complementarity ablations

- `ablation_v1/README.md` (7930 bytes)
- `ablation_v1/MILESTONE3_SUMMARY.md` (8816 bytes)
- `ablation_v1/joined/README.md` (1055 bytes)
- `ablation_v1/joined/build_ablation_join_summary.json` (2408 bytes)
- `ablation_v1/joined/joined_mismatch.jsonl.gz` (877277 bytes)
- `ablation_v1/joined/joined_videoauth.jsonl.gz` (845599 bytes)
- `ablation_v1/metrics/metrics_ablation_mismatch_visual_only_thr05.json` (1664 bytes)
- `ablation_v1/metrics/metrics_ablation_mismatch_sync_only_thr05.json` (1813 bytes)
- `ablation_v1/metrics/metrics_ablation_mismatch_visual_sync_thr05.json` (1823 bytes)
- `ablation_v1/metrics/metrics_ablation_videoauth_visual_only_thr05.json` (1805 bytes)
- `ablation_v1/metrics/metrics_ablation_videoauth_sync_only_thr05.json` (1796 bytes)
- `ablation_v1/metrics/metrics_ablation_videoauth_visual_sync_thr05.json` (1804 bytes)

## Manifest and environment

- `manifests/avsync_manifest_v2_with_paths.jsonl` (18178353 bytes)

## Snapshot structure

```text
avsync_target_aligned/
  avsync_target_aligned/metrics/
    avsync_target_aligned/metrics/metrics_avsync_mismatch_thr05.json
    avsync_target_aligned/metrics/metrics_avsync_videoauth_thr05.json
    avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_f1.json
    avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_fpr01.json
    avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_f1.json
    avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_fpr01.json
  avsync_target_aligned/models/
    avsync_target_aligned/models/mismatch/
    avsync_target_aligned/models/videoauth/
  avsync_target_aligned/preds/
    avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz
    avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz
  avsync_target_aligned/subgroup/
    avsync_target_aligned/subgroup/avsync_mismatch_subgroup_metrics.csv
    avsync_target_aligned/subgroup/avsync_videoauth_subgroup_metrics.csv
  avsync_target_aligned/taskdefs/
    avsync_target_aligned/taskdefs/avsync_features_mismatch.jsonl.gz
    avsync_target_aligned/taskdefs/avsync_features_videoauth.jsonl.gz
    avsync_target_aligned/taskdefs/derive_avsync_taskdefs_summary.json
    avsync_target_aligned/taskdefs/README.md
  avsync_target_aligned/README.md
```

## Ablation structure

```text
ablation_v1/
  ablation_v1/joined/
    ablation_v1/joined/build_ablation_join_summary.json
    ablation_v1/joined/joined_mismatch.jsonl.gz
    ablation_v1/joined/joined_videoauth.jsonl.gz
    ablation_v1/joined/README.md
  ablation_v1/metrics/
    ablation_v1/metrics/metrics_ablation_mismatch_sync_only_thr05.json
    ablation_v1/metrics/metrics_ablation_mismatch_visual_only_thr05.json
    ablation_v1/metrics/metrics_ablation_mismatch_visual_sync_thr05.json
    ablation_v1/metrics/metrics_ablation_videoauth_sync_only_thr05.json
    ablation_v1/metrics/metrics_ablation_videoauth_visual_only_thr05.json
    ablation_v1/metrics/metrics_ablation_videoauth_visual_sync_thr05.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_sync_only_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_sync_only_fpr01.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_only_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_only_fpr01.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_sync_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_sync_fpr01.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_sync_only_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_sync_only_fpr01.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_only_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_only_fpr01.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_sync_f1.json
    ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_sync_fpr01.json
  ablation_v1/models/
    ablation_v1/models/mismatch/
    ablation_v1/models/videoauth/
  ablation_v1/preds/
    ablation_v1/preds/ablation_preds_mismatch_sync_only.jsonl.gz
    ablation_v1/preds/ablation_preds_mismatch_visual_only.jsonl.gz
    ablation_v1/preds/ablation_preds_mismatch_visual_sync.jsonl.gz
    ablation_v1/preds/ablation_preds_videoauth_sync_only.jsonl.gz
    ablation_v1/preds/ablation_preds_videoauth_visual_only.jsonl.gz
    ablation_v1/preds/ablation_preds_videoauth_visual_sync.jsonl.gz
  ablation_v1/subgroup/
    ablation_v1/subgroup/ablation_mismatch_sync_only_subgroup_metrics.csv
    ablation_v1/subgroup/ablation_mismatch_visual_only_subgroup_metrics.csv
    ablation_v1/subgroup/ablation_mismatch_visual_sync_subgroup_metrics.csv
    ablation_v1/subgroup/ablation_videoauth_sync_only_subgroup_metrics.csv
    ablation_v1/subgroup/ablation_videoauth_visual_only_subgroup_metrics.csv
    ablation_v1/subgroup/ablation_videoauth_visual_sync_subgroup_metrics.csv
  ablation_v1/MILESTONE3_SUMMARY.md
  ablation_v1/README.md
```

## Notes

- `avsync_target_aligned/` contains the Milestone 2 task-aligned retraining artefacts.
- `ablation_v1/` contains the Milestone 3 visual/sync complementarity ablations.
- Checksums and file inventory should be used as the source of truth for integrity verification.
