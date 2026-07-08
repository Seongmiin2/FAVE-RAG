"""Generate deterministic mock outputs for pipeline testing."""

from __future__ import annotations

import argparse
from pathlib import Path

from common.jsonl_utils import read_jsonl, write_jsonl


def response(item: dict, method: str, correct: bool, arbitration: bool = False) -> dict:
    row = {
        "id": item["id"],
        "method": method,
        "selected_formula": item["gold_formula"] if correct else "context-selected incorrect formula",
        "final_answer": item["gold_answer"] if correct else "0",
        "unit": "as requested",
        "used_evidence": item["clean_context"] if correct else item["mixed_context"],
    }
    if arbitration:
        labels = {}
        for label, ids in item["expected_arbitration"].items():
            for eid in ids:
                labels[eid] = label
        row["predicted_arbitration"] = labels
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/pilot/fave_bench_10.jsonl")
    parser.add_argument("--output_dir", default="outputs/mock")
    args = parser.parse_args()

    rows = list(read_jsonl(args.input))
    out = Path(args.output_dir)
    write_jsonl(out / "llm_only.jsonl", [response(item, "LLM-only", i % 3 != 0) for i, item in enumerate(rows)])
    write_jsonl(out / "vanilla_clean.jsonl", [response(item, "Vanilla RAG Clean", True) for item in rows])
    write_jsonl(out / "vanilla_mixed.jsonl", [response(item, "Vanilla RAG Mixed", i % 2 == 0) for i, item in enumerate(rows)])
    write_jsonl(out / "demo_mixed.jsonl", [response(item, "DeMo-style Mixed", i % 3 != 1) for i, item in enumerate(rows)])
    write_jsonl(out / "fave_mixed.jsonl", [response(item, "FAVE-RAG Mixed", True, arbitration=True) for item in rows])
    print(f"Wrote mock outputs for {len(rows)} rows under {out}")


if __name__ == "__main__":
    main()
