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
4 passed, 0 failed

All harness gates passed.
```

## Human review
Decision: ACCEPT


Justification

I reviewed the Smart Todo CLI against the acceptance criteria in the specification, and every criterion I checked was satisfied. Specifically, I was able to:

add a task, which started with the status todo
complete a task, reopen it, and move it to review
list all tasks
view a priority-sorted list
delete a record

The behaviour was predictable and repeatable: the same input gave the same output each time, which is what the deterministic design and the specification-derived tests are meant to guarantee.

Decision: ACCEPT


Limitations

Rigid, exact-match behaviour. Because the app is deterministic, it only handles the inputs and transitions defined in the specification. Anything outside those definitions is rejected rather than interpreted, so it can’t adapt to loosely phrased or unexpected input the way an AI-based app could.

Security. [Your security observation goes here. Your note was cut off after “other than that security”, so tell me what you meant.] Static checks such as Bandit catch known code-level issues, but they don’t prove the app is secure. For example, tasks are stored in a plain JSON file with no access control or encryption. Keep this line only if it’s true of your app.
