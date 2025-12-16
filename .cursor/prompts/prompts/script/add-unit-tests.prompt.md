---
name: Add Unit Tests for Script
description: "Add unit tests for PowerShell or Python scripts using test frameworks"
category: script
tags: [testing, quality, unit-tests, pester, pytest]
---

# Add Unit Tests for Script

## Context

Add unit tests to achieve Advanced quality level (50%+ coverage required) or Production quality level (80%+ coverage required).

## Instructions

### PowerShell (Pester)

1. Install Pester: `Install-Module -Name Pester -Force`
2. Create test file: `script-name.Tests.ps1`
3. Write tests:
```powershell
Describe "Script-Name Tests" {
    It "Should validate thresholds correctly" {
        $result = Test-Threshold -Value 85 -Threshold 80
        $result | Should -Be $true
    }
}
```
4. Run: `Invoke-Pester`

### Python (pytest)

1. Install pytest: `pip install pytest pytest-cov`
2. Create test file: `test_script_name.py`
3. Write tests (see [pytest exemplar](../../exemplars/script/python/pytest.exemplar.md))
4. Run: `pytest -v --cov=script_name --cov-report=html`

## Quality Checklist

- [ ] Test file created with naming convention
- [ ] Tests for core functions
- [ ] Fixtures for test setup
- [ ] Parametrized tests for multiple scenarios
- [ ] Exception testing for error cases
- [ ] 50%+ code coverage (Advanced) or 80%+ (Production)

---
Produced-by: prompt.scripts.add-tests.v1 | ts=2025-12-07T00:00:00Z
