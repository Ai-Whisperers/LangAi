"""Centralized logging utility.

This module provides a standardized way to get loggers across the codebase,
eliminating the need for repetitive `logger = logging.getLogger(__name__)`
statements in every file.

Usage:
    from company_researcher.utils import get_logger

    logger = get_logger(__name__)
    logger.info("Processing started")
    logger.error("An error occurred", exc_info=True)
"""

import logging
import sys
from typing import Optional

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cache for configured loggers
_configured_loggers: set = set()
_root_configured = False


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a logger with the specified name.

    This is the standard way to get a logger in company_researcher.
    It ensures consistent naming and configuration.

    Args:
        name: The logger name, typically __name__ from the calling module.
        level: Optional logging level. If not provided, inherits from root.

    Returns:
        A configured logging.Logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def configure_logging(
    level: int = logging.INFO,
    format_str: str = DEFAULT_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    stream: Optional[object] = None,
) -> None:
    """Configure the root logger for the application.

    This should be called once at application startup to configure
    logging for the entire application.

    Args:
        level: The logging level (default: INFO).
        format_str: The log message format string.
        date_format: The date format string.
        stream: The output stream (default: sys.stderr).

    Example:
        >>> configure_logging(level=logging.DEBUG)
    """
    global _root_configured

    if _root_configured:
        return

    if stream is None:
        stream = sys.stderr

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add new handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter(format_str, date_format)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    _root_configured = True


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to log messages.

    Useful for adding request IDs, company names, or other context
    to all log messages from a particular component.

    Example:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {"company": "Tesla"})
        >>> logger.info("Processing")  # Logs: [Tesla] Processing
    """

    def process(self, msg: str, kwargs: dict) -> tuple:
        """Process the log message to add context."""
        extra = self.extra or {}
        prefix_parts = []

        if "company" in extra:
            prefix_parts.append(extra["company"])
        if "request_id" in extra:
            prefix_parts.append(f"req:{extra['request_id']}")

        if prefix_parts:
            prefix = f"[{' | '.join(prefix_parts)}] "
            msg = f"{prefix}{msg}"

        return msg, kwargs
