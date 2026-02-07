#!/usr/bin/env python3
"""
Run Cursor config validation for this repository.

Runs:
- YAML validation under .cursor/
- Prompt collection validation
- Rule-index validation

Usage:
  python .cursor/scripts/validate-cursor-config.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)


def main() -> int:
    root = Path(__file__).resolve().parents[2]

    checks: list[tuple[str, list[str]]] = [
        ("YAML (.cursor)", [sys.executable, str(root / ".cursor" / "scripts" / "validate-yaml.py"), ".cursor", "--recurse"]),
        ("Prompt collections", [sys.executable, str(root / ".cursor" / "scripts" / "validate-prompt-collections.py")]),
        ("Rule index", [sys.executable, str(root / ".cursor" / "scripts" / "validate-rule-index.py")]),
    ]

    failures: list[str] = []
    for name, cmd in checks:
        code = run(cmd)
        if code != 0:
            failures.append(name)

    if failures:
        print("\nERROR: Cursor config validation failed:")
        for name in failures:
            print(f"- {name}")
        return 1

    print("\nOK: Cursor config validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
