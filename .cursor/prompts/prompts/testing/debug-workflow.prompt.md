---
name: debug-workflow
description: "Systematic debug workflow: syntax, imports, lint, types, tests (repo-appropriate)."
category: testing
tags: debugging, pytest, ruff, mypy
argument-hint: "Optional: target module or test path (e.g., src/company_researcher or tests/unit)"
---

# Debug workflow (systematic)

Use this when you hit unexpected errors or failing tests and want a deterministic triage sequence.

## Steps (run in order)

### 1) Syntax check

```powershell
python -m compileall src tests
```

### 2) Import sanity check

```powershell
python -c "import company_researcher; print('ok')"
```

### 3) Lint (Ruff)

```powershell
ruff check src tests
```

### 4) Types (mypy, if configured)

```powershell
mypy src
```

### 5) Tests

```powershell
$env:PYTHONPATH = "."
python -m pytest tests -v --tb=short
```

## Common failure patterns

- **ModuleNotFoundError**: `PYTHONPATH` / environment mismatch. Prefer running from repo root.
- **Missing optional deps**: install extras or guard imports with clear error messages.
- **Network/API failures**: ensure tests are using mocks (avoid real external calls).
