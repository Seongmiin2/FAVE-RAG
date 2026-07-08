"""Select real WirelessMathBench rows that are useful for FAVE-RAG annotation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common.jsonl_utils import read_jsonl, write_jsonl


KEYWORDS = [
    "snr",
    "sinr",
    "capacity",
    "rate",
    "bandwidth",
    "path loss",
    "power",
    "interference",
    "noise",
    "mimo",
    "channel",
    "outage",
    "ber",
    "efficiency",
    "db",
    "beamforming",
]


def score_row(row: dict) -> int:
    text = " ".join(str(row.get(key, "")) for key in ["background", "question_text", "equation", "correct_answer"]).lower()
    score = sum(1 for keyword in KEYWORDS if keyword in text)
    if row.get("equation"):
        score += 2
    if row.get("correct_answer"):
        score += 1
    if row.get("type") in {"fill_in_the_blank", "fill_blank_50", "fill_blank_100"}:
        score += 1
    return score


def normalize_row(row: dict, source: str) -> dict:
    return {
        "source": source,
        "source_id": row.get("id") or row.get("question_id"),
        "paper_id": row.get("paper_id"),
        "type": row.get("type"),
        "domain": row.get("domain"),
        "background": row.get("background"),
        "question_text": row.get("question_text"),
        "equation": row.get("equation"),
        "options": row.get("options"),
        "correct_answer": row.get("correct_answer"),
        "candidate_score": score_row(row),
        "fave_annotation_status": "unlabeled",
        "notes": "Real dataset candidate. Needs gold formula, units, valid evidence, and true-but-inapplicable evidence annotation.",
    }


def load_candidates(path: Path, source: str) -> list[dict]:
    if not path.exists():
        return []
    return [normalize_row(row, source) for row in read_jsonl(path)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=40)
    parser.add_argument("--output_jsonl", default="data/raw/fave_candidate_40.jsonl")
    parser.add_argument("--output_csv", default="data/raw/fave_candidate_40.csv")
    args = parser.parse_args()

    rows = []
    wmb_path = Path("data/raw/wirelessmathbench_full.jsonl")
    wmb_xl_path = Path("data/raw/wirelessmathbench_xl_full.jsonl")
    if not wmb_path.exists():
        wmb_path = Path("data/raw/wirelessmathbench_sample.jsonl")
    if not wmb_xl_path.exists():
        wmb_xl_path = Path("data/raw/wirelessmathbench_xl_sample.jsonl")

    rows.extend(load_candidates(wmb_path, "WirelessMathBench"))
    rows.extend(load_candidates(wmb_xl_path, "WirelessMATHBench-XL"))
    rows = [row for row in rows if row["candidate_score"] > 0]
    rows.sort(key=lambda row: (row["candidate_score"], str(row.get("source_id"))), reverse=True)
    selected = rows[: args.n]

    write_jsonl(args.output_jsonl, selected)
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "source",
            "source_id",
            "paper_id",
            "type",
            "domain",
            "candidate_score",
            "question_text",
            "equation",
            "correct_answer",
            "fave_annotation_status",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in selected:
            writer.writerow({key: row.get(key) for key in fieldnames})

    print(f"Selected {len(selected)} real candidates from {len(rows)} scored rows")
    print(f"Wrote {args.output_jsonl}")
    print(f"Wrote {args.output_csv}")


if __name__ == "__main__":
    main()
