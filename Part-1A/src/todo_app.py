from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Optional

VALID_STATUSES = {"todo", "in_progress", "done"}
VALID_PRIORITIES = {1, 2, 3}


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: str = "todo"
    priority: int = 1
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            priority=int(data.get("priority", 1)),
            tags=list(data.get("tags", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TaskStore:
    def __init__(self, storage_path: Optional[str | Path] = None):
        self.storage_path = Path(storage_path) if storage_path else Path.cwd() / "tasks.json"
        self.tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            self.tasks = []
            return
        with self.storage_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        self.tasks = [Task.from_dict(item) for item in raw]

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as fh:
            json.dump([task.to_dict() for task in self.tasks], fh, indent=2)

    def _validate_status(self, status: str) -> str:
        normalized = status.strip().lower()
        if normalized not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Allowed values: {sorted(VALID_STATUSES)}")
        return normalized

    def _validate_priority(self, priority: int) -> int:
        value = int(priority)
        if value not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {sorted(VALID_PRIORITIES)}")
        return value

    def _normalize_tags(self, tags: Iterable[str]) -> List[str]:
        normalized = []
        for tag in tags:
            cleaned = str(tag).strip().lower()
            if cleaned:
                normalized.append(cleaned)
        return normalized

    def create_task(
        self,
        title: str,
        description: str = "",
        *,
        status: str = "todo",
        priority: int = 1,
        tags: Optional[Iterable[str]] = None,
    ) -> Task:
        task_title = str(title).strip()
        if not task_title:
            raise ValueError("Title is required")
        task = Task(
            id=str(uuid.uuid4())[:8],
            title=task_title,
            description=str(description or ""),
            status=self._validate_status(status),
            priority=self._validate_priority(priority),
            tags=self._normalize_tags(tags or []),
        )
        self.tasks.append(task)
        self._save()
        return task

    def get_task(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"Task {task_id} was not found")

    def list_tasks(self, *, status: Optional[str] = None, tag: Optional[str] = None, sort_by: str = "priority") -> List[Task]:
        filtered = list(self.tasks)
        if status:
            filtered = [task for task in filtered if task.status == self._validate_status(status)]
        if tag:
            normalized = self._normalize_tags([tag])[0]
            filtered = [task for task in filtered if normalized in task.tags]
        if sort_by == "priority":
            filtered = sorted(filtered, key=lambda task: (-task.priority, task.title.lower()))
        elif sort_by == "title":
            filtered = sorted(filtered, key=lambda task: task.title.lower())
        else:
            raise ValueError("sort_by must be either 'priority' or 'title'")
        return filtered

    def update_task(self, task_id: str, **changes: Any) -> Task:
        try:
            task = self.get_task(task_id)
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        for key, value in changes.items():
            if key == "title":
                if not value or not str(value).strip():
                    raise ValueError("Title is required")
                task.title = str(value).strip()
            elif key == "description":
                task.description = str(value or "")
            elif key == "status":
                task.status = self._validate_status(str(value))
            elif key == "priority":
                task.priority = self._validate_priority(value)
            elif key == "tags":
                task.tags = self._normalize_tags(value or [])
            else:
                raise ValueError(f"Unsupported field: {key}")
        self._save()
        return task

    def delete_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self._save()

    def complete_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        task.status = "done"
        self._save()
        return task

    def reopen_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        task.status = "todo"
        self._save()
        return task


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a small task list.")
    parser.add_argument("--storage", default="tasks.json", help="Path to the JSON task store")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Create a new task")
    add_parser.add_argument("title")
    add_parser.add_argument("--description", default="")
    add_parser.add_argument("--status", default="todo")
    add_parser.add_argument("--priority", type=int, default=1)
    add_parser.add_argument("--tags", default="")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status")
    list_parser.add_argument("--tag")
    list_parser.add_argument("--sort-by", choices=["priority", "title"], default="priority")

    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("task_id")
    update_parser.add_argument("--title")
    update_parser.add_argument("--description")
    update_parser.add_argument("--status")
    update_parser.add_argument("--priority", type=int)
    update_parser.add_argument("--tags")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done")
    complete_parser.add_argument("task_id")

    reopen_parser = subparsers.add_parser("reopen", help="Re-open a task")
    reopen_parser.add_argument("task_id")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    store = TaskStore(args.storage)

    try:
        if args.command == "add":
            task = store.create_task(
                args.title,
                description=args.description,
                status=args.status,
                priority=args.priority,
                tags=[tag.strip() for tag in args.tags.split(",") if tag.strip()],
            )
            print(json.dumps(task.to_dict(), indent=2))
            return 0
        if args.command == "list":
            tasks = store.list_tasks(status=args.status, tag=args.tag, sort_by=args.sort_by)
            print(json.dumps([task.to_dict() for task in tasks], indent=2))
            return 0
        if args.command == "update":
            payload = {}
            if args.title is not None:
                payload["title"] = args.title
            if args.description is not None:
                payload["description"] = args.description
            if args.status is not None:
                payload["status"] = args.status
            if args.priority is not None:
                payload["priority"] = args.priority
            if args.tags is not None:
                payload["tags"] = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
            task = store.update_task(args.task_id, **payload)
            print(json.dumps(task.to_dict(), indent=2))
            return 0
        if args.command == "delete":
            store.delete_task(args.task_id)
            print(f"Deleted task {args.task_id}")
            return 0
        if args.command == "complete":
            task = store.complete_task(args.task_id)
            print(json.dumps(task.to_dict(), indent=2))
            return 0
        if args.command == "reopen":
            task = store.reopen_task(args.task_id)
            print(json.dumps(task.to_dict(), indent=2))
            return 0
    except Exception as exc:  # pragma: no cover - command surface
        print(f"ERROR: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
