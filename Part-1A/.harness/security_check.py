from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BAD_PATTERNS = {
    "eval": "eval" ,
    "exec": "exec",
    "subprocess": "subprocess",
    "os.system": "os.system",
    "pickle.loads": "pickle.loads",
}


def main() -> int:
    findings: list[str] = []
    for file_path in sorted((ROOT / "src").rglob("*.py")):
        text = file_path.read_text(encoding="utf-8")
        for name, pattern in BAD_PATTERNS.items():
            if re.search(rf"\b{re.escape(pattern)}\b", text):
                findings.append(f"{file_path.relative_to(ROOT)}: found {name}")
    if findings:
        for item in findings:
            print(item)
        return 1
    print("Static security scan passed. No dangerous patterns found in src/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
