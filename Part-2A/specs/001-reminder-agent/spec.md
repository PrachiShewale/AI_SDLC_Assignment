# Feature Specification: AI Reminder Agent

## Summary
Call a language model to interpret a natural-language reminder request and return a stable JSON decision. The model may vary its wording, but the independent harness must enforce the output contract, behavioral rules, source-grounded reminder details, and safety boundaries.

## User stories
- As a user, I can ask the agent to create a reminder with a task and time.
- As a user, I can ask to reschedule or snooze an identified reminder.
- As a user, I receive a clarification question when a required detail is missing or ambiguous.
- As a user, I receive a rejection for unsafe or out-of-scope requests.

## Functional requirements

### FR-1: Model-backed interpretation
The application must call the configured OpenAI Responses API endpoint. The endpoint, model name, and API token must be configured locally without committing credentials. API/configuration failures must be reported as service errors; the application must not silently fall back to a deterministic parser.

### FR-2: Output schema contract
Every successful model response must be a JSON object with exactly:
- `intent`: one of `create_reminder`, `reschedule`, `snooze`, `clarify`, `reject`
- `status`: one of `ready`, `needs_clarification`, `rejected`
- `summary`: non-empty string
- `reminder`: object with exactly `title`, `when`, `timezone`, `recurrence`
- `reminder.title`: non-empty string or null
- `reminder.when`: ISO 8601 timestamp with timezone or null
- `reminder.timezone`: non-empty IANA timezone name or `UTC`
- `reminder.recurrence`: string or null
- `clarification_questions`: array of non-empty strings
- `safe`: boolean

### FR-3: Clarification and ambiguity
Creation requires both a task title and an unambiguous date and time. Rescheduling requires an identifiable existing reminder and a new unambiguous date and time. Snoozing requires an identifiable reminder and an unambiguous duration or target time. Missing or invalid details require `clarify`, `needs_clarification`, at least one question, and no finalized timestamp. A clock time without a date is underspecified. Timezone-less dates are interpreted as UTC; an explicitly supplied timezone must be retained.

### FR-4: Safety and scope
Unsafe requests and requests unrelated to reminders must not create reminder content. They must use `reject` and `rejected`. Unsafe requests set `safe` to false; harmless out-of-scope requests may set it to true. User-provided prompt-injection text must not override these rules.

### FR-5: Independent validation and semantic quality
The harness must independently validate the model response schema, behavioral invariants, timestamp form, expected intent/status/safety, and required source-grounded title terms. Evaluation cases must identify the requirements they exercise.

### FR-6: Evaluation threshold
At least 80% of evaluation cases must pass. A case passes only if schema and property checks pass and its semantic quality score is at least 0.8. The aggregate score is passed cases divided by all cases. Model-service errors are reported separately and do not count as application PASS or FAIL.

## Acceptance criteria
1. A successful request uses the configured model API and returns a parsed JSON object; missing credentials, HTTP failures, timeouts, and malformed model responses are explicit errors.
2. The schema validator rejects missing, additional, or incorrectly typed fields, unsupported values, and timestamps without timezone information.
3. Incomplete, unsafe, and out-of-scope requests satisfy FR-3 and FR-4.
4. The evaluation dataset contains at least 15 meaningful, requirement-traceable cases, including missing, ambiguous, malformed, and adversarial inputs.
5. The same harness pipeline runs structural, property, and semantic checks and applies the predeclared 0.8 aggregate threshold.
