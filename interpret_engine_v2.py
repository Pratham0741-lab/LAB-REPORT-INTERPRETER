# interpret_engine_v2.py
import re
from difflib import get_close_matches
from typing import Dict, List, Any
from interpretation_config import TEST_ALIASES, TEST_CONFIG
from value_extractor import extract_value_unit


def fuzzy_match_test(line: str) -> str:
    """
    Fuzzy matching to identify test name even if spelled incorrectly
    or appears in long sentences.
    """
    all_aliases = {alias: key for key, vals in TEST_ALIASES.items() for alias in vals}
    words = re.split(r"[^a-zA-Z0-9]+", line.lower())

    candidates = []
    for w in words:
        m = get_close_matches(w, all_aliases.keys(), n=1, cutoff=0.75)
        if m:
            return all_aliases[m[0]]
    return ""


def parse_report_lines(lines: List[str]) -> Dict[str, Any]:
    """
    Advanced multi-line, fuzzy, robust parser for all report types.
    """
    results = {}

    for line in lines:
        line_clean = line.strip()

        # Identify test key
        test_key = fuzzy_match_test(line_clean)
        if not test_key:
            continue

        # Extract value + unit
        value, unit = extract_value_unit(line_clean)
        if value is None:
            continue

        # If missing unit, use default from config
        if not unit:
            unit = TEST_CONFIG[test_key]["unit"]

        # Save result
        results[test_key] = {
            "raw_line": line_clean,
            "value": value,
            "unit": unit
        }

    return results


def interpret_results_advanced(page_texts: List[str]):
    """
    End-to-end interpretation using the upgraded parser.
    """
    # Combine all pages into lines
    lines = []
    for page in page_texts:
        for row in page.split("\n"):
            if row.strip():
                lines.append(row.strip())

    parsed = parse_report_lines(lines)

    # Map every test to severity
    interpreted = []
    group_severity = {}
    rank = {"Normal": 0, "Mild": 1, "Moderate": 2, "Severe": 3}

    for test_key, obj in parsed.items():
        cfg = TEST_CONFIG[test_key]

        low, high = cfg["normal_range"]
        v = obj["value"]

        if low <= v <= high:
            status = "Normal"
            sev = "Normal"
        else:
            status = "High" if v > high else "Low"
            diff = abs(v - (high if v > high else low)) / max(high, low)
            sev = "Mild" if diff < 0.10 else "Moderate" if diff < 0.30 else "Severe"

        interpreted.append({
            "test_key": test_key,
            "test_name": cfg["label"],
            "group": cfg["group"],
            "value": obj["value"],
            "unit": obj["unit"],
            "normal_range": cfg["normal_range"],
            "status": status,
            "severity": sev,
            "comment": cfg["high_msg"] if status == "High" else cfg["low_msg"],
            "raw_line": obj["raw_line"]
        })

        # Group-level severity
        g = cfg["group"]
        prev = group_severity.get(g, "Normal")
        if rank[sev] > rank[prev]:
            group_severity[g] = sev

    # Overall severity
    if interpreted:
        worst = max(rank[t["severity"]] for t in interpreted)
        overall = ["Normal", "Mild", "Moderate", "Severe"][worst]
    else:
        overall = "Unknown"

    return {
        "tests": interpreted,
        "group_severity": group_severity,
        "overall_severity": overall,
        "risk_score": round(worst / 3, 2) if interpreted else 0.0
    }
