from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from reminder_agent import generate_reminder_output
from schema_validator import validate_schema
from property_checks import evaluate_properties
from quality_eval import evaluate_quality


def evaluate_case(case: dict) -> dict:
    output = generate_reminder_output(case["input"])
    schema_ok, schema_error = validate_schema(output)
    property_ok, property_error = evaluate_properties(output)
    quality_score, quality_error = evaluate_quality(output, case["expected_intent"], case["expected_status"])

    passed = schema_ok and property_ok and quality_error is None
    return {
        "id": case["id"],
        "input": case["input"],
        "expected": {"intent": case["expected_intent"], "status": case["expected_status"]},
        "actual": output,
        "schema_ok": schema_ok,
        "property_ok": property_ok,
        "quality_score": quality_score,
        "passed": passed,
        "schema_error": schema_error,
        "property_error": property_error,
        "quality_error": quality_error,
    }


def main() -> int:
    dataset = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    results = [evaluate_case(case) for case in dataset]
    passed = sum(1 for result in results if result["passed"])
    score = passed / len(results)
    summary = {
        "threshold": 0.8,
        "cases_total": len(results),
        "cases_passed": passed,
        "score": score,
        "pass": score >= 0.8,
        "results": results,
    }
    print(json.dumps({"summary": summary}, indent=2))
    (ROOT / "evidence" / "final-generation" / "eval-results.json").parent.mkdir(exist_ok=True, parents=True)
    (ROOT / "evidence" / "final-generation" / "eval-results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0 if score >= 0.8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
