# AV-sync target-aligned retraining (Milestone 2)

## Overview

This folder contains the target-aligned retraining results for the AV-sync branch.

The purpose of this milestone was to stop relying on inherited authenticity labels and instead retrain the synchronisation baseline on explicit task definitions derived from provenance.

Two target tasks were used:

1. **mismatch proxy**
   - positive (`label=1`): exactly one modality manipulated
   - negative (`label=0`): both modalities matched

2. **video authenticity**
   - positive (`label=1`): `FakeVideo-*`
   - negative (`label=0`): `RealVideo-*`

This keeps the AV-sync branch aligned with the dissertation’s methodological claim: apparent multimodal performance depends materially on the target definition, and synchronisation-aware evidence should be trained and evaluated on task-aligned labels rather than inherited labels.

## Inputs

- feature file: `/mnt/scratch/users/40432309/fakeav_xception/data_avsync/features_avsync_v1/features_merged.jsonl.gz`
- manifest cross-check: `/mnt/scratch/users/40432309/fakeav_xception/manifests_v2/avsync_manifest_v2_with_paths.jsonl`

## Derived task-definition files

- `taskdefs/avsync_features_mismatch.jsonl.gz`
- `taskdefs/avsync_features_videoauth.jsonl.gz`
- `taskdefs/derive_avsync_taskdefs_summary.json`

### Label derivation rules

#### mismatch proxy
- `RealVideo-RealAudio -> 0`
- `FakeVideo-FakeAudio -> 0`
- `RealVideo-FakeAudio -> 1`
- `FakeVideo-RealAudio -> 1`

#### video authenticity
- `RealVideo-* -> 0`
- `FakeVideo-* -> 1`

### Task 2.1 derivation summary

- total rows: 20434
- split counts: {'test': 3171, 'train': 14106, 'val': 3157}
- manifest rows checked: 20434
- manifest mismatches: 0

#### provenance counts by split
```json
{
  "test": {
    "RealVideo-FakeAudio": 51,
    "FakeVideo-FakeAudio": 1641,
    "RealVideo-RealAudio": 51,
    "FakeVideo-RealAudio": 1428
  },
  "train": {
    "FakeVideo-FakeAudio": 7395,
    "RealVideo-FakeAudio": 148,
    "RealVideo-RealAudio": 147,
    "FakeVideo-RealAudio": 6416
  },
  "val": {
    "RealVideo-FakeAudio": 45,
    "FakeVideo-FakeAudio": 1619,
    "RealVideo-RealAudio": 45,
    "FakeVideo-RealAudio": 1448
  }
}
```

#### mismatch label counts by split
```json
{
  "test": {
    "1": 1479,
    "0": 1692
  },
  "train": {
    "0": 7542,
    "1": 6564
  },
  "val": {
    "1": 1493,
    "0": 1664
  }
}
```

#### video-authenticity label counts by split
```json
{
  "test": {
    "0": 102,
    "1": 3069
  },
  "train": {
    "1": 13811,
    "0": 295
  },
  "val": {
    "0": 90,
    "1": 3067
  }
}
```

## Model

A lightweight logistic-regression baseline was trained separately for each task using the derived AV-sync feature files.

### Common setup
- model family: logistic regression
- penalty: `l2`
- solver: `liblinear`
- fixed seed: `42`
- max iterations: `1000`

## Features used

### mismatch
- feature count: 15
- features: `dt_sec`, `features.audio_mean`, `features.audio_mean_nonspeech`, `features.audio_mean_speech`, `features.best_corr`, `features.best_lag_ms`, `features.corr_all`, `features.corr_nonspeech`, `features.corr_speech`, `features.mouth_mean`, `features.mouth_mean_nonspeech`, `features.mouth_mean_speech`, `has_speech`, `n_samples`, `speech_fraction`

Top coefficients by absolute value:
- `features.audio_mean_speech`: 4.1400 (positive-class increasing)
- `features.audio_mean`: -3.5175 (positive-class decreasing)
- `n_samples`: 0.7983 (positive-class increasing)
- `features.corr_nonspeech`: -0.6458 (positive-class decreasing)
- `features.mouth_mean`: 0.5878 (positive-class increasing)
- `speech_fraction`: -0.5299 (positive-class decreasing)
- `features.mouth_mean_speech`: -0.4427 (positive-class decreasing)
- `features.audio_mean_nonspeech`: 0.4162 (positive-class increasing)

### video authenticity
- feature count: 15
- features: `dt_sec`, `features.audio_mean`, `features.audio_mean_nonspeech`, `features.audio_mean_speech`, `features.best_corr`, `features.best_lag_ms`, `features.corr_all`, `features.corr_nonspeech`, `features.corr_speech`, `features.mouth_mean`, `features.mouth_mean_nonspeech`, `features.mouth_mean_speech`, `has_speech`, `n_samples`, `speech_fraction`

Top coefficients by absolute value:
- `speech_fraction`: 0.5616 (positive-class increasing)
- `features.audio_mean_nonspeech`: 0.5167 (positive-class increasing)
- `n_samples`: -0.3427 (positive-class decreasing)
- `features.corr_all`: -0.3172 (positive-class decreasing)
- `features.audio_mean_speech`: -0.3149 (positive-class decreasing)
- `features.corr_nonspeech`: 0.2981 (positive-class increasing)
- `features.corr_speech`: 0.2772 (positive-class increasing)
- `features.best_corr`: 0.2700 (positive-class increasing)

## Class balance

### mismatch
- train: negatives=7542, positives=6564, positive rate=46.53%
- val: negatives=1664, positives=1493, positive rate=47.29%
- test: negatives=1692, positives=1479, positive rate=46.64%

### video authenticity
- train: negatives=295, positives=13811, positive rate=97.91%
- val: negatives=90, positives=3067, positive rate=97.15%
- test: negatives=102, positives=3069, positive rate=96.78%

The video-authenticity task is highly imbalanced because the AV-sync feature subset contains very few `RealVideo-*` examples relative to `FakeVideo-*`. This makes threshold-dependent behaviour, particularly low-FPR operation, stricter and potentially less stable than ranking metrics alone.

## Results at threshold 0.5

### mismatch

| split | AUROC | inverted AUROC | accuracy @0.5 | precision @0.5 | recall @0.5 | F1 @0.5 | FPR @0.5 | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.8166 | 0.1834 | 0.7406 | 0.7608 | 0.6584 | 0.7059 | 0.1857 | 1355 | 309 | 510 | 983 |
| test | 0.8114 | 0.1886 | 0.7389 | 0.7533 | 0.6545 | 0.7004 | 0.1874 | 1375 | 317 | 511 | 968 |

Normal score direction is better than inverted if AUROC exceeds inverted AUROC. For this task: validation 0.8166 vs 0.1834; test 0.8114 vs 0.1886.

### video authenticity

| split | AUROC | inverted AUROC | accuracy @0.5 | precision @0.5 | recall @0.5 | F1 @0.5 | FPR @0.5 | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.7516 | 0.2484 | 0.9715 | 0.9715 | 1.0000 | 0.9855 | 1.0000 | 0 | 90 | 0 | 3067 |
| test | 0.7509 | 0.2491 | 0.9685 | 0.9684 | 1.0000 | 0.9840 | 0.9804 | 2 | 100 | 0 | 3069 |

Normal score direction is better than inverted if AUROC exceeds inverted AUROC. For this task: validation 0.7516 vs 0.2484; test 0.7509 vs 0.2491.

## Threshold sweeps

### mismatch: best validation F1 threshold

- selected threshold: 0.3566
- rule: max validation F1

| split | F1 | precision | recall | FPR | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.7367 | 0.6733 | 0.8131 | 0.3540 | 1075 | 589 | 279 | 1214 |
| test | 0.7271 | 0.6703 | 0.7945 | 0.3416 | 1114 | 578 | 304 | 1175 |

### mismatch: validation FPR <= 0.01 threshold

- selected threshold: 0.8864
- rule: max_recall subject to validation FPR <= 0.01 and recall > 0

| split | F1 | precision | recall | FPR | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.3390 | 0.9506 | 0.2063 | 0.0096 | 1648 | 16 | 1185 | 308 |
| test | 0.3585 | 0.9116 | 0.2231 | 0.0189 | 1660 | 32 | 1149 | 330 |

### video authenticity: best validation F1 threshold

- selected threshold: 0.7533
- rule: max validation F1

| split | F1 | precision | recall | FPR | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.9857 | 0.9724 | 0.9993 | 0.9667 | 3 | 87 | 2 | 3065 |
| test | 0.9836 | 0.9684 | 0.9993 | 0.9804 | 2 | 100 | 2 | 3067 |

### video authenticity: validation FPR <= 0.01 threshold

- selected threshold: 0.9958
- rule: max_recall subject to validation FPR <= 0.01 and recall > 0

| split | F1 | precision | recall | FPR | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.1679 | 1.0000 | 0.0916 | 0.0000 | 90 | 0 | 2786 | 281 |
| test | 0.1500 | 0.9960 | 0.0811 | 0.0098 | 101 | 1 | 2820 | 249 |

## Interpretation

### mismatch
The retrained mismatch model is the most important result in this milestone because it directly targets the synchronisation-style question. In these results, the normal AUROC is stronger than the inverted AUROC on both validation and test, which indicates that the retrained score direction is aligned with the intended positive class rather than requiring the earlier post hoc inversion diagnostic.

### video authenticity
The retrained video-authenticity model provides a cleaner comparison point against the corrected visual baseline because it uses an explicit `FakeVideo` versus `RealVideo` target. However, the task is heavily imbalanced in this AV-sync subset, so threshold-0.5 behaviour should be interpreted carefully. In particular, high recall with very high FPR may still coexist with moderate ranking performance.

## Outputs

### models
- `models/mismatch/avsync_lr_model.json`
- `models/videoauth/avsync_lr_model.json`

### predictions
- `preds/avsync_preds_mismatch.jsonl.gz`
- `preds/avsync_preds_videoauth.jsonl.gz`

### metrics
- `metrics/metrics_avsync_mismatch_thr05.json`
- `metrics/metrics_avsync_videoauth_thr05.json`
- `metrics/threshold_sweep_avsync_mismatch_f1.json`
- `metrics/threshold_sweep_avsync_mismatch_fpr01.json`
- `metrics/threshold_sweep_avsync_videoauth_f1.json`
- `metrics/threshold_sweep_avsync_videoauth_fpr01.json`

### subgroup summaries
- `subgroup/avsync_mismatch_subgroup_metrics.csv`
- `subgroup/avsync_videoauth_subgroup_metrics.csv`

## Reproduction

### Task 2.1: derive target-aligned labels
```bash
python scripts/avsync_models/taskdefs_v1.py \
  --infile data_avsync/features_avsync_v1/features_merged.jsonl.gz \
  --manifest manifests_v2/avsync_manifest_v2_with_paths.jsonl \
  --outdir results_preds_v2/avsync_target_aligned/taskdefs
```

### Task 2.2: train mismatch model
```bash
python scripts/avsync_models/train_avsync_lr_v1.py \
  --infile results_preds_v2/avsync_target_aligned/taskdefs/avsync_features_mismatch.jsonl.gz \
  --task mismatch \
  --outroot results_preds_v2/avsync_target_aligned \
  --seed 42
```

### Task 2.3: train video-authenticity model
```bash
python scripts/avsync_models/train_avsync_lr_v1.py \
  --infile results_preds_v2/avsync_target_aligned/taskdefs/avsync_features_videoauth.jsonl.gz \
  --task videoauth \
  --outroot results_preds_v2/avsync_target_aligned \
  --seed 42
```

## Caveats

- These results are based on the existing AV-sync feature extraction pipeline and a lightweight logistic-regression baseline. They do not establish deployment readiness.
- The mismatch task is a proxy target derived from modality provenance rather than a direct real-world fraud label.
- The video-authenticity task in this subset is strongly imbalanced, so operating-point results should be interpreted alongside AUROC rather than in isolation.
- The March 2026 frozen snapshot under `results_registry/frozen_snapshot_2026-03-10/` remains a Milestone 1 snapshot and was not modified by this milestone.

## Conclusion

Milestone 2 establishes that the AV-sync branch can now be interpreted using explicit task-aligned labels. The key output is the direct mismatch retraining result. This provides a cleaner foundation for the next stage: complementarity ablations comparing sync-only, visual-only, and visual+sync models on video-authenticity and mismatch targets.

Mismatch retraining worked and this is the key result

validation AUROC: 0.8166
test AUROC: 0.8114
inverted AUROC is much worse, so the retrained score direction is now aligned with the positive class.

Video-authenticity retraining has ranking signal

validation AUROC: 0.7516
test AUROC: 0.7509
But video-authenticity at threshold 0.5 is a poor operating point
because the AV-sync subset is extremely imbalanced toward FakeVideo-*
so threshold-dependent performance must be interpreted separately from AUROC.