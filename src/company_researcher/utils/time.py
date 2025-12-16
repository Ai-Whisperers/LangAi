"""Centralized time and date utilities.

This module provides standardized time handling across the codebase,
eliminating inconsistent patterns like datetime.now() vs datetime.utcnow()
vs time.time().

All times should be in UTC by default for consistency.

Usage:
    from company_researcher.utils import utc_now, format_timestamp, duration_str

    start = utc_now()
    # ... do work ...
    elapsed = (utc_now() - start).total_seconds()
    logger.info(f"Completed in {duration_str(elapsed)}")
"""

from datetime import datetime, timezone
from typing import Optional, Union


def utc_now() -> datetime:
    """Get the current UTC timestamp.

    This is the standard way to get the current time in company_researcher.
    Always returns a timezone-aware datetime in UTC.

    Returns:
        A timezone-aware datetime object in UTC.

    Example:
        >>> timestamp = utc_now()
        >>> print(timestamp.tzinfo)  # UTC
    """
    return datetime.now(timezone.utc)


def format_timestamp(
    dt: Optional[datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    include_tz: bool = False,
) -> str:
    """Format a datetime as a string.

    Args:
        dt: The datetime to format. If None, uses current UTC time.
        format_str: The format string (default: ISO-like).
        include_tz: Whether to include timezone info.

    Returns:
        A formatted timestamp string.

    Example:
        >>> format_timestamp()
        '2024-01-15 14:30:00'
        >>> format_timestamp(include_tz=True)
        '2024-01-15 14:30:00 UTC'
    """
    if dt is None:
        dt = utc_now()

    result = dt.strftime(format_str)

    if include_tz and dt.tzinfo is not None:
        result += f" {dt.tzname()}"

    return result


def parse_timestamp(
    timestamp_str: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    assume_utc: bool = True,
) -> datetime:
    """Parse a timestamp string into a datetime.

    Args:
        timestamp_str: The timestamp string to parse.
        format_str: The expected format string.
        assume_utc: If True, assumes UTC for naive datetimes.

    Returns:
        A datetime object, timezone-aware if assume_utc is True.

    Raises:
        ValueError: If the string cannot be parsed.

    Example:
        >>> parse_timestamp("2024-01-15 14:30:00")
        datetime.datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
    """
    dt = datetime.strptime(timestamp_str, format_str)

    if assume_utc and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def duration_str(seconds: Union[int, float]) -> str:
    """Format a duration in seconds as a human-readable string.

    Args:
        seconds: The duration in seconds.

    Returns:
        A human-readable duration string.

    Example:
        >>> duration_str(65)
        '1m 5s'
        >>> duration_str(3665)
        '1h 1m 5s'
        >>> duration_str(0.5)
        '0.5s'
    """
    if seconds < 0:
        return f"-{duration_str(abs(seconds))}"

    if seconds < 1:
        return f"{seconds:.1f}s"

    seconds = int(seconds)

    parts = []

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def elapsed_since(start_time: Optional[datetime]) -> float:
    """Calculate seconds elapsed since a start time.

    Handles None gracefully by returning 0.0.

    Args:
        start_time: The start timestamp, or None.

    Returns:
        Seconds elapsed, or 0.0 if start_time is None.

    Example:
        >>> start = utc_now()
        >>> # ... do work ...
        >>> elapsed = elapsed_since(start)
    """
    if start_time is None:
        return 0.0

    now = utc_now()

    # Handle timezone-naive datetimes
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)

    return (now - start_time).total_seconds()


def is_recent(
    dt: Optional[datetime],
    max_age_seconds: float = 3600,
) -> bool:
    """Check if a datetime is within the specified age.

    Args:
        dt: The datetime to check.
        max_age_seconds: Maximum age in seconds (default: 1 hour).

    Returns:
        True if the datetime is within max_age_seconds of now.

    Example:
        >>> is_recent(utc_now())
        True
        >>> is_recent(utc_now() - timedelta(hours=2))
        False
    """
    if dt is None:
        return False

    return elapsed_since(dt) <= max_age_seconds


# ==============================================================================
# Research-Specific Time Utilities
# ==============================================================================


def get_current_year() -> int:
    """Get the current year.

    Returns:
        Current year as integer (e.g., 2024)

    Example:
        >>> year = get_current_year()
        >>> print(year)  # 2024
    """
    return utc_now().year


def get_current_date_str(format_str: str = "%Y-%m-%d") -> str:
    """Get current date as a formatted string.

    Args:
        format_str: Date format string.

    Returns:
        Formatted date string.

    Example:
        >>> get_current_date_str()
        '2024-12-12'
    """
    return utc_now().strftime(format_str)


def get_relevant_years(
    depth: str = "standard",
    include_current: bool = True,
) -> list[int]:
    """Get relevant years for research based on depth.

    Different research depths require different historical context:
    - "basic": Current year only
    - "standard": Current + 1 previous year
    - "deep": Current + 2 previous years
    - "comprehensive": Current + 3 previous years

    Args:
        depth: Research depth level
        include_current: Whether to include current year

    Returns:
        List of relevant years (most recent first)

    Example:
        >>> get_relevant_years("standard")  # In 2024
        [2024, 2023]
        >>> get_relevant_years("deep")
        [2024, 2023, 2022]
    """
    current_year = get_current_year()

    depth_to_years = {
        "basic": 0,
        "standard": 1,
        "deep": 2,
        "comprehensive": 3,
    }

    num_previous = depth_to_years.get(depth, 1)

    years = []
    if include_current:
        years.append(current_year)

    for i in range(1, num_previous + 1):
        years.append(current_year - i)

    return years


def get_year_range_str(years: list[int]) -> str:
    """Convert list of years to a search-friendly range string.

    Args:
        years: List of years

    Returns:
        String like "2023-2024" or "2024"

    Example:
        >>> get_year_range_str([2024, 2023])
        '2023-2024'
        >>> get_year_range_str([2024])
        '2024'
    """
    if not years:
        return str(get_current_year())

    if len(years) == 1:
        return str(years[0])

    min_year = min(years)
    max_year = max(years)

    return f"{min_year}-{max_year}"


def get_date_filter_query(year: Optional[int] = None) -> str:
    """Get a date filter string for search queries.

    Args:
        year: Specific year to filter for. If None, uses current year.

    Returns:
        Date filter string like "2024" or "after:2023"

    Example:
        >>> get_date_filter_query()  # Current year is 2024
        '2024'
        >>> get_date_filter_query(2023)
        '2023'
    """
    if year is None:
        year = get_current_year()
    return str(year)


def get_freshness_indicator(field_type: str) -> str:
    """Get appropriate freshness indicator for different data types.

    Some fields need current data, others benefit from historical context.

    Args:
        field_type: Type of field being researched

    Returns:
        Year string or range appropriate for the field

    Example:
        >>> get_freshness_indicator("ceo")
        '2024'  # Need current CEO
        >>> get_freshness_indicator("revenue")
        '2023-2024'  # Financial data may lag
        >>> get_freshness_indicator("history")
        ''  # No date filter for history
    """
    current_year = get_current_year()
    prev_year = current_year - 1

    # Fields that need absolutely current data
    current_only = {
        "ceo",
        "leadership",
        "management",
        "executives",
        "headquarters",
        "employees",
        "headcount",
    }

    # Fields where data may lag by a year (financial reports)
    financial_lag = {
        "revenue",
        "profit",
        "earnings",
        "financial",
        "market_share",
        "subscribers",
        "arpu",
        "ebitda",
        "margin",
        "growth",
    }

    # Fields that don't need date filtering
    no_date = {
        "history",
        "founded",
        "origin",
        "background",
        "overview",
        "about",
    }

    field_lower = field_type.lower()

    for field in current_only:
        if field in field_lower:
            return str(current_year)

    for field in financial_lag:
        if field in field_lower:
            return f"{prev_year}-{current_year}"

    for field in no_date:
        if field in field_lower:
            return ""

    # Default: current year
    return str(current_year)
