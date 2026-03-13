# Task-aligned multimodal deepfake detection

This repository is a curated dissertation-facing subset of the working research repository for an MSc Cyber Security project on multimodal deepfake detection for fraud and extortion prevention.

## Scope

The repository focuses on the final reproducible experimental story rather than the full operational research environment.

Included:

- target-aligned AV-sync retraining artefacts
- Milestone 3 complementarity ablation artefacts
- final result tables
- manifest, scripts, Slurm wrappers, and frozen snapshot metadata

Excluded:

- raw datasets
- extracted audio, frame, and crop directories
- checkpoints
- operational logs
- legacy intermediate artefacts not needed for supervisor review

## Core contribution

The central methodological finding is that multimodal performance is task-dependent:

- synchronisation-aware evidence is most informative for the mismatch proxy task
- combined visual and synchronisation evidence provides the strongest ranking performance for video authenticity
- ranking performance and operating-point behaviour must be interpreted separately

## Repository structure

- docs/ — overview and interpretation documents
- configs/ — experiment configuration files
- manifests/ — final manifest used by derivation and joining
- scripts/ — reproducibility scripts
- slurm/ — cluster job wrappers
- results/ — final target-aligned, ablation, summary, and frozen snapshot artefacts
  
```text
.
├── README.md
├── docs/
│   ├── project_overview.md
│   ├── experiment_map.md
│   ├── key_findings.md
│   └── environment/
│       └── conda_env_export.yml
├── configs/
├── manifests/
│   └── avsync_manifest_v2_with_paths.jsonl
├── scripts/
│   ├── avsync_models/
│   └── archive/
├── slurm/
└── results/
    ├── avsync_target_aligned/
    ├── ablation_v1/
    ├── final_tables/
    └── frozen_snapshot_2026-03-11_m2_m3/

## Important result areas

- results/avsync_target_aligned/
- results/ablation_v1/
- results/final_tables/
- results/frozen_snapshot_2026-03-11_m2_m3/

## Notes

This curated repository is intended for academic review. It is not a raw-data archive and does not claim deployment readiness.