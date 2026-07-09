"""Generate deterministic v0.2 mock outputs for metric testing."""

from __future__ import annotations

import argparse
from pathlib import Path

from common.jsonl_utils import read_jsonl, write_jsonl


def arbitration_labels(item: dict, imperfect: bool = False) -> dict:
    labels = {}
    for label, ids in item["expected_arbitration"].items():
        for eid in ids:
            labels[eid] = label
    if imperfect and item["invalid_evidence"]:
        labels[item["invalid_evidence"][0]["id"]] = "Contested"
    return labels


def gold_response(item: dict, method: str, arbitration: bool = False) -> dict:
    row = {
        "id": item["id"],
        "method": method,
        "selected_formula": item["gold_formula"],
        "final_answer": f"{item['gold_value']} {item['gold_unit']}",
        "unit": item["gold_unit"],
    }
    if arbitration:
        row["predicted_arbitration"] = arbitration_labels(item)
    return row


def trap_response(item: dict, method: str, arbitration: bool = False) -> dict:
    trap = item["invalid_evidence"][0]
    row = {
        "id": item["id"],
        "method": method,
        "selected_formula": "trap procedure",
        "final_answer": f"{trap['trap_answer']} {trap['trap_unit']}",
        "unit": trap["trap_unit"],
    }
    if arbitration:
        row["predicted_arbitration"] = arbitration_labels(item, imperfect=True)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/pilot/fave_bench_10.jsonl")
    parser.add_argument("--output_dir", default="outputs/mock")
    args = parser.parse_args()

    rows = list(read_jsonl(args.input))
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jsonl"):
        old.unlink()
    write_jsonl(out / "always_gold.jsonl", [gold_response(item, "Always Gold Mock", arbitration=True) for item in rows])
    write_jsonl(out / "always_trap.jsonl", [trap_response(item, "Always Trap Mock") for item in rows])
    write_jsonl(out / "imperfect_arbitration.jsonl", [gold_response(item, "Imperfect Arbitration Mock", arbitration=True) if i % 2 else trap_response(item, "Imperfect Arbitration Mock", arbitration=True) for i, item in enumerate(rows)])
    write_jsonl(out / "llm_only.jsonl", [gold_response(item, "LLM-only") if i % 3 else trap_response(item, "LLM-only") for i, item in enumerate(rows)])
    write_jsonl(out / "vanilla_clean.jsonl", [gold_response(item, "Vanilla RAG Clean") for item in rows])
    write_jsonl(out / "vanilla_mixed.jsonl", [trap_response(item, "Vanilla RAG Mixed") if i % 2 else gold_response(item, "Vanilla RAG Mixed") for i, item in enumerate(rows)])
    write_jsonl(out / "demo_clean.jsonl", [gold_response(item, "DeMo-style Clean") for item in rows])
    write_jsonl(out / "demo_mixed.jsonl", [gold_response(item, "DeMo-style Mixed") if i % 3 else trap_response(item, "DeMo-style Mixed") for i, item in enumerate(rows)])
    write_jsonl(out / "fave_clean.jsonl", [gold_response(item, "FAVE-RAG Clean", arbitration=True) for item in rows])
    write_jsonl(out / "fave_mixed_soft.jsonl", [gold_response(item, "FAVE-RAG Mixed Soft", arbitration=True) for item in rows])
    print(f"Wrote v0.2 mock outputs for {len(rows)} rows under {out}")


if __name__ == "__main__":
    main()
