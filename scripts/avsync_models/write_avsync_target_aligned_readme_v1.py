#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt(x: Any, ndp: int = 4) -> str:
    if x is None or x == "":
        return "N/A"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        return f"{x:.{ndp}f}"
    return str(x)


def fmt_pct(num: int, den: int, ndp: int = 2) -> str:
    if den == 0:
        return "N/A"
    return f"{(100.0 * num / den):.{ndp}f}%"


def add_json_block(lines: list[str], obj: Any) -> None:
    lines.append("```json")
    lines.append(json.dumps(obj, indent=2))
    lines.append("```")


def label_count_line(model_json: dict[str, Any], split: str) -> str:
    counts = model_json.get("label_counts_by_split", {}).get(split, {})
    neg = int(counts.get("0", counts.get(0, 0)))
    pos = int(counts.get("1", counts.get(1, 0)))
    total = neg + pos
    return f"- {split}: negatives={neg}, positives={pos}, positive rate={fmt_pct(pos, total)}"


def top_coeff_lines(model_json: dict[str, Any], k: int = 8) -> list[str]:
    coeffs = model_json.get("coefficients", {})
    if not coeffs:
        return ["- coefficients unavailable"]

    ranked = sorted(coeffs.items(), key=lambda kv: abs(float(kv[1])), reverse=True)[:k]
    out = []
    for name, value in ranked:
        direction = "positive-class increasing" if float(value) > 0 else "positive-class decreasing"
        out.append(f"- `{name}`: {float(value):.4f} ({direction})")
    return out


def add_thr05_section(lines: list[str], title: str, metrics_thr05: dict[str, Any]) -> None:
    sd = metrics_thr05.get("score_direction", {})
    val_m = metrics_thr05.get("val_metrics", {})
    test_m = metrics_thr05.get("test_metrics", {})

    lines.append(f"### {title}")
    lines.append("")
    lines.append("| split | AUROC | inverted AUROC | accuracy @0.5 | precision @0.5 | recall @0.5 | F1 @0.5 | FPR @0.5 | TN | FP | FN | TP |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| val | {fmt(sd.get('validation_auroc'))} | {fmt(sd.get('validation_auroc_inverted'))} | "
        f"{fmt(val_m.get('accuracy'))} | {fmt(val_m.get('precision'))} | {fmt(val_m.get('recall'))} | "
        f"{fmt(val_m.get('f1'))} | {fmt(val_m.get('fpr'))} | {fmt(val_m.get('tn'), 0)} | "
        f"{fmt(val_m.get('fp'), 0)} | {fmt(val_m.get('fn'), 0)} | {fmt(val_m.get('tp'), 0)} |"
    )
    lines.append(
        f"| test | {fmt(sd.get('test_auroc'))} | {fmt(sd.get('test_auroc_inverted'))} | "
        f"{fmt(test_m.get('accuracy'))} | {fmt(test_m.get('precision'))} | {fmt(test_m.get('recall'))} | "
        f"{fmt(test_m.get('f1'))} | {fmt(test_m.get('fpr'))} | {fmt(test_m.get('tn'), 0)} | "
        f"{fmt(test_m.get('fp'), 0)} | {fmt(test_m.get('fn'), 0)} | {fmt(test_m.get('tp'), 0)} |"
    )
    lines.append("")
    lines.append(
        "Normal score direction is better than inverted if AUROC exceeds inverted AUROC. "
        f"For this task: validation {fmt(sd.get('validation_auroc'))} vs {fmt(sd.get('validation_auroc_inverted'))}; "
        f"test {fmt(sd.get('test_auroc'))} vs {fmt(sd.get('test_auroc_inverted'))}."
    )
    lines.append("")


def add_sweep_section(lines: list[str], title: str, payload: dict[str, Any]) -> None:
    lines.append(f"### {title}")
    lines.append("")

    if payload.get("infeasible") is True:
        lines.append("- selected threshold: infeasible")
        lines.append(f"- rule: {payload.get('selection_rule', 'N/A')}")
        lines.append(f"- reason: {payload.get('reason', 'N/A')}")
        lines.append(f"- validation negatives: {payload.get('validation_negatives', 'N/A')}")
        lines.append(f"- validation FPR resolution: {fmt(payload.get('validation_fpr_resolution'))}")
        lines.append("")
        return

    val_m = payload.get("val_metrics", {})
    test_m = payload.get("test_metrics", {})
    lines.append(f"- selected threshold: {fmt(payload.get('selected_threshold'))}")
    lines.append(f"- rule: {payload.get('selection_rule', 'N/A')}")
    lines.append("")
    lines.append("| split | F1 | precision | recall | FPR | TN | FP | FN | TP |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| val | {fmt(val_m.get('f1'))} | {fmt(val_m.get('precision'))} | {fmt(val_m.get('recall'))} | "
        f"{fmt(val_m.get('fpr'))} | {fmt(val_m.get('tn'), 0)} | {fmt(val_m.get('fp'), 0)} | "
        f"{fmt(val_m.get('fn'), 0)} | {fmt(val_m.get('tp'), 0)} |"
    )
    lines.append(
        f"| test | {fmt(test_m.get('f1'))} | {fmt(test_m.get('precision'))} | {fmt(test_m.get('recall'))} | "
        f"{fmt(test_m.get('fpr'))} | {fmt(test_m.get('tn'), 0)} | {fmt(test_m.get('fp'), 0)} | "
        f"{fmt(test_m.get('fn'), 0)} | {fmt(test_m.get('tp'), 0)} |"
    )
    lines.append("")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Write README.md for AV-sync target-aligned retraining results.")
    p.add_argument(
        "--root",
        default="results_preds_v2/avsync_target_aligned",
        help="Root results directory for Milestone 2 outputs",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    root = Path(args.root)

    taskdefs_dir = root / "taskdefs"
    metrics_dir = root / "metrics"
    models_dir = root / "models"

    derive_summary = load_json(taskdefs_dir / "derive_avsync_taskdefs_summary.json")

    mismatch_thr05 = load_json(metrics_dir / "metrics_avsync_mismatch_thr05.json")
    mismatch_f1 = load_json(metrics_dir / "threshold_sweep_avsync_mismatch_f1.json")
    mismatch_fpr = load_json(metrics_dir / "threshold_sweep_avsync_mismatch_fpr01.json")

    videoauth_thr05 = load_json(metrics_dir / "metrics_avsync_videoauth_thr05.json")
    videoauth_f1 = load_json(metrics_dir / "threshold_sweep_avsync_videoauth_f1.json")
    videoauth_fpr = load_json(metrics_dir / "threshold_sweep_avsync_videoauth_fpr01.json")

    mismatch_model = load_json(models_dir / "mismatch" / "avsync_lr_model.json")
    videoauth_model = load_json(models_dir / "videoauth" / "avsync_lr_model.json")

    mismatch_features = mismatch_model.get("feature_names", [])
    videoauth_features = videoauth_model.get("feature_names", [])

    lines: list[str] = []
    lines.append("# AV-sync target-aligned retraining (Milestone 2)")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("This folder contains the target-aligned retraining results for the AV-sync branch.")
    lines.append("")
    lines.append(
        "The purpose of this milestone was to stop relying on inherited authenticity labels and instead "
        "retrain the synchronisation baseline on explicit task definitions derived from provenance."
    )
    lines.append("")
    lines.append("Two target tasks were used:")
    lines.append("")
    lines.append("1. **mismatch proxy**")
    lines.append("   - positive (`label=1`): exactly one modality manipulated")
    lines.append("   - negative (`label=0`): both modalities matched")
    lines.append("")
    lines.append("2. **video authenticity**")
    lines.append("   - positive (`label=1`): `FakeVideo-*`")
    lines.append("   - negative (`label=0`): `RealVideo-*`")
    lines.append("")
    lines.append(
        "This keeps the AV-sync branch aligned with the dissertation’s methodological claim: "
        "apparent multimodal performance depends materially on the target definition, and "
        "synchronisation-aware evidence should be trained and evaluated on task-aligned labels "
        "rather than inherited labels."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- feature file: `{derive_summary['infile_features']}`")
    lines.append(f"- manifest cross-check: `{derive_summary['infile_manifest']}`")
    lines.append("")
    lines.append("## Derived task-definition files")
    lines.append("")
    lines.append("- `taskdefs/avsync_features_mismatch.jsonl.gz`")
    lines.append("- `taskdefs/avsync_features_videoauth.jsonl.gz`")
    lines.append("- `taskdefs/derive_avsync_taskdefs_summary.json`")
    lines.append("")
    lines.append("### Label derivation rules")
    lines.append("")
    lines.append("#### mismatch proxy")
    lines.append("- `RealVideo-RealAudio -> 0`")
    lines.append("- `FakeVideo-FakeAudio -> 0`")
    lines.append("- `RealVideo-FakeAudio -> 1`")
    lines.append("- `FakeVideo-RealAudio -> 1`")
    lines.append("")
    lines.append("#### video authenticity")
    lines.append("- `RealVideo-* -> 0`")
    lines.append("- `FakeVideo-* -> 1`")
    lines.append("")
    lines.append("### Task 2.1 derivation summary")
    lines.append("")
    lines.append(f"- total rows: {derive_summary['rows_total']}")
    lines.append(f"- split counts: {derive_summary['counts_by_split']}")
    lines.append(f"- manifest rows checked: {derive_summary['manifest_crosscheck']['rows_checked']}")
    lines.append(f"- manifest mismatches: {derive_summary['manifest_crosscheck']['mismatch_count']}")
    lines.append("")
    lines.append("#### provenance counts by split")
    add_json_block(lines, derive_summary["provenance_counts_by_split"])
    lines.append("")
    lines.append("#### mismatch label counts by split")
    add_json_block(lines, derive_summary["mismatch_label_counts_by_split"])
    lines.append("")
    lines.append("#### video-authenticity label counts by split")
    add_json_block(lines, derive_summary["videoauth_label_counts_by_split"])
    lines.append("")
    lines.append("## Model")
    lines.append("")
    lines.append(
        "A lightweight logistic-regression baseline was trained separately for each task using the "
        "derived AV-sync feature files."
    )
    lines.append("")
    lines.append("### Common setup")
    lines.append("- model family: logistic regression")
    lines.append("- penalty: `l2`")
    lines.append("- solver: `liblinear`")
    lines.append(f"- fixed seed: `{mismatch_model.get('seed', 'N/A')}`")
    lines.append(f"- max iterations: `{mismatch_model.get('hyperparameters', {}).get('max_iter', 'N/A')}`")
    lines.append("")
    lines.append("## Features used")
    lines.append("")
    lines.append("### mismatch")
    lines.append(f"- feature count: {mismatch_model.get('feature_count', 'N/A')}")
    lines.append(f"- features: {', '.join(f'`{x}`' for x in mismatch_features)}")
    lines.append("")
    lines.append("Top coefficients by absolute value:")
    lines.extend(top_coeff_lines(mismatch_model))
    lines.append("")
    lines.append("### video authenticity")
    lines.append(f"- feature count: {videoauth_model.get('feature_count', 'N/A')}")
    lines.append(f"- features: {', '.join(f'`{x}`' for x in videoauth_features)}")
    lines.append("")
    lines.append("Top coefficients by absolute value:")
    lines.extend(top_coeff_lines(videoauth_model))
    lines.append("")
    lines.append("## Class balance")
    lines.append("")
    lines.append("### mismatch")
    lines.append(label_count_line(mismatch_model, "train"))
    lines.append(label_count_line(mismatch_model, "val"))
    lines.append(label_count_line(mismatch_model, "test"))
    lines.append("")
    lines.append("### video authenticity")
    lines.append(label_count_line(videoauth_model, "train"))
    lines.append(label_count_line(videoauth_model, "val"))
    lines.append(label_count_line(videoauth_model, "test"))
    lines.append("")
    lines.append(
        "The video-authenticity task is highly imbalanced because the AV-sync feature subset contains "
        "very few `RealVideo-*` examples relative to `FakeVideo-*`. This makes threshold-dependent "
        "behaviour, particularly low-FPR operation, stricter and potentially less stable than ranking "
        "metrics alone."
    )
    lines.append("")
    lines.append("## Results at threshold 0.5")
    lines.append("")
    add_thr05_section(lines, "mismatch", mismatch_thr05)
    add_thr05_section(lines, "video authenticity", videoauth_thr05)
    lines.append("## Threshold sweeps")
    lines.append("")
    add_sweep_section(lines, "mismatch: best validation F1 threshold", mismatch_f1)
    add_sweep_section(lines, "mismatch: validation FPR <= 0.01 threshold", mismatch_fpr)
    add_sweep_section(lines, "video authenticity: best validation F1 threshold", videoauth_f1)
    add_sweep_section(lines, "video authenticity: validation FPR <= 0.01 threshold", videoauth_fpr)
    lines.append("## Interpretation")
    lines.append("")
    lines.append("### mismatch")
    lines.append(
        "The retrained mismatch model is the most important result in this milestone because it directly "
        "targets the synchronisation-style question. In these results, the normal AUROC is stronger than "
        "the inverted AUROC on both validation and test, which indicates that the retrained score direction "
        "is aligned with the intended positive class rather than requiring the earlier post hoc inversion diagnostic."
    )
    lines.append("")
    lines.append("### video authenticity")
    lines.append(
        "The retrained video-authenticity model provides a cleaner comparison point against the corrected "
        "visual baseline because it uses an explicit `FakeVideo` versus `RealVideo` target. However, the "
        "task is heavily imbalanced in this AV-sync subset, so threshold-0.5 behaviour should be interpreted "
        "carefully. In particular, high recall with very high FPR may still coexist with moderate ranking performance."
    )
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("### models")
    lines.append("- `models/mismatch/avsync_lr_model.json`")
    lines.append("- `models/videoauth/avsync_lr_model.json`")
    lines.append("")
    lines.append("### predictions")
    lines.append("- `preds/avsync_preds_mismatch.jsonl.gz`")
    lines.append("- `preds/avsync_preds_videoauth.jsonl.gz`")
    lines.append("")
    lines.append("### metrics")
    lines.append("- `metrics/metrics_avsync_mismatch_thr05.json`")
    lines.append("- `metrics/metrics_avsync_videoauth_thr05.json`")
    lines.append("- `metrics/threshold_sweep_avsync_mismatch_f1.json`")
    lines.append("- `metrics/threshold_sweep_avsync_mismatch_fpr01.json`")
    lines.append("- `metrics/threshold_sweep_avsync_videoauth_f1.json`")
    lines.append("- `metrics/threshold_sweep_avsync_videoauth_fpr01.json`")
    lines.append("")
    lines.append("### subgroup summaries")
    lines.append("- `subgroup/avsync_mismatch_subgroup_metrics.csv`")
    lines.append("- `subgroup/avsync_videoauth_subgroup_metrics.csv`")
    lines.append("")
    lines.append("## Reproduction")
    lines.append("")
    lines.append("### Task 2.1: derive target-aligned labels")
    lines.append("```bash")
    lines.append("python scripts/avsync_models/taskdefs_v1.py \\")
    lines.append("  --infile data_avsync/features_avsync_v1/features_merged.jsonl.gz \\")
    lines.append("  --manifest manifests_v2/avsync_manifest_v2_with_paths.jsonl \\")
    lines.append("  --outdir results_preds_v2/avsync_target_aligned/taskdefs")
    lines.append("```")
    lines.append("")
    lines.append("### Task 2.2: train mismatch model")
    lines.append("```bash")
    lines.append("python scripts/avsync_models/train_avsync_lr_v1.py \\")
    lines.append("  --infile results_preds_v2/avsync_target_aligned/taskdefs/avsync_features_mismatch.jsonl.gz \\")
    lines.append("  --task mismatch \\")
    lines.append("  --outroot results_preds_v2/avsync_target_aligned \\")
    lines.append("  --seed 42")
    lines.append("```")
    lines.append("")
    lines.append("### Task 2.3: train video-authenticity model")
    lines.append("```bash")
    lines.append("python scripts/avsync_models/train_avsync_lr_v1.py \\")
    lines.append("  --infile results_preds_v2/avsync_target_aligned/taskdefs/avsync_features_videoauth.jsonl.gz \\")
    lines.append("  --task videoauth \\")
    lines.append("  --outroot results_preds_v2/avsync_target_aligned \\")
    lines.append("  --seed 42")
    lines.append("```")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- These results are based on the existing AV-sync feature extraction pipeline and a lightweight logistic-regression baseline. They do not establish deployment readiness.")
    lines.append("- The mismatch task is a proxy target derived from modality provenance rather than a direct real-world fraud label.")
    lines.append("- The video-authenticity task in this subset is strongly imbalanced, so operating-point results should be interpreted alongside AUROC rather than in isolation.")
    lines.append("- The March 2026 frozen snapshot under `results_registry/frozen_snapshot_2026-03-10/` remains a Milestone 1 snapshot and was not modified by this milestone.")
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        "Milestone 2 establishes that the AV-sync branch can now be interpreted using explicit task-aligned "
        "labels. The key output is the direct mismatch retraining result. This provides a cleaner foundation "
        "for the next stage: complementarity ablations comparing sync-only, visual-only, and visual+sync "
        "models on video-authenticity and mismatch targets."
    )
    lines.append("")

    outpath = root / "README.md"
    outpath.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {outpath}")


if __name__ == "__main__":
    main()
