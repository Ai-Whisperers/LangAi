# Company Researcher Python Style Guide

This document defines coding standards and patterns for the Company Researcher codebase.
Following these guidelines ensures consistency, maintainability, and readability.

## Table of Contents

1. [Naming Conventions](#naming-conventions)
2. [Import Style](#import-style)
3. [Type Annotations](#type-annotations)
4. [String Formatting](#string-formatting)
5. [Error Handling](#error-handling)
6. [Logging](#logging)
7. [Configuration Access](#configuration-access)
8. [Time Handling](#time-handling)
9. [Dictionary Access](#dictionary-access)
10. [Class Definitions](#class-definitions)
11. [Documentation](#documentation)
12. [Testing](#testing)

---

## Naming Conventions

### Variables and Functions
- Use `snake_case` for all variables and functions
- Use descriptive names that indicate purpose

```python
# Good
company_name = "Tesla"
search_results = []
def calculate_quality_score(metrics: dict) -> float:
    pass

# Bad
companyName = "Tesla"  # camelCase
sr = []  # Too short
def cqs(m):  # Unclear
    pass
```

### Classes
- Use `PascalCase` for class names
- Use nouns that describe the entity

```python
# Good
class CompanyAnalyzer:
    pass

class FinancialReport:
    pass

# Bad
class company_analyzer:  # Wrong case
    pass
```

### Constants
- Use `UPPER_SNAKE_CASE` for constants
- Define at module level

```python
# Good
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Bad
maxRetries = 3  # Wrong case
```

### Private Members
- Use single underscore prefix for internal methods/attributes
- Use double underscore only for name mangling

```python
# Good
class Agent:
    def __init__(self):
        self._cache = {}  # Internal

    def _process_data(self):  # Internal method
        pass

# Bad
class Agent:
    def __init__(self):
        self.cache = {}  # Should be private
```

---

## Import Style

### Order
1. Standard library imports
2. Third-party imports
3. Local application imports

Use blank lines to separate groups.

```python
# Good
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import anthropic
import requests
from pydantic import BaseModel

from company_researcher.utils import get_logger, utc_now
from company_researcher.config import settings
```

### Absolute vs Relative Imports
- **Prefer relative imports** within the package
- Use absolute imports for external packages

```python
# Good (within company_researcher package)
from ..config import settings
from .utils import helper

# Also Good (absolute within package)
from company_researcher.config import settings
```

### Import Format
- One import per line for long imports
- Group related imports

```python
# Good
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

# Avoid
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
```

---

## Type Annotations

### Required Locations
- All public function parameters and return types
- Class attributes
- Module-level variables

```python
# Good
def analyze_company(
    company_name: str,
    depth: int = 3,
    include_financials: bool = True,
) -> Dict[str, Any]:
    """Analyze a company."""
    pass

# Bad
def analyze_company(company_name, depth=3, include_financials=True):
    pass
```

### Type Hints Style
- Use `typing` module for compatibility
- Use `Optional[X]` instead of `X | None` for Python 3.9 compatibility

```python
# Good
from typing import Dict, List, Optional, Union

def process(data: Optional[Dict[str, Any]] = None) -> List[str]:
    pass

# Also acceptable (Python 3.10+)
def process(data: dict[str, Any] | None = None) -> list[str]:
    pass
```

---

## String Formatting

### Use f-strings Exclusively
- f-strings are fastest and most readable
- Avoid `.format()`, `%` formatting, and concatenation

```python
# Good
message = f"Processing {company_name} with {num_queries} queries"
log_message = f"Error in {func_name}: {error}"

# Bad
message = "Processing {} with {} queries".format(company_name, num_queries)
message = "Processing %s with %d queries" % (company_name, num_queries)
message = "Processing " + company_name + " with " + str(num_queries) + " queries"
```

---

## Error Handling

### Catch Specific Exceptions
- Never use bare `except:`
- Catch the most specific exception possible

```python
# Good
try:
    data = json.loads(response_text)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    return None

# Bad
try:
    data = json.loads(response_text)
except Exception:
    return None  # Too broad, hides real errors
```

### Use Custom Exceptions
- Define domain-specific exceptions
- Include relevant context

```python
# Good
class CompanyNotFoundError(Exception):
    def __init__(self, company_name: str):
        self.company_name = company_name
        super().__init__(f"Company not found: {company_name}")

# Usage
raise CompanyNotFoundError(company_name)
```

### Standard Error Handling Pattern
Use the centralized safe operations:

```python
from company_researcher.utils import safe_execute, safe_json_parse

# Good
result = safe_execute(risky_function, default=None, log_errors=True)
data = safe_json_parse(json_string, default={})
```

---

## Logging

### Use Centralized Logger
- Always use `get_logger()` from utils
- Never use `print()` for debugging

```python
# Good
from company_researcher.utils import get_logger

logger = get_logger(__name__)

def process():
    logger.info("Starting process")
    logger.debug("Debug details: %s", details)
    logger.error("Error occurred", exc_info=True)

# Bad
import logging
logger = logging.getLogger(__name__)  # Inconsistent

print("Debug:", value)  # Never use print
```

### Log Levels
- `DEBUG`: Detailed diagnostic info
- `INFO`: General operational events
- `WARNING`: Unexpected but handled situations
- `ERROR`: Errors that need attention
- `CRITICAL`: System-threatening issues

---

## Configuration Access

### Use Centralized Config Utils

```python
# Good
from company_researcher.utils import get_config, get_required_config

api_key = get_required_config("ANTHROPIC_API_KEY")
max_retries = get_config("MAX_RETRIES", default=3, cast=int)
debug = get_config("DEBUG", default=False, cast=lambda x: x.lower() == "true")

# Bad
import os
api_key = os.getenv("ANTHROPIC_API_KEY")  # No validation
api_key = os.environ["ANTHROPIC_API_KEY"]  # Crashes if missing
```

---

## Time Handling

### Use UTC Consistently
- All timestamps should be UTC
- Use timezone-aware datetimes

```python
# Good
from company_researcher.utils import utc_now, format_timestamp, duration_str

start_time = utc_now()
# ... do work ...
elapsed = (utc_now() - start_time).total_seconds()
logger.info(f"Completed in {duration_str(elapsed)}")

# Bad
from datetime import datetime
start_time = datetime.now()  # Local time, not UTC
start_time = datetime.utcnow()  # UTC but naive (no timezone)
```

---

## Dictionary Access

### Use Safe Access Patterns

```python
# Good
from company_researcher.utils import safe_get

value = safe_get(data, "key", default="fallback")
nested = safe_get(data, ["level1", "level2", "key"], default=None)

# Also Good
value = data.get("key", "fallback")

# Bad
value = data["key"]  # KeyError if missing
```

---

## Class Definitions

### Prefer Pydantic for Data Classes

```python
# Good - For data models
from pydantic import BaseModel, Field

class CompanyData(BaseModel):
    name: str
    ticker: Optional[str] = None
    revenue: float = Field(ge=0)

# Good - For simple data containers
from dataclasses import dataclass

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str

# Avoid mixing patterns for similar purposes
```

### TypedDict for State

```python
# Good - For LangGraph state
from typing import TypedDict, Annotated
from operator import add

class OverallState(TypedDict, total=False):
    company_name: str
    search_results: Annotated[list, add]
    quality_score: float
```

---

## Documentation

### Docstring Style: Google Format

```python
def analyze_company(
    company_name: str,
    depth: int = 3,
) -> Dict[str, Any]:
    """Analyze a company and return comprehensive data.

    Performs multi-source research including financial data,
    news analysis, and competitive positioning.

    Args:
        company_name: The name of the company to analyze.
        depth: Search depth (1-5). Higher values = more thorough.

    Returns:
        A dictionary containing:
            - 'financials': Financial metrics and ratios
            - 'news': Recent news sentiment analysis
            - 'competitors': List of identified competitors

    Raises:
        CompanyNotFoundError: If the company cannot be identified.
        APIError: If external API calls fail.

    Example:
        >>> result = analyze_company("Tesla", depth=3)
        >>> print(result['financials']['revenue'])
        81462000000
    """
    pass
```

---

## Testing

### Test File Structure

```
tests/
├── unit/
│   ├── agents/
│   │   └── test_analyst.py
│   └── utils/
│       └── test_safe_ops.py
├── integration/
│   └── test_workflow.py
└── conftest.py
```

### Test Naming

```python
# Good - Descriptive test names
def test_analyze_company_returns_financial_data():
    pass

def test_analyze_company_raises_on_invalid_name():
    pass

# Bad
def test_1():
    pass

def test_analyze():
    pass
```

---

## Quick Reference

| Pattern | Standard | Example |
|---------|----------|---------|
| Logger | `get_logger(__name__)` | `from company_researcher.utils import get_logger` |
| Config | `get_config("KEY")` | `from company_researcher.utils import get_config` |
| Time | `utc_now()` | `from company_researcher.utils import utc_now` |
| Safe access | `safe_get(data, "key")` | `from company_researcher.utils import safe_get` |
| Strings | f-strings | `f"Value: {value}"` |
| Types | typing module | `from typing import Dict, Optional` |
| Exceptions | Specific catches | `except ValueError as e:` |

---

## Enforcement

These standards are enforced by:

1. **Pre-commit hooks** - Automatic formatting and linting
2. **CI/CD pipeline** - Type checking and tests
3. **Code review** - Manual verification

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```
