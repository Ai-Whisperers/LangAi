"""Centralized configuration access utility.

This module provides a standardized way to access configuration values,
eliminating inconsistent patterns like os.getenv(), config.get(), settings.KEY.

All configuration should be accessed through these utilities.

Usage:
    from company_researcher.utils import get_config, get_required_config

    # Optional config with default
    api_key = get_config("ANTHROPIC_API_KEY", default="")

    # Required config (raises if missing)
    api_key = get_required_config("ANTHROPIC_API_KEY")
"""

import os
from typing import Optional, TypeVar, Union, Callable


T = TypeVar("T")


class ConfigError(Exception):
    """Raised when a required configuration value is missing."""

    def __init__(self, key: str, message: Optional[str] = None):
        self.key = key
        if message is None:
            message = f"Required configuration '{key}' is not set"
        super().__init__(message)


def get_config(
    key: str,
    default: Optional[T] = None,
    cast: Optional[Callable[[str], T]] = None,
) -> Optional[Union[str, T]]:
    """Get a configuration value from environment variables.

    This is the standard way to access configuration in company_researcher.

    Args:
        key: The environment variable name.
        default: Default value if not set.
        cast: Optional function to cast the value (e.g., int, float, bool).

    Returns:
        The configuration value, or the default if not set.

    Example:
        >>> get_config("API_KEY", default="")
        ''
        >>> get_config("MAX_RETRIES", default=3, cast=int)
        3
        >>> get_config("DEBUG", default=False, cast=lambda x: x.lower() == "true")
        False
    """
    value = os.getenv(key)

    if value is None:
        return default

    if cast is not None:
        try:
            return cast(value)
        except (ValueError, TypeError):
            return default

    return value


def get_required_config(
    key: str,
    cast: Optional[Callable[[str], T]] = None,
) -> Union[str, T]:
    """Get a required configuration value.

    Raises ConfigError if the value is not set.

    Args:
        key: The environment variable name.
        cast: Optional function to cast the value.

    Returns:
        The configuration value.

    Raises:
        ConfigError: If the configuration value is not set.

    Example:
        >>> api_key = get_required_config("ANTHROPIC_API_KEY")
        >>> port = get_required_config("PORT", cast=int)
    """
    value = os.getenv(key)

    if value is None:
        raise ConfigError(key)

    if cast is not None:
        try:
            return cast(value)
        except (ValueError, TypeError) as e:
            raise ConfigError(
                key,
                f"Configuration '{key}' has invalid value '{value}': {e}"
            )

    return value


def get_bool_config(key: str, default: bool = False) -> bool:
    """Get a boolean configuration value.

    Recognizes 'true', '1', 'yes', 'on' as True (case-insensitive).

    Args:
        key: The environment variable name.
        default: Default value if not set.

    Returns:
        The boolean value.

    Example:
        >>> get_bool_config("DEBUG")
        False
        >>> get_bool_config("ENABLE_CACHE", default=True)
        True
    """
    value = os.getenv(key)

    if value is None:
        return default

    return value.lower() in ("true", "1", "yes", "on")


def get_int_config(key: str, default: int = 0) -> int:
    """Get an integer configuration value.

    Args:
        key: The environment variable name.
        default: Default value if not set or invalid.

    Returns:
        The integer value.

    Example:
        >>> get_int_config("MAX_RETRIES", default=3)
        3
    """
    return get_config(key, default=default, cast=int) or default


def get_float_config(key: str, default: float = 0.0) -> float:
    """Get a float configuration value.

    Args:
        key: The environment variable name.
        default: Default value if not set or invalid.

    Returns:
        The float value.

    Example:
        >>> get_float_config("TEMPERATURE", default=0.7)
        0.7
    """
    return get_config(key, default=default, cast=float) or default


def get_list_config(
    key: str,
    default: Optional[list] = None,
    separator: str = ",",
) -> list:
    """Get a list configuration value.

    Splits the value by the separator.

    Args:
        key: The environment variable name.
        default: Default value if not set.
        separator: The separator character (default: comma).

    Returns:
        A list of strings.

    Example:
        >>> # ALLOWED_HOSTS=localhost,127.0.0.1,example.com
        >>> get_list_config("ALLOWED_HOSTS")
        ['localhost', '127.0.0.1', 'example.com']
    """
    if default is None:
        default = []

    value = os.getenv(key)

    if value is None:
        return default

    return [item.strip() for item in value.split(separator) if item.strip()]
