"""Tests for config utilities."""

import os
import pytest
from unittest.mock import patch

from company_researcher.utils.config import (
    ConfigError,
    get_config,
    get_required_config,
    get_bool_config,
    get_int_config,
    get_float_config,
    get_list_config,
)


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_default_message(self):
        """ConfigError should have default message."""
        error = ConfigError("MY_KEY")
        assert error.key == "MY_KEY"
        assert "MY_KEY" in str(error)
        assert "not set" in str(error)

    def test_custom_message(self):
        """ConfigError should accept custom message."""
        error = ConfigError("MY_KEY", "Custom error message")
        assert error.key == "MY_KEY"
        assert str(error) == "Custom error message"


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_env_value(self):
        """get_config should return environment variable value."""
        with patch.dict(os.environ, {"TEST_KEY": "test_value"}):
            result = get_config("TEST_KEY")
            assert result == "test_value"

    def test_returns_default_when_missing(self):
        """get_config should return default when env var missing."""
        # Ensure the key doesn't exist
        os.environ.pop("NONEXISTENT_KEY", None)
        result = get_config("NONEXISTENT_KEY", default="default_value")
        assert result == "default_value"

    def test_returns_none_when_missing_no_default(self):
        """get_config should return None when missing and no default."""
        os.environ.pop("NONEXISTENT_KEY", None)
        result = get_config("NONEXISTENT_KEY")
        assert result is None

    def test_cast_to_int(self):
        """get_config should cast value to int."""
        with patch.dict(os.environ, {"INT_KEY": "42"}):
            result = get_config("INT_KEY", cast=int)
            assert result == 42
            assert isinstance(result, int)

    def test_cast_to_float(self):
        """get_config should cast value to float."""
        with patch.dict(os.environ, {"FLOAT_KEY": "3.14"}):
            result = get_config("FLOAT_KEY", cast=float)
            assert result == pytest.approx(3.14)

    def test_cast_failure_returns_default(self):
        """get_config should return default when cast fails."""
        with patch.dict(os.environ, {"INVALID_INT": "not_a_number"}):
            result = get_config("INVALID_INT", default=99, cast=int)
            assert result == 99


class TestGetRequiredConfig:
    """Tests for get_required_config function."""

    def test_returns_env_value(self):
        """get_required_config should return environment variable value."""
        with patch.dict(os.environ, {"REQUIRED_KEY": "required_value"}):
            result = get_required_config("REQUIRED_KEY")
            assert result == "required_value"

    def test_raises_when_missing(self):
        """get_required_config should raise ConfigError when missing."""
        os.environ.pop("MISSING_REQUIRED", None)
        with pytest.raises(ConfigError) as exc_info:
            get_required_config("MISSING_REQUIRED")
        assert exc_info.value.key == "MISSING_REQUIRED"

    def test_cast_works(self):
        """get_required_config should cast value."""
        with patch.dict(os.environ, {"REQUIRED_INT": "100"}):
            result = get_required_config("REQUIRED_INT", cast=int)
            assert result == 100

    def test_cast_failure_raises_config_error(self):
        """get_required_config should raise ConfigError when cast fails."""
        with patch.dict(os.environ, {"INVALID_CAST": "not_a_number"}):
            with pytest.raises(ConfigError) as exc_info:
                get_required_config("INVALID_CAST", cast=int)
            assert "invalid value" in str(exc_info.value)


class TestGetBoolConfig:
    """Tests for get_bool_config function."""

    def test_true_values(self):
        """get_bool_config should recognize true values."""
        true_values = ["true", "True", "TRUE", "1", "yes", "Yes", "on", "ON"]
        for value in true_values:
            with patch.dict(os.environ, {"BOOL_KEY": value}):
                result = get_bool_config("BOOL_KEY")
                assert result is True, f"Failed for value: {value}"

    def test_false_values(self):
        """get_bool_config should treat other values as false."""
        false_values = ["false", "False", "0", "no", "off", "anything"]
        for value in false_values:
            with patch.dict(os.environ, {"BOOL_KEY": value}):
                result = get_bool_config("BOOL_KEY")
                assert result is False, f"Failed for value: {value}"

    def test_default_when_missing(self):
        """get_bool_config should return default when missing."""
        os.environ.pop("MISSING_BOOL", None)
        assert get_bool_config("MISSING_BOOL") is False
        assert get_bool_config("MISSING_BOOL", default=True) is True


class TestGetIntConfig:
    """Tests for get_int_config function."""

    def test_returns_int_value(self):
        """get_int_config should return integer value."""
        with patch.dict(os.environ, {"INT_CONFIG": "42"}):
            result = get_int_config("INT_CONFIG")
            assert result == 42

    def test_default_when_missing(self):
        """get_int_config should return default when missing."""
        os.environ.pop("MISSING_INT", None)
        assert get_int_config("MISSING_INT") == 0
        assert get_int_config("MISSING_INT", default=10) == 10

    def test_default_on_invalid_value(self):
        """get_int_config should return default on invalid value."""
        with patch.dict(os.environ, {"INVALID_INT": "not_an_int"}):
            result = get_int_config("INVALID_INT", default=5)
            assert result == 5


class TestGetFloatConfig:
    """Tests for get_float_config function."""

    def test_returns_float_value(self):
        """get_float_config should return float value."""
        with patch.dict(os.environ, {"FLOAT_CONFIG": "3.14"}):
            result = get_float_config("FLOAT_CONFIG")
            assert result == pytest.approx(3.14)

    def test_default_when_missing(self):
        """get_float_config should return default when missing."""
        os.environ.pop("MISSING_FLOAT", None)
        assert get_float_config("MISSING_FLOAT") == pytest.approx(0.0)
        assert get_float_config("MISSING_FLOAT", default=1.5) == pytest.approx(1.5)

    def test_default_on_invalid_value(self):
        """get_float_config should return default on invalid value."""
        with patch.dict(os.environ, {"INVALID_FLOAT": "not_a_float"}):
            result = get_float_config("INVALID_FLOAT", default=2.5)
            assert result == pytest.approx(2.5)


class TestGetListConfig:
    """Tests for get_list_config function."""

    def test_returns_list_from_csv(self):
        """get_list_config should split CSV into list."""
        with patch.dict(os.environ, {"LIST_KEY": "a,b,c"}):
            result = get_list_config("LIST_KEY")
            assert result == ["a", "b", "c"]

    def test_strips_whitespace(self):
        """get_list_config should strip whitespace from items."""
        with patch.dict(os.environ, {"LIST_KEY": " a , b , c "}):
            result = get_list_config("LIST_KEY")
            assert result == ["a", "b", "c"]

    def test_empty_items_removed(self):
        """get_list_config should remove empty items."""
        with patch.dict(os.environ, {"LIST_KEY": "a,,b,  ,c"}):
            result = get_list_config("LIST_KEY")
            assert result == ["a", "b", "c"]

    def test_custom_separator(self):
        """get_list_config should use custom separator."""
        with patch.dict(os.environ, {"LIST_KEY": "a;b;c"}):
            result = get_list_config("LIST_KEY", separator=";")
            assert result == ["a", "b", "c"]

    def test_default_when_missing(self):
        """get_list_config should return default when missing."""
        os.environ.pop("MISSING_LIST", None)
        assert get_list_config("MISSING_LIST") == []
        assert get_list_config("MISSING_LIST", default=["x"]) == ["x"]

    def test_single_item(self):
        """get_list_config should handle single item."""
        with patch.dict(os.environ, {"LIST_KEY": "single"}):
            result = get_list_config("LIST_KEY")
            assert result == ["single"]
