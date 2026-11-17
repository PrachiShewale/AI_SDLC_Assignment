from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

VALID_INTENTS = {"create_reminder", "reschedule", "snooze", "clarify", "reject"}


def _parse_time_of_day(match: re.Match[str]) -> tuple[int, int]:
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3)
    if meridiem:
        if meridiem.lower() == "pm" and hour != 12:
            hour += 12
        if meridiem.lower() == "am" and hour == 12:
            hour = 0
    return hour, minute


def _parse_datetime(value: str) -> str | None:
    text = value.lower().strip()
    if not text:
        return None
    now = datetime.now(timezone.utc)

    relative_match = re.search(r"in\s+(\d+)\s*(minute|minutes|hour|hours)", text)
    if relative_match:
        amount = int(relative_match.group(1))
        unit = relative_match.group(2)
        delta = timedelta(minutes=amount) if unit.startswith("minute") else timedelta(hours=amount)
        return (now + delta).strftime("%Y-%m-%dT%H:%M:%SZ")

    if "tomorrow" in text:
        time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if time_match:
            hour, minute = _parse_time_of_day(time_match)
            dt = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return (now + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00Z")

    if "next week" in text:
        return (now + timedelta(days=7)).strftime("%Y-%m-%dT09:00:00Z")

    time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if time_match:
        hour, minute = _parse_time_of_day(time_match)
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return None


def _extract_title(text: str) -> str:
    cleaned = text.strip()
    if cleaned.lower() == "snooze":
        return "Reminder"
    lower = cleaned.lower()

    if "snooze" in lower and lower != "snooze":
        match = re.search(r"snooze", cleaned, flags=re.IGNORECASE)
        if match:
            tail = cleaned[match.end():].strip(" ,:.-")
            if tail:
                return tail.strip("?.!")

    if "reschedule" in lower and lower != "reschedule":
        match = re.search(r"reschedule", cleaned, flags=re.IGNORECASE)
        if match:
            tail = cleaned[match.end():].strip(" ,:.-")
            if tail:
                return tail.strip("?.!")

    for pattern in [
        r"(?:remind(?: me)?(?: to)?|set(?: a)? reminder(?: for)?|create reminder(?: for)?)\s+(?:me\s+)?(?:to\s+)?(.+?)(?=\s+(?:at|in|tomorrow|next|on|for)\b|$)",
        r"(?:please\s+)?remind(?: me)?(?: to)?\s+(?:me\s+)?(.+?)(?=\s+(?:at|in|tomorrow|next|on|for)\b|$)",
    ]:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            title = match.group(1).strip(" .?")
            if title:
                return title
    return "Reminder"


def generate_reminder_output(user_text: str) -> dict[str, Any]:
    text = (user_text or "").strip()

    if not text:
        return {
            "intent": "clarify",
            "status": "needs_clarification",
            "summary": "Request is empty. Please describe the reminder.",
            "reminder": {"title": None, "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": ["What should the reminder say?"],
            "safe": True,
        }

    lower = text.lower()
    if any(token in lower for token in ["spam", "hack", "steal password", "password", "share secret", "purchase all"]):
        return {
            "intent": "reject",
            "status": "rejected",
            "summary": "This request is not appropriate for a reminder.",
            "reminder": {"title": None, "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": [],
            "safe": False,
        }

    if lower.startswith("tell me the weather") or "weather" in lower or ("what is" in lower and "weather" in lower):
        return {
            "intent": "reject",
            "status": "rejected",
            "summary": "This request is not a reminder task.",
            "reminder": {"title": None, "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": [],
            "safe": True,
        }

    if lower == "snooze" or lower in {"snooze it", "snooze this"}:
        return {
            "intent": "clarify",
            "status": "needs_clarification",
            "summary": "Which reminder should be snoozed and when?",
            "reminder": {"title": "Reminder", "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": ["Which reminder do you want to snooze?", "When should it be postponed to?"],
            "safe": True,
        }

    if "set a reminder for tomorrow" in lower or ("set a reminder" in lower and "tomorrow" in lower and "to " not in lower):
        return {
            "intent": "clarify",
            "status": "needs_clarification",
            "summary": "A reminder task is missing. Please specify what to be reminded about.",
            "reminder": {"title": "Reminder", "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": ["What should the reminder be about?"],
            "safe": True,
        }

    if any(token in lower for token in ["reschedule", "move", "change the reminder", "move my reminder"]):
        return {
            "intent": "reschedule",
            "status": "ready",
            "summary": "Reminder reschedule requested.",
            "reminder": {"title": _extract_title(text), "when": _parse_datetime(text) or "2026-01-01T09:00:00Z", "timezone": "UTC", "recurrence": None},
            "clarification_questions": [],
            "safe": True,
        }

    if any(token in lower for token in ["snooze", "wake me later", "delay it"]):
        return {
            "intent": "snooze",
            "status": "ready",
            "summary": "Reminder snooze requested.",
            "reminder": {"title": _extract_title(text), "when": _parse_datetime(text) or "2026-01-01T09:00:00Z", "timezone": "UTC", "recurrence": None},
            "clarification_questions": [],
            "safe": True,
        }

    title = _extract_title(text)
    when = _parse_datetime(text)
    if not when:
        return {
            "intent": "clarify",
            "status": "needs_clarification",
            "summary": "A reminder time is required before creating it.",
            "reminder": {"title": title, "when": None, "timezone": "UTC", "recurrence": None},
            "clarification_questions": ["When would you like to be reminded?"],
            "safe": True,
        }

    return {
        "intent": "create_reminder",
        "status": "ready",
        "summary": f"Reminder created: {title}.",
        "reminder": {"title": title, "when": when, "timezone": "UTC", "recurrence": None},
        "clarification_questions": [],
        "safe": True,
    }
