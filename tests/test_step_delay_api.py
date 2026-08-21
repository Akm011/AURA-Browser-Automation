from aura_api.schemas import ExecuteRequest, TaskCreateRequest


def test_execute_request_uses_server_default_when_delay_is_omitted() -> None:
    request = ExecuteRequest(request="Open https://example.com", headed=True)

    assert request.step_delay_seconds is None


def test_queued_task_uses_server_default_when_delay_is_omitted() -> None:
    request = TaskCreateRequest(request="Open https://example.com", headed=True)

    assert request.step_delay_seconds is None


def test_api_request_accepts_an_explicit_step_delay() -> None:
    request = ExecuteRequest(
        request="Open https://example.com",
        headed=True,
        step_delay_seconds=2.5,
    )

    assert request.step_delay_seconds == 2.5
