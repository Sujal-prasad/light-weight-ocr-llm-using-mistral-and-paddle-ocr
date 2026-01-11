import re

KNOWN_TESTS = {
    "Hemoglobin": "g/dL",
    "Creatinine": "mg/dL",
    "Urea": "mg/dL",
    "WBC": "cells/cumm",
    "Platelet Count": "lakhs/cumm"
}

def parse_reference_range(range_text):
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", range_text)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def classify_status(value, low, high):
    if low is None or high is None:
        return "UNKNOWN"
    if value < low:
        return "LOW"
    elif value > high:
        return "HIGH"
    return "NORMAL"


def extract_tests(text):
    results = []

    for test_name, unit in KNOWN_TESTS.items():
        pattern = rf"{test_name}\s+(\d+\.?\d*)\s*({unit})?\s*.*?(\d+\.?\d*\s*-\s*\d+\.?\d*)"
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        value = float(match.group(1))
        ref_range = match.group(3)
        low, high = parse_reference_range(ref_range)
        status = classify_status(value, low, high)

        results.append({
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": ref_range,
            "status": status
        })

    return results
