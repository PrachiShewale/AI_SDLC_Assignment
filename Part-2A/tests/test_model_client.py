import json
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from part_2a_src.model_client import ModelClientError, complete_json


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(self.body).encode("utf-8")


def test_model_client_sends_configured_chat_request():
    model_reply = {
        "intent": "reject",
        "status": "rejected",
        "summary": "Not a reminder request.",
        "reminder": {
            "title": None,
            "when": None,
            "timezone": "UTC",
            "recurrence": None,
        },
        "clarification_questions": [],
        "safe": True,
    }
    response = FakeResponse(
        {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": json.dumps(model_reply)}
                    ],
                }
            ]
        }
    )

    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen", return_value=response) as urlopen:
        result = complete_json("system prompt", "user request")

    assert result == model_reply
    request = urlopen.call_args.args[0]
    request_body = json.loads(request.data)
    assert request.full_url == "https://api.example.test/v1/responses"
    assert request.get_header("Authorization") == "Bearer test-token"
    assert request_body["model"] == "gpt-6-luna"
    assert request_body["store"] is False
    assert request_body["text"]["format"] == {"type": "json_object"}


def test_model_client_requires_credentials():
    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen") as urlopen:
        with pytest.raises(ModelClientError, match="REMINDER_API_KEY"):
            complete_json("system", "user")

    urlopen.assert_not_called()


def test_model_client_rejects_non_https_endpoint():
    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "http://example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen") as urlopen:
        with pytest.raises(ModelClientError, match="REMINDER_API_URL must use HTTPS"):
            complete_json("system", "user")

    urlopen.assert_not_called()


def test_model_client_rejects_non_json_model_content():
    response = FakeResponse(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "not json"}],
                }
            ]
        }
    )

    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen", return_value=response):
        with pytest.raises(ModelClientError, match="invalid Responses API"):
            complete_json("system", "user")


def test_http_error_reports_provider_message_without_leaking_key():
    response_body = json.dumps(
        {
            "error": {
                "message": "Model is unavailable.",
                "type": "invalid_request_error",
                "code": "model_not_found",
                "param": "model",
            }
        }
    ).encode("utf-8")
    error = HTTPError(
        "https://api.example.test/v1/responses",
        400,
        "Bad Request",
        {},
        BytesIO(response_body),
    )

    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen", side_effect=error):
        with pytest.raises(ModelClientError) as raised:
            complete_json("system", "user")

    assert "HTTP 400" in str(raised.value)
    assert "code=model_not_found" in str(raised.value)
    assert "param=model" in str(raised.value)
    assert "test-token" not in str(raised.value)


def test_http_error_supports_string_error_bodies():
    response_body = json.dumps({"error": "Unsupported model identifier."}).encode("utf-8")
    error = HTTPError(
        "https://api.example.test/v1/responses",
        400,
        "Bad Request",
        {},
        BytesIO(response_body),
    )

    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen", side_effect=error):
        with pytest.raises(ModelClientError, match="Unsupported model identifier"):
            complete_json("system", "user")


def test_http_error_reports_safe_metadata_when_body_is_empty():
    error = HTTPError(
        "https://api.example.test/v1/responses",
        400,
        "Bad Request",
        {"Content-Type": "application/json", "x-request-id": "request-123"},
        BytesIO(b""),
    )

    with patch.dict(
        "os.environ",
        {
            "REMINDER_API_KEY": "test-token",
            "REMINDER_API_URL": "https://api.example.test/v1/responses",
            "REMINDER_MODEL": "gpt-6-luna",
        },
        clear=True,
    ), patch("part_2a_src.model_client.urlopen", side_effect=error):
        with pytest.raises(ModelClientError) as raised:
            complete_json("system", "user")

    assert "provider returned an empty error body" in str(raised.value)
    assert "content_type=application/json" in str(raised.value)
    assert "request_id=request-123" in str(raised.value)
