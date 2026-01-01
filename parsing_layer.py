# parsing_layer.py
from typing import Dict, Iterable, Any
import re

from lab_config import LAB_NAME_ALIASES


def _get_page_text(page: Any) -> str:

    if isinstance(page, dict):
        return str(page.get("text", ""))
    return str(getattr(page, "text", ""))


def normalize_test_name(raw_name: str) -> str | None:
    raw = raw_name.lower().strip()
    for key, aliases in LAB_NAME_ALIASES.items():
        for alias in aliases:
            if alias in raw:
                return key
    return None


def extract_labs_from_text(ocr_pages: Iterable[Any]) -> Dict[str, float]:
    """
    Takes OCR output pages and extracts many blood test values.

    Returns:
        parsed_labs = {'hemoglobin': 12.5, 'wbc': 7800, 'creatinine': 1.4, ...}
    """
    text_full = "\n".join(_get_page_text(p) for p in ocr_pages).lower()

    parsed_labs: Dict[str, float] = {}

    # Patterns like:
    #   Hemoglobin 13.2 g/dL
    #   WBC - 7800 /µL
    #   Creatinine: 1.4 mg/dL
    number_patterns = [
        r"([a-zA-Z \-/\(\)%\.]+)\s*[:=\-]\s*([0-9]+\.[0-9]+)",
        r"([a-zA-Z \-/\(\)%\.]+)\s*[:=\-]\s*([0-9]+)",
    ]

    for pattern in number_patterns:
        for match in re.finditer(pattern, text_full):
            raw_name = match.group(1).strip()
            raw_value = match.group(2)

            key = normalize_test_name(raw_name)
            if not key:
                continue

            try:
                value = float(raw_value)
            except ValueError:
                continue

            parsed_labs[key] = value

    return parsed_labs
