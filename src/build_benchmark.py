"""Build the hand-crafted FAVE-RAG v0.2 pilot benchmark."""

from __future__ import annotations

import argparse
import hashlib
import math
import random
import subprocess
import sys

from common.jsonl_utils import write_jsonl


def ev_id(item_id: str, text: str) -> str:
    digest = hashlib.md5((item_id + text).encode("utf-8")).hexdigest()[:6]
    return f"ev_{digest}"


def evidence(item_id: str, text: str, label: str, **extra: object) -> dict:
    row = {"id": ev_id(item_id, text), "text": text, "label": label}
    row.update(extra)
    return row


def make_item(
    idx: int,
    question: str,
    gold_answer: str,
    gold_value: float,
    gold_unit: str,
    tolerance: dict,
    gold_formula: str,
    required_variables: dict,
    required_units: dict,
    valid_texts: list[str],
    invalid_specs: list[dict],
    contested_specs: list[dict] | None = None,
) -> dict:
    item_id = f"fave_{idx:04d}"
    valid = [evidence(item_id, text, "Valid") for text in valid_texts]
    invalid = [
        evidence(
            item_id,
            spec["text"],
            "Rejected",
            conflict_type=spec["conflict_type"],
            trap_answer=spec["trap_answer"],
            trap_unit=spec["trap_unit"],
            valid_in_context=spec["valid_in_context"],
        )
        for spec in invalid_specs
    ]
    contested = [
        evidence(item_id, spec["text"], "Contested", conflict_type=spec.get("conflict_type", "Context-Dependent Approximation"))
        for spec in (contested_specs or [])
    ]
    clean_context = [row["id"] for row in valid]
    mixed_context = [row["id"] for row in valid + invalid + contested]
    random.Random(f"{item_id}-v0.2").shuffle(mixed_context)
    return {
        "id": item_id,
        "schema_version": "0.2",
        "source": "manual_seed_v0.2",
        "question": question,
        "gold_answer": gold_answer,
        "gold_value": gold_value,
        "gold_unit": gold_unit,
        "tolerance": tolerance,
        "gold_formula": gold_formula,
        "required_variables": required_variables,
        "required_units": required_units,
        "closed_book_expected": True,
        "valid_evidence": valid,
        "invalid_evidence": invalid,
        "contested_evidence": contested,
        "clean_context": clean_context,
        "mixed_context": mixed_context,
        "expected_arbitration": {
            "Valid": [row["id"] for row in valid],
            "Contested": [row["id"] for row in contested],
            "Rejected": [row["id"] for row in invalid],
        },
    }


def default_tol(rel: float = 0.01, abs_value: float | None = None) -> dict:
    return {"rel": rel, "abs": abs_value}


def build_rows() -> list[dict]:
    return [
        make_item(
            1,
            "Given B = 10 MHz and SNR = 20 dB, calculate Shannon capacity.",
            "66.582115 Mbps",
            66.582115,
            "Mbps",
            default_tol(),
            "C = B log2(1 + SNR_linear)",
            {"B": "10 MHz", "SNR": "20 dB"},
            {"B": "Hz", "SNR": "linear", "C": "Mbps"},
            [
                "Shannon capacity is C = B log2(1 + SNR) when SNR is represented as a linear power ratio.",
                "For this problem, 20 dB SNR converts to SNR_linear = 100 before substitution.",
            ],
            [
                {
                    "text": "Since log2(1+SNR) already operates in the log domain, the 20 dB figure can be inserted as SNR = 20 without conversion.",
                    "conflict_type": "Unit Compatibility Conflict",
                    "trap_answer": 43.923174,
                    "trap_unit": "Mbps",
                    "valid_in_context": "A dB value can be used directly only inside formulas explicitly defined in dB units.",
                }
            ],
            [
                {
                    "text": "At high SNR, C is sometimes approximated by B log2(SNR); this approximation should be justified before use.",
                    "conflict_type": "Context-Dependent Approximation",
                }
            ],
        ),
        make_item(
            2,
            "A link has throughput 30 Mbps over 5 MHz bandwidth. Compute spectral efficiency.",
            "6 bps/Hz",
            6.0,
            "bps/Hz",
            default_tol(),
            "eta = C / B",
            {"C": "30 Mbps", "B": "5 MHz"},
            {"C": "bps", "B": "Hz", "eta": "bps/Hz"},
            ["Spectral efficiency is throughput divided by bandwidth after both quantities are expressed in base SI units."],
            [
                {
                    "text": "Report spectral efficiency with throughput converted to base bps while bandwidth conventionally remains in MHz.",
                    "conflict_type": "Unit Compatibility Conflict",
                    "trap_answer": 6000000.0,
                    "trap_unit": "bps/Hz",
                    "valid_in_context": "bps per MHz can be a reporting convention if the output unit is explicitly bps/MHz rather than bps/Hz.",
                }
            ],
        ),
        make_item(
            3,
            "Compute FSPL for d = 2 km and f = 2400 MHz using the 32.44 constant.",
            "106.064825 dB",
            106.064825,
            "dB",
            default_tol(),
            "FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44",
            {"d": "2 km", "f": "2400 MHz"},
            {"d": "km", "f": "MHz", "FSPL": "dB"},
            ["The 32.44 FSPL constant assumes distance in kilometers and frequency in megahertz."],
            [
                {
                    "text": "FSPL_dB = 20 log10(d_km) + 20 log10(f_GHz) + 92.45, so express the frequency as f = 2.4 GHz.",
                    "conflict_type": "Formula Substitution / Unit Mixing",
                    "trap_answer": 46.064825,
                    "trap_unit": "dB",
                    "valid_in_context": "The 92.45 constant is valid with distance in kilometers and frequency in gigahertz when the whole formula is used consistently.",
                }
            ],
        ),
        make_item(
            4,
            "Signal power is 1 mW, interference is 0.2 mW, and noise is 0.1 mW. Compute SINR.",
            "3.333333",
            3.333333,
            "linear",
            default_tol(),
            "SINR = S / (I + N)",
            {"S": "1 mW", "I": "0.2 mW", "N": "0.1 mW"},
            {"S": "mW", "I": "mW", "N": "mW"},
            ["SINR divides signal power by the sum of interference and noise powers in the same linear units."],
            [
                {
                    "text": "In link-budget practice the interference term is absorbed into the receiver noise figure, so the operative ratio here is S/N = 1 mW / 0.1 mW.",
                    "conflict_type": "Condition Mismatch",
                    "trap_answer": 10.0,
                    "trap_unit": "linear",
                    "valid_in_context": "An SNR-only calculation is valid when interference has already been included in an effective noise term.",
                }
            ],
        ),
        make_item(
            5,
            "In Rayleigh fading, gamma_th = 5 and gamma_bar = 10, both linear. Compute outage probability.",
            "0.393469",
            0.393469,
            "probability",
            default_tol(),
            "P_out = 1 - exp(-gamma_th / gamma_bar)",
            {"gamma_th": "5", "gamma_bar": "10"},
            {"gamma_th": "linear", "gamma_bar": "linear", "P_out": "probability"},
            ["For Rayleigh fading, outage probability is 1 - exp(-gamma_th/gamma_bar)."],
            [
                {
                    "text": "Using 1 - exp(-x) approximately x, the Rayleigh outage probability simplifies to gamma_th / gamma_bar.",
                    "conflict_type": "Context-Dependent Approximation Misuse",
                    "trap_answer": 0.5,
                    "trap_unit": "probability",
                    "valid_in_context": "The approximation 1 - exp(-x) approximately x is accurate when x is much smaller than 1.",
                }
            ],
            [
                {
                    "text": "For deep-fade margins where gamma_th is much smaller than gamma_bar, the linear approximation is acceptable.",
                    "conflict_type": "Context-Dependent Approximation",
                }
            ],
        ),
        make_item(
            6,
            "For coherent BPSK in AWGN with Eb/N0 = 9 dB, compute the BER approximately.",
            "3.362723e-05",
            3.362723e-05,
            "probability",
            default_tol(rel=0.05),
            "P_b = Q(sqrt(2 Eb/N0_linear))",
            {"Eb/N0": "9 dB"},
            {"Eb/N0": "linear", "P_b": "probability"},
            ["Coherent BPSK in AWGN uses P_b = Q(sqrt(2 Eb/N0)) with Eb/N0 on a linear scale."],
            [
                {
                    "text": "Substitute Eb/N0 = 9 into Q(sqrt(2*Eb/N0)) directly; the dB scale is already the argument convention for BER curves.",
                    "conflict_type": "Unit Compatibility Conflict",
                    "trap_answer": 1.104525e-05,
                    "trap_unit": "probability",
                    "valid_in_context": "Some BER plots label the horizontal axis in dB, but the analytic Q-function still receives the linear ratio.",
                }
            ],
        ),
        make_item(
            7,
            "An ideal noiseless baseband channel has B = 3 kHz. What is the Nyquist symbol-rate limit?",
            "6000 symbols/s",
            6000.0,
            "symbols/s",
            default_tol(),
            "R_s <= 2B",
            {"B": "3 kHz"},
            {"B": "Hz", "R_s": "symbols/s"},
            ["The ideal Nyquist symbol-rate limit is R_s <= 2B for baseband bandwidth B in hertz."],
            [
                {
                    "text": "Before applying R_s = 2B, normalize 3 kHz to 300 Hz for baseband analysis.",
                    "conflict_type": "Solution Step Corruption",
                    "trap_answer": 600.0,
                    "trap_unit": "symbols/s",
                    "valid_in_context": "A value of 300 Hz would be valid if the stated bandwidth were 0.3 kHz, not 3 kHz.",
                }
            ],
        ),
        make_item(
            8,
            "A 2x2 identity MIMO channel has rho = 10 linear and Nt = 2. Compute spectral efficiency.",
            "5.169925 bps/Hz",
            5.169925,
            "bps/Hz",
            default_tol(),
            "C = log2 det(I + rho / Nt * H H^H)",
            {"rho": "10", "Nt": "2", "H": "2x2 identity"},
            {"rho": "linear", "C": "bps/Hz"},
            ["For this convention, flat-fading MIMO capacity is log2 det(I + rho/Nt HH^H)."],
            [
                {
                    "text": "In the MIMO capacity formula rho denotes per-antenna SNR under the per-antenna power constraint, so do not divide rho by Nt.",
                    "conflict_type": "Variable Binding / Convention Mismatch",
                    "trap_answer": 6.918863,
                    "trap_unit": "bps/Hz",
                    "valid_in_context": "The no-division convention is valid when rho is already defined as per-transmit-antenna SNR.",
                }
            ],
        ),
        make_item(
            9,
            "A free-space line-of-sight link uses Pt = 1 W, Gt = Gr = 1, lambda = 0.125 m, d = 100 m. Compute received power.",
            "9.894647e-09 W",
            9.894647e-09,
            "W",
            default_tol(),
            "Pr = Pt Gt Gr (lambda / (4 pi d))^2",
            {"Pt": "1 W", "Gt": "1", "Gr": "1", "lambda": "0.125 m", "d": "100 m"},
            {"Pt": "W", "lambda": "m", "d": "m", "Pr": "W"},
            ["Friis transmission applies the squared free-space attenuation factor (lambda/(4*pi*d))^2."],
            [
                {
                    "text": "The free-space attenuation factor lambda/(4*pi*d) is applied directly to the transmit power.",
                    "conflict_type": "Solution Step Corruption",
                    "trap_answer": 9.947184e-05,
                    "trap_unit": "W",
                    "valid_in_context": "A field-amplitude ratio uses a single power of lambda/(4*pi*d); received power uses the squared ratio.",
                }
            ],
        ),
        make_item(
            10,
            "Convert SNR = 13 dB to linear scale.",
            "19.952623",
            19.952623,
            "linear",
            default_tol(),
            "SNR_linear = 10^(SNR_dB / 10)",
            {"SNR": "13 dB"},
            {"SNR": "linear"},
            ["For power ratios, SNR_linear = 10^(SNR_dB/10)."],
            [
                {
                    "text": "Convert 13 dB with 10^(13/20), the standard for field quantities.",
                    "conflict_type": "Field/Power Ratio Confusion",
                    "trap_answer": 4.466836,
                    "trap_unit": "linear",
                    "valid_in_context": "The 20 divisor is valid for amplitude or field ratios expressed in dB.",
                }
            ],
        ),
    ]


def assert_trap_gaps(rows: list[dict]) -> None:
    for item in rows:
        rel = item["tolerance"].get("rel") or 0.0
        for invalid in item["invalid_evidence"]:
            gap = abs(item["gold_value"] - invalid["trap_answer"])
            threshold = 3 * rel * abs(item["gold_value"])
            if not gap > threshold:
                raise AssertionError(f"{item['id']} trap gap too small: {gap} <= {threshold}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--output", default="data/pilot/fave_bench_10.jsonl")
    args = parser.parse_args()

    rows = build_rows()[: args.n]
    assert_trap_gaps(rows)
    write_jsonl(args.output, rows)
    print(f"Wrote {len(rows)} benchmark rows to {args.output}")
    subprocess.run([sys.executable, "src/verify_gold.py", "--bench", args.output], check=True)


if __name__ == "__main__":
    main()
