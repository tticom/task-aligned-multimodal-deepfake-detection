# Ablation join inputs for Milestone 3

This folder contains joined row-level inputs for complementarity ablations.

## Inputs
- visual predictions: `data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz`
- sync mismatch predictions: `results_preds_v2/avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz`
- sync videoauth predictions: `results_preds_v2/avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz`
- manifest: `manifests_v2/avsync_manifest_v2_with_paths.jsonl`

## Outputs
- `joined_mismatch.jsonl.gz`
- `joined_videoauth.jsonl.gz`
- `build_ablation_join_summary.json`

## Join logic
Rows are aligned primarily by `manifest_index`. Visual rows are resolved to manifest entries via:
1. `manifest_index`, if present in the visual prediction row, otherwise
2. exact `video_path`-style match against the manifest.

The output rows contain:
- task label (`label`)
- provenance metadata
- `visual_score`
- `sync_score`

These files are intended for Milestone 3 ablations:
- visual-only
- sync-only
- visual+sync
