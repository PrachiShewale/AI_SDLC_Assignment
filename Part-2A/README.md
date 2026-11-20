# AI Reminder Agent

This project calls a language model to interpret reminder requests. The evaluation harness independently checks the JSON contract, behavioral invariants, and source-grounded semantic criteria.

## Configure a model

The app uses the OpenAI Responses API. Set the endpoint, model name, and API token as environment variables. The API token is read from `REMINDER_API_KEY`; do not commit it or paste it into source files.

In the VS Code PowerShell terminal, enter the token without echoing it and set the endpoint/model values:

```powershell
$secure = Read-Host "OpenAI API key" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:REMINDER_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
$env:REMINDER_API_URL = "https://api.openai.com/v1/responses"
$env:REMINDER_MODEL = "gpt-6-luna"
```

The client sends a JSON-mode request with `store: false` to the configured Responses API URL using bearer-token authentication.

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
