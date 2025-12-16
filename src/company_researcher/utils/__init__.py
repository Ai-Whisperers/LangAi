"""Centralized utilities for company_researcher.

This module provides standardized utilities to ensure consistent patterns
across the codebase, reducing code duplication and improving maintainability.

Usage:
    from company_researcher.utils import get_logger, utc_now, get_config

    logger = get_logger(__name__)
    timestamp = utc_now()
    api_key = get_config("ANTHROPIC_API_KEY")
"""

from .config import ConfigError, get_config, get_required_config
from .logger import configure_logging, get_logger
from .safe_ops import safe_execute, safe_get, safe_json_parse
from .time import (
    duration_str,
    elapsed_since,
    format_timestamp,
    get_current_date_str,
    get_current_year,
    get_date_filter_query,
    get_freshness_indicator,
    get_relevant_years,
    get_year_range_str,
    is_recent,
    parse_timestamp,
    utc_now,
)

__all__ = [
    # Logger utilities
    "get_logger",
    "configure_logging",
    # Time utilities
    "utc_now",
    "format_timestamp",
    "parse_timestamp",
    "duration_str",
    "elapsed_since",
    "is_recent",
    # Research-specific time utilities
    "get_current_year",
    "get_current_date_str",
    "get_relevant_years",
    "get_year_range_str",
    "get_date_filter_query",
    "get_freshness_indicator",
    # Config utilities
    "get_config",
    "get_required_config",
    "ConfigError",
    # Safe operations
    "safe_get",
    "safe_json_parse",
    "safe_execute",
]
