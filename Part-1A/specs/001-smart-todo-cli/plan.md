# Plan

## Architecture
- Keep the app as a small Python module with a `TaskStore` that manages JSON persistence.
- Use a dataclass for tasks and validation methods for statuses and priorities.
- Provide CLI access with argparse for deterministic command execution.

## Validation
- Use pytest for deterministic unit tests derived from acceptance criteria.
- Run compileall or `py_compile` for syntax validation.
- Run a static security scan with Bandit and record results.
