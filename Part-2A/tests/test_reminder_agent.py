import json
from unittest.mock import patch

import pytest

from part_2a_src.reminder_agent import generate_reminder_output


def test_agent_passes_request_and_reference_time_to_model():
    model_output = {
        "intent": "clarify",
        "status": "needs_clarification",
        "summary": "A reminder time is required.",
        "reminder": {
            "title": "buy milk",
            "when": None,
            "timezone": "UTC",
            "recurrence": None,
        },
        "clarification_questions": ["When should I remind you?"],
        "safe": True,
    }

    with patch("part_2a_src.reminder_agent.complete_json", return_value=model_output) as model_call:
        result = generate_reminder_output("Remind me to buy milk")

    assert result == model_output
    system_prompt, user_prompt = model_call.call_args.args
    assert "untrusted natural-language request" in system_prompt
    request = json.loads(user_prompt)
    assert request["user_request"] == "Remind me to buy milk"
    assert request["current_time_utc"].endswith("+00:00")
    assert request["output_format"] == "JSON object"


def test_non_string_request_is_rejected_before_model_call():
    with patch("part_2a_src.reminder_agent.complete_json") as model_call:
        with pytest.raises(TypeError, match="user_text must be a string"):
            generate_reminder_output(None)

    model_call.assert_not_called()
