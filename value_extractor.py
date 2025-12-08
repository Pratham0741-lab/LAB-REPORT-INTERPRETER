# value_extractor.py
import re
from typing import Optional, Tuple

VALUE_PATTERNS = [
    r"(-?\d+\.\d+)",          # decimals
    r"(-?\d+)",               # integers
]

UNIT_PATTERNS = [
    r"(mg/dl)", r"(mmol/l)", r"(g/dl)", r"(iu/l)", r"(u/l)", r"(μiu/ml)",
    r"(10\^9/l)", r"(10\^3/µl)", r"(%|ng/ml|pg|fl|µg/l)"
]

def extract_value_unit(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Extracts both numeric value and unit from ANY messy text string.
    """
    value = None
    unit = None

    # Find value
    for vp in VALUE_PATTERNS:
        match = re.search(vp, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                break
            except:
                continue

    # Find unit
    for up in UNIT_PATTERNS:
        um = re.search(up, text, re.IGNORECASE)
        if um:
            unit = um.group(1)
            break

    return value, unit
