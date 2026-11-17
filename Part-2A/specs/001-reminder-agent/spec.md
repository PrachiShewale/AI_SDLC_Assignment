# Feature Specification: Reminder Agent

## Summary
Build a reminder agent that interprets natural-language reminders and returns a stable structured JSON response. The output must remain valid even though the underlying wording can vary across model runs.

## User stories
- As a user, I can ask to create a reminder for a task and a time.
- As a user, I can request a reschedule or snooze for an existing reminder.
- As a user, if required information is missing, the agent asks for clarification instead of guessing.
- As a user, I receive a structured output with a consistent schema.

## Functional requirements
1. The agent must support the intents `create_reminder`, `reschedule`, `snooze`, `clarify`, and `reject`.
2. The output schema must include `intent`, `status`, `summary`, `reminder`, `clarification_questions`, and `safe`.
3. If the text is ambiguous or lacks a task description or time, the agent must return `clarify` and request missing information.
4. The agent must reject unsafe or irrelevant requests.
5. Valid reminder timestamps must be ISO 8601 strings in UTC or local time with timezone information.

## Acceptance criteria
1. Every output must validate against the JSON schema and include required fields.
2. Missing mandatory reminder details must trigger `clarify` rather than a guessed reminder.
3. Supported intents must remain limited to the defined list.
4. The aggregate evaluation score must be at least 0.8 before human acceptance.
5. The harness must show structural, property, and semantic evaluation evidence.
