from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model_client import complete_json

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "reminder_agent_prompt.txt"


def generate_reminder_output(user_text: str) -> dict[str, Any]:
    if not isinstance(user_text, str):
        raise TypeError("user_text must be a string")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    current_time = datetime.now(timezone.utc).isoformat(timespec="seconds")
    request = json.dumps(
        {"current_time_utc": current_time, "user_request": user_text},
        ensure_ascii=False,
    )
    return complete_json(system_prompt, request)
