import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".harness"))

from quality_eval import evaluate_quality
from schema_validator import validate_schema


def test_schema_requires_timezone_on_timestamps():
    output = {
        "intent": "create_reminder",
        "status": "ready",
        "summary": "Reminder created.",
        "reminder": {
            "title": "buy milk",
            "when": "2026-11-21T09:00:00",
            "timezone": "UTC",
            "recurrence": None,
        },
        "clarification_questions": [],
        "safe": True,
    }

    valid, error = validate_schema(output)

    assert not valid
    assert error == "reminder.when must include a timezone"


def test_quality_rubric_detects_wrong_reminder_title():
    case = {
        "expected_intent": "create_reminder",
        "expected_status": "ready",
        "expected_title_terms": ["pay", "rent"],
        "expected_safe": True,
    }
    output = {
        "intent": "create_reminder",
        "status": "ready",
        "safe": True,
        "reminder": {"title": "buy groceries"},
    }

    score, errors = evaluate_quality(output, case)

    assert score == 0.75
    assert any("source-grounded terms" in error for error in errors)
