# AV-sync target-aligned task-definition files

This folder contains task-aligned AV-sync feature files derived from:

- `data_avsync/features_avsync_v1/features_merged.jsonl.gz`

## Outputs
- `avsync_features_mismatch.jsonl.gz`
- `avsync_features_videoauth.jsonl.gz`
- `derive_avsync_taskdefs_summary.json`

## Task definitions

### mismatch_proxy
- `label = 1` -> exactly one modality manipulated
- `label = 0` -> both modalities matched

### video_authenticity
- `label = 1` -> FakeVideo
- `label = 0` -> RealVideo

## Preserved and added fields
Each output row preserves the original AV-sync feature fields and adds:
- `label_original`
- `provenance_class`
- `is_video_fake`
- `is_audio_fake`
- `task_name`
- `label_semantics`

## Notes
The top-level `label` field is intentionally overwritten so the derived files can be used directly by downstream evaluation scripts that expect a default label key.
