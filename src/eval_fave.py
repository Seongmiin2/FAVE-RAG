"""Evaluate FAVE-RAG pilot outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common.jsonl_utils import read_jsonl
from common.metrics import conflict_detection_counts, precision_recall_f1
from common.numeric_utils import is_close


METHOD_FILES = {
    "LLM-only": "llm_only.jsonl",
    "Vanilla RAG Clean": "vanilla_clean.jsonl",
    "Vanilla RAG Mixed": "vanilla_mixed.jsonl",
    "DeMo-style Mixed": "demo_mixed.jsonl",
    "FAVE-RAG Mixed": "fave_mixed.jsonl",
}


def accuracy(bench_by_id: dict[str, dict], pred_rows: list[dict]) -> float:
    if not pred_rows:
        return 0.0
    correct = 0
    for pred in pred_rows:
        gold = bench_by_id[pred["id"]]["gold_answer"]
        correct += int(is_close(pred.get("final_answer"), gold))
    return correct / len(pred_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", default="data/pilot/fave_bench_10.jsonl")
    parser.add_argument("--pred_dir", default="outputs/mock")
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()

    bench_rows = list(read_jsonl(args.bench))
    bench_by_id = {row["id"]: row for row in bench_rows}
    pred_dir = Path(args.pred_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    loaded = {
        method: list(read_jsonl(pred_dir / filename))
        for method, filename in METHOD_FILES.items()
        if (pred_dir / filename).exists()
    }
    clean_acc = accuracy(bench_by_id, loaded.get("Vanilla RAG Clean", []))

    summary_rows = []
    for method, preds in loaded.items():
        acc = accuracy(bench_by_id, preds)
        mixed_acc = acc if method != "Vanilla RAG Clean" else ""
        drop = clean_acc - acc if "Mixed" in method else ""
        summary_rows.append(
            {
                "Method": method,
                "N": len(preds),
                "Clean Accuracy": clean_acc if method == "Vanilla RAG Clean" else "",
                "Mixed Accuracy": mixed_acc,
                "Robustness Drop": drop,
            }
        )

    with (results_dir / "fave_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Method", "N", "Clean Accuracy", "Mixed Accuracy", "Robustness Drop"])
        writer.writeheader()
        writer.writerows(summary_rows)

    conflict_rows = []
    for method, preds in loaded.items():
        counts = conflict_detection_counts(bench_rows, preds)
        prf = precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])
        conflict_rows.append(
            {
                "Method": method,
                "TP": counts["tp"],
                "FP": counts["fp"],
                "FN": counts["fn"],
                "Precision": prf["precision"],
                "Recall": prf["recall"],
                "F1": prf["f1"],
            }
        )

    with (results_dir / "fave_conflict_detection.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Method", "TP", "FP", "FN", "Precision", "Recall", "F1"])
        writer.writeheader()
        writer.writerows(conflict_rows)

    print(f"Wrote {results_dir / 'fave_summary.csv'}")
    print(f"Wrote {results_dir / 'fave_conflict_detection.csv'}")


if __name__ == "__main__":
    main()
