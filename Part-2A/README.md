# AI Reminder Agent

This project calls a language model to interpret reminder requests. The evaluation harness independently checks the JSON contract, behavioral invariants, and source-grounded semantic criteria.

## Configure a model

The app uses Google's Gemini `generateContent` API. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/apikey), then edit the ignored `Part-2A/.env` file:

```dotenv
REMINDER_API_KEY=
REMINDER_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent
REMINDER_MODEL=gemini-flash-latest
```

Paste the Gemini API key after `REMINDER_API_KEY=` with no quotes or extra spaces. The app loads these settings from `.env`; `.gitignore` excludes the file, so never force-add it to Git or share its contents. The client sends the key in the `x-goog-api-key` header and requests JSON output.

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
Gemini requests are allowed up to seven minutes to accommodate slow responses.

If Gemini returns HTTP 429 with a quota-exceeded message, generation is blocked by the Google AI project quota, not by Postman or the local app. Check the [AI Studio rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [usage dashboard](https://ai.dev/rate-limit); wait for quota to reset or arrange an eligible plan/quota increase before retrying. The client retries 429 responses only when Google supplies a retry delay.

## Run the application locally with Postman

From the repository root, start the local server in a terminal:

```powershell
Set-Location .\Part-2A
python -m src.app_server
```

The server listens only on `127.0.0.1:8000`. In Postman, check `GET http://127.0.0.1:8000/health`, then send a `POST` to `http://127.0.0.1:8000/api/reminders` with `Content-Type: application/json` and a raw JSON body:

```json
{
  "text": "Remind me to submit report tomorrow at 9am"
}
```

The local server reads the Gemini key from `.env`; do not put the key in Postman or share it. A successful response contains the reminder agent's JSON result. Upstream Gemini errors are returned as HTTP 502 JSON errors.
