import json
from pathlib import Path

import pytest

from src.todo_app import TaskStore


@pytest.fixture
def store(tmp_path):
    storage = tmp_path / "tasks.json"
    return TaskStore(storage)


def test_create_and_list_tasks(store):
    first = store.create_task("Write report", description="Quarterly update", priority=2, tags=["work", "urgent"])
    second = store.create_task("Pay bills", priority=3, tags=["home"])

    all_tasks = store.list_tasks()
    assert [task.id for task in all_tasks] == [second.id, first.id]
    assert all_tasks[0].priority == 3

    filtered = store.list_tasks(tag="work")
    assert [task.title for task in filtered] == ["Write report"]


def test_status_transition_and_update(store):
    task = store.create_task("Plan sprint", status="todo", priority=1, tags=["planning"])
    store.complete_task(task.id)
    assert store.get_task(task.id).status == "done"

    updated = store.update_task(task.id, status="in_progress", tags=["planning", "active"])
    assert updated.status == "in_progress"
    assert updated.tags == ["planning", "active"]

    reopened = store.reopen_task(task.id)
    assert reopened.status == "todo"


def test_invalid_inputs_are_rejected(store):
    with pytest.raises(ValueError):
        store.create_task("", priority=1)
    with pytest.raises(ValueError):
        store.create_task("Bad task", priority=9)
    with pytest.raises(ValueError):
        store.update_task("missing", title="")


def test_cli_round_trip(tmp_path):
    storage = tmp_path / "tasks.json"
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "src.todo_app", "--storage", str(storage), "add", "Review PR", "--priority", "2", "--tags", "code,review"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["title"] == "Review PR"
    assert payload["status"] == "todo"
    assert payload["tags"] == ["code", "review"]

    list_result = subprocess.run(
        [sys.executable, "-m", "src.todo_app", "--storage", str(storage), "list"],
        capture_output=True,
        text=True,
        check=True,
    )
    tasks = json.loads(list_result.stdout)
    assert tasks[0]["title"] == "Review PR"
