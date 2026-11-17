# Harness Log

## Project context
- App: Smart Todo CLI
- Deterministic scope: CRUD operations, status transitions, priority sorting, tag filtering, JSON persistence.
- Specification references:
  - `specs/001-smart-todo-cli/spec.md`
  - `.specify/memory/constitution.md`

## Initial generation
The initial implementation was generated against the specification and then validated with the deterministic test harness.

Observed issue:
- `list_tasks()` returned tasks in ascending priority order instead of descending order.
- `update_task()` raised `KeyError` for a missing task instead of a validation-level `ValueError`.

Relevant evidence from the initial pytest run:
```text
2 failed, 2 passed in 0.47s
AssertionError: expected priority-descending order
KeyError: 'Task missing was not found'
```

## Repair cycle
The coding agent was supplied with the failure evidence and repaired the implementation by:
1. Sorting priority lists with `(-priority, title.lower())` to enforce descending priority order.
2. Catching missing-task lookups in `update_task()` and raising `ValueError` to match the API contract.
3. Preserving deterministic validation for invalid inputs.

## Re-validation
The same harness was rerun after the fix:
```text
=== lint ===
lint passed

=== security ===
security passed

=== tests ===
tests passed

All harness gates passed.
```

## Human review
Decision: ACCEPT

Justification:
- The specification acceptance criteria were satisfied.
- The implementation passed the lint gate, static security pass, and deterministic tests.
- The repair cycle was documented and revalidated without weakening the requirements.

Known limitations:
- The JSON-backed persistence is intentionally simple and file-based; it does not implement a multi-process locking mechanism.
- The static security check is focused on dangerous Python patterns relevant to this small deterministic application.
