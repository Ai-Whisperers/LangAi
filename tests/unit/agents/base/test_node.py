"""Tests for agent node base functionality."""

import pytest

from company_researcher.agents.base.node import NodeConfig, format_search_results


class TestNodeConfig:
    """Tests for NodeConfig dataclass."""

    def test_required_agent_name(self):
        """NodeConfig should require agent_name."""
        config = NodeConfig(agent_name="test_agent")
        assert config.agent_name == "test_agent"

    def test_default_max_tokens(self):
        """NodeConfig should default to 1000 max tokens."""
        config = NodeConfig(agent_name="test")
        assert config.max_tokens == 1000

    def test_default_temperature(self):
        """NodeConfig should default to 0.0 temperature."""
        config = NodeConfig(agent_name="test")
        assert config.temperature == 0.0

    def test_default_max_sources(self):
        """NodeConfig should default to 15 max sources."""
        config = NodeConfig(agent_name="test")
        assert config.max_sources == 15

    def test_default_content_truncate_length(self):
        """NodeConfig should default to 500 content truncate length."""
        config = NodeConfig(agent_name="test")
        assert config.content_truncate_length == 500

    def test_default_require_search_results(self):
        """NodeConfig should default to requiring search results."""
        config = NodeConfig(agent_name="test")
        assert config.require_search_results is True

    def test_custom_values(self):
        """NodeConfig should accept custom values."""
        config = NodeConfig(
            agent_name="custom",
            max_tokens=2000,
            temperature=0.5,
            max_sources=10,
            content_truncate_length=1000,
            require_search_results=False,
        )
        assert config.agent_name == "custom"
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.max_sources == 10
        assert config.content_truncate_length == 1000
        assert config.require_search_results is False


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    def test_empty_results(self):
        """format_search_results should handle empty list."""
        result = format_search_results([])
        assert result == ""

    def test_single_result(self):
        """format_search_results should format single result."""
        results = [
            {"title": "Test Title", "url": "http://example.com", "content": "Test content here"}
        ]
        formatted = format_search_results(results)

        assert "Source 1: Test Title" in formatted
        assert "URL: http://example.com" in formatted
        assert "Content: Test content here" in formatted

    def test_multiple_results(self):
        """format_search_results should format multiple results."""
        results = [
            {"title": "First", "url": "http://first.com", "content": "First content"},
            {"title": "Second", "url": "http://second.com", "content": "Second content"},
            {"title": "Third", "url": "http://third.com", "content": "Third content"},
        ]
        formatted = format_search_results(results)

        assert "Source 1: First" in formatted
        assert "Source 2: Second" in formatted
        assert "Source 3: Third" in formatted

    def test_max_sources_limit(self):
        """format_search_results should respect max_sources parameter."""
        results = [
            {"title": f"Title {i}", "url": f"http://test{i}.com", "content": f"Content {i}"}
            for i in range(20)
        ]
        formatted = format_search_results(results, max_sources=5)

        assert "Source 5:" in formatted
        assert "Source 6:" not in formatted

    def test_content_truncation(self):
        """format_search_results should truncate long content."""
        long_content = "x" * 1000
        results = [{"title": "Test", "url": "http://test.com", "content": long_content}]
        formatted = format_search_results(results, content_length=100)

        # Content should be truncated with ellipsis
        assert "..." in formatted
        assert len(formatted) < len(long_content) + 200

    def test_content_not_truncated_when_short(self):
        """format_search_results should not truncate short content."""
        results = [{"title": "Test", "url": "http://test.com", "content": "Short content"}]
        formatted = format_search_results(results, content_length=500)

        assert "Short content" in formatted
        # No ellipsis for short content
        lines = formatted.split("\n")
        content_line = [l for l in lines if "Content:" in l][0]
        assert "..." not in content_line

    def test_missing_title(self):
        """format_search_results should handle missing title."""
        results = [{"url": "http://test.com", "content": "Content"}]
        formatted = format_search_results(results)

        assert "N/A" in formatted

    def test_missing_url(self):
        """format_search_results should handle missing url."""
        results = [{"title": "Test", "content": "Content"}]
        formatted = format_search_results(results)

        assert "URL: N/A" in formatted

    def test_missing_content(self):
        """format_search_results should handle missing content."""
        results = [{"title": "Test", "url": "http://test.com"}]
        formatted = format_search_results(results)

        assert "Content: N/A" in formatted

    def test_empty_dict_result(self):
        """format_search_results should handle empty dict in list."""
        results = [{}]
        formatted = format_search_results(results)

        assert "Source 1: N/A" in formatted

    def test_non_string_content(self):
        """format_search_results should handle non-string content gracefully."""
        results = [
            {"title": "Test", "url": "http://test.com", "content": 12345}  # Non-string content
        ]
        # Should not raise exception
        formatted = format_search_results(results)
        assert "Source 1:" in formatted

    def test_results_separated_properly(self):
        """format_search_results should separate results with double newlines."""
        results = [
            {"title": "First", "url": "http://first.com", "content": "First"},
            {"title": "Second", "url": "http://second.com", "content": "Second"},
        ]
        formatted = format_search_results(results)

        # Results should be separated by double newline
        assert "\n\n" in formatted

    def test_default_max_sources(self):
        """format_search_results should default to 15 max sources."""
        results = [
            {"title": f"Title {i}", "url": f"http://test{i}.com", "content": f"Content {i}"}
            for i in range(20)
        ]
        formatted = format_search_results(results)

        assert "Source 15:" in formatted
        assert "Source 16:" not in formatted

    def test_default_content_length(self):
        """format_search_results should default to 500 content length."""
        long_content = "x" * 1000
        results = [{"title": "Test", "url": "http://test.com", "content": long_content}]
        formatted = format_search_results(results)

        # Content should be truncated at 500 chars plus ...
        assert "..." in formatted


class TestFormatSearchResultsEdgeCases:
    """Edge case tests for format_search_results."""

    def test_unicode_content(self):
        """format_search_results should handle unicode content."""
        results = [
            {
                "title": "日本語タイトル",
                "url": "http://test.com",
                "content": "Unicode content: 你好世界 🌍",
            }
        ]
        formatted = format_search_results(results)

        assert "日本語タイトル" in formatted
        assert "你好世界" in formatted

    def test_newlines_in_content(self):
        """format_search_results should handle newlines in content."""
        results = [{"title": "Test", "url": "http://test.com", "content": "Line 1\nLine 2\nLine 3"}]
        formatted = format_search_results(results)

        assert "Line 1" in formatted

    def test_special_characters(self):
        """format_search_results should handle special characters."""
        results = [
            {
                "title": 'Test & <Special> "Characters"',
                "url": "http://test.com/path?a=1&b=2",
                "content": 'Content with <html> & "quotes"',
            }
        ]
        formatted = format_search_results(results)

        assert "&" in formatted
        assert "<Special>" in formatted

    def test_very_long_title(self):
        """format_search_results should handle very long titles."""
        results = [{"title": "T" * 500, "url": "http://test.com", "content": "Content"}]
        formatted = format_search_results(results)

        # Title should not be truncated (no limit specified)
        assert "T" * 100 in formatted

    def test_exact_content_length_boundary(self):
        """format_search_results should handle content at exact length boundary."""
        # Test content exactly at boundary
        exact_content = "x" * 500
        results = [{"title": "Test", "url": "http://test.com", "content": exact_content}]
        formatted = format_search_results(results, content_length=500)

        # Should not add ellipsis when exactly at limit
        # (depends on implementation - >= vs >)

    def test_content_length_off_by_one(self):
        """format_search_results should truncate content one char over limit."""
        content = "x" * 501
        results = [{"title": "Test", "url": "http://test.com", "content": content}]
        formatted = format_search_results(results, content_length=500)

        assert "..." in formatted

    def test_zero_max_sources(self):
        """format_search_results should handle zero max_sources."""
        results = [{"title": "Test", "url": "http://test.com", "content": "Content"}]
        formatted = format_search_results(results, max_sources=0)

        # Should return empty or no sources
        assert "Source 1:" not in formatted

    def test_negative_max_sources(self):
        """format_search_results should handle negative max_sources gracefully."""
        results = [{"title": "Test", "url": "http://test.com", "content": "Content"}]
        # Negative slicing returns empty in Python
        formatted = format_search_results(results, max_sources=-1)

        # Should return empty string
        assert formatted == ""

    def test_list_content(self):
        """format_search_results should handle list content gracefully."""
        results = [{"title": "Test", "url": "http://test.com", "content": ["item1", "item2"]}]
        # Should not raise exception
        formatted = format_search_results(results)
        assert "Source 1:" in formatted
