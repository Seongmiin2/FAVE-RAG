"""Optional public dataset access check for telecom math sources.

This script is allowed to fail gracefully. The FAVE-RAG pilot can run from the
manual seed benchmark while Hugging Face access is being configured.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from common.jsonl_utils import write_jsonl


DATASETS = [
    (
        "XINLI1997/WirelessMathBench",
        "data/raw/wirelessmathbench_full.jsonl",
        "data/raw/wirelessmathbench_sample.jsonl",
    ),
    (
        "XINLI1997/WirelessMATHBench-XL",
        "data/raw/wirelessmathbench_xl_full.jsonl",
        "data/raw/wirelessmathbench_xl_sample.jsonl",
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Use only cached Hugging Face datasets.")
    args = parser.parse_args()
    if args.offline:
        os.environ["HF_DATASETS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"

    report_lines = ["# Data Access Report", ""]
    try:
        from datasets import load_dataset
    except ImportError:
        report_lines.extend(
            [
                "datasets package is not installed.",
                "Install requirements.txt to try Hugging Face dataset loading.",
            ]
        )
        Path("data/raw/data_access_report.md").write_text("\n".join(report_lines), encoding="utf-8")
        print("datasets package is missing; wrote data/raw/data_access_report.md")
        return

    for dataset_name, full_output_path, sample_output_path in DATASETS:
        report_lines.extend([f"## {dataset_name}", ""])
        try:
            ds = load_dataset(dataset_name)
            report_lines.append(f"Splits: {list(ds.keys())}")
            split_name = next(iter(ds.keys()))
            split = ds[split_name]
            report_lines.append(f"Selected split: {split_name}")
            report_lines.append(f"Rows: {len(split)}")
            report_lines.append(f"Columns: {list(split.column_names)}")
            full_rows = [dict(row) for row in split]
            sample = full_rows[: min(30, len(full_rows))]
            write_jsonl(full_output_path, full_rows)
            write_jsonl(sample_output_path, sample)
            report_lines.append(f"Saved full split: {full_output_path}")
            report_lines.append(f"Saved sample: {sample_output_path}")
            report_lines.append("")
            print(f"Loaded {dataset_name}: {len(split)} rows in split {split_name}")
        except Exception as exc:  # noqa: BLE001 - report any dataset/network/access issue.
            report_lines.append(f"Access failed: {type(exc).__name__}: {exc}")
            report_lines.append("")
            print(f"Could not load {dataset_name}: {exc}")

    report_lines.extend(
        [
            "## TeleMath",
            "",
            "TeleMath is treated as optional because access may be gated or require separate authentication.",
        ]
    )
    Path("data/raw/data_access_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    print("Wrote data/raw/data_access_report.md")


if __name__ == "__main__":
    main()
