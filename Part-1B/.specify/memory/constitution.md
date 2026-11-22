# Reminder Agent Constitution

## Core Principles

### I. Specification-First Evaluation
Every AI feature must define a measurable JSON contract, behavioural invariants, and pass threshold before implementation. If requirements are ambiguous, the specification must be corrected before coding continues.

### II. Stable Output Contract
The agent must always return a machine-readable JSON object with a fixed schema, supported intents, and a deterministic `safe` flag even when the textual wording varies.

### III. Validation Before Acceptance
Every generated response is evaluated through schema validation, invariant checks, and semantic quality checks. An output is accepted only after the threshold is satisfied.

### IV. Safety and Guardrails
Requests that are unsafe, outside the reminder scope, or missing required information must be rejected or clarified rather than guessed.

### V. Evidence-Driven Repair
If the harness fails, the failure evidence must be recorded and supplied back to the implementation before re-running the same guardrails.

## Additional Constraints
- Supported intents are limited to `create_reminder`, `reschedule`, `snooze`, `clarify`, and `reject`.
- All valid reminders must include an ISO 8601 timestamp with timezone information.
- Clarification is required when mandatory task details or times are missing.
- The aggregate evaluation threshold is 0.8, calculated as passed cases divided by total cases.

## Development Workflow
- The accepted specification drives implementation and dataset design.
- All evaluation results are reviewed by a human before the final ACCEPT/REJECT decision.
- Any legitimate requirement change must be reflected in the specification and the evaluation dataset.

## Governance
This constitution governs the reminder-agent project. All changes must remain traceable to the approved specification and evaluation harness.

**Version**: 1.0.0 | **Ratified**: 2026-11-17 | **Last Amended**: 2026-11-17
