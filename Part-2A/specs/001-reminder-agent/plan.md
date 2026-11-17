# Plan

## Architecture
- Implement a reminder parser that turns natural-language inputs into a JSON result.
- Keep the output contract stable while allowing variation in wording.
- Validate every result with schema, property, and semantic checks.

## Validation
- Create a 15-case evaluation dataset spanning normal behaviour, boundary cases, ambiguity, and guardrails.
- Evaluate output using structural validation, invariant checks, and rubric-based semantic checks.
- Require an aggregate score of at least 0.8 for PASS.
