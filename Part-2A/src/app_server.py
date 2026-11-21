from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .model_client import ModelClientError
from .reminder_agent import generate_reminder_output

MAX_REQUEST_BYTES = 64 * 1024


class ReminderRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(404, {"error": "Not found"})
            return
        self._send_json(200, {"status": "ok"})

    def do_POST(self) -> None:
        if self.path != "/api/reminders":
            self._send_json(404, {"error": "Not found"})
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(411, {"error": "A valid Content-Length header is required"})
            return
        if content_length <= 0:
            self._send_json(400, {"error": "Request body must not be empty"})
            return
        if content_length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request body is too large"})
            return
        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON"})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str) or not payload["text"].strip():
            self._send_json(400, {"error": "JSON body must include a non-empty string field 'text'"})
            return

        try:
            result = generate_reminder_output(payload["text"])
        except ModelClientError as exc:
            self._send_json(502, {"error": str(exc)})
            return
        self._send_json(200, result)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ReminderRequestHandler)
    print("Reminder Agent listening on http://127.0.0.1:8000 (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Reminder Agent.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
