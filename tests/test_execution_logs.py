from aura_execution.log_store import LogStore
from aura_execution.task_store import TaskStatus, TaskStore


def test_logs_are_persisted_and_filterable_by_session(tmp_path) -> None:
    tasks = TaskStore()
    task = tasks.create("Open https://example.com", session_id="demo session", enqueue=False)
    task = tasks.update(task.id, status=TaskStatus.COMPLETED)
    logs = LogStore(tmp_path)

    logs.save(task)

    entries = logs.list(session_id="demo session")
    assert entries[0]["session_id"] == "demo session"
    assert entries[0]["request"] == "Open https://example.com"


def test_logs_use_task_id_when_no_session_was_supplied(tmp_path) -> None:
    task = TaskStore().create("Open https://example.com", enqueue=False)
    logs = LogStore(tmp_path)

    logs.save(task)

    assert logs.list(session_id=task.id)[0]["session_id"] == task.id
