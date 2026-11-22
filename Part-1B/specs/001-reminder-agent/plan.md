# Plan

## Architecture
- Call a configured Google Gemini `generateContent` endpoint using Python's standard library.
- Read the API token, model name, and optional endpoint from environment variables; never store credentials in the repository.
- Send a fixed system prompt and the request plus current UTC time to the model.
- Parse the model's JSON response and surface service/format errors; do not provide a rule-based fallback.
- Validate the result independently through schema, property, and source-grounded semantic checks.

## Evaluation
- Maintain a requirement-traceable dataset of normal, boundary, ambiguous, malformed, missing-data, and guardrail cases.
- Score intent, status, expected title terms, and safety against the case rubric.
- A case passes only if structural and property checks pass and semantic quality is at least 0.8.
- The aggregate pass threshold is 0.8; service errors are reported separately.

## Security
- Require HTTPS for the model endpoint.
- Keep credentials in local environment variables and never print or persist them.
- Treat user input as untrusted and do not execute model output as actions.
