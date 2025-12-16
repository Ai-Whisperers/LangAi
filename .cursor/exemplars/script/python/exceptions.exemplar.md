# Python Custom Exception Hierarchy Pattern Exemplar

## Overview

Custom exception hierarchy provides domain-specific error handling with clear error types and contexts.

## When to Use

- **Use for**: Advanced quality level scripts, clear error semantics
- **Critical for**: Libraries, complex workflows with multiple failure modes

## Good Pattern ✅

```python
class CoverageError(Exception):
    """Base exception for coverage analysis errors."""
    pass

class ConfigurationError(CoverageError):
    """Configuration is invalid or missing."""
    pass

class ThresholdError(CoverageError):
    """Coverage threshold not met."""

    def __init__(self, metric: str, actual: float, threshold: float):
        self.metric = metric
        self.actual = actual
        self.threshold = threshold
        super().__init__(
            f"{metric} coverage ({actual:.2f}%) below threshold ({threshold}%)"
        )

class BuildError(CoverageError):
    """Build or test execution failed."""
    pass

# Usage:
def validate_thresholds(results: Dict, thresholds: Dict):
    """Validate coverage against thresholds."""

    if results['line_coverage'] < thresholds['line']:
        raise ThresholdError('line', results['line_coverage'], thresholds['line'])

    if results['branch_coverage'] < thresholds['branch']:
        raise ThresholdError('branch', results['branch_coverage'], thresholds['branch'])

try:
    validate_thresholds(results, config.thresholds)
    return 0

except ThresholdError as e:
    logger.error(str(e))
    return 1

except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    return 2

except CoverageError as e:
    logger.error(f"Coverage analysis error: {e}")
    return 4
```

**Why this is good:**
- Clear exception hierarchy
- Domain-specific errors
- Structured error data
- Exit code mapping

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
