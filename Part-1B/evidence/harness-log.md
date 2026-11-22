# Harness Log

## Project context
- App: Natural-Language Reminder Agent
- Specification references: It defines the output schema, clarification rules, safety boundaries, measurable checks, and the 0.8 threshold.

## Initial generation and repair cycle
- Initial harness result: python -m pytest -q
    [pytest-failure.txt](./initial-generation/pytest-failure.txt)

- Issues observed: 
    Configuration of AI key in the code, 
    AI model timeout 
- Changes made: 
    Used .env file to do the same and added it to .gitignore to avoid revealing the API key
    Increased the wait time till the model responds
- Re-validation performed:
    Run python Part-1B\.harness\run_evaluation.py 
    checked the test cases passed
    Also, performed API calls through postman with different scenerios and her it successfully worked 

## Final evaluation
- Evaluation command: python Part-1B\.harness\run_evaluation.py
- Run timestamp: 2026-11-21T19:54:26.250861+00:00
- Model: gemini-flash-latest
- Cases passed / total: 19/19
- Aggregate score: 1.0
- Acceptance threshold: 0.8
- Evidence file: [eval-results.json](./final-generation/eval-results.json)



# Justification


Natural phrasing was understood. 
When I entered a reminder in ordinary, slightly informal wording, the agent correctly identified the task and the intent.
Exact time was handled correctly. When I gave a specific time, the reminder was set at exactly that time. When the time was vague or missing, the agent asked me to specify the exact time instead of guessing.
Clarification worked. When the request was unclear or incomplete, the agent asked a clarifying question instead of creating a reminder from assumptions.
Scope stayed within the specification. The agent only performed the  permitted actions: create_reminder, reschedule, snooze, clarify, and reject. It did not carry out other actions.


# Decision
Decision: ACCEPT.



# Limitations
Results vary between runs. The agent calls a language model, so the same input can produce different wording or timing choices. Passing the evaluation means the score met the threshold on the dataset, not that every future input will behave correctly.
Limited scope by design. It only supports setting, rescheduling and clarifying,snoozing, etc. Requests outside that, such as deleting or listing reminders, are not handled. If the spec included snooze, mention whether it works.
Ambiguous time expressions. Vague phrases like “evening” or “later” depend on the agent asking for clarification, and a case that slips past the check could produce a wrong time.
Dependence on the model and its availability. The agent relies on an external model, so outages, rate limits or a model update could change behaviour.
Evaluation covers a finite dataset. The evaluation set has a limited number of cases, so rare phrasings and adversarial inputs not in the set remain untested.