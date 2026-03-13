#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


EXCLUDE_KEYS = {
    "label",
    "label_original",
    "task_name",
    "label_semantics",
    "split",
    "source_key",
    "video_path",
    "wav_path",
    "align_path",
    "manifest_index",
    "provenance_class",
    "is_video_fake",
    "is_audio_fake",
}
EXCLUDE_PREFIXES = ("timing.",)


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


def write_jsonl_gz(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Train and evaluate lightweight AV-sync logistic regression on a task-aligned label file."
    )
    p.add_argument("--infile", required=True, help="Derived AV-sync feature JSONL.GZ")
    p.add_argument("--task", required=True, choices=["mismatch", "videoauth"])
    p.add_argument("--outroot", default="results_preds_v2/avsync_target_aligned")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--c", type=float, default=1.0)
    p.add_argument("--max-iter", type=int, default=1000)
    p.add_argument("--fpr-target", type=float, default=0.01)
    return p


def is_numeric_value(v: Any) -> bool:
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)):
        try:
            return math.isfinite(float(v))
        except Exception:
            return False
    return False


def detect_feature_names(rows: list[dict[str, Any]]) -> list[str]:
    candidate = set()
    non_numeric = set()

    for row in rows:
        for k, v in row.items():
            if k in EXCLUDE_KEYS or any(k.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            if v is None:
                continue
            if is_numeric_value(v):
                candidate.add(k)
            else:
                non_numeric.add(k)

    return sorted(k for k in candidate if k not in non_numeric)


def rows_to_matrix(rows: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
    X = np.full((len(rows), len(feature_names)), np.nan, dtype=np.float64)
    for i, row in enumerate(rows):
        for j, feat in enumerate(feature_names):
            v = row.get(feat)
            if is_numeric_value(v):
                X[i, j] = float(v)
    return X


def prepare_features(train_rows, val_rows, test_rows):
    feature_names = detect_feature_names(train_rows + val_rows + test_rows)
    if not feature_names:
        raise ValueError("No numeric features detected")

    X_train = rows_to_matrix(train_rows, feature_names)
    X_val = rows_to_matrix(val_rows, feature_names)
    X_test = rows_to_matrix(test_rows, feature_names)

    with np.errstate(all="ignore"):
        medians = np.nanmedian(X_train, axis=0)

    keep = ~np.isnan(medians)
    if not np.any(keep):
        raise ValueError("All candidate features are entirely missing on train split")

    X_train = X_train[:, keep]
    X_val = X_val[:, keep]
    X_test = X_test[:, keep]
    medians = medians[keep]
    kept_feature_names = [f for f, k in zip(feature_names, keep) if k]

    def impute(X):
        X = X.copy()
        inds = np.where(np.isnan(X))
        X[inds] = medians[inds[1]]
        return X

    X_train = impute(X_train)
    X_val = impute(X_val)
    X_test = impute(X_test)

    means = X_train.mean(axis=0)
    stds = X_train.std(axis=0)
    keep_var = stds > 0

    X_train = X_train[:, keep_var]
    X_val = X_val[:, keep_var]
    X_test = X_test[:, keep_var]
    means = means[keep_var]
    stds = stds[keep_var]
    medians = medians[keep_var]
    kept_feature_names = [f for f, k in zip(kept_feature_names, keep_var) if k]

    X_train = (X_train - means) / stds
    X_val = (X_val - means) / stds
    X_test = (X_test - means) / stds

    return {
        "feature_names": kept_feature_names,
        "train_mean": means,
        "train_std": stds,
        "train_median": medians,
        "X_train": X_train,
        "X_val": X_val,
        "X_test": X_test,
    }


def labels_from_rows(rows):
    y = np.asarray([int(r["label"]) for r in rows], dtype=np.int64)
    bad = set(np.unique(y)) - {0, 1}
    if bad:
        raise ValueError(f"Labels must be binary 0/1; found {sorted(bad)}")
    return y


def safe_auroc(y_true, scores):
    classes = np.unique(y_true)
    if len(classes) < 2:
        return None
    return float(roc_auc_score(y_true, scores))


def metrics_at_threshold(y_true, prob_pos, thr):
    y_pred = (prob_pos >= thr).astype(np.int64)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    fpr = fp / (fp + tn) if (fp + tn) else None

    return {
        "threshold": float(thr),
        "support": int(len(y_true)),
        "positives": int(y_true.sum()),
        "negatives": int((y_true == 0).sum()),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "fpr": None if fpr is None else float(fpr),
        "tpr": float(recall),
        "auroc": safe_auroc(y_true, prob_pos),
        "auroc_inverted": safe_auroc(y_true, 1.0 - prob_pos),
    }


def candidate_thresholds(prob_pos: np.ndarray) -> np.ndarray:
    uniq = np.unique(prob_pos)
    extra = np.array([0.0, 1.0 + 1e-12], dtype=np.float64)
    return np.unique(np.concatenate([extra, uniq]))


def choose_best_f1(y_true, prob_pos):
    best = None
    for thr in candidate_thresholds(prob_pos):
        m = metrics_at_threshold(y_true, prob_pos, float(thr))
        key = (m["f1"], m["recall"], -m["threshold"])
        if best is None or key > best[0]:
            best = (key, m)
    return best[1]


def choose_fpr_threshold(y_true, prob_pos, fpr_target):
    feasible = []
    for thr in candidate_thresholds(prob_pos):
        m = metrics_at_threshold(y_true, prob_pos, float(thr))
        if m["fpr"] is not None and m["fpr"] <= fpr_target and m["recall"] > 0:
            feasible.append(m)

    if not feasible:
        return None

    feasible.sort(
        key=lambda m: (m["recall"], m["precision"], -m["threshold"]),
        reverse=True,
    )
    return feasible[0]


def compact_prediction_rows(rows, prob_pos, thr05):
    out = []
    eps = 1e-12
    for row, p in zip(rows, prob_pos):
        p = float(p)
        p_clip = min(max(p, eps), 1.0 - eps)
        out.append({
            "manifest_index": row.get("manifest_index"),
            "split": row.get("split"),
            "source_key": row.get("source_key"),
            "video_path": row.get("video_path"),
            "provenance_class": row.get("provenance_class"),
            "label": int(row["label"]),
            "label_original": row.get("label_original"),
            "task_name": row.get("task_name"),
            "is_video_fake": row.get("is_video_fake"),
            "is_audio_fake": row.get("is_audio_fake"),
            "score_prob": p,
            "score_logit": float(math.log(p_clip / (1.0 - p_clip))),
            "pred_label_thr05": int(p >= thr05),
        })
    return out


def write_subgroup_csv(path: Path, rows, prob_pos, thr05):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "split",
        "group_type",
        "group_value",
        "support",
        "positives",
        "negatives",
        "auroc",
        "auroc_inverted",
        "accuracy_thr05",
        "precision_thr05",
        "recall_thr05",
        "f1_thr05",
        "fpr_thr05",
        "tn",
        "fp",
        "fn",
        "tp",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        def emit(group_type, group_value, subset_rows, subset_scores):
            y = np.asarray([int(r["label"]) for r in subset_rows], dtype=np.int64)
            m = metrics_at_threshold(y, np.asarray(subset_scores, dtype=np.float64), thr05)
            w.writerow({
                "split": subset_rows[0]["split"] if subset_rows else "",
                "group_type": group_type,
                "group_value": group_value,
                "support": m["support"],
                "positives": m["positives"],
                "negatives": m["negatives"],
                "auroc": m["auroc"],
                "auroc_inverted": m["auroc_inverted"],
                "accuracy_thr05": m["accuracy"],
                "precision_thr05": m["precision"],
                "recall_thr05": m["recall"],
                "f1_thr05": m["f1"],
                "fpr_thr05": m["fpr"],
                "tn": m["tn"],
                "fp": m["fp"],
                "fn": m["fn"],
                "tp": m["tp"],
            })

        by_split = {}
        for row, score in zip(rows, prob_pos):
            by_split.setdefault(row["split"], []).append((row, score))

        for split, items in sorted(by_split.items()):
            split_rows = [r for r, _ in items]
            split_scores = [s for _, s in items]
            emit("overall", "ALL", split_rows, split_scores)

            prov_groups = {}
            for r, s in items:
                prov_groups.setdefault(r.get("provenance_class", "UNKNOWN"), []).append((r, s))

            for prov, prov_items in sorted(prov_groups.items()):
                emit(
                    "provenance_class",
                    prov,
                    [r for r, _ in prov_items],
                    [s for _, s in prov_items],
                )


def main():
    args = build_parser().parse_args()

    infile = Path(args.infile)
    outroot = Path(args.outroot)
    if not infile.exists():
        raise FileNotFoundError(f"Missing infile: {infile}")

    rows = list(read_jsonl_gz(infile))
    if not rows:
        raise ValueError("Input file is empty")

    split_counts = Counter(r["split"] for r in rows)
    required_splits = {"train", "val", "test"}
    if set(split_counts) != required_splits:
        raise ValueError(f"Expected splits {required_splits}; got {dict(split_counts)}")

    train_rows = [r for r in rows if r["split"] == "train"]
    val_rows = [r for r in rows if r["split"] == "val"]
    test_rows = [r for r in rows if r["split"] == "test"]

    feats = prepare_features(train_rows, val_rows, test_rows)
    X_train = feats["X_train"]
    X_val = feats["X_val"]
    X_test = feats["X_test"]
    feature_names = feats["feature_names"]

    y_train = labels_from_rows(train_rows)
    y_val = labels_from_rows(val_rows)
    y_test = labels_from_rows(test_rows)

    clf = LogisticRegression(
        penalty="l2",
        C=args.c,
        solver="liblinear",
        max_iter=args.max_iter,
        random_state=args.seed,
        class_weight=None,
    )
    clf.fit(X_train, y_train)

    p_train = clf.predict_proba(X_train)[:, 1]
    p_val = clf.predict_proba(X_val)[:, 1]
    p_test = clf.predict_proba(X_test)[:, 1]

    thr05 = 0.5
    val_thr05 = metrics_at_threshold(y_val, p_val, thr05)
    test_thr05 = metrics_at_threshold(y_test, p_test, thr05)

    best_f1 = choose_best_f1(y_val, p_val)
    best_f1_test = metrics_at_threshold(y_test, p_test, best_f1["threshold"])

    best_fpr = choose_fpr_threshold(y_val, p_val, args.fpr_target)
    if best_fpr is None:
        fpr_payload = {
            "timestamp_utc": utc_now_compact(),
            "task": args.task,
            "selection_rule": f"max_recall subject to validation FPR <= {args.fpr_target} and recall > 0",
            "fpr_target": args.fpr_target,
            "selected_threshold": None,
            "infeasible": True,
            "reason": "No validation threshold achieved target FPR with non-zero recall.",
            "validation_negatives": int((y_val == 0).sum()),
            "validation_fpr_resolution": float(1.0 / max(1, int((y_val == 0).sum()))),
            "val_metrics": None,
            "test_metrics": None,
        }
    else:
        best_fpr_test = metrics_at_threshold(y_test, p_test, best_fpr["threshold"])
        fpr_payload = {
            "timestamp_utc": utc_now_compact(),
            "task": args.task,
            "selection_rule": f"max_recall subject to validation FPR <= {args.fpr_target} and recall > 0",
            "fpr_target": args.fpr_target,
            "selected_threshold": best_fpr["threshold"],
            "infeasible": False,
            "validation_negatives": int((y_val == 0).sum()),
            "validation_fpr_resolution": float(1.0 / max(1, int((y_val == 0).sum()))),
            "val_metrics": best_fpr,
            "test_metrics": best_fpr_test,
        }

    model_dir = outroot / "models" / args.task
    preds_dir = outroot / "preds"
    metrics_dir = outroot / "metrics"
    subgroup_dir = outroot / "subgroup"

    model_dir.mkdir(parents=True, exist_ok=True)
    preds_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    subgroup_dir.mkdir(parents=True, exist_ok=True)

    model_json = model_dir / "avsync_lr_model.json"
    preds_jsonl = preds_dir / f"avsync_preds_{args.task}.jsonl.gz"
    metrics_thr05_json = metrics_dir / f"metrics_avsync_{args.task}_thr05.json"
    thr_f1_json = metrics_dir / f"threshold_sweep_avsync_{args.task}_f1.json"
    thr_fpr_json = metrics_dir / f"threshold_sweep_avsync_{args.task}_fpr01.json"
    subgroup_csv = subgroup_dir / f"avsync_{args.task}_subgroup_metrics.csv"

    model_payload = {
        "timestamp_utc": utc_now_compact(),
        "task": args.task,
        "infile": str(infile.resolve()),
        "seed": args.seed,
        "hyperparameters": {
            "penalty": "l2",
            "C": args.c,
            "solver": "liblinear",
            "max_iter": args.max_iter,
            "class_weight": None,
        },
        "split_counts": dict(split_counts),
        "label_counts_by_split": {
            "train": dict(Counter(map(int, y_train.tolist()))),
            "val": dict(Counter(map(int, y_val.tolist()))),
            "test": dict(Counter(map(int, y_test.tolist()))),
        },
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "train_imputation_median": {
            f: float(v) for f, v in zip(feature_names, feats["train_median"].tolist())
        },
        "train_standardisation_mean": {
            f: float(v) for f, v in zip(feature_names, feats["train_mean"].tolist())
        },
        "train_standardisation_std": {
            f: float(v) for f, v in zip(feature_names, feats["train_std"].tolist())
        },
        "intercept": float(clf.intercept_[0]),
        "coefficients": {
            f: float(c) for f, c in zip(feature_names, clf.coef_[0].tolist())
        },
    }

    with model_json.open("w", encoding="utf-8") as f:
        json.dump(model_payload, f, indent=2)

    pred_rows = (
        compact_prediction_rows(train_rows, p_train, thr05)
        + compact_prediction_rows(val_rows, p_val, thr05)
        + compact_prediction_rows(test_rows, p_test, thr05)
    )
    write_jsonl_gz(preds_jsonl, pred_rows)

    metrics_payload = {
        "timestamp_utc": utc_now_compact(),
        "task": args.task,
        "positive_class": 1,
        "positive_semantics": rows[0].get("label_semantics"),
        "infile": str(infile.resolve()),
        "model_json": str(model_json.resolve()),
        "predictions_jsonl_gz": str(preds_jsonl.resolve()),
        "split_counts": dict(split_counts),
        "threshold": 0.5,
        "score_direction": {
            "higher_score_means_more_likely_positive": True,
            "validation_auroc": safe_auroc(y_val, p_val),
            "validation_auroc_inverted": safe_auroc(y_val, 1.0 - p_val),
            "test_auroc": safe_auroc(y_test, p_test),
            "test_auroc_inverted": safe_auroc(y_test, 1.0 - p_test),
        },
        "val_metrics": val_thr05,
        "test_metrics": test_thr05,
    }
    with metrics_thr05_json.open("w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    f1_payload = {
        "timestamp_utc": utc_now_compact(),
        "task": args.task,
        "selection_rule": "max validation F1",
        "selected_threshold": best_f1["threshold"],
        "val_metrics": best_f1,
        "test_metrics": best_f1_test,
    }
    with thr_f1_json.open("w", encoding="utf-8") as f:
        json.dump(f1_payload, f, indent=2)

    with thr_fpr_json.open("w", encoding="utf-8") as f:
        json.dump(fpr_payload, f, indent=2)

    write_subgroup_csv(subgroup_csv, val_rows + test_rows, np.concatenate([p_val, p_test]), thr05)

    print(f"Wrote model: {model_json}")
    print(f"Wrote predictions: {preds_jsonl}")
    print(f"Wrote thr05 metrics: {metrics_thr05_json}")
    print(f"Wrote F1 sweep: {thr_f1_json}")
    print(f"Wrote FPR sweep: {thr_fpr_json}")
    print(f"Wrote subgroup CSV: {subgroup_csv}")
    print(f"Feature count: {len(feature_names)}")
    print(f"Train labels: {dict(Counter(map(int, y_train.tolist())))}")
    print(f"Val labels: {dict(Counter(map(int, y_val.tolist())))}")
    print(f"Test labels: {dict(Counter(map(int, y_test.tolist())))}")
    print(f"Validation AUROC: {safe_auroc(y_val, p_val)}")
    print(f"Test AUROC: {safe_auroc(y_test, p_test)}")


if __name__ == "__main__":
    main()