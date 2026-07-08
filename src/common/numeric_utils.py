"""Numeric parsing and tolerant answer comparison."""

from __future__ import annotations

import math
import re
from typing import Optional


NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def extract_first_number(text: object) -> Optional[float]:
    if text is None:
        return None
    match = NUMBER_RE.search(str(text).replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def is_close(pred: object, gold: object, rel_tol: float = 0.03, abs_tol: float = 1e-3) -> bool:
    pred_num = extract_first_number(pred)
    gold_num = extract_first_number(gold)
    if pred_num is None or gold_num is None:
        return False
    return math.isclose(pred_num, gold_num, rel_tol=rel_tol, abs_tol=abs_tol)
