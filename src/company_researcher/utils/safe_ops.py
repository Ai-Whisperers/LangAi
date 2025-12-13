"""Safe operation utilities for consistent error handling.

This module provides standardized safe operations that handle errors
gracefully, eliminating inconsistent try/except patterns across the codebase.

Usage:
    from company_researcher.utils import get_logger, safe_execute, safe_get, safe_json_parse

    # Safe dictionary access
    value = safe_get(data, "key", "default")
    value = safe_get(data, ["nested", "key"], default=None)

    # Safe JSON parsing
    data = safe_json_parse(json_string, default={})

    # Safe function execution
    result = safe_execute(risky_function, default=None, log_errors=True)
"""

import json
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from .logger import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


def safe_get(
    data: Union[Dict, List, Any],
    keys: Union[str, int, List[Union[str, int]]],
    default: Optional[T] = None,
) -> Union[Any, T]:
    """Safely get a value from a nested data structure.

    Handles None, missing keys, and index errors gracefully.

    Args:
        data: The data structure to access.
        keys: A single key or list of keys for nested access.
        default: Value to return if the key path doesn't exist.

    Returns:
        The value at the key path, or the default if not found.

    Example:
        >>> data = {"user": {"name": "John", "scores": [10, 20, 30]}}
        >>> safe_get(data, "user")
        {'name': 'John', 'scores': [10, 20, 30]}
        >>> safe_get(data, ["user", "name"])
        'John'
        >>> safe_get(data, ["user", "scores", 1])
        20
        >>> safe_get(data, ["user", "missing"], "default")
        'default'
        >>> safe_get(None, "key", "default")
        'default'
    """
    if data is None:
        return default

    # Convert single key to list
    if not isinstance(keys, list):
        keys = [keys]

    current = data
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, (list, tuple)) and isinstance(key, int):
                current = current[key]
            else:
                return default

            if current is None:
                return default
        except (KeyError, IndexError, TypeError):
            return default

    return current


def safe_json_parse(
    text: str,
    default: Optional[T] = None,
    strict: bool = False,
) -> Union[Any, T]:
    """Safely parse a JSON string.

    Args:
        text: The JSON string to parse.
        default: Value to return if parsing fails.
        strict: If True, don't allow control characters.

    Returns:
        The parsed JSON data, or the default if parsing fails.

    Example:
        >>> safe_json_parse('{"key": "value"}')
        {'key': 'value'}
        >>> safe_json_parse('invalid json', default={})
        {}
        >>> safe_json_parse(None, default=[])
        []
    """
    if text is None:
        return default

    if not isinstance(text, str):
        return default

    try:
        return json.loads(text, strict=strict)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default


def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    log_errors: bool = True,
    error_message: Optional[str] = None,
    **kwargs,
) -> Union[T, None]:
    """Safely execute a function, catching exceptions.

    This provides a standardized way to handle errors in function calls.

    Args:
        func: The function to execute.
        *args: Positional arguments to pass to the function.
        default: Value to return if the function raises an exception.
        log_errors: Whether to log errors (default: True).
        error_message: Custom error message prefix.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The function's return value, or the default if an error occurred.

    Example:
        >>> def risky():
        ...     raise ValueError("oops")
        >>> safe_execute(risky, default="fallback")
        'fallback'
        >>> safe_execute(lambda x: x * 2, 5)
        10
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            func_name = getattr(func, "__name__", str(func))
            msg = error_message or f"Error in {func_name}"
            logger.error(f"{msg}: {e}")
        return default


async def safe_execute_async(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    log_errors: bool = True,
    error_message: Optional[str] = None,
    **kwargs,
) -> Union[T, None]:
    """Safely execute an async function, catching exceptions.

    Args:
        func: The async function to execute.
        *args: Positional arguments to pass to the function.
        default: Value to return if the function raises an exception.
        log_errors: Whether to log errors (default: True).
        error_message: Custom error message prefix.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The function's return value, or the default if an error occurred.

    Example:
        >>> async def risky_async():
        ...     raise ValueError("oops")
        >>> await safe_execute_async(risky_async, default="fallback")
        'fallback'
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            func_name = getattr(func, "__name__", str(func))
            msg = error_message or f"Error in {func_name}"
            logger.error(f"{msg}: {e}")
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int.

    Args:
        value: The value to convert.
        default: Default if conversion fails.

    Returns:
        The integer value, or default if conversion fails.

    Example:
        >>> safe_int("42")
        42
        >>> safe_int("invalid", default=-1)
        -1
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float.

    Args:
        value: The value to convert.
        default: Default if conversion fails.

    Returns:
        The float value, or default if conversion fails.

    Example:
        >>> safe_float("3.14")
        3.14
        >>> safe_float("invalid", default=0.0)
        0.0
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
