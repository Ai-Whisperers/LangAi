"""
Tests for agents.base.types module.

Tests the standardized types for agent results.
"""

import pytest
from src.company_researcher.agents.base.types import (
    AgentStatus,
    TokenUsage,
    AgentOutput,
    AgentResult,
    AgentConfig,
    AgentContext,
    create_empty_result,
    create_agent_result,
    merge_agent_results,
)


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert AgentStatus.SUCCESS.value == "success"
        assert AgentStatus.PARTIAL.value == "partial"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.NO_DATA.value == "no_data"


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AgentConfig()
        assert config.max_tokens == 1000
        assert config.temperature == 0.0
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.max_sources == 15
        assert config.content_truncate_length == 500

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AgentConfig(
            max_tokens=2000,
            temperature=0.5,
            max_retries=5
        )
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.max_retries == 5


class TestAgentContext:
    """Tests for AgentContext dataclass."""

    def test_default_context(self):
        """Test context with minimal required fields."""
        context = AgentContext(company_name="Tesla")
        assert context.company_name == "Tesla"
        assert context.search_results == []
        assert isinstance(context.config, AgentConfig)
        assert context.metadata == {}

    def test_context_with_search_results(self):
        """Test context with search results."""
        results = [
            {"title": "Test", "url": "http://test.com", "content": "Test content"}
        ]
        context = AgentContext(
            company_name="Apple",
            search_results=results
        )
        assert len(context.search_results) == 1
        assert context.search_results[0]["title"] == "Test"


class TestCreateEmptyResult:
    """Tests for create_empty_result function."""

    def test_default_empty_result(self):
        """Test creating empty result with defaults."""
        result = create_empty_result("financial")

        assert "agent_outputs" in result
        assert "financial" in result["agent_outputs"]
        assert result["agent_outputs"]["financial"]["analysis"] == "No search results available"
        assert result["agent_outputs"]["financial"]["data_extracted"] is False
        assert result["agent_outputs"]["financial"]["cost"] == 0.0
        assert result["total_cost"] == 0.0

    def test_custom_message(self):
        """Test creating empty result with custom message."""
        result = create_empty_result(
            "market",
            message="Custom error message",
            status=AgentStatus.ERROR
        )

        assert result["agent_outputs"]["market"]["analysis"] == "Custom error message"
        assert result["agent_outputs"]["market"]["status"] == "error"


class TestCreateAgentResult:
    """Tests for create_agent_result function."""

    def test_basic_result(self):
        """Test creating a basic agent result."""
        result = create_agent_result(
            agent_name="financial",
            analysis="Test analysis",
            input_tokens=100,
            output_tokens=200,
            cost=0.05
        )

        assert "agent_outputs" in result
        assert "financial" in result["agent_outputs"]

        output = result["agent_outputs"]["financial"]
        assert output["analysis"] == "Test analysis"
        assert output["tokens"]["input"] == 100
        assert output["tokens"]["output"] == 200
        assert output["cost"] == 0.05
        assert output["data_extracted"] is True
        assert output["status"] == "success"

    def test_result_with_error_status(self):
        """Test creating result with error status."""
        result = create_agent_result(
            agent_name="market",
            analysis="Error occurred",
            input_tokens=50,
            output_tokens=0,
            cost=0.01,
            status=AgentStatus.ERROR
        )

        assert result["agent_outputs"]["market"]["status"] == "error"
        assert result["agent_outputs"]["market"]["data_extracted"] is False

    def test_result_with_extra_fields(self):
        """Test creating result with extra fields."""
        result = create_agent_result(
            agent_name="synthesizer",
            analysis="Synthesis complete",
            input_tokens=500,
            output_tokens=1000,
            cost=0.15,
            sources_used=10,
            confidence=0.85,
            company_overview="Test overview"
        )

        assert result["agent_outputs"]["synthesizer"]["sources_used"] == 10
        assert result["agent_outputs"]["synthesizer"]["confidence"] == 0.85
        assert result.get("company_overview") == "Test overview"


class TestMergeAgentResults:
    """Tests for merge_agent_results function."""

    def test_merge_two_results(self):
        """Test merging two agent results."""
        result1 = create_agent_result(
            agent_name="financial",
            analysis="Financial analysis",
            input_tokens=100,
            output_tokens=200,
            cost=0.05
        )

        result2 = create_agent_result(
            agent_name="market",
            analysis="Market analysis",
            input_tokens=150,
            output_tokens=250,
            cost=0.08
        )

        merged = merge_agent_results(result1, result2)

        # Check both agents are in merged result
        assert "financial" in merged["agent_outputs"]
        assert "market" in merged["agent_outputs"]

        # Check costs are summed
        assert merged["total_cost"] == pytest.approx(0.13)

        # Check tokens are summed
        assert merged["total_tokens"]["input"] == 250
        assert merged["total_tokens"]["output"] == 450

    def test_merge_three_results(self):
        """Test merging three agent results."""
        results = [
            create_agent_result("financial", "F", 100, 100, 0.01),
            create_agent_result("market", "M", 100, 100, 0.02),
            create_agent_result("product", "P", 100, 100, 0.03),
        ]

        merged = merge_agent_results(*results)

        assert len(merged["agent_outputs"]) == 3
        assert merged["total_cost"] == pytest.approx(0.06)
        assert merged["total_tokens"]["input"] == 300
        assert merged["total_tokens"]["output"] == 300

    def test_merge_preserves_extra_fields(self):
        """Test that merge preserves extra fields from last result."""
        result1 = create_agent_result(
            agent_name="analyst",
            analysis="Analysis",
            input_tokens=100,
            output_tokens=200,
            cost=0.05
        )

        result2 = create_agent_result(
            agent_name="synthesizer",
            analysis="Synthesis",
            input_tokens=200,
            output_tokens=400,
            cost=0.10,
            company_overview="Company overview text"
        )

        merged = merge_agent_results(result1, result2)

        assert merged.get("company_overview") == "Company overview text"
