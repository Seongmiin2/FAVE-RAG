"""Small unit normalization helpers for the v0.2 evaluator."""

from __future__ import annotations

import math
from typing import Optional


POWER_UNITS = {"W": 1.0, "mW": 1e-3, "uW": 1e-6, "µW": 1e-6, "nW": 1e-9, "pW": 1e-12}
RATE_UNITS = {"bps": 1.0, "kbps": 1e3, "Mbps": 1e6, "Gbps": 1e9}
FREQ_UNITS = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
SYMBOL_UNITS = {"symbols/s": 1.0}
DIRECT_UNITS = {"bps/Hz", "dB", "linear", "probability"}


def canonical_unit(unit: Optional[str]) -> Optional[str]:
    if not unit:
        return None
    aliases = {"mw": "mW", "uw": "uW", "µw": "µW", "nw": "nW", "pw": "pW", "dbm": "dBm", "db": "dB"}
    return aliases.get(unit, aliases.get(unit.lower(), unit))


def convert_value(value: float, from_unit: Optional[str], gold_unit: str) -> tuple[Optional[float], bool]:
    """Return (value in gold unit, unit_ambiguous)."""
    from_unit = canonical_unit(from_unit)
    gold_unit = canonical_unit(gold_unit) or gold_unit
    if from_unit is None:
        return value, True
    if from_unit == gold_unit:
        return value, False
    if gold_unit in DIRECT_UNITS and from_unit in DIRECT_UNITS:
        return value, False
    if gold_unit in POWER_UNITS:
        if from_unit in POWER_UNITS:
            return value * POWER_UNITS[from_unit] / POWER_UNITS[gold_unit], False
        if from_unit == "dBm":
            watts = 10 ** ((value - 30) / 10)
            return watts / POWER_UNITS[gold_unit], False
    if gold_unit in RATE_UNITS and from_unit in RATE_UNITS:
        return value * RATE_UNITS[from_unit] / RATE_UNITS[gold_unit], False
    if gold_unit in FREQ_UNITS and from_unit in FREQ_UNITS:
        return value * FREQ_UNITS[from_unit] / FREQ_UNITS[gold_unit], False
    if gold_unit in SYMBOL_UNITS and from_unit in SYMBOL_UNITS:
        return value, False
    return None, False


def close_to(value: Optional[float], target: float, tolerance: dict) -> bool:
    if value is None:
        return False
    rel = tolerance.get("rel") or 0.0
    abs_tol = tolerance.get("abs")
    if abs_tol is None:
        abs_tol = rel * max(abs(target), 1e-12)
    return math.isclose(value, target, rel_tol=rel, abs_tol=abs_tol)
