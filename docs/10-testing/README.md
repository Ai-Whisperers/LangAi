# Testing Guide

This section documents how tests are organized and how to run them in this repository.

---

## Test layout

Tests live under `tests/`:

- `tests/unit/`: unit tests (fast, no external dependencies)
- `tests/integration/`: integration tests (may exercise multiple modules)
- `tests/conftest.py`: shared fixtures and test environment setup

---

## Important defaults

`tests/conftest.py` sets sane defaults for tests:

- `ENVIRONMENT=test`
- `DEBUG=true`
- `MOCK_EXTERNAL_APIS=true` (disables external API calls by default)

If a test truly requires real API keys, it should be explicitly marked (see markers below).

---

## Running tests

### Install dependencies (once)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run all tests

```bash
pytest tests/
```

### Run with coverage

```bash
pytest tests/ --cov=src/company_researcher --cov-report=term-missing
```

### Run by marker

Markers are defined in `pytest.ini` under `[pytest]`.

```bash
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m slow
pytest tests/ -m "not slow"
pytest tests/ -m requires_api
pytest tests/ -m requires_llm
```

### Run a specific test file

```bash
pytest tests/test_quality_modules.py
```

---

## Notes for Windows

All commands above work in PowerShell as-is. If you are using a virtual environment, activate it before running `pytest`.

For convenience, you can also use the repository runner:

```powershell
.\scripts\run_tests.ps1
.\scripts\run_tests.ps1 -Suite unit
.\scripts\run_tests.ps1 -Suite integration
.\scripts\run_tests.ps1 -Coverage
```
