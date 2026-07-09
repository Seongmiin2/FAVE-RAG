"""Numeric parsing for final-answer fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


SCI_RE = re.compile(
    r"([-+]?\d+(?:\.\d+)?)\s*(?:\\times|×|x|\*)\s*10\s*\^?\s*\{?([-+]?\d+)\}?",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?")
UNIT_RE = re.compile(r"(bps/Hz|symbols/s|Mbps|kbps|Gbps|bps|GHz|MHz|kHz|Hz|dBm|dB|mW|uW|µW|nW|pW|W|probability|linear)\b", re.IGNORECASE)


@dataclass
class ParsedAnswer:
    value: Optional[float]
    unit: Optional[str]
    raw: str


def _normalize_text(text: object) -> str:
    return "" if text is None else str(text).replace(",", "")


def parse_number(text: object) -> Optional[float]:
    raw = _normalize_text(text)
    sci_matches = list(SCI_RE.finditer(raw))
    if sci_matches:
        match = sci_matches[-1]
        return float(match.group(1)) * (10 ** int(match.group(2)))
    matches = list(NUMBER_RE.finditer(raw))
    if not matches:
        return None
    return float(matches[-1].group(0))


def parse_final_answer(text: object) -> ParsedAnswer:
    raw = _normalize_text(text)
    unit_matches = list(UNIT_RE.finditer(raw))
    unit = unit_matches[-1].group(1) if unit_matches else None
    return ParsedAnswer(value=parse_number(raw), unit=unit, raw=raw)


def extract_first_number(text: object) -> Optional[float]:
    raw = _normalize_text(text)
    match = NUMBER_RE.search(raw)
    return float(match.group(0)) if match else None


def extract_numbers(text: object) -> list[float]:
    raw = _normalize_text(text)
    return [float(match.group(0)) for match in NUMBER_RE.finditer(raw)]
