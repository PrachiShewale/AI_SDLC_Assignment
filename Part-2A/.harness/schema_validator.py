from __future__ import annotations

from datetime import datetime
from typing import Any

REQUIRED_KEYS = {"intent", "status", "summary", "reminder", "clarification_questions", "safe"}
REQUIRED_REMINDER_KEYS = {"title", "when", "timezone", "recurrence"}
VALID_INTENTS = {"create_reminder", "reschedule", "snooze", "clarify", "reject"}
VALID_STATUSES = {"ready", "needs_clarification", "rejected"}


def validate_schema(output: Any) -> tuple[bool, str | None]:
    if not isinstance(output, dict):
        return False, "Root output is not an object"
    if set(output) != REQUIRED_KEYS:
        return False, f"Output keys must be exactly {sorted(REQUIRED_KEYS)}"
    if not isinstance(output["intent"], str) or output["intent"] not in VALID_INTENTS:
        return False, f"Unsupported intent: {output['intent']}"
    if not isinstance(output["status"], str) or output["status"] not in VALID_STATUSES:
        return False, f"Unsupported status: {output['status']}"
    if not isinstance(output["summary"], str) or not output["summary"].strip():
        return False, "summary must be a non-empty string"
    if not isinstance(output["safe"], bool):
        return False, "safe must be a boolean"
    questions = output["clarification_questions"]
    if not isinstance(questions, list) or not all(
        isinstance(question, str) and question.strip() for question in questions
    ):
        return False, "clarification_questions must be a list of non-empty strings"
    reminder = output["reminder"]
    if not isinstance(reminder, dict):
        return False, "reminder must be an object"
    if set(reminder) != REQUIRED_REMINDER_KEYS:
        return False, f"Reminder keys must be exactly {sorted(REQUIRED_REMINDER_KEYS)}"
    title = reminder["title"]
    if title is not None and (not isinstance(title, str) or not title.strip()):
        return False, "reminder.title must be null or a non-empty string"
    timestamp = reminder["when"]
    if timestamp is not None:
        if not isinstance(timestamp, str):
            return False, "reminder.when must be null or an ISO 8601 string"
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return False, "reminder.when must be an ISO 8601 string"
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return False, "reminder.when must include a timezone"
    if not isinstance(reminder["timezone"], str) or not reminder["timezone"].strip():
        return False, "reminder.timezone must be a non-empty string"
    if reminder["recurrence"] is not None and not isinstance(reminder["recurrence"], str):
        return False, "reminder.recurrence must be null or a string"
    return True, None
