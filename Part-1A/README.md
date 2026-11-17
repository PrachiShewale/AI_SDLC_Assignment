# Smart Todo CLI

This project implements a deterministic task manager that supports CRUD operations, tag filtering, status transitions, priority sorting, and JSON persistence.

## Features
- Create, update, list, delete, complete, and reopen tasks.
- Track priority values 1-3 and sort by priority descending.
- Filter by task status and tag.
- Persist tasks to a JSON store for deterministic behavior.

## Usage
```bash
python -m src.todo_app --storage tasks.json add "Write report" --priority 2 --tags "work,urgent"
python -m src.todo_app --storage tasks.json list --status todo --tag work
```
