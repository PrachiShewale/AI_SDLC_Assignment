from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENT_KEYS = {"REMINDER_API_KEY", "REMINDER_API_URL", "REMINDER_MODEL"}
MAX_TRANSIENT_RETRIES = 3


class ModelClientError(RuntimeError):
    """Raised when the configured model service cannot return valid JSON."""


def load_local_environment(env_path: Path | None = None) -> None:
    path = env_path or ROOT / ".env"
    if not path.exists():
        return

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if "=" not in cleaned:
            raise ModelClientError(f"Invalid .env syntax on line {line_number}; expected KEY=VALUE.")

        name, value = cleaned.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if name in ENVIRONMENT_KEYS and not os.environ.get(name):
            os.environ[name] = value


def _retry_delay(exc: HTTPError, response_body: bytes, retry_number: int) -> float:
    retry_after = exc.headers.get("Retry-After") if exc.headers else None
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass

    message = response_body.decode("utf-8", errors="replace")
    match = re.search(
        r"try again in\s+(\d+(?:\.\d+)?)\s*(ms|s|sec(?:ond)?s?|m|min(?:ute)?s?)\b",
        message,
        re.IGNORECASE,
    )
    if match:
        delay = float(match.group(1))
        unit = match.group(2).lower()
        if unit == "ms":
            return delay / 1000
        if unit.startswith("m"):
            return delay * 60
        return delay

    return min(2 ** (retry_number + 1), 30)


def _raise_http_error(exc: HTTPError, response_body: bytes, api_key: str | None) -> None:
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


def complete_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    load_local_environment()
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
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        retry_number = 0
        while True:
            try:
                with urlopen(request, timeout=60) as response:
                    response_body = response.read()
                break
            except HTTPError as exc:
                response_body = exc.read()
                if exc.code in {408, 429, 500, 502, 503, 504} and retry_number < MAX_TRANSIENT_RETRIES:
                    time.sleep(_retry_delay(exc, response_body, retry_number))
                    retry_number += 1
                    continue
                _raise_http_error(exc, response_body, api_key)
    except URLError as exc:
        raise ModelClientError(f"Could not reach model service: {exc.reason}.") from exc
    except TimeoutError as exc:
        raise ModelClientError("Model service request timed out.") from exc

    try:
        completion = json.loads(response_body)
        candidates = completion["candidates"]
        if not candidates:
            raise KeyError("candidates")
        parts = candidates[0]["content"]["parts"]
        content = [
            part["text"]
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        if not content:
            raise KeyError("candidate.content.parts.text")
        result = json.loads("".join(content))
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise ModelClientError("Gemini returned an invalid generateContent JSON response.") from exc

    if not isinstance(result, dict):
        raise ModelClientError("Model response must be a JSON object.")
    return result
