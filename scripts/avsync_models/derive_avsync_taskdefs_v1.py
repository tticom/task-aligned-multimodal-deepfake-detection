#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProvenanceInfo:
    provenance_class: str
    is_video_fake: int
    is_audio_fake: int
    mismatch_label: int
    videoauth_label: int


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


def write_jsonl_gz(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def derive_provenance(video_path: str) -> ProvenanceInfo:
    vp = video_path.lower()

    if "/fakevideo-" in vp:
        is_video_fake = 1
        video_prefix = "FakeVideo"
    elif "/realvideo-" in vp:
        is_video_fake = 0
        video_prefix = "RealVideo"
    else:
        raise ValueError(f"Could not derive video provenance from path: {video_path}")

    if "-fakeaudio/" in vp:
        is_audio_fake = 1
        audio_suffix = "FakeAudio"
    elif "-realaudio/" in vp:
        is_audio_fake = 0
        audio_suffix = "RealAudio"
    else:
        raise ValueError(f"Could not derive audio provenance from path: {video_path}")

    provenance_class = f"{video_prefix}-{audio_suffix}"
    mismatch_label = int(is_video_fake ^ is_audio_fake)
    videoauth_label = int(is_video_fake)

    return ProvenanceInfo(
        provenance_class=provenance_class,
        is_video_fake=is_video_fake,
        is_audio_fake=is_audio_fake,
        mismatch_label=mismatch_label,
        videoauth_label=videoauth_label,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Derive task-aligned AV-sync feature files for mismatch proxy and video authenticity."
    )
    p.add_argument(
        "--infile",
        default="data_avsync/features_avsync_v1/features_merged.jsonl.gz",
        help="Merged AV-sync features JSONL.GZ",
    )
    p.add_argument(
        "--manifest",
        default="manifests_v2/avsync_manifest_v2_with_paths.jsonl",
        help="Optional manifest for path cross-checking",
    )
    p.add_argument(
        "--outdir",
        default="results_preds_v2/avsync_target_aligned/taskdefs",
        help="Output directory",
    )
    p.add_argument(
        "--strict-manifest-check",
        action="store_true",
        help="Fail if any manifest/video_path cross-check mismatch is found",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    infile = Path(args.infile)
    manifest = Path(args.manifest)
    outdir = Path(args.outdir)

    if not infile.exists():
        raise FileNotFoundError(f"Missing infile: {infile}")

    manifest_rows: list[dict[str, Any]] | None = None
    if manifest.exists():
        manifest_rows = list(read_jsonl(manifest))
    else:
        manifest_rows = None

    mismatch_rows: list[dict[str, Any]] = []
    videoauth_rows: list[dict[str, Any]] = []

    counts_by_split = Counter()
    provenance_counts_by_split: dict[str, Counter] = defaultdict(Counter)
    mismatch_counts_by_split: dict[str, Counter] = defaultdict(Counter)
    videoauth_counts_by_split: dict[str, Counter] = defaultdict(Counter)

    manifest_checked = 0
    manifest_mismatches: list[dict[str, Any]] = []

    rows_total = 0

    for row in read_jsonl_gz(infile):
        rows_total += 1

        if "video_path" not in row:
            raise KeyError(f"Row {rows_total} is missing required key 'video_path'")
        if "split" not in row:
            raise KeyError(f"Row {rows_total} is missing required key 'split'")

        video_path = row["video_path"]
        split = row["split"]
        prov = derive_provenance(video_path)

        counts_by_split[split] += 1
        provenance_counts_by_split[split][prov.provenance_class] += 1
        mismatch_counts_by_split[split][str(prov.mismatch_label)] += 1
        videoauth_counts_by_split[split][str(prov.videoauth_label)] += 1

        # Optional manifest cross-check via manifest_index if available
        if manifest_rows is not None and "manifest_index" in row:
            idx = row["manifest_index"]
            if isinstance(idx, int) and 0 <= idx < len(manifest_rows):
                manifest_checked += 1
                manifest_video_path = manifest_rows[idx].get("video_path")
                if manifest_video_path != video_path:
                    mismatch = {
                        "manifest_index": idx,
                        "features_video_path": video_path,
                        "manifest_video_path": manifest_video_path,
                    }
                    manifest_mismatches.append(mismatch)

        base = dict(row)
        base["label_original"] = row.get("label")
        base["provenance_class"] = prov.provenance_class
        base["is_video_fake"] = prov.is_video_fake
        base["is_audio_fake"] = prov.is_audio_fake

        mismatch_row = dict(base)
        mismatch_row["label"] = prov.mismatch_label
        mismatch_row["task_name"] = "mismatch_proxy"
        mismatch_row["label_semantics"] = "1=exactly_one_modality_manipulated;0=both_modalities_matched"
        mismatch_rows.append(mismatch_row)

        videoauth_row = dict(base)
        videoauth_row["label"] = prov.videoauth_label
        videoauth_row["task_name"] = "video_authenticity"
        videoauth_row["label_semantics"] = "1=FakeVideo;0=RealVideo"
        videoauth_rows.append(videoauth_row)

    if args.strict_manifest_check and manifest_mismatches:
        raise ValueError(
            f"Manifest cross-check found {len(manifest_mismatches)} mismatches; "
            "rerun without --strict-manifest-check to inspect summary JSON."
        )

    outdir.mkdir(parents=True, exist_ok=True)

    mismatch_path = outdir / "avsync_features_mismatch.jsonl.gz"
    videoauth_path = outdir / "avsync_features_videoauth.jsonl.gz"
    summary_path = outdir / "derive_avsync_taskdefs_summary.json"
    readme_path = outdir / "README.md"

    write_jsonl_gz(mismatch_path, mismatch_rows)
    write_jsonl_gz(videoauth_path, videoauth_rows)

    summary = {
        "timestamp_utc": utc_now_compact(),
        "infile_features": str(infile.resolve()),
        "infile_manifest": str(manifest.resolve()) if manifest.exists() else None,
        "outputs": {
            "mismatch_features": str(mismatch_path.resolve()),
            "videoauth_features": str(videoauth_path.resolve()),
            "summary_json": str(summary_path.resolve()),
            "readme": str(readme_path.resolve()),
        },
        "rows_total": rows_total,
        "counts_by_split": dict(counts_by_split),
        "provenance_counts_by_split": {
            split: dict(counter) for split, counter in provenance_counts_by_split.items()
        },
        "mismatch_label_counts_by_split": {
            split: dict(counter) for split, counter in mismatch_counts_by_split.items()
        },
        "videoauth_label_counts_by_split": {
            split: dict(counter) for split, counter in videoauth_counts_by_split.items()
        },
        "rules": {
            "mismatch_proxy": {
                "1": "exactly one modality manipulated",
                "0": "both modalities matched",
                "mapping": {
                    "RealVideo-RealAudio": 0,
                    "FakeVideo-FakeAudio": 0,
                    "RealVideo-FakeAudio": 1,
                    "FakeVideo-RealAudio": 1,
                },
            },
            "video_authenticity": {
                "1": "FakeVideo",
                "0": "RealVideo",
                "mapping": {
                    "FakeVideo-FakeAudio": 1,
                    "FakeVideo-RealAudio": 1,
                    "RealVideo-FakeAudio": 0,
                    "RealVideo-RealAudio": 0,
                },
            },
        },
        "manifest_crosscheck": {
            "manifest_provided": manifest.exists(),
            "rows_checked": manifest_checked,
            "mismatch_count": len(manifest_mismatches),
            "example_mismatches": manifest_mismatches[:10],
        },
        "sanity_examples": {
            "expected_interpretation": {
                "RealVideo-FakeAudio": {
                    "mismatch_label": 1,
                    "videoauth_label": 0
                },
                "FakeVideo-RealAudio": {
                    "mismatch_label": 1,
                    "videoauth_label": 1
                },
                "RealVideo-RealAudio": {
                    "mismatch_label": 0,
                    "videoauth_label": 0
                },
                "FakeVideo-FakeAudio": {
                    "mismatch_label": 0,
                    "videoauth_label": 1
                },
            }
        },
    }

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    readme_text = f"""# AV-sync target-aligned task-definition files

This folder contains task-aligned AV-sync feature files derived from:

- `{infile}`

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
"""
    readme_path.write_text(readme_text, encoding="utf-8")

    print(f"Wrote: {mismatch_path}")
    print(f"Wrote: {videoauth_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {readme_path}")
    print(f"Rows total: {rows_total}")
    print(f"Split counts: {dict(counts_by_split)}")
    print(f"Mismatch counts by split: { {k: dict(v) for k, v in mismatch_counts_by_split.items()} }")
    print(f"Video-auth counts by split: { {k: dict(v) for k, v in videoauth_counts_by_split.items()} }")
    if manifest.exists():
        print(f"Manifest rows checked: {manifest_checked}")
        print(f"Manifest mismatches: {len(manifest_mismatches)}")


if __name__ == "__main__":
    main()