# Reminder Agent

This project demonstrates a non-deterministic reminder agent that turns unstructured natural-language requests into a structured reminder JSON contract. The application uses a deterministic validator harness to enforce schema, behaviour, and quality boundaries.

## Modules
- `src/reminder_agent.py`: reminder-generation logic
- `evals/dataset.json`: 15 evaluation cases
- `.harness/`: schema, property, and quality validators
- `evidence/`: initial and final evaluation logs
