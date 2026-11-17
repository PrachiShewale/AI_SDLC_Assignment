from __future__ import annotations

from typing import Any


def evaluate_properties(output: dict[str, Any]) -> tuple[bool, str | None]:
    intent = output.get("intent")
    status = output.get("status")
    reminder = output.get("reminder", {})

    if intent == "clarify" and status != "needs_clarification":
        return False, "clarify intent must use needs_clarification status"
    if intent == "reject" and status != "rejected":
        return False, "reject intent must use rejected status"
    if status == "needs_clarification":
        if not isinstance(output.get("clarification_questions"), list) or not output["clarification_questions"]:
            return False, "Clarification responses require at least one question"
        if reminder.get("when") is not None:
            return False, "Clarification should not include a finalized timestamp"
    if status == "ready" and intent in {"create_reminder", "reschedule", "snooze"}:
        if not reminder.get("title"):
            return False, "Ready reminders require a non-empty title"
        if reminder.get("when") is None:
            return False, "Ready reminders require a timestamp"
    return True, None
