"""Metrics for answer robustness and evidence arbitration."""

from __future__ import annotations

from collections import Counter


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def precision_recall_f1(tp: int, fp: int, fn: int) -> dict:
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2 * precision * recall, precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def conflict_detection_counts(bench_rows: list[dict], pred_rows: list[dict]) -> Counter:
    counts: Counter = Counter()
    pred_by_id = {row["id"]: row for row in pred_rows}
    for item in bench_rows:
        predicted = pred_by_id.get(item["id"], {}).get("predicted_arbitration", {})
        rejected_gold = set(item.get("expected_arbitration", {}).get("Rejected", []))
        rejected_pred = {eid for eid, label in predicted.items() if label == "Rejected"}
        counts["tp"] += len(rejected_gold & rejected_pred)
        counts["fp"] += len(rejected_pred - rejected_gold)
        counts["fn"] += len(rejected_gold - rejected_pred)
    return counts
