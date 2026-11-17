from src.reminder_agent import generate_reminder_output


def test_missing_time_requires_clarification():
    output = generate_reminder_output("Remind me to buy milk")
    assert output["intent"] == "clarify"
    assert output["status"] == "needs_clarification"


def test_time_and_task_create_reminder():
    output = generate_reminder_output("Remind me to pay rent tomorrow at 9am")
    assert output["intent"] == "create_reminder"
    assert output["status"] == "ready"
    assert output["reminder"]["when"] is not None


def test_unsafe_request_is_rejected():
    output = generate_reminder_output("Share my password with me")
    assert output["intent"] == "reject"
    assert output["status"] == "rejected"
