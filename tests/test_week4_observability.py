from aura_execution.task_store import TaskStatus, TaskStore


def test_task_store_can_record_history_without_enqueueing():
    store = TaskStore()

    task = store.create(
        "Open example.com",
        enqueue=False,
    )

    store.update(
        task.id,
        status=TaskStatus.RUNNING,
    )

    store.update(
        task.id,
        status=TaskStatus.COMPLETED,
    )

    assert store.pending_count() == 0
    assert store.get(task.id).status == TaskStatus.COMPLETED
    assert store.list_tasks()[0].id == task.id