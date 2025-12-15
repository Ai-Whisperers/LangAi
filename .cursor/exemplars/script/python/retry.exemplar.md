# Python Retry Decorator Pattern Exemplar

## Overview

Retry decorator with exponential backoff automatically handles transient failures for network operations, API calls, and external services.

## When to Use

- **Use for**: Advanced quality level scripts, network operations, API calls
- **Critical for**: Production scripts, unreliable networks, cloud services
- **Skip for**: Local operations, deterministic errors, non-idempotent operations

## Good Pattern ✅

```python
import functools
import time
from typing import Callable, TypeVar, Type

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    delay: int = 5,
    backoff: int = 2,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay in seconds
        backoff: Delay multiplier for exponential backoff
        exceptions: Tuple of exception types to catch
    
    Returns:
        Decorated function with retry logic
    
    Example:
        @retry(max_attempts=3, delay=5, backoff=2)
        def fetch_data():
            return requests.get(url)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            
            return None  # Should never reach here
        
        return wrapper
    return decorator


# Usage:
@retry(max_attempts=3, delay=5, exceptions=(requests.RequestException,))
def fetch_coverage_data(url: str) -> Dict:
    """Fetch coverage data with automatic retry."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

**Why this is good:**
- **Decorator pattern**: Clean, reusable, doesn't clutter function logic
- **Exponential backoff**: Delays increase (5s, 10s, 20s) reducing server load
- **Configurable**: Customize attempts, delay, backoff, exception types
- **Type hints**: Full type safety with generics
- **Preserves function metadata**: `@functools.wraps` keeps __name__, __doc__

## Bad Pattern ❌

```python
# ❌ Manual retry with fixed delay
def fetch_data(url):
    for attempt in range(3):
        try:
            return requests.get(url)
        except Exception:
            time.sleep(5)  # Fixed delay - not exponential
    raise Exception("Failed after 3 attempts")

# ❌ No exponential backoff
# ❌ Catches ALL exceptions (too broad)
# ❌ No logging
# ❌ Repeated code in every function
```

**Why this is bad:**
- **Fixed delay**: Hammers server with constant retry rate
- **Too broad exception handling**: Retries non-transient errors
- **Code duplication**: Retry logic repeated in every function
- **No logging**: Can't diagnose retry behavior

## Performance Characteristics

- **Total retry time**: 3 retries at 5s, 10s, 20s = 35s max overhead
- **Success on retry**: Most transient errors resolve in 1-2 retries
- **Reduced failures**: 90%+ reduction in transient failure rate

## Related Patterns

- [Logging](./logging.exemplar.md) - Log retry attempts
- [Type Hints](./type-hints.exemplar.md) - Generic type hints for decorators
- See also: `rule.scripts.python-standards.v1` section "Retry Decorator"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

