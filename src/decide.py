"""Apply pre-registered FAVE-RAG v0.2 decision criteria."""

from __future__ import annotations

import argparse
from collections import defaultdict

from common.jsonl_utils import read_jsonl
from common.metrics import precision_recall_f1


def rate(rows: list[dict], field: str) -> float:
    return sum(bool(row.get(field)) for row in rows) / len(rows) if rows else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per_item", default="results/per_item.jsonl")
    args = parser.parse_args()

    rows = list(read_jsonl(args.per_item))
    by_method: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)

    vanilla = by_method.get("Vanilla RAG Mixed", [])
    fave = by_method.get("FAVE-RAG Mixed Soft") or by_method.get("FAVE-RAG Mixed", [])
    vanilla_poison = rate(vanilla, "trap_hit")
    fave_poison = rate(fave, "trap_hit")

    tp = fp = fn = 0
    for row in fave:
        predicted = row.get("predicted_arbitration", {}) or {}
        gold = set(row.get("expected_rejected_ids", []))
        pred = {eid for eid, label in predicted.items() if label == "Rejected"}
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)
    prf = precision_recall_f1(tp, fp, fn)

    h1 = vanilla_poison >= 0.30
    h1_weak = vanilla_poison < 0.15
    h2_eval = h1
    h2 = fave_poison <= 0.5 * vanilla_poison if h2_eval else False
    h3 = prf["f1"] >= 0.80

    print("VERDICT BLOCK")
    print(f"H1 {'PASS' if h1 else 'FAIL'}: Vanilla trap_hit {sum(r.get('trap_hit') for r in vanilla)}/{len(vanilla)} = {vanilla_poison:.3f} (threshold >= 0.30)")
    if h1_weak:
        print('H1 verdict detail: PROBLEM_WEAK because poisoning_rate < 0.15')
    print(f"H2 {'PASS' if h2 else ('FAIL' if h2_eval else 'NOT-EVALUATED')}: FAVE trap_hit {sum(r.get('trap_hit') for r in fave)}/{len(fave)} = {fave_poison:.3f}; required <= 0.5 * Vanilla ({0.5 * vanilla_poison:.3f})")
    print(f"H3 {'PASS' if h3 else 'FAIL'}: FAVE rejected-class F1 = {prf['f1']:.3f} with TP={tp}, FP={fp}, FN={fn} (threshold >= 0.80)")


if __name__ == "__main__":
    main()
