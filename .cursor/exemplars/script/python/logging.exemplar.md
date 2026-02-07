# Python Structured Logging Pattern Exemplar

## Overview

Python's `logging` module provides structured logging with levels, handlers, and formatters for professional-grade scripts.

## When to Use

- **Use for**: Standard quality level and above, production scripts, complex workflows
- **Critical for**: Debugging, operational visibility, CI/CD diagnostics
- **Skip for**: Simple scripts where print() is sufficient

## Good Pattern ✅

```python
import logging
import sys
import os
from pathlib import Path

def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Configure structured logging with console and file handlers.

    Args:
        verbose: Enable debug logging
        log_file: Optional file path for log output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('coverage_analyzer')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Format: [2025-12-07 14:30:15] [INFO] Message
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler with detailed format (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    # Azure Pipelines integration
    if os.getenv('AGENT_TEMPDIRECTORY'):
        azure_handler = AzurePipelinesHandler()
        logger.addHandler(azure_handler)

    return logger


class AzurePipelinesHandler(logging.Handler):
    """Custom handler for Azure Pipelines logging commands."""

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            print(f"##vso[task.logissue type=error]{record.getMessage()}")
        elif record.levelno >= logging.WARNING:
            print(f"##vso[task.logissue type=warning]{record.getMessage()}")


# Usage:
logger = setup_logging(verbose=args.verbose, log_file=Path("coverage.log"))

logger.info("Starting coverage analysis")
logger.warning("Coverage below threshold")
logger.error("Build failed")
logger.debug(f"Processing package: {package_name}")
```

**Why this is good:**
- **Severity levels**: INFO, WARNING, ERROR, DEBUG clearly separated
- **Multiple handlers**: Console (colored), file (detailed), Azure Pipelines
- **Configurable verbosity**: DEBUG only shown with --verbose
- **Timestamps**: Every message includes when it occurred
- **Structured format**: Consistent, parseable log format

## Bad Pattern ❌

```python
# ❌ Just print statements
print("Starting analysis")
print("Warning: Coverage is low")
print("Error: Failed!")

# ❌ No timestamps
# ❌ No levels
# ❌ No file logging
# ❌ No Azure Pipelines integration
```

**Why this is bad:**
- **No structure**: Can't filter by level or parse programmatically
- **No timestamps**: Can't correlate events or measure duration
- **No file logging**: Logs lost after execution
- **CI/CD unfriendly**: Errors don't surface in pipeline UI

## Performance Characteristics

- **Minimal overhead**: <1ms per log statement
- **Lazy evaluation**: Use f-strings only when logging level matches
- **Handler efficiency**: Multiple handlers add minimal cost

## Related Patterns

- [Error Handling](../powershell/error-handling.exemplar.md) - Log errors with context
- [Type Hints](./type-hints.exemplar.md) - Type hints on setup_logging function
- See also: `rule.scripts.python-standards.v1` section "Structured Logging"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
