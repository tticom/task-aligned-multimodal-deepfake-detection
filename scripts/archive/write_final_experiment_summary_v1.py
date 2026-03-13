#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def val(d: dict[str, Any] | None, key: str):
    if not isinstance(d, dict):
        return None
    return d.get(key)


def add_thr05_row(rows, experiment_group, task, mode, path):
    d = load_json(Path(path))
    vm = d.get("val_metrics", {})
    tm = d.get("test_metrics", {})
    rows.append({
        "experiment_group": experiment_group,
        "task": task,
        "mode": mode,
        "metric_source": Path(path).name,
        "val_auroc": val(vm, "auroc"),
        "test_auroc": val(tm, "auroc"),
        "val_f1_thr05": val(vm, "f1"),
        "test_f1_thr05": val(tm, "f1"),
        "val_precision_thr05": val(vm, "precision"),
        "test_precision_thr05": val(tm, "precision"),
        "val_recall_thr05": val(vm, "recall"),
        "test_recall_thr05": val(tm, "recall"),
        "val_fpr_thr05": val(vm, "fpr"),
        "test_fpr_thr05": val(tm, "fpr"),
        "threshold_thr05": d.get("threshold", d.get("selected_threshold")),
        "f1_selected_threshold": None,
        "fpr01_selected_threshold": None,
        "fpr01_infeasible": None,
    })


def apply_f1_threshold(rows, experiment_group, task, mode, path):
    d = load_json(Path(path))
    for row in rows:
        if row["experiment_group"] == experiment_group and row["task"] == task and row["mode"] == mode:
            row["f1_selected_threshold"] = d.get("selected_threshold")
            return


def apply_fpr01_threshold(rows, experiment_group, task, mode, path):
    d = load_json(Path(path))
    for row in rows:
        if row["experiment_group"] == experiment_group and row["task"] == task and row["mode"] == mode:
            row["fpr01_selected_threshold"] = d.get("selected_threshold")
            row["fpr01_infeasible"] = d.get("infeasible", False)
            return


def main():
    outdir = Path("results_preds_v2/final_tables")
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []

    # Milestone 2
    add_thr05_row(
        rows, "milestone2_avsync", "mismatch", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/metrics_avsync_mismatch_thr05.json"
    )
    apply_f1_threshold(
        rows, "milestone2_avsync", "mismatch", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_f1.json"
    )
    apply_fpr01_threshold(
        rows, "milestone2_avsync", "mismatch", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_fpr01.json"
    )

    add_thr05_row(
        rows, "milestone2_avsync", "videoauth", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/metrics_avsync_videoauth_thr05.json"
    )
    apply_f1_threshold(
        rows, "milestone2_avsync", "videoauth", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_f1.json"
    )
    apply_fpr01_threshold(
        rows, "milestone2_avsync", "videoauth", "sync_only",
        "results_preds_v2/avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_fpr01.json"
    )

    # Milestone 3 mismatch
    for mode in ["visual_only", "sync_only", "visual_sync"]:
        add_thr05_row(
            rows, "milestone3_ablation", "mismatch", mode,
            f"results_preds_v2/ablation_v1/metrics/metrics_ablation_mismatch_{mode}_thr05.json"
        )
        apply_f1_threshold(
            rows, "milestone3_ablation", "mismatch", mode,
            f"results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_{mode}_f1.json"
        )
        apply_fpr01_threshold(
            rows, "milestone3_ablation", "mismatch", mode,
            f"results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_{mode}_fpr01.json"
        )

    # Milestone 3 videoauth
    for mode in ["visual_only", "sync_only", "visual_sync"]:
        add_thr05_row(
            rows, "milestone3_ablation", "videoauth", mode,
            f"results_preds_v2/ablation_v1/metrics/metrics_ablation_videoauth_{mode}_thr05.json"
        )
        apply_f1_threshold(
            rows, "milestone3_ablation", "videoauth", mode,
            f"results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_{mode}_f1.json"
        )
        apply_fpr01_threshold(
            rows, "milestone3_ablation", "videoauth", mode,
            f"results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_{mode}_fpr01.json"
        )

    csv_path = outdir / "final_experiment_summary.csv"
    fieldnames = [
        "experiment_group", "task", "mode", "metric_source",
        "val_auroc", "test_auroc",
        "val_f1_thr05", "test_f1_thr05",
        "val_precision_thr05", "test_precision_thr05",
        "val_recall_thr05", "test_recall_thr05",
        "val_fpr_thr05", "test_fpr_thr05",
        "threshold_thr05",
        "f1_selected_threshold",
        "fpr01_selected_threshold",
        "fpr01_infeasible",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    md_path = outdir / "final_experiment_summary.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Final experiment summary\n\n")
        f.write("| group | task | mode | test AUROC | test F1@0.5 | test FPR@0.5 | FPR<=0.01 infeasible |\n")
        f.write("|---|---|---|---:|---:|---:|---|\n")
        for r in rows:
            f.write(
                f"| {r['experiment_group']} | {r['task']} | {r['mode']} | "
                f"{r['test_auroc']} | {r['test_f1_thr05']} | {r['test_fpr_thr05']} | {r['fpr01_infeasible']} |\n"
            )

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()