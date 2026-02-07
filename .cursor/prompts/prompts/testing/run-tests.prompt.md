---
name: run-tests
description: "Run the project's pytest suite with repo-appropriate defaults (Windows + macOS/Linux)."
category: testing
tags: pytest, testing, validation
argument-hint: "Optional: test path (e.g., tests/unit) or pytest args (e.g., -k \"name\")"
---

# Run tests (pytest)

Run the test suite in a consistent, repo-appropriate way.

## PowerShell (Windows)

```powershell
# From repo root
$env:PYTHONPATH = "."
python -m pytest tests -v --tb=short
```

## Bash (macOS/Linux)

```bash
# From repo root
PYTHONPATH=".:${PYTHONPATH}" python -m pytest tests -v --tb=short
```

## Notes

- If you want to run a subset, pass a path or flags (e.g., `tests/unit -k "keyword"`).
- If tests require external services (Redis, etc.), start them first (see repo docs under `deploy/`).
