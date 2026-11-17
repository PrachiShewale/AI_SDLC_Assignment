from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_stage(label: str, command: list[str]) -> int:
    print(f"\n=== {label} ===")
    result = subprocess.run(command, cwd=ROOT, text=True)
    if result.returncode != 0:
        print(f"{label} failed with code {result.returncode}")
        return result.returncode
    print(f"{label} passed")
    return 0


def main() -> int:
    stages = [
        ("lint", [sys.executable, str(ROOT / ".harness" / "lint.py")]),
        ("security", [sys.executable, str(ROOT / ".harness" / "security_check.py")]),
        ("tests", [sys.executable, "-m", "pytest", "-q"]),
    ]

    for label, command in stages:
        code = run_stage(label, command)
        if code != 0:
            return code
    print("\nAll harness gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
