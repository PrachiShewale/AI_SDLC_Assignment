from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class ModelClientError(RuntimeError):
    """Raised when the configured model service cannot return valid JSON."""


def complete_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    api_key = os.environ.get("REMINDER_API_KEY")
    api_url = os.environ.get("REMINDER_API_URL", "").strip()
    model = os.environ.get("REMINDER_MODEL", "")
    missing = [
        name
        for name, value in (
            ("REMINDER_API_KEY", api_key),
            ("REMINDER_API_URL", api_url),
            ("REMINDER_MODEL", model),
        )
        if not value
    ]
    if missing:
        raise ModelClientError(
            f"Missing model configuration: {', '.join(missing)}. "
            "Set them in your local environment; do not commit credentials."
        )

    if not api_url.startswith("https://"):
        raise ModelClientError("REMINDER_API_URL must use HTTPS.")

    payload = {
        "model": model,
        "instructions": system_prompt,
        "input": user_prompt,
        "store": False,
        "text": {"format": {"type": "json_object"}},
    }
    request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            response_body = response.read()
    except HTTPError as exc:
        response_body = exc.read()
        try:
            error_response = json.loads(response_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_response = None

        provider_error = error_response.get("error") if isinstance(error_response, dict) else None
        if isinstance(provider_error, dict):
            message = provider_error.get("message") or provider_error.get("detail") or ""
            code = provider_error.get("code", "")
            parameter = provider_error.get("param", "")
        elif isinstance(provider_error, str):
            message = provider_error
            code = ""
            parameter = ""
        elif isinstance(error_response, dict):
            message = error_response.get("message") or error_response.get("detail") or ""
            code = error_response.get("code", "")
            parameter = error_response.get("param", "")
        else:
            message = ""
            code = ""
            parameter = ""

        diagnostic = "; ".join(
            part for part in (
                f"code={code}" if isinstance(code, str) and code else "",
                f"param={parameter}" if isinstance(parameter, str) and parameter else "",
                message if isinstance(message, str) and message else "",
            )
            if part
        )
        if not diagnostic:
            diagnostic = response_body.decode("utf-8", errors="replace").strip()
        if not diagnostic:
            diagnostic = "provider returned an empty error body"
        response_headers = exc.headers
        if response_headers:
            content_type = response_headers.get("Content-Type", "")
            request_id = response_headers.get("x-request-id", "")
            metadata = []
            if content_type:
                metadata.append(f"content_type={content_type}")
            if request_id:
                metadata.append(f"request_id={request_id}")
            if metadata:
                diagnostic = f"{diagnostic}; " + "; ".join(metadata)
        if api_key:
            diagnostic = diagnostic.replace(api_key, "[redacted]")
        diagnostic = re.sub(
            r"(?i)\bBearer\s+[^\s\"'<>]+",
            "Bearer [redacted]",
            diagnostic,
        )
        diagnostic = re.sub(r"\s+", " ", diagnostic)
        if len(diagnostic) > 400:
            diagnostic = diagnostic[:400] + "..."
        detail = f" {diagnostic}" if diagnostic else ""
        raise ModelClientError(f"Model service returned HTTP {exc.code}.{detail}") from exc
    except URLError as exc:
        raise ModelClientError(f"Could not reach model service: {exc.reason}.") from exc
    except TimeoutError as exc:
        raise ModelClientError("Model service request timed out.") from exc

    try:
        completion = json.loads(response_body)
        content = [
            item["text"]
            for output_item in completion["output"]
            if output_item.get("type") == "message"
            for item in output_item.get("content", [])
            if item.get("type") == "output_text"
        ]
        if not content:
            raise KeyError("output_text")
        result = json.loads("".join(content))
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise ModelClientError("Model service returned an invalid Responses API JSON response.") from exc

    if not isinstance(result, dict):
        raise ModelClientError("Model response must be a JSON object.")
    return result
