# AI Reminder Agent

This project calls a language model to interpret reminder requests. The evaluation harness independently checks the JSON contract, behavioral invariants, and source-grounded semantic criteria.

## Configure a model

The app uses the OpenAI Responses API. For a simple local setup, edit the ignored `Part-2A/.env` file and enter:

```dotenv
REMINDER_API_KEY=
REMINDER_API_URL=https://api.openai.com/v1/responses
REMINDER_MODEL=gpt-6-luna
```

Paste the actual secret after `REMINDER_API_KEY=` with no quotes or extra spaces. The app loads these settings from `.env`; `.gitignore` excludes the file, so never force-add it to Git or share its contents. The client sends a JSON-mode request with `store: false` using bearer-token authentication.

## Run tests and evaluation

From the repository root, run both parts' tests. They use a mocked API and do not require a token or network access:

```powershell
python -m pytest -q
```

The live evaluation calls the configured model once per case and may consume provider quota:

```powershell
python Part-2A\.harness\run_evaluation.py
```

The harness writes the model name, aggregate score, individual outcomes, and any model-service error to `evidence/final-generation/eval-results.json`. It never writes the API token. A service error is not treated as an evaluation PASS or FAIL.
