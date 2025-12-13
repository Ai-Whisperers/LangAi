"""Tests for time utilities."""

import pytest
from datetime import datetime, timezone, timedelta

from company_researcher.utils.time import (
    utc_now,
    format_timestamp,
    parse_timestamp,
    duration_str,
    elapsed_since,
    is_recent,
)


class TestUtcNow:
    """Tests for utc_now function."""

    def test_returns_datetime(self):
        """utc_now should return a datetime object."""
        result = utc_now()
        assert isinstance(result, datetime)

    def test_is_timezone_aware(self):
        """utc_now should return a timezone-aware datetime."""
        result = utc_now()
        assert result.tzinfo is not None

    def test_is_utc_timezone(self):
        """utc_now should be in UTC timezone."""
        result = utc_now()
        assert result.tzinfo == timezone.utc

    def test_returns_current_time(self):
        """utc_now should return approximately the current time."""
        before = datetime.now(timezone.utc)
        result = utc_now()
        after = datetime.now(timezone.utc)

        assert before <= result <= after


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_default_format(self):
        """format_timestamp with default format should work."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt)
        assert result == "2024-01-15 14:30:00"

    def test_custom_format(self):
        """format_timestamp with custom format should work."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt, format_str="%Y/%m/%d")
        assert result == "2024/01/15"

    def test_include_timezone(self):
        """format_timestamp with include_tz should append timezone."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt, include_tz=True)
        assert result == "2024-01-15 14:30:00 UTC"

    def test_none_uses_current_time(self):
        """format_timestamp with None should use current time."""
        result = format_timestamp(None)
        # Should be a valid timestamp string
        assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"

    def test_naive_datetime_no_timezone_suffix(self):
        """format_timestamp with naive datetime and include_tz should not add tz."""
        dt = datetime(2024, 1, 15, 14, 30, 0)  # naive
        result = format_timestamp(dt, include_tz=True)
        # Should not have timezone suffix since tzinfo is None
        assert result == "2024-01-15 14:30:00"


class TestParseTimestamp:
    """Tests for parse_timestamp function."""

    def test_parse_default_format(self):
        """parse_timestamp should parse default format."""
        result = parse_timestamp("2024-01-15 14:30:00")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0

    def test_assume_utc_adds_timezone(self):
        """parse_timestamp with assume_utc should add UTC timezone."""
        result = parse_timestamp("2024-01-15 14:30:00", assume_utc=True)
        assert result.tzinfo == timezone.utc

    def test_assume_utc_false_keeps_naive(self):
        """parse_timestamp with assume_utc=False should keep naive datetime."""
        result = parse_timestamp("2024-01-15 14:30:00", assume_utc=False)
        assert result.tzinfo is None

    def test_custom_format(self):
        """parse_timestamp with custom format should work."""
        result = parse_timestamp("15/01/2024", format_str="%d/%m/%Y")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_invalid_format_raises_error(self):
        """parse_timestamp with invalid format should raise ValueError."""
        with pytest.raises(ValueError):
            parse_timestamp("invalid timestamp")


class TestDurationStr:
    """Tests for duration_str function."""

    def test_sub_second(self):
        """duration_str should format sub-second durations."""
        assert duration_str(0.5) == "0.5s"
        assert duration_str(0.1) == "0.1s"

    def test_seconds_only(self):
        """duration_str should format seconds-only durations."""
        assert duration_str(45) == "45s"
        assert duration_str(1) == "1s"

    def test_minutes_and_seconds(self):
        """duration_str should format minutes and seconds."""
        assert duration_str(65) == "1m 5s"
        assert duration_str(120) == "2m"

    def test_hours_minutes_seconds(self):
        """duration_str should format hours, minutes, and seconds."""
        assert duration_str(3665) == "1h 1m 5s"
        assert duration_str(3600) == "1h"

    def test_zero(self):
        """duration_str should handle zero (treated as sub-second)."""
        assert duration_str(0) == "0.0s"

    def test_negative(self):
        """duration_str should handle negative durations."""
        assert duration_str(-65) == "-1m 5s"

    def test_exact_hour(self):
        """duration_str should handle exact hours."""
        assert duration_str(7200) == "2h"

    def test_exact_minute(self):
        """duration_str should handle exact minutes."""
        assert duration_str(300) == "5m"


class TestElapsedSince:
    """Tests for elapsed_since function."""

    def test_none_returns_zero(self):
        """elapsed_since with None should return 0.0."""
        assert elapsed_since(None) == pytest.approx(0.0)

    def test_calculates_elapsed_time(self):
        """elapsed_since should calculate elapsed seconds."""
        start = utc_now() - timedelta(seconds=10)
        result = elapsed_since(start)
        # Allow some tolerance for test execution time
        assert 9.9 <= result <= 10.5

    def test_naive_datetime_assumed_utc(self):
        """elapsed_since should handle naive datetime as UTC."""
        # Create a naive datetime (without timezone info) for testing
        start = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=5)
        result = elapsed_since(start)
        assert 4.9 <= result <= 5.5

    def test_recent_time(self):
        """elapsed_since with very recent time should be small."""
        start = utc_now()
        result = elapsed_since(start)
        assert result < 1.0


class TestIsRecent:
    """Tests for is_recent function."""

    def test_none_returns_false(self):
        """is_recent with None should return False."""
        assert is_recent(None) is False

    def test_current_time_is_recent(self):
        """is_recent with current time should return True."""
        assert is_recent(utc_now()) is True

    def test_old_time_not_recent(self):
        """is_recent with old time should return False."""
        old = utc_now() - timedelta(hours=2)
        assert is_recent(old) is False

    def test_custom_max_age(self):
        """is_recent with custom max_age should work."""
        recent = utc_now() - timedelta(seconds=30)
        old = utc_now() - timedelta(seconds=120)

        assert is_recent(recent, max_age_seconds=60) is True
        assert is_recent(old, max_age_seconds=60) is False

    def test_edge_case_exactly_at_max_age(self):
        """is_recent at exactly max_age should return True (<=)."""
        # Due to execution time, we test close to max_age
        dt = utc_now() - timedelta(seconds=3599)
        assert is_recent(dt, max_age_seconds=3600) is True
