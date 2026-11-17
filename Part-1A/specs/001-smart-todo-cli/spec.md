# Feature Specification: Smart Todo CLI

## Summary
Provide a deterministic task management CLI and Python API for creating, updating, listing, and completing tasks. The system stores tasks in JSON and enforces fixed validation rules.

## User stories
- As a user, I can create a task with a title, optional description, priority, tags, and initial status.
- As a user, I can list tasks filtered by status or tag and sorted by priority.
- As a user, I can update status and metadata without corrupting the task list.
- As a user, I can complete or reopen tasks and persist the state.

## Acceptance criteria
1. A task must include a non-empty title.
2. Status values must be one of `todo`, `in_progress`, or `done`.
3. Priority values must be one of `1`, `2`, or `3`.
4. Listing tasks must return tasks sorted by priority in descending order.
5. Filtering by tag must match a normalized lowercase tag string.
6. Saving and reloading the task store must preserve task state.
