# Milestone 3: complementarity ablations for AV-sync and visual evidence

## Overview

This folder contains the Milestone 3 ablation experiments used to test whether synchronisation-aware evidence adds value beyond the corrected visual baseline, and whether that value depends on the target definition.

Two target tasks were evaluated:

1. **mismatch proxy**
   - positive (`label=1`): exactly one modality manipulated
   - negative (`label=0`): both modalities matched

2. **video authenticity**
   - positive (`label=1`): `FakeVideo-*`
   - negative (`label=0`): `RealVideo-*`

Three ablation modes were compared on each task:

- `visual_only`
- `sync_only`
- `visual_sync`

The main aim of this milestone was to test complementarity rather than to introduce a larger model. All models used lightweight logistic-regression baselines over joined score features.

---

## Inputs

### Visual input
- `data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz`

### AV-sync inputs
- `results_preds_v2/avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz`
- `results_preds_v2/avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz`

### Metadata input
- `manifests_v2/avsync_manifest_v2_with_paths.jsonl`

### Join outputs
- `joined/joined_mismatch.jsonl.gz`
- `joined/joined_videoauth.jsonl.gz`
- `joined/build_ablation_join_summary.json`

For join details, see:
- `joined/README.md`

---

## Join summary

The ablation tables were built by joining corrected visual predictions with the target-aligned AV-sync predictions on the shared evaluation subset.

### mismatch join
- rows joined: 20434
- splits: train, val, test
- labels:
  - `0` = both modalities matched
  - `1` = exactly one modality manipulated

### video-authenticity join
- rows joined: 20434
- splits: train, val, test
- labels:
  - `0` = `RealVideo-*`
  - `1` = `FakeVideo-*`

The join summary JSON is:
- `joined/build_ablation_join_summary.json`

---

## Models compared

For each task, the following models were trained and evaluated:

### mismatch
- `visual_only`
- `sync_only`
- `visual_sync`

### video authenticity
- `visual_only`
- `sync_only`
- `visual_sync`

The feature sets were:

- `visual_only`: corrected visual score only
- `sync_only`: target-aligned AV-sync score only
- `visual_sync`: both corrected visual and AV-sync scores

All models used logistic regression with a fixed seed for reproducibility.

---

## Outputs

### Models
- `models/mismatch/ablation_lr_visual_only.json`
- `models/mismatch/ablation_lr_sync_only.json`
- `models/mismatch/ablation_lr_visual_sync.json`
- `models/videoauth/ablation_lr_visual_only.json`
- `models/videoauth/ablation_lr_sync_only.json`
- `models/videoauth/ablation_lr_visual_sync.json`

### Predictions
- `preds/ablation_preds_mismatch_visual_only.jsonl.gz`
- `preds/ablation_preds_mismatch_sync_only.jsonl.gz`
- `preds/ablation_preds_mismatch_visual_sync.jsonl.gz`
- `preds/ablation_preds_videoauth_visual_only.jsonl.gz`
- `preds/ablation_preds_videoauth_sync_only.jsonl.gz`
- `preds/ablation_preds_videoauth_visual_sync.jsonl.gz`

### Threshold 0.5 metrics
- `metrics/metrics_ablation_mismatch_visual_only_thr05.json`
- `metrics/metrics_ablation_mismatch_sync_only_thr05.json`
- `metrics/metrics_ablation_mismatch_visual_sync_thr05.json`
- `metrics/metrics_ablation_videoauth_visual_only_thr05.json`
- `metrics/metrics_ablation_videoauth_sync_only_thr05.json`
- `metrics/metrics_ablation_videoauth_visual_sync_thr05.json`

### Threshold sweeps
- `metrics/threshold_sweep_ablation_mismatch_visual_only_f1.json`
- `metrics/threshold_sweep_ablation_mismatch_visual_only_fpr01.json`
- `metrics/threshold_sweep_ablation_mismatch_sync_only_f1.json`
- `metrics/threshold_sweep_ablation_mismatch_sync_only_fpr01.json`
- `metrics/threshold_sweep_ablation_mismatch_visual_sync_f1.json`
- `metrics/threshold_sweep_ablation_mismatch_visual_sync_fpr01.json`
- `metrics/threshold_sweep_ablation_videoauth_visual_only_f1.json`
- `metrics/threshold_sweep_ablation_videoauth_visual_only_fpr01.json`
- `metrics/threshold_sweep_ablation_videoauth_sync_only_f1.json`
- `metrics/threshold_sweep_ablation_videoauth_sync_only_fpr01.json`
- `metrics/threshold_sweep_ablation_videoauth_visual_sync_f1.json`
- `metrics/threshold_sweep_ablation_videoauth_visual_sync_fpr01.json`

### Subgroup summaries
- `subgroup/ablation_mismatch_visual_only_subgroup_metrics.csv`
- `subgroup/ablation_mismatch_sync_only_subgroup_metrics.csv`
- `subgroup/ablation_mismatch_visual_sync_subgroup_metrics.csv`
- `subgroup/ablation_videoauth_visual_only_subgroup_metrics.csv`
- `subgroup/ablation_videoauth_sync_only_subgroup_metrics.csv`
- `subgroup/ablation_videoauth_visual_sync_subgroup_metrics.csv`

---

## Headline results

## 1. Mismatch proxy

### Threshold 0.5 test AUROC
- `visual_only`: **0.1349**
- `sync_only`: **0.8114**
- `visual_sync`: **0.8154**

### Threshold 0.5 test F1
- `visual_only`: **0.0000**
- `sync_only`: **0.7031**
- `visual_sync`: **0.7052**

### Interpretation
The synchronisation-aware score carried the useful signal for the mismatch task. The corrected visual score was not useful for mismatch and appeared directionally misaligned with the target. Adding the visual score to the AV-sync score produced only a marginal improvement over `sync_only`.

This suggests that, for the mismatch proxy task, performance is driven primarily by synchronisation-aware evidence rather than by visual authenticity evidence.

---

## 2. Video authenticity

### Threshold 0.5 test AUROC
- `visual_only`: **0.6721**
- `sync_only`: **0.7509**
- `visual_sync`: **0.8969**

### Threshold 0.5 test F1
- `visual_only`: **0.9909**
- `sync_only`: **0.9838**
- `visual_sync`: **0.9911**

### Threshold 0.5 test FPR
- `visual_only`: **0.4902**
- `sync_only`: **0.9804**
- `visual_sync`: **0.4706**

### Interpretation
For video authenticity, the combined `visual_sync` model produced a substantial ranking improvement over either unimodal model. The corrected visual score alone reproduced the previously observed corrected visual baseline, while the synchronisation-only score also showed ranking signal on the aligned subset. However, threshold-dependent behaviour remained problematic because the joined video-authenticity subset was highly imbalanced. Ranking performance and operating-point behaviour therefore need to be interpreted separately.

---

## Overall interpretation

The Milestone 3 results support the dissertation’s central methodological claim that multimodal value is task-dependent rather than task-invariant.

- On **mismatch**, synchronisation-aware evidence is the primary informative signal.
- On **video authenticity**, combining visual and synchronisation evidence materially improves ranking performance.
- Therefore, the apparent benefit of multimodal fusion depends on the task definition and cannot be interpreted reliably from inherited labels alone.

---

## Threshold-sweep notes

Threshold sweeps were run for:

- best validation F1 threshold
- validation FPR `<= 0.01`

These outputs are stored under `metrics/`.

One notable result is that some low-FPR regimes were infeasible, particularly where the model or task definition did not support sufficiently selective operation at the required false-positive constraint. These cases should be reported explicitly rather than hidden, because they are part of the operating-point story.

---

## Reproduction

### Build joined ablation tables
```bash
python scripts/avsync_models/build_ablation_join_v1.py \
  --visual-preds data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz \
  --sync-preds-mismatch results_preds_v2/avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz \
  --sync-preds-videoauth results_preds_v2/avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz \
  --manifest manifests_v2/avsync_manifest_v2_with_paths.jsonl \
  --outdir results_preds_v2/ablation_v1/joined