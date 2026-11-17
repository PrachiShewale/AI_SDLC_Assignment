from __future__ import annotations

from typing import Any


def evaluate_quality(output: dict[str, Any], expected_intent: str, expected_status: str) -> tuple[float, str | None]:
    score = 0.0
    if output.get("intent") == expected_intent:
        score += 0.5
    else:
        return 0.0, f"Intent mismatch: expected {expected_intent}, got {output.get('intent')}"

    if output.get("status") == expected_status:
        score += 0.5
    else:
        return 0.0, f"Status mismatch: expected {expected_status}, got {output.get('status')}"

    return score, None
