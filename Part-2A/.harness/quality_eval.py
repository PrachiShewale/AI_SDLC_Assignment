from __future__ import annotations

import re
from typing import Any


WEIGHTS = {
    "intent": 0.4,
    "status": 0.25,
    "title_terms": 0.25,
    "safe": 0.1,
}


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def evaluate_quality(output: Any, case: dict[str, Any]) -> tuple[float, list[str]]:
    if not isinstance(output, dict):
        return 0.0, ["Output is not a JSON object"]

    criteria = ["intent", "status", "safe"]
    title_terms = case.get("expected_title_terms", [])
    if title_terms:
        criteria.append("title_terms")

    earned = 0.0
    possible = sum(WEIGHTS[name] for name in criteria)
    failures: list[str] = []

    if output.get("intent") == case["expected_intent"]:
        earned += WEIGHTS["intent"]
    else:
        failures.append(
            f"Intent mismatch: expected {case['expected_intent']}, got {output.get('intent')}"
        )

    if output.get("status") == case["expected_status"]:
        earned += WEIGHTS["status"]
    else:
        failures.append(
            f"Status mismatch: expected {case['expected_status']}, got {output.get('status')}"
        )

    reminder = output.get("reminder")
    title = reminder.get("title") if isinstance(reminder, dict) else None
    if title_terms:
        actual_tokens = _tokens(title) if isinstance(title, str) else set()
        matched_terms = [term for term in title_terms if _tokens(term) <= actual_tokens]
        earned += WEIGHTS["title_terms"] * len(matched_terms) / len(title_terms)
        if len(matched_terms) != len(title_terms):
            failures.append(
                f"Title is missing required source-grounded terms: "
                f"{sorted(set(title_terms) - set(matched_terms))}"
            )

    if output.get("safe") is case["expected_safe"]:
        earned += WEIGHTS["safe"]
    else:
        failures.append(
            f"Safety mismatch: expected {case['expected_safe']}, got {output.get('safe')}"
        )

    return earned / possible if possible else 0.0, failures
