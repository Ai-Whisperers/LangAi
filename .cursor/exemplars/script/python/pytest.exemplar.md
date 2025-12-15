# Python Pytest Unit Testing Pattern Exemplar

## Overview

pytest provides powerful unit testing with fixtures, parametrization, and excellent assertion introspection.

## When to Use

- **Use for**: Advanced quality level and above (50%+ coverage required)
- **Critical for**: Reusable functions, critical business logic

## Good Pattern ✅

```python
# test_coverage_analyzer.py
import pytest
from pathlib import Path
from coverage_analyzer import (
    CoverageAnalyzer,
    CoverageConfig,
    ThresholdError
)

@pytest.fixture
def config():
    """Provide test configuration."""
    return CoverageConfig(
        configuration="Release",
        thresholds={'line': 80, 'branch': 70}
    )

@pytest.fixture
def analyzer(config):
    """Provide analyzer instance."""
    return CoverageAnalyzer(config)

@pytest.fixture
def temp_workspace(tmp_path):
    """Provide temporary workspace."""
    workspace = tmp_path / "coverage"
    workspace.mkdir()
    return workspace


def test_threshold_validation_pass(analyzer):
    """Test threshold validation passes with good coverage."""
    results = {'line_coverage': 85, 'branch_coverage': 75}
    assert analyzer.validate_thresholds(results) is True


def test_threshold_validation_fail(analyzer):
    """Test threshold validation fails with low coverage."""
    results = {'line_coverage': 65, 'branch_coverage': 55}
    
    with pytest.raises(ThresholdError) as exc_info:
        analyzer.validate_thresholds(results)
    
    assert "line coverage" in str(exc_info.value).lower()


@pytest.mark.parametrize("line,branch,expected", [
    (85, 75, True),   # Both pass
    (65, 75, False),  # Line fails
    (85, 55, False),  # Branch fails
    (90, 85, True),   # Both exceed
])
def test_threshold_validation_parametrized(analyzer, line, branch, expected):
    """Test threshold validation with multiple scenarios."""
    results = {'line_coverage': line, 'branch_coverage': branch}
    
    if expected:
        assert analyzer.validate_thresholds(results) is True
    else:
        with pytest.raises(ThresholdError):
            analyzer.validate_thresholds(results)


# Run tests:
# pytest test_coverage_analyzer.py -v --cov=coverage_analyzer --cov-report=html
```

**Why this is good:**
- Fixtures for test setup
- Parametrized tests for multiple cases
- Clear test names
- Exception testing

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

