"""Evaluate FAVE-RAG v0.2 outputs."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from common.jsonl_utils import read_jsonl, write_jsonl
from common.metrics import precision_recall_f1
from common.numeric_utils import parse_final_answer
from common.unit_utils import close_to, convert_value


FILE_TO_METHOD = {
    "llm_only.jsonl": "LLM-only",
    "vanilla_clean.jsonl": "Vanilla RAG Clean",
    "vanilla_mixed.jsonl": "Vanilla RAG Mixed",
    "demo_clean.jsonl": "DeMo-style Clean",
    "demo_mixed.jsonl": "DeMo-style Mixed",
    "fave_clean.jsonl": "FAVE-RAG Clean",
    "fave_mixed_soft.jsonl": "FAVE-RAG Mixed Soft",
    "fave_mixed_hard.jsonl": "FAVE-RAG Mixed Hard",
    "fave_mixed_silent.jsonl": "FAVE-RAG Mixed Silent",
    "always_gold.jsonl": "Always Gold Mock",
    "always_trap.jsonl": "Always Trap Mock",
    "imperfect_arbitration.jsonl": "Imperfect Arbitration Mock",
}


def expected_labels(item: dict) -> dict[str, str]:
    labels = {}
    for label, ids in item["expected_arbitration"].items():
        for eid in ids:
            labels[eid] = label
    return labels


def evaluate_prediction(item: dict, method: str, pred: dict) -> dict:
    raw = pred.get("final_answer", pred.get("answer", ""))
    parsed = parse_final_answer(raw)
    converted, unit_ambiguous = (None, False)
    if parsed.value is not None:
        converted, unit_ambiguous = convert_value(parsed.value, parsed.unit, item["gold_unit"])
    correct = close_to(converted, item["gold_value"], item["tolerance"])

    trap_hit = False
    trap_id = ""
    if not correct:
        for ev in item.get("invalid_evidence", []):
            trap_value, _ = convert_value(parsed.value, parsed.unit, ev.get("trap_unit", item["gold_unit"])) if parsed.value is not None else (None, False)
            if close_to(trap_value, ev["trap_answer"], item["tolerance"]):
                trap_hit = True
                trap_id = ev["id"]
                break

    labels = expected_labels(item)
    expected_rejected = [eid for eid, label in labels.items() if label == "Rejected"]
    predicted = pred.get("predicted_arbitration", {}) or {}
    arbitration_total = len(labels)
    arbitration_correct_count = sum(1 for eid, label in labels.items() if predicted.get(eid) == label)
    arbitration_correct = arbitration_correct_count == arbitration_total if arbitration_total else None

    return {
        "id": item["id"],
        "method": method,
        "final_answer_raw": raw,
        "parsed_value": converted,
        "parsed_unit": parsed.unit,
        "unit_ambiguous": unit_ambiguous if parsed.unit is None and correct else False,
        "gold_value": item["gold_value"],
        "gold_unit": item["gold_unit"],
        "correct": bool(correct),
        "trap_hit": bool(trap_hit),
        "trap_matched_id": trap_id,
        "predicted_arbitration": predicted,
        "expected_rejected_ids": expected_rejected,
        "arbitration_correct": arbitration_correct,
        "arbitration_correct_count": arbitration_correct_count,
        "arbitration_total": arbitration_total,
        "error": pred.get("error", ""),
    }


def load_predictions(pred_dir: Path) -> dict[str, list[dict]]:
    loaded = {}
    for path in sorted(pred_dir.glob("*.jsonl")):
        if path.name not in FILE_TO_METHOD:
            continue
        method = FILE_TO_METHOD[path.name]
        loaded[method] = list(read_jsonl(path))
    return loaded


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", default="data/pilot/fave_bench_10.jsonl")
    parser.add_argument("--pred_dir", default="outputs/mock")
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()

    bench_rows = list(read_jsonl(args.bench))
    bench_by_id = {row["id"]: row for row in bench_rows}
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    per_item = []
    for method, preds in load_predictions(Path(args.pred_dir)).items():
        for pred in preds:
            item = bench_by_id[pred["id"]]
            per_item.append(evaluate_prediction(item, method, pred))
    write_jsonl(results_dir / "per_item.jsonl", per_item)
    if results_dir != Path("results"):
        write_jsonl("results/per_item.jsonl", per_item)

    by_method: dict[str, list[dict]] = defaultdict(list)
    for row in per_item:
        by_method[row["method"]].append(row)

    def acc(method: str) -> str:
        rows = by_method.get(method, [])
        return "" if not rows else sum(r["correct"] for r in rows) / len(rows)

    summary_rows = []
    for method, rows in by_method.items():
        clean_acc = ""
        mixed_acc = ""
        drop = ""
        if "Clean" in method:
            clean_acc = acc(method)
        elif "Mixed" in method:
            mixed_acc = acc(method)
            clean_name = method.replace("Mixed Soft", "Clean").replace("Mixed Hard", "Clean").replace("Mixed Silent", "Clean").replace("Mixed", "Clean")
            if by_method.get(clean_name):
                drop = acc(clean_name) - mixed_acc
        poisoning = sum(r["trap_hit"] for r in rows) / len(rows) if rows else 0.0
        summary_rows.append(
            {
                "Method": method,
                "N": len(rows),
                "n_errors": sum(1 for r in rows if r["error"]),
                "Clean Accuracy": clean_acc,
                "Mixed Accuracy": mixed_acc if "Mixed" in method or "LLM" in method or "Mock" in method else "",
                "Robustness Drop": drop,
                "Poisoning Rate": poisoning,
                "drop_vs_vanilla_clean": (acc("Vanilla RAG Clean") - (mixed_acc if mixed_acc != "" else acc(method))) if by_method.get("Vanilla RAG Clean") else "",
            }
        )
    write_csv(
        results_dir / "fave_summary.csv",
        summary_rows,
        ["Method", "N", "n_errors", "Clean Accuracy", "Mixed Accuracy", "Robustness Drop", "Poisoning Rate", "drop_vs_vanilla_clean"],
    )

    poison_rows = [{"Method": method, "N": len(rows), "Poisoning Rate": sum(r["trap_hit"] for r in rows) / len(rows)} for method, rows in by_method.items()]
    write_csv(results_dir / "fave_poisoning.csv", poison_rows, ["Method", "N", "Poisoning Rate"])

    arbitration_rows = []
    conflict_counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for method, preds in load_predictions(Path(args.pred_dir)).items():
        tp = fp = fn = 0
        micro_correct = micro_total = 0
        for pred in preds:
            item = bench_by_id[pred["id"]]
            labels = expected_labels(item)
            predicted = pred.get("predicted_arbitration", {}) or {}
            rejected_gold = {eid for eid, label in labels.items() if label == "Rejected"}
            rejected_pred = {eid for eid, label in predicted.items() if label == "Rejected"}
            tp += len(rejected_gold & rejected_pred)
            fp += len(rejected_pred - rejected_gold)
            fn += len(rejected_gold - rejected_pred)
            for eid, label in labels.items():
                micro_total += 1
                micro_correct += int(predicted.get(eid) == label)
            for ev in item.get("invalid_evidence", []):
                key = (method, ev["conflict_type"])
                conflict_counts[key]["total"] += 1
                conflict_counts[key]["detected"] += int(predicted.get(ev["id"]) == "Rejected")
        prf = precision_recall_f1(tp, fp, fn)
        arbitration_rows.append(
            {
                "Method": method,
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "Precision": prf["precision"],
                "Recall": prf["recall"],
                "F1": prf["f1"],
                "Arbitration Accuracy": micro_correct / micro_total if micro_total else 0.0,
            }
        )
    write_csv(results_dir / "fave_conflict_detection.csv", arbitration_rows, ["Method", "TP", "FP", "FN", "Precision", "Recall", "F1", "Arbitration Accuracy"])
    write_csv(results_dir / "fave_arbitration.csv", arbitration_rows, ["Method", "TP", "FP", "FN", "Precision", "Recall", "F1", "Arbitration Accuracy"])

    conflict_rows = [
        {"Method": method, "conflict_type": conflict_type, "N": counts["total"], "Recall": counts["detected"] / counts["total"] if counts["total"] else 0.0}
        for (method, conflict_type), counts in sorted(conflict_counts.items())
    ]
    write_csv(results_dir / "fave_conflict_type_recall.csv", conflict_rows, ["Method", "conflict_type", "N", "Recall"])

    print(f"Wrote {results_dir / 'per_item.jsonl'}")
    print(f"Wrote {results_dir / 'fave_summary.csv'}")
    print(f"Wrote {results_dir / 'fave_conflict_detection.csv'}")
    print(f"Wrote {results_dir / 'fave_poisoning.csv'}")
    print(f"Wrote {results_dir / 'fave_arbitration.csv'}")


if __name__ == "__main__":
    main()
