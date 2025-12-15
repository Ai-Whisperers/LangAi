# Python Context Managers Pattern Exemplar

## Overview

Context managers with `@contextmanager` decorator provide automatic resource cleanup and setup/teardown patterns.

## When to Use

- **Use for**: Resource management, temporary files, database connections
- **Critical for**: Ensuring cleanup happens even on errors

## Good Pattern ✅

```python
from contextlib import contextmanager
import tempfile
import shutil
from pathlib import Path

@contextmanager
def temporary_workspace(prefix: str = "coverage_"):
    """
    Create temporary workspace with automatic cleanup.
    
    Example:
        with temporary_workspace() as workspace:
            coverage_file = workspace / "coverage.xml"
            # Work with files...
        # Automatic cleanup after block
    """
    workspace = Path(tempfile.mkdtemp(prefix=prefix))
    logger.debug(f"Created temporary workspace: {workspace}")
    
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
        logger.debug(f"Cleaned up workspace: {workspace}")

@contextmanager
def coverage_session(config: CoverageConfig):
    """Context manager for coverage analysis session."""
    session = CoverageSession(config)
    
    try:
        session.setup()
        yield session
    except Exception as e:
        logger.error(f"Coverage session failed: {e}")
        raise
    finally:
        session.cleanup()

# Usage:
with temporary_workspace() as workspace:
    results_file = workspace / "results.json"
    # Work with files
    # Automatic cleanup on exit

with coverage_session(config) as session:
    results = session.analyze()
    # Automatic cleanup on exit or exception
```

**Why this is good:**
- Automatic cleanup (finally block)
- Works with exceptions
- Clean, readable syntax
- No resource leaks

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

