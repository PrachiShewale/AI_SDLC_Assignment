from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".harness"))

from property_checks import evaluate_properties
from quality_eval import evaluate_quality
from schema_validator import validate_schema
from src.model_client import ModelClientError
from src.reminder_agent import generate_reminder_output

THRESHOLD = 0.8
RESULTS_PATH = ROOT / "evidence" / "final-generation" / "eval-results.json"


def _model_configuration() -> dict[str, str]:
    return {
        "provider": "OpenAI Responses API",
        "model": os.environ.get("REMINDER_MODEL", "<not configured>"),
        "api_url": os.environ.get("REMINDER_API_URL", "<not configured>"),
    }


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    output = generate_reminder_output(case["input"])
    schema_ok, schema_error = validate_schema(output)
    property_ok, property_error = (
        evaluate_properties(output) if isinstance(output, dict) else (False, "Output is not an object")
    )
    quality_score, quality_errors = evaluate_quality(output, case)
    passed = schema_ok and property_ok and quality_score >= 0.8

    failed_checks = []
    if not schema_ok:
        failed_checks.append("schema")
    if not property_ok:
        failed_checks.append("properties")
    if quality_score < 0.8:
        failed_checks.append("semantic_quality")

    return {
        "id": case["id"],
        "requirement_ids": case["requirement_ids"],
        "input": case["input"],
        "expected": {
            "intent": case["expected_intent"],
            "status": case["expected_status"],
            "title_terms": case.get("expected_title_terms", []),
            "safe": case["expected_safe"],
        },
        "actual": output,
        "schema_ok": schema_ok,
        "schema_error": schema_error,
        "property_ok": property_ok,
        "property_error": property_error,
        "quality_score": quality_score,
        "quality_errors": quality_errors,
        "failed_checks": failed_checks,
        "passed": passed,
    }


def _write_results(results: dict[str, Any]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")


def main() -> int:
    dataset = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    results = []

    for case in dataset:
        try:
            results.append(evaluate_case(case))
        except ModelClientError as exc:
            failure = {
                "run_status": "model_service_error",
                "started_utc": datetime.now(timezone.utc).isoformat(),
                "model_configuration": _model_configuration(),
                "threshold": THRESHOLD,
                "completed_cases": len(results),
                "failed_case_id": case["id"],
                "error": str(exc),
                "evaluation_completed": False,
            }
            _write_results(failure)
            print(json.dumps(failure, indent=2), file=sys.stderr)
            return 2

    cases_passed = sum(result["passed"] for result in results)
    score = cases_passed / len(results) if results else 0.0
    summary = {
        "run_status": "completed",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "model_configuration": _model_configuration(),
        "threshold": THRESHOLD,
        "scoring": (
            "Case pass requires schema and property checks plus semantic score >= 0.8. "
            "Aggregate score is passed cases divided by total cases."
        ),
        "cases_total": len(results),
        "cases_passed": cases_passed,
        "score": score,
        "pass": bool(results) and score >= THRESHOLD,
        "results": results,
    }
    _write_results(summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "results"}, indent=2))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
