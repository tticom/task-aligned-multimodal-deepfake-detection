#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root))


def exists(root: Path, relpath: str) -> bool:
    return (root / relpath).exists()


def file_line(lines: list[str], root: Path, relpath: str) -> None:
    p = root / relpath
    if p.exists():
        size = p.stat().st_size
        lines.append(f"- `{relpath}` ({size} bytes)")
    else:
        lines.append(f"- `{relpath}` [missing]")


def add_section(lines: list[str], title: str, root: Path, relpaths: list[str]) -> None:
    present = [rp for rp in relpaths if exists(root, rp)]
    if not present:
        return
    lines.append(f"## {title}")
    lines.append("")
    for rp in relpaths:
        if exists(root, rp):
            file_line(lines, root, rp)
    lines.append("")


def add_tree(lines: list[str], title: str, root: Path, subdir: str, max_depth: int = 2) -> None:
    base = root / subdir
    if not base.exists():
        return

    lines.append(f"## {title}")
    lines.append("")
    lines.append("```text")

    def walk(p: Path, depth: int) -> None:
        if depth > max_depth:
            return
        children = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        for child in children:
            prefix = "  " * depth
            rel_child = child.relative_to(root)
            if child.is_dir():
                lines.append(f"{prefix}{rel_child}/")
                walk(child, depth + 1)
            else:
                lines.append(f"{prefix}{rel_child}")

    lines.append(f"{subdir}/")
    walk(base, 1)
    lines.append("```")
    lines.append("")


def count_files(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.is_file())


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate ARTIFACT_MAP.md for a frozen snapshot.")
    ap.add_argument(
        "--snapshot-root",
        required=True,
        help="Path to frozen snapshot root, e.g. results_registry/frozen_snapshot_2026-03-11_m2_m3",
    )
    args = ap.parse_args()

    root = Path(args.snapshot_root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Snapshot root does not exist: {root}")

    outpath = root / "ARTIFACT_MAP.md"

    lines: list[str] = []
    lines.append(f"# Artifact map: {root.name}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- snapshot root: `{root}`")
    lines.append(f"- total files: {count_files(root)}")
    lines.append("")
    lines.append("This snapshot preserves the post-Milestone 2 and Milestone 3 artefacts without modifying the earlier frozen snapshot.")
    lines.append("")

    add_section(
        lines,
        "Top-level registry files",
        root,
        [
            "README.md",
            "COPY_MAP.tsv",
            "SHA256SUMS.txt",
            "SHA256SUMS.csv",
            "file_inventory.csv",
        ],
    )

    add_section(
        lines,
        "Milestone 2: target-aligned AV-sync",
        root,
        [
            "avsync_target_aligned/README.md",
            "avsync_target_aligned/MILESTONE2_SUMMARY.md",
            "avsync_target_aligned/taskdefs/avsync_features_mismatch.jsonl.gz",
            "avsync_target_aligned/taskdefs/avsync_features_videoauth.jsonl.gz",
            "avsync_target_aligned/taskdefs/derive_avsync_taskdefs_summary.json",
            "avsync_target_aligned/metrics/metrics_avsync_mismatch_thr05.json",
            "avsync_target_aligned/metrics/metrics_avsync_videoauth_thr05.json",
            "avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_f1.json",
            "avsync_target_aligned/metrics/threshold_sweep_avsync_mismatch_fpr01.json",
            "avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_f1.json",
            "avsync_target_aligned/metrics/threshold_sweep_avsync_videoauth_fpr01.json",
            "avsync_target_aligned/models/mismatch/avsync_lr_model.json",
            "avsync_target_aligned/models/videoauth/avsync_lr_model.json",
            "avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz",
            "avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz",
        ],
    )

    add_section(
        lines,
        "Milestone 3: complementarity ablations",
        root,
        [
            "ablation_v1/README.md",
            "ablation_v1/MILESTONE3_SUMMARY.md",
            "ablation_v1/joined/README.md",
            "ablation_v1/joined/build_ablation_join_summary.json",
            "ablation_v1/joined/joined_mismatch.jsonl.gz",
            "ablation_v1/joined/joined_videoauth.jsonl.gz",
            "ablation_v1/metrics/metrics_ablation_mismatch_visual_only_thr05.json",
            "ablation_v1/metrics/metrics_ablation_mismatch_sync_only_thr05.json",
            "ablation_v1/metrics/metrics_ablation_mismatch_visual_sync_thr05.json",
            "ablation_v1/metrics/metrics_ablation_videoauth_visual_only_thr05.json",
            "ablation_v1/metrics/metrics_ablation_videoauth_sync_only_thr05.json",
            "ablation_v1/metrics/metrics_ablation_videoauth_visual_sync_thr05.json",
        ],
    )

    add_section(
        lines,
        "Manifest and environment",
        root,
        [
            "manifests/avsync_manifest_v2_with_paths.jsonl",
            "docs/environment/conda_env_export.yml",
        ],
    )

    add_section(
        lines,
        "Reproducibility scripts",
        root,
        [
            "scripts/avsync_models/taskdefs_v1.py",
            "scripts/avsync_models/train_avsync_lr_v1.py",
            "scripts/avsync_models/write_avsync_target_aligned_readme_v1.py",
            "scripts/avsync_models/build_ablation_join_v1.py",
            "scripts/avsync_models/train_ablation_lr_v1.py",
            "slurm/derive_avsync_taskdefs_v1.slurm",
            "slurm/build_ablation_join_v1.slurm",
            "slurm/train_ablation_lr_v1.slurm",
        ],
    )

    add_tree(lines, "Snapshot structure", root, "avsync_target_aligned", max_depth=2)
    add_tree(lines, "Ablation structure", root, "ablation_v1", max_depth=2)

    lines.append("## Notes")
    lines.append("")
    lines.append("- `avsync_target_aligned/` contains the Milestone 2 task-aligned retraining artefacts.")
    lines.append("- `ablation_v1/` contains the Milestone 3 visual/sync complementarity ablations.")
    lines.append("- Checksums and file inventory should be used as the source of truth for integrity verification.")
    lines.append("")

    outpath.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {outpath}")


if __name__ == "__main__":
    main()