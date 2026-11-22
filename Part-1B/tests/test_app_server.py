import json
import threading
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from part_2a_src.app_server import ReminderRequestHandler
from part_2a_src.model_client import ModelClientError


@pytest.fixture
def api_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ReminderRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_health_endpoint_does_not_call_model(api_server):
    with patch("part_2a_src.app_server.generate_reminder_output") as generate:
        with urlopen(f"{api_server}/health") as response:
            assert response.status == 200
            assert json.loads(response.read()) == {"status": "ok"}

    generate.assert_not_called()


def test_reminder_endpoint_validates_and_forwards_text(api_server):
    expected = {"intent": "clarify", "status": "needs_clarification"}
    request = Request(
        f"{api_server}/api/reminders",
        data=json.dumps({"text": "Remind me to buy milk"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with patch("part_2a_src.app_server.generate_reminder_output", return_value=expected) as generate:
        with urlopen(request) as response:
            assert response.status == 200
            assert json.loads(response.read()) == expected

    generate.assert_called_once_with("Remind me to buy milk")


def test_reminder_endpoint_rejects_invalid_input(api_server):
    request = Request(
        f"{api_server}/api/reminders",
        data=json.dumps({"text": 42}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with patch("part_2a_src.app_server.generate_reminder_output") as generate:
        with pytest.raises(HTTPError) as raised:
            urlopen(request)

    assert raised.value.code == 400
    assert json.loads(raised.value.read()) == {
        "error": "JSON body must include a non-empty string field 'text'"
    }
    generate.assert_not_called()


def test_reminder_endpoint_reports_model_service_failure_as_bad_gateway(api_server):
    request = Request(
        f"{api_server}/api/reminders",
        data=json.dumps({"text": "Remind me tomorrow"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with patch(
        "part_2a_src.app_server.generate_reminder_output",
        side_effect=ModelClientError("Model service request timed out."),
    ):
        with pytest.raises(HTTPError) as raised:
            urlopen(request)

    assert raised.value.code == 502
    assert json.loads(raised.value.read()) == {
        "error": "Model service request timed out."
    }
