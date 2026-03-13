#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_jsonl_gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}: {e}") from e


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}: {e}") from e


def write_jsonl_gz(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build joined visual/sync ablation tables for Milestone 3.")
    p.add_argument(
        "--visual-preds",
        default="data_visual/preds_xception_v2_crops_gpu_run_2/visual_xception_preds_v2.jsonl.gz",
        help="Corrected visual baseline prediction file",
    )
    p.add_argument(
        "--sync-preds-mismatch",
        default="results_preds_v2/avsync_target_aligned/preds/avsync_preds_mismatch.jsonl.gz",
        help="Task-aligned AV-sync mismatch predictions",
    )
    p.add_argument(
        "--sync-preds-videoauth",
        default="results_preds_v2/avsync_target_aligned/preds/avsync_preds_videoauth.jsonl.gz",
        help="Task-aligned AV-sync videoauth predictions",
    )
    p.add_argument(
        "--manifest",
        default="manifests_v2/avsync_manifest_v2_with_paths.jsonl",
        help="Manifest used for key resolution and provenance cross-checking",
    )
    p.add_argument(
        "--outdir",
        default="results_preds_v2/ablation_v1/joined",
        help="Output directory for joined ablation files",
    )
    return p


def normalise_path(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def get_first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return None


def infer_score_field(sample_row: dict[str, Any], preferred: list[str], prefix: str) -> str:
    for key in preferred:
        if key in sample_row:
            return key

    numeric_candidates: list[str] = []
    for key, value in sample_row.items():
        if not isinstance(value, (int, float)):
            continue
        lk = key.lower()
        if any(token in lk for token in ["score", "prob", "logit"]):
            numeric_candidates.append(key)

    if len(numeric_candidates) == 1:
        return numeric_candidates[0]

    raise ValueError(
        f"Could not infer {prefix} score field. Sample keys={sorted(sample_row.keys())}; "
        f"numeric score-like candidates={numeric_candidates}"
    )


def manifest_maps(manifest_path: Path):
    by_index: dict[int, dict[str, Any]] = {}
    by_video_path: dict[str, dict[str, Any]] = {}

    for idx, row in enumerate(read_jsonl(manifest_path)):
        by_index[idx] = row
        vp = normalise_path(row.get("video_path"))
        if vp:
            if vp in by_video_path:
                raise ValueError(f"Duplicate video_path in manifest: {vp}")
            by_video_path[vp] = row

    return by_index, by_video_path


def resolve_visual_row(
    row: dict[str, Any],
    manifest_by_index: dict[int, dict[str, Any]],
    manifest_by_video_path: dict[str, dict[str, Any]],
) -> tuple[int, str, str | None, str | None]:
    if "manifest_index" in row and row["manifest_index"] is not None:
        idx = int(row["manifest_index"])
        if idx not in manifest_by_index:
            raise KeyError(f"Visual row manifest_index {idx} not present in manifest")
        mrow = manifest_by_index[idx]
        return idx, str(mrow.get("video_path")), row.get("split") or mrow.get("split"), row.get("label")

    for key in ["video_path", "source_video_path", "input_path", "path"]:
        vp = normalise_path(row.get(key))
        if vp and vp in manifest_by_video_path:
            mrow = manifest_by_video_path[vp]
            idx = next(i for i, mr in manifest_by_index.items() if mr is mrow)
            return idx, vp, row.get("split") or mrow.get("split"), row.get("label")

    raise ValueError(
        "Could not resolve visual row to manifest. Expected manifest_index or exact video_path-like field. "
        f"Available keys={sorted(row.keys())}"
    )


def index_visual_preds(
    visual_path: Path,
    manifest_by_index: dict[int, dict[str, Any]],
    manifest_by_video_path: dict[str, dict[str, Any]],
) -> tuple[dict[int, dict[str, Any]], str]:
    rows = list(read_jsonl_gz(visual_path))
    if not rows:
        raise ValueError(f"Visual predictions file is empty: {visual_path}")

    visual_score_field = infer_score_field(
        rows[0],
        preferred=[
            "score_prob",
            "prob_fake",
            "y_prob",
            "y_score",
            "score",
            "prob",
            "logit",
        ],
        prefix="visual",
    )

    out: dict[int, dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        idx, resolved_video_path, resolved_split, resolved_label = resolve_visual_row(
            row, manifest_by_index, manifest_by_video_path
        )
        item = {
            "manifest_index": idx,
            "video_path": resolved_video_path,
            "split": resolved_split,
            "visual_score": float(row[visual_score_field]),
            "visual_score_field": visual_score_field,
            "visual_label_original": resolved_label,
        }
        if idx in out:
            duplicates += 1
        out[idx] = item

    if duplicates:
        raise ValueError(f"Visual prediction index contains duplicate manifest_index entries: {duplicates}")

    return out, visual_score_field


def index_sync_preds(sync_path: Path) -> tuple[dict[int, dict[str, Any]], str]:
    rows = list(read_jsonl_gz(sync_path))
    if not rows:
        raise ValueError(f"Sync predictions file is empty: {sync_path}")

    score_field = infer_score_field(
        rows[0],
        preferred=["score_prob", "prob", "score", "score_logit", "logit"],
        prefix="sync",
    )

    out: dict[int, dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        if "manifest_index" not in row:
            raise KeyError(f"Sync prediction row missing manifest_index. Keys={sorted(row.keys())}")
        idx = int(row["manifest_index"])
        item = dict(row)
        item["_resolved_score"] = float(row[score_field])
        if idx in out:
            duplicates += 1
        out[idx] = item

    if duplicates:
        raise ValueError(f"Sync prediction index contains duplicate manifest_index entries: {duplicates}")

    return out, score_field


def build_join_rows(
    task_name: str,
    visual_index: dict[int, dict[str, Any]],
    sync_index: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    visual_keys = set(visual_index)
    sync_keys = set(sync_index)
    common = sorted(visual_keys & sync_keys)

    dropped_visual_only = len(visual_keys - sync_keys)
    dropped_sync_only = len(sync_keys - visual_keys)

    rows: list[dict[str, Any]] = []
    split_counts = Counter()
    label_counts = Counter()
    provenance_counts = Counter()

    for idx in common:
        v = visual_index[idx]
        s = sync_index[idx]

        row = {
            "manifest_index": idx,
            "split": s.get("split") or v.get("split"),
            "source_key": s.get("source_key"),
            "video_path": s.get("video_path") or v.get("video_path"),
            "provenance_class": s.get("provenance_class"),
            "label": int(s["label"]),
            "task_name": task_name,
            "label_semantics": s.get("task_name") if False else s.get("task_name"),
            "is_video_fake": s.get("is_video_fake"),
            "is_audio_fake": s.get("is_audio_fake"),
            "visual_score": float(v["visual_score"]),
            "sync_score": float(s["_resolved_score"]),
            "sync_score_logit": s.get("score_logit"),
            "sync_label_original": s.get("label_original"),
            "visual_label_original": v.get("visual_label_original"),
        }

        # Preserve explicit semantics from sync predictions if present.
        if "label_semantics" in s:
            row["label_semantics"] = s["label_semantics"]

        split_counts[row["split"]] += 1
        label_counts[int(row["label"])] += 1
        provenance_counts[str(row.get("provenance_class"))] += 1
        rows.append(row)

    summary = {
        "rows_joined": len(rows),
        "rows_visual_total": len(visual_index),
        "rows_sync_total": len(sync_index),
        "rows_dropped_visual_only": dropped_visual_only,
        "rows_dropped_sync_only": dropped_sync_only,
        "split_counts": dict(split_counts),
        "label_counts": dict(label_counts),
        "provenance_counts": dict(provenance_counts),
    }
    return rows, summary


def main() -> None:
    args = build_parser().parse_args()

    visual_path = Path(args.visual_preds)
    sync_mismatch_path = Path(args.sync_preds_mismatch)
    sync_videoauth_path = Path(args.sync_preds_videoauth)
    manifest_path = Path(args.manifest)
    outdir = Path(args.outdir)

    for p in [visual_path, sync_mismatch_path, sync_videoauth_path, manifest_path]:
        if not p.exists():
            raise FileNotFoundError(f"Missing input: {p}")

    manifest_by_index, manifest_by_video_path = manifest_maps(manifest_path)
    visual_index, visual_score_field = index_visual_preds(visual_path, manifest_by_index, manifest_by_video_path)
    sync_mismatch_index, sync_mismatch_score_field = index_sync_preds(sync_mismatch_path)
    sync_videoauth_index, sync_videoauth_score_field = index_sync_preds(sync_videoauth_path)

    mismatch_rows, mismatch_summary = build_join_rows("mismatch", visual_index, sync_mismatch_index)
    videoauth_rows, videoauth_summary = build_join_rows("videoauth", visual_index, sync_videoauth_index)

    outdir.mkdir(parents=True, exist_ok=True)
    mismatch_out = outdir / "joined_mismatch.jsonl.gz"
    videoauth_out = outdir / "joined_videoauth.jsonl.gz"
    summary_out = outdir / "build_ablation_join_summary.json"
    readme_out = outdir / "README.md"

    write_jsonl_gz(mismatch_out, mismatch_rows)
    write_jsonl_gz(videoauth_out, videoauth_rows)

    summary = {
        "timestamp_utc": utc_now_compact(),
        "inputs": {
            "visual_preds": str(visual_path.resolve()),
            "sync_preds_mismatch": str(sync_mismatch_path.resolve()),
            "sync_preds_videoauth": str(sync_videoauth_path.resolve()),
            "manifest": str(manifest_path.resolve()),
        },
        "resolved_fields": {
            "visual_score_field": visual_score_field,
            "sync_mismatch_score_field": sync_mismatch_score_field,
            "sync_videoauth_score_field": sync_videoauth_score_field,
        },
        "outputs": {
            "joined_mismatch": str(mismatch_out.resolve()),
            "joined_videoauth": str(videoauth_out.resolve()),
            "summary_json": str(summary_out.resolve()),
            "readme": str(readme_out.resolve()),
        },
        "tasks": {
            "mismatch": mismatch_summary,
            "videoauth": videoauth_summary,
        },
    }

    with summary_out.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    readme_text = f"""# Ablation join inputs for Milestone 3

This folder contains joined row-level inputs for complementarity ablations.

## Inputs
- visual predictions: `{visual_path}`
- sync mismatch predictions: `{sync_mismatch_path}`
- sync videoauth predictions: `{sync_videoauth_path}`
- manifest: `{manifest_path}`

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
"""
    readme_out.write_text(readme_text, encoding="utf-8")

    print(f"Wrote: {mismatch_out}")
    print(f"Wrote: {videoauth_out}")
    print(f"Wrote: {summary_out}")
    print(f"Wrote: {readme_out}")
    print(f"Resolved visual score field: {visual_score_field}")
    print(f"Resolved sync mismatch score field: {sync_mismatch_score_field}")
    print(f"Resolved sync videoauth score field: {sync_videoauth_score_field}")
    print(f"Mismatch join summary: {mismatch_summary}")
    print(f"Videoauth join summary: {videoauth_summary}")


if __name__ == "__main__":
    main()
