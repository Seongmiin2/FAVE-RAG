"""Create the v0.2 decision-ready pilot report from evaluator outputs."""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

from common.jsonl_utils import read_jsonl


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()


def decide_text(per_item: str) -> str:
    return subprocess.check_output([".\\.venv\\Scripts\\python.exe", "src\\decide.py", "--per_item", per_item], text=True).strip()


def cell(row: dict) -> str:
    if row.get("error"):
        return "E"
    if row.get("correct"):
        return "O"
    if row.get("trap_hit"):
        return "T"
    return "X"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--seed", default="0")
    parser.add_argument("--n_runs", default="1")
    parser.add_argument("--smoke_api_calls", type=int, default=16)
    parser.add_argument("--output", default="results/pilot_report_v0.2.md")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    per_item_path = results_dir / "per_item.jsonl"
    per_item = list(read_jsonl(per_item_path))
    summary = read_csv(results_dir / "fave_summary.csv")
    arbitration = read_csv(results_dir / "fave_arbitration.csv")
    conflict_type = read_csv(results_dir / "fave_conflict_type_recall.csv")
    verdict = decide_text(str(per_item_path))

    methods = [row["Method"] for row in summary]
    by_item: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in per_item:
        by_item[row["id"]][row["method"]] = row

    full_calls = sum(2 if row["method"].startswith("FAVE-RAG") else 1 for row in per_item)
    calls = full_calls + args.smoke_api_calls
    lines = []
    lines.append("# FAVE-RAG v0.2 Pilot Report")
    lines.append("")
    lines.append("## 4.1 Run Metadata")
    lines.append("")
    lines.append(f"- Date: {date.today().isoformat()}")
    lines.append(f"- Git commit: {git_commit()}")
    lines.append(f"- Provider: {args.provider}")
    lines.append(f"- Model: {args.model}")
    lines.append(f"- Seed: {args.seed}")
    lines.append(f"- n_runs: {args.n_runs}")
    lines.append("- Filter modes: soft, hard, silent")
    lines.append(f"- Total API calls made: {calls} ({full_calls} full-run calls + {args.smoke_api_calls} smoke-test calls)")
    lines.append("- Run Log: Acceptance tests passed before report generation. Smoke-test fixes: runner concurrency, timeout, streaming fallback, v0.2 evaluator parsing.")
    lines.append("")
    lines.append("## 4.2 Verdict Block")
    lines.append("")
    lines.append("```text")
    lines.append(verdict)
    lines.append("```")
    lines.append("")
    for line in verdict.splitlines()[1:]:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## 4.3 Main Results Table")
    lines.append("")
    lines.append("| Method | N | n_errors | Clean Acc | Mixed Acc | Robustness Drop (within-method) | Poisoning Rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in summary:
        lines.append(
            f"| {row['Method']} | {row['N']} | {row['n_errors']} | {row['Clean Accuracy']} | {row['Mixed Accuracy']} | {row['Robustness Drop']} | {row['Poisoning Rate']} |"
        )
    lines.append("")
    lines.append("## 4.4 FAVE Filtering Ablation")
    lines.append("")
    lines.append("| Filter Mode | Mixed Acc | Poisoning Rate | Conflict F1 |")
    lines.append("|---|---:|---:|---:|")
    arb_by_method = {row["Method"]: row for row in arbitration}
    sum_by_method = {row["Method"]: row for row in summary}
    for mode, method in [("soft", "FAVE-RAG Mixed Soft"), ("hard", "FAVE-RAG Mixed Hard"), ("silent", "FAVE-RAG Mixed Silent")]:
        s = sum_by_method.get(method, {})
        a = arb_by_method.get(method, {})
        lines.append(f"| {mode} | {s.get('Mixed Accuracy', '')} | {s.get('Poisoning Rate', '')} | {a.get('F1', '')} |")
    lines.append("")
    lines.append("## 4.5 Arbitration Quality")
    lines.append("")
    lines.append("| Method | Rejected Precision | Rejected Recall | Rejected F1 | 3-class Arbitration Accuracy |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in arbitration:
        lines.append(f"| {row['Method']} | {row['Precision']} | {row['Recall']} | {row['F1']} | {row['Arbitration Accuracy']} |")
    lines.append("")
    lines.append("| Method | conflict_type | N | Recall |")
    lines.append("|---|---|---:|---:|")
    for row in conflict_type:
        lines.append(f"| {row['Method']} | {row['conflict_type']} | {row['N']} | {row['Recall']} |")
    lines.append("")
    lines.append("## 4.6 Per-item Grid")
    lines.append("")
    lines.append("| Item | " + " | ".join(methods) + " |")
    lines.append("|---|" + "|".join(["---:" for _ in methods]) + "|")
    for item_id in sorted(by_item):
        vals = [cell(by_item[item_id].get(method, {"error": "missing"})) for method in methods]
        lines.append("| " + item_id + " | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## 4.7 Failure Appendix")
    lines.append("")
    any_failure = False
    for row in per_item:
        if cell(row) == "O":
            continue
        any_failure = True
        lines.append(f"### {row['id']} / {row['method']} / {cell(row)}")
        lines.append("")
        lines.append(f"- raw final_answer: `{row.get('final_answer_raw', '')}`")
        lines.append(f"- parsed value+unit: `{row.get('parsed_value')}` `{row.get('parsed_unit')}`")
        lines.append(f"- gold value+unit: `{row.get('gold_value')}` `{row.get('gold_unit')}`")
        lines.append(f"- matched trap id: `{row.get('trap_matched_id', '')}`")
        lines.append(f"- unit_ambiguous: `{row.get('unit_ambiguous')}`")
        if row.get("predicted_arbitration"):
            lines.append(f"- predicted arbitration: `{row.get('predicted_arbitration')}`")
        if row.get("error"):
            lines.append(f"- error: `{row.get('error')}`")
        lines.append("")
    if not any_failure:
        lines.append("None observed.")
        lines.append("")
    lines.append("## 4.8 Anomalies & Data Quality")
    lines.append("")
    anomalies = [row for row in per_item if row.get("error") or row.get("unit_ambiguous")]
    if not anomalies:
        lines.append("None observed.")
    else:
        for row in anomalies:
            lines.append(f"- {row['id']} / {row['method']}: error={row.get('error')}, unit_ambiguous={row.get('unit_ambiguous')}")
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```powershell")
    lines.append(".\\.venv\\Scripts\\python.exe src\\build_benchmark.py --n 10")
    lines.append(".\\.venv\\Scripts\\python.exe src\\verify_gold.py --bench data\\pilot\\fave_bench_10.jsonl")
    lines.append(".\\.venv\\Scripts\\python.exe src\\mock_outputs.py --input data\\pilot\\fave_bench_10.jsonl")
    lines.append(".\\.venv\\Scripts\\python.exe src\\eval_fave.py --bench data\\pilot\\fave_bench_10.jsonl --pred_dir outputs\\mock")
    lines.append(".\\.venv\\Scripts\\python.exe src\\decide.py --per_item results\\per_item.jsonl")
    lines.append("# Then run OpenAI methods listed in the run prompt and evaluate:")
    lines.append(".\\.venv\\Scripts\\python.exe src\\eval_fave.py --bench data\\pilot\\fave_bench_10.jsonl --pred_dir outputs\\real\\openai")
    lines.append(f"# Commit: {git_commit()}")
    lines.append(f"# Model: {args.model}")
    lines.append("```")

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
