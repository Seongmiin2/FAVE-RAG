"""Build the hand-crafted FAVE-RAG v0.1 pilot benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

from common.jsonl_utils import write_jsonl
from generate_invalid_evidence import (
    condition_mismatch,
    contested_evidence,
    formula_substitution,
    physical_constraint_violation,
    solution_step_corruption,
    unit_compatibility,
    variable_binding,
)


def evidence(eid: str, text: str, label: str, conflict_type: str | None = None) -> dict:
    row = {"id": eid, "text": text, "label": label}
    if conflict_type:
        row["conflict_type"] = conflict_type
    return row


def make_item(
    idx: int,
    question: str,
    gold_answer: str,
    gold_formula: str,
    required_variables: dict,
    required_units: dict,
    valid_texts: list[str],
    invalid_rows: list[dict],
    contested_rows: list[dict] | None = None,
) -> dict:
    valid = [evidence(f"e{idx}_{i+1}", text, "Valid") for i, text in enumerate(valid_texts)]
    offset = len(valid) + 1
    invalid = [
        evidence(f"e{idx}_{offset+i}", row["text"], row["label"], row.get("conflict_type"))
        for i, row in enumerate(invalid_rows)
    ]
    contested = [
        evidence(
            f"e{idx}_{offset+len(invalid)+i}",
            row["text"],
            row["label"],
            row.get("conflict_type"),
        )
        for i, row in enumerate(contested_rows or [], start=1)
    ]
    all_evidence = valid + invalid + contested
    return {
        "id": f"fave_{idx:04d}",
        "source": "manual_seed_v0.1",
        "question": question,
        "gold_answer": gold_answer,
        "gold_formula": gold_formula,
        "required_variables": required_variables,
        "required_units": required_units,
        "valid_evidence": valid,
        "invalid_evidence": invalid,
        "contested_evidence": contested,
        "clean_context": [row["id"] for row in valid],
        "mixed_context": [row["id"] for row in all_evidence],
        "expected_arbitration": {
            "Valid": [row["id"] for row in valid],
            "Contested": [row["id"] for row in contested],
            "Rejected": [row["id"] for row in invalid],
        },
    }


def build_rows() -> list[dict]:
    return [
        make_item(
            1,
            "Given B = 10 MHz and SNR = 20 dB, calculate Shannon capacity.",
            "66.58 Mbps",
            "C = B log2(1 + SNR_linear)",
            {"B": "10 MHz", "SNR": "20 dB"},
            {"B": "Hz", "SNR": "linear", "C": "bps"},
            [
                "Shannon capacity is C = B log2(1 + SNR) when SNR is linear.",
                "20 dB SNR must be converted to SNR_linear = 100 before substitution.",
            ],
            [unit_compatibility("SNR in dB")],
            [contested_evidence("At high SNR, C is sometimes approximated by B log2(SNR); this approximation should be justified before use.")],
        ),
        make_item(
            2,
            "A link has throughput 30 Mbps over 5 MHz bandwidth. Compute spectral efficiency.",
            "6 bps/Hz",
            "eta = C / B",
            {"C": "30 Mbps", "B": "5 MHz"},
            {"C": "bps", "B": "Hz", "eta": "bps/Hz"},
            ["Spectral efficiency is throughput divided by bandwidth using consistent units."],
            [variable_binding("B", "bits per modulation symbol rather than bandwidth")],
        ),
        make_item(
            3,
            "Compute FSPL for d = 2 km and f = 2400 MHz using the 32.44 constant.",
            "106.07 dB",
            "FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44",
            {"d": "2 km", "f": "2400 MHz"},
            {"d": "km", "f": "MHz", "FSPL": "dB"},
            ["The 32.44 FSPL constant assumes distance in km and frequency in MHz."],
            [unit_compatibility("distance in km and frequency in MHz")],
        ),
        make_item(
            4,
            "Signal power is 1 mW, interference is 0.2 mW, and noise is 0.1 mW. Compute SINR.",
            "3.33",
            "SINR = S / (I + N)",
            {"S": "1 mW", "I": "0.2 mW", "N": "0.1 mW"},
            {"S": "linear power", "I": "linear power", "N": "linear power"},
            ["SINR is signal power divided by interference plus noise power in the same linear units."],
            [formula_substitution("SINR")],
        ),
        make_item(
            5,
            "In Rayleigh fading, gamma_th = 5 and gamma_bar = 10, both linear. Compute outage probability.",
            "0.3935",
            "P_out = 1 - exp(-gamma_th / gamma_bar)",
            {"gamma_th": "5", "gamma_bar": "10"},
            {"gamma_th": "linear", "gamma_bar": "linear", "P_out": "probability"},
            ["For Rayleigh fading, outage probability is 1 - exp(-gamma_th/gamma_bar)."],
            [physical_constraint_violation("The resulting outage probability may exceed 1 when threshold SNR is high.")],
        ),
        make_item(
            6,
            "For coherent BPSK in AWGN with Eb/N0 = 9 dB, compute the BER approximately.",
            "3.36e-5",
            "P_b = Q(sqrt(2 Eb/N0_linear))",
            {"Eb/N0": "9 dB"},
            {"Eb/N0": "linear", "P_b": "probability"},
            ["Coherent BPSK in AWGN uses P_b = Q(sqrt(2 Eb/N0)) with linear Eb/N0."],
            [unit_compatibility("Eb/N0 in dB")],
        ),
        make_item(
            7,
            "An ideal noiseless baseband channel has B = 3 kHz. What is the Nyquist symbol-rate limit?",
            "6000 symbols/s",
            "R_s <= 2B",
            {"B": "3 kHz"},
            {"B": "Hz", "R_s": "symbols/s"},
            ["The ideal Nyquist symbol-rate limit is R_s <= 2B for baseband bandwidth B."],
            [solution_step_corruption("3 kHz should be converted to 300 Hz before applying R_s = 2B.")],
        ),
        make_item(
            8,
            "A 2x2 identity MIMO channel has rho = 10 linear and Nt = 2. Compute spectral efficiency.",
            "5.17 bps/Hz",
            "C = log2 det(I + rho / Nt * H H^H)",
            {"rho": "10", "Nt": "2", "H": "2x2 identity"},
            {"rho": "linear", "C": "bps/Hz"},
            ["For flat-fading MIMO, C = log2 det(I + rho/Nt HH^H)."],
            [variable_binding("Nt", "the number of receive antennas only")],
        ),
        make_item(
            9,
            "A free-space line-of-sight link uses Pt = 1 W, Gt = Gr = 1, lambda = 0.125 m, d = 100 m. Compute received power.",
            "9.89e-9 W",
            "Pr = Pt Gt Gr (lambda / (4 pi d))^2",
            {"Pt": "1 W", "Gt": "1", "Gr": "1", "lambda": "0.125 m", "d": "100 m"},
            {"Pt": "W", "lambda": "m", "d": "m", "Pr": "W"},
            ["Friis transmission applies to free-space line-of-sight far-field links."],
            [condition_mismatch("the link is strongly obstructed and not line-of-sight")],
        ),
        make_item(
            10,
            "Convert SNR = 13 dB to linear scale.",
            "19.95",
            "SNR_linear = 10^(SNR_dB / 10)",
            {"SNR": "13 dB"},
            {"SNR": "linear"},
            ["For power ratios, SNR_linear = 10^(SNR_dB/10)."],
            [solution_step_corruption("13 dB should be converted with 10^(13/20) because SNR is a power ratio.")],
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--output", default="data/pilot/fave_bench_10.jsonl")
    args = parser.parse_args()

    rows = build_rows()[: args.n]
    write_jsonl(args.output, rows)
    print(f"Wrote {len(rows)} benchmark rows to {args.output}")


if __name__ == "__main__":
    main()
