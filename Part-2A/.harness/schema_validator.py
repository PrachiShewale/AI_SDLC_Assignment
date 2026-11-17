from __future__ import annotations

from typing import Any

REQUIRED_KEYS = {"intent", "status", "summary", "reminder", "clarification_questions", "safe"}
REQUIRED_REMINDER_KEYS = {"title", "when", "timezone", "recurrence"}
VALID_INTENTS = {"create_reminder", "reschedule", "snooze", "clarify", "reject"}
VALID_STATUSES = {"ready", "needs_clarification", "rejected"}


def validate_schema(output: Any) -> tuple[bool, str | None]:
    if not isinstance(output, dict):
        return False, "Root output is not an object"
    missing = sorted(REQUIRED_KEYS - set(output.keys()))
    if missing:
        return False, f"Missing required keys: {missing}"
    if output["intent"] not in VALID_INTENTS:
        return False, f"Unsupported intent: {output['intent']}"
    if output["status"] not in VALID_STATUSES:
        return False, f"Unsupported status: {output['status']}"
    if not isinstance(output["safe"], bool):
        return False, "safe must be a boolean"
    if not isinstance(output["clarification_questions"], list):
        return False, "clarification_questions must be a list"
    reminder = output["reminder"]
    if not isinstance(reminder, dict):
        return False, "reminder must be an object"
    reminder_missing = sorted(REQUIRED_REMINDER_KEYS - set(reminder.keys()))
    if reminder_missing:
        return False, f"Missing reminder keys: {reminder_missing}"
    if reminder.get("timezone") is None:
        return False, "timezone is required"
    return True, None
