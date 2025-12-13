"""Tests for safe operation utilities."""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock

from company_researcher.utils.safe_ops import (
    safe_get,
    safe_json_parse,
    safe_execute,
    safe_execute_async,
    safe_int,
    safe_float,
)


class TestSafeGet:
    """Tests for safe_get function."""

    def test_simple_dict_access(self):
        """safe_get should access dict keys."""
        data = {"key": "value"}
        assert safe_get(data, "key") == "value"

    def test_nested_dict_access(self):
        """safe_get should access nested dict keys."""
        data = {"user": {"name": "John", "age": 30}}
        assert safe_get(data, ["user", "name"]) == "John"
        assert safe_get(data, ["user", "age"]) == 30

    def test_list_access(self):
        """safe_get should access list items by index."""
        data = {"items": [10, 20, 30]}
        assert safe_get(data, ["items", 0]) == 10
        assert safe_get(data, ["items", 1]) == 20
        assert safe_get(data, ["items", 2]) == 30

    def test_missing_key_returns_default(self):
        """safe_get should return default for missing key."""
        data = {"key": "value"}
        assert safe_get(data, "missing") is None
        assert safe_get(data, "missing", "default") == "default"

    def test_nested_missing_key_returns_default(self):
        """safe_get should return default for missing nested key."""
        data = {"user": {"name": "John"}}
        assert safe_get(data, ["user", "missing"], "default") == "default"
        assert safe_get(data, ["missing", "nested"], "default") == "default"

    def test_none_data_returns_default(self):
        """safe_get should return default when data is None."""
        assert safe_get(None, "key") is None
        assert safe_get(None, "key", "default") == "default"

    def test_index_out_of_range_returns_default(self):
        """safe_get should return default for out of range index."""
        data = {"items": [1, 2, 3]}
        assert safe_get(data, ["items", 10], "default") == "default"

    def test_none_value_returns_default(self):
        """safe_get should return default when value is None."""
        data = {"key": None}
        assert safe_get(data, "key", "default") == "default"

    def test_deeply_nested_access(self):
        """safe_get should handle deep nesting."""
        data = {"a": {"b": {"c": {"d": "deep"}}}}
        assert safe_get(data, ["a", "b", "c", "d"]) == "deep"

    def test_mixed_dict_list_access(self):
        """safe_get should handle mixed dict/list access."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        assert safe_get(data, ["users", 0, "name"]) == "Alice"
        assert safe_get(data, ["users", 1, "name"]) == "Bob"


class TestSafeJsonParse:
    """Tests for safe_json_parse function."""

    def test_valid_json_object(self):
        """safe_json_parse should parse valid JSON object."""
        result = safe_json_parse('{"key": "value"}')
        assert result == {"key": "value"}

    def test_valid_json_array(self):
        """safe_json_parse should parse valid JSON array."""
        result = safe_json_parse('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_valid_json_primitives(self):
        """safe_json_parse should parse JSON primitives."""
        assert safe_json_parse('"string"') == "string"
        assert safe_json_parse('123') == 123
        assert safe_json_parse('true') is True
        assert safe_json_parse('null') is None

    def test_invalid_json_returns_default(self):
        """safe_json_parse should return default for invalid JSON."""
        assert safe_json_parse("invalid json") is None
        assert safe_json_parse("invalid json", default={}) == {}
        assert safe_json_parse("{broken", default=[]) == []

    def test_none_input_returns_default(self):
        """safe_json_parse should return default for None input."""
        assert safe_json_parse(None) is None
        assert safe_json_parse(None, default=[]) == []

    def test_non_string_input_returns_default(self):
        """safe_json_parse should return default for non-string input."""
        assert safe_json_parse(123) is None
        assert safe_json_parse({"key": "value"}) is None

    def test_empty_string_returns_default(self):
        """safe_json_parse should return default for empty string."""
        assert safe_json_parse("") is None
        assert safe_json_parse("", default={}) == {}


class TestSafeExecute:
    """Tests for safe_execute function."""

    def test_successful_execution(self):
        """safe_execute should return function result on success."""
        result = safe_execute(lambda: 42)
        assert result == 42

    def test_with_arguments(self):
        """safe_execute should pass arguments to function."""
        result = safe_execute(lambda x, y: x + y, 3, 4)
        assert result == 7

    def test_with_kwargs(self):
        """safe_execute should pass kwargs to function."""
        def func(a, b=10):
            return a * b
        result = safe_execute(func, 5, b=3)
        assert result == 15

    def test_exception_returns_default(self):
        """safe_execute should return default on exception."""
        def failing():
            raise ValueError("error")
        result = safe_execute(failing, default="fallback")
        assert result == "fallback"

    def test_exception_returns_none_by_default(self):
        """safe_execute should return None when no default specified."""
        def failing():
            raise RuntimeError()
        result = safe_execute(failing)
        assert result is None

    def test_log_errors_true(self):
        """safe_execute should log errors when log_errors=True."""
        def failing():
            raise ValueError("test error")

        with patch("company_researcher.utils.safe_ops.logger") as mock_logger:
            safe_execute(failing, log_errors=True)
            mock_logger.error.assert_called_once()

    def test_log_errors_false(self):
        """safe_execute should not log when log_errors=False."""
        def failing():
            raise ValueError("test error")

        with patch("company_researcher.utils.safe_ops.logger") as mock_logger:
            safe_execute(failing, log_errors=False)
            mock_logger.error.assert_not_called()

    def test_custom_error_message(self):
        """safe_execute should use custom error message."""
        def failing():
            raise ValueError("test error")

        with patch("company_researcher.utils.safe_ops.logger") as mock_logger:
            safe_execute(failing, error_message="Custom error")
            args = mock_logger.error.call_args[0][0]
            assert "Custom error" in args


class TestSafeExecuteAsync:
    """Tests for safe_execute_async function."""

    @pytest.mark.asyncio
    async def test_successful_async_execution(self):
        """safe_execute_async should return function result on success."""
        async def async_func():
            return 42
        result = await safe_execute_async(async_func)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_with_arguments(self):
        """safe_execute_async should pass arguments to async function."""
        async def async_func(x, y):
            return x + y
        result = await safe_execute_async(async_func, 3, 4)
        assert result == 7

    @pytest.mark.asyncio
    async def test_async_exception_returns_default(self):
        """safe_execute_async should return default on exception."""
        async def failing_async():
            raise ValueError("error")
        result = await safe_execute_async(failing_async, default="fallback")
        assert result == "fallback"

    @pytest.mark.asyncio
    async def test_async_log_errors(self):
        """safe_execute_async should log errors when log_errors=True."""
        async def failing_async():
            raise ValueError("test error")

        with patch("company_researcher.utils.safe_ops.logger") as mock_logger:
            await safe_execute_async(failing_async, log_errors=True)
            mock_logger.error.assert_called_once()


class TestSafeInt:
    """Tests for safe_int function."""

    def test_valid_int_string(self):
        """safe_int should convert valid int string."""
        assert safe_int("42") == 42
        assert safe_int("-10") == -10
        assert safe_int("0") == 0

    def test_actual_int(self):
        """safe_int should handle actual int."""
        assert safe_int(42) == 42

    def test_float_truncates(self):
        """safe_int should truncate float."""
        assert safe_int(3.9) == 3
        assert safe_int(3.1) == 3

    def test_invalid_returns_default(self):
        """safe_int should return default for invalid input."""
        assert safe_int("invalid") == 0
        assert safe_int("invalid", default=-1) == -1

    def test_none_returns_default(self):
        """safe_int should return default for None."""
        assert safe_int(None) == 0
        assert safe_int(None, default=5) == 5

    def test_empty_string_returns_default(self):
        """safe_int should return default for empty string."""
        assert safe_int("") == 0


class TestSafeFloat:
    """Tests for safe_float function."""

    def test_valid_float_string(self):
        """safe_float should convert valid float string."""
        assert safe_float("3.14") == pytest.approx(3.14)
        assert safe_float("-2.5") == pytest.approx(-2.5)
        assert safe_float("0.0") == pytest.approx(0.0)

    def test_int_string(self):
        """safe_float should convert int string to float."""
        assert safe_float("42") == pytest.approx(42.0)

    def test_actual_float(self):
        """safe_float should handle actual float."""
        assert safe_float(3.14) == pytest.approx(3.14)

    def test_actual_int_to_float(self):
        """safe_float should convert int to float."""
        assert safe_float(42) == pytest.approx(42.0)

    def test_invalid_returns_default(self):
        """safe_float should return default for invalid input."""
        assert safe_float("invalid") == pytest.approx(0.0)
        assert safe_float("invalid", default=1.5) == pytest.approx(1.5)

    def test_none_returns_default(self):
        """safe_float should return default for None."""
        assert safe_float(None) == pytest.approx(0.0)
        assert safe_float(None, default=2.5) == pytest.approx(2.5)
