"""Verify FAVE-RAG v0.2 gold and trap computations."""

from __future__ import annotations

import argparse
import math
import re

from scipy.stats import norm

from common.jsonl_utils import read_jsonl


EXPECTED = {
    "fave_0001": (lambda: 10 * math.log2(1 + 100), lambda: 10 * math.log2(1 + 20)),
    "fave_0002": (lambda: 30 / 5, lambda: 30_000_000 / 5),
    "fave_0003": (
        lambda: 20 * math.log10(2) + 20 * math.log10(2400) + 32.44,
        lambda: 20 * math.log10(2) + 20 * math.log10(2.4) + 32.44,
    ),
    "fave_0004": (lambda: 1 / (0.2 + 0.1), lambda: 1 / 0.1),
    "fave_0005": (lambda: 1 - math.exp(-5 / 10), lambda: 5 / 10),
    "fave_0006": (lambda: norm.sf(math.sqrt(2 * 10 ** (9 / 10))), lambda: norm.sf(math.sqrt(2 * 9))),
    "fave_0007": (lambda: 2 * 3000, lambda: 2 * 300),
    "fave_0008": (lambda: 2 * math.log2(1 + 10 / 2), lambda: 2 * math.log2(1 + 10)),
    "fave_0009": (
        lambda: (0.125 / (4 * math.pi * 100)) ** 2,
        lambda: 0.125 / (4 * math.pi * 100),
    ),
    "fave_0010": (lambda: 10 ** (13 / 10), lambda: 10 ** (13 / 20)),
}


def close(a: float, b: float, rel: float = 0.001) -> bool:
    return math.isclose(a, b, rel_tol=rel, abs_tol=rel * max(abs(a), abs(b), 1e-12))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", default="data/pilot/fave_bench_10.jsonl")
    args = parser.parse_args()

    rows = list(read_jsonl(args.bench))
    texts: set[str] = set()
    for item in rows:
        if item.get("schema_version") != "0.2":
            raise AssertionError(f"{item['id']} schema_version is not 0.2")
        if item["id"] not in EXPECTED:
            raise AssertionError(f"No verification function for {item['id']}")

        gold_fn, trap_fn = EXPECTED[item["id"]]
        gold = gold_fn()
        trap = trap_fn()
        if not close(gold, item["gold_value"]):
            raise AssertionError(f"{item['id']} gold mismatch: computed {gold}, stored {item['gold_value']}")

        invalid = item["invalid_evidence"]
        if not invalid:
            raise AssertionError(f"{item['id']} has no invalid evidence")
        if not close(trap, invalid[0]["trap_answer"]):
            raise AssertionError(f"{item['id']} trap mismatch: computed {trap}, stored {invalid[0]['trap_answer']}")

        rel = item["tolerance"].get("rel") or 0.0
        if abs(item["gold_value"] - invalid[0]["trap_answer"]) <= 3 * rel * abs(item["gold_value"]):
            raise AssertionError(f"{item['id']} trap gap is too small")

        for bucket in ["valid_evidence", "invalid_evidence", "contested_evidence"]:
            for ev in item.get(bucket, []):
                if re.fullmatch(r"e\d+_\d+", ev["id"]):
                    raise AssertionError(f"{item['id']} positional evidence id found: {ev['id']}")
                if ev["text"] in texts:
                    raise AssertionError(f"Duplicate evidence text: {ev['text']}")
                old_template = "preserve the " + "same ordering"
                if old_template in ev["text"]:
                    raise AssertionError("Old template phrase still present")
                texts.add(ev["text"])

        for ev in invalid:
            if ev.get("trap_answer") is None:
                raise AssertionError(f"{item['id']} invalid evidence missing trap_answer")
            if not ev.get("valid_in_context"):
                raise AssertionError(f"{item['id']} invalid evidence missing valid_in_context")

    print(f"Verified {len(rows)} v0.2 benchmark items")


if __name__ == "__main__":
    main()
