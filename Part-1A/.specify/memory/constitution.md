# Smart Todo CLI Constitution

## Core Principles

### I. Specification-first implementation
Every feature must have measurable acceptance criteria before implementation. When an ambiguity is found, the relevant specification artifact should be updated before coding continues.

### II. Deterministic tooling and CLI contract
The application must expose stable CLI behavior and store state in JSON. Outputs must be predictable across runs when given the same inputs.

### III. Test-first validation
Tests are required before acceptance. They must exercise both valid flows and invalid inputs, and they must fail before implementation repairs are applied.

### IV. Security and quality gates
All implementations must pass syntax checking, a static security pass, and deterministic tests before a human accepts the result.

### V. Observable evidence
All failures, repairs, and validations must be captured in project evidence so that the specification-to-implementation path remains traceable.

## Additional Constraints
- Task titles are mandatory and non-empty.
- Supported statuses are limited to `todo`, `in_progress`, and `done`.
- Supported priorities are limited to `1`, `2`, and `3`.
- Tag normalization is lowercase and de-duplicated in the stored representation.

## Development Workflow
- Changes must follow the approved specification and task breakdown.
- Any failing harness result must be recorded and fed back into implementation repairs.
- Final acceptance is a human decision after automated gates pass.
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
