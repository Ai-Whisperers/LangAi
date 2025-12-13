"""Tests for agent type definitions and helper functions."""

import pytest

from company_researcher.agents.base.types import (
    AgentStatus,
    TokenUsage,
    AgentOutput,
    AgentResult,
    SearchResult,
    AgentConfig,
    AgentContext,
    create_empty_result,
    create_agent_result,
    merge_agent_results,
)


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_success_value(self):
        """AgentStatus.SUCCESS should have correct value."""
        assert AgentStatus.SUCCESS.value == "success"

    def test_partial_value(self):
        """AgentStatus.PARTIAL should have correct value."""
        assert AgentStatus.PARTIAL.value == "partial"

    def test_error_value(self):
        """AgentStatus.ERROR should have correct value."""
        assert AgentStatus.ERROR.value == "error"

    def test_no_data_value(self):
        """AgentStatus.NO_DATA should have correct value."""
        assert AgentStatus.NO_DATA.value == "no_data"

    def test_all_statuses_present(self):
        """AgentStatus should have 4 members."""
        assert len(AgentStatus) == 4


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_default_values(self):
        """AgentConfig should have sensible defaults."""
        config = AgentConfig()
        assert config.max_tokens == 1000
        assert config.temperature == 0.0
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.max_sources == 15
        assert config.content_truncate_length == 500

    def test_custom_values(self):
        """AgentConfig should accept custom values."""
        config = AgentConfig(
            max_tokens=2000,
            temperature=0.7,
            max_retries=5,
            timeout=60.0,
            max_sources=20,
            content_truncate_length=1000
        )
        assert config.max_tokens == 2000
        assert config.temperature == 0.7
        assert config.max_retries == 5
        assert config.timeout == 60.0
        assert config.max_sources == 20
        assert config.content_truncate_length == 1000


class TestAgentContext:
    """Tests for AgentContext dataclass."""

    def test_minimal_context(self):
        """AgentContext should work with just company name."""
        ctx = AgentContext(company_name="TestCorp")
        assert ctx.company_name == "TestCorp"
        assert ctx.search_results == []
        assert isinstance(ctx.config, AgentConfig)
        assert ctx.metadata == {}

    def test_full_context(self):
        """AgentContext should store all fields."""
        search_results = [{"title": "Test", "url": "http://test.com", "content": "Test content"}]
        config = AgentConfig(max_tokens=500)
        metadata = {"source": "test"}

        ctx = AgentContext(
            company_name="TestCorp",
            search_results=search_results,
            config=config,
            metadata=metadata
        )
        assert ctx.company_name == "TestCorp"
        assert len(ctx.search_results) == 1
        assert ctx.config.max_tokens == 500
        assert ctx.metadata["source"] == "test"


class TestCreateEmptyResult:
    """Tests for create_empty_result function."""

    def test_basic_empty_result(self):
        """create_empty_result should create valid structure."""
        result = create_empty_result("test_agent")

        assert "agent_outputs" in result
        assert "test_agent" in result["agent_outputs"]
        assert result["total_cost"] == 0.0
        assert result["total_tokens"]["input"] == 0
        assert result["total_tokens"]["output"] == 0

    def test_default_message(self):
        """create_empty_result should use default message."""
        result = create_empty_result("test_agent")

        output = result["agent_outputs"]["test_agent"]
        assert output["analysis"] == "No search results available"
        assert output["data_extracted"] is False

    def test_custom_message(self):
        """create_empty_result should accept custom message."""
        result = create_empty_result("test_agent", message="Custom error")

        output = result["agent_outputs"]["test_agent"]
        assert output["analysis"] == "Custom error"

    def test_default_status(self):
        """create_empty_result should default to NO_DATA status."""
        result = create_empty_result("test_agent")

        output = result["agent_outputs"]["test_agent"]
        assert output["status"] == "no_data"

    def test_custom_status(self):
        """create_empty_result should accept custom status."""
        result = create_empty_result("test_agent", status=AgentStatus.ERROR)

        output = result["agent_outputs"]["test_agent"]
        assert output["status"] == "error"

    def test_zero_tokens(self):
        """create_empty_result should have zero tokens."""
        result = create_empty_result("test_agent")

        output = result["agent_outputs"]["test_agent"]
        assert output["tokens"]["input"] == 0
        assert output["tokens"]["output"] == 0

    def test_zero_cost(self):
        """create_empty_result should have zero cost."""
        result = create_empty_result("test_agent")

        output = result["agent_outputs"]["test_agent"]
        assert output["cost"] == 0.0


class TestCreateAgentResult:
    """Tests for create_agent_result function."""

    def test_basic_result(self):
        """create_agent_result should create valid structure."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test analysis",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        assert "agent_outputs" in result
        assert "test_agent" in result["agent_outputs"]
        assert result["total_cost"] == 0.01
        assert result["total_tokens"]["input"] == 100
        assert result["total_tokens"]["output"] == 50

    def test_analysis_stored(self):
        """create_agent_result should store analysis text."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Detailed analysis",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        output = result["agent_outputs"]["test_agent"]
        assert output["analysis"] == "Detailed analysis"

    def test_default_success_status(self):
        """create_agent_result should default to SUCCESS status."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        output = result["agent_outputs"]["test_agent"]
        assert output["status"] == "success"
        assert output["data_extracted"] is True

    def test_custom_status(self):
        """create_agent_result should accept custom status."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            status=AgentStatus.PARTIAL
        )

        output = result["agent_outputs"]["test_agent"]
        assert output["status"] == "partial"

    def test_sources_used(self):
        """create_agent_result should track sources used."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            sources_used=5
        )

        output = result["agent_outputs"]["test_agent"]
        assert output["sources_used"] == 5

    def test_confidence_score(self):
        """create_agent_result should include confidence when provided."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            confidence=0.85
        )

        output = result["agent_outputs"]["test_agent"]
        assert output["confidence"] == 0.85

    def test_extra_fields(self):
        """create_agent_result should accept extra fields."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            company_overview="Overview text"
        )

        assert result["company_overview"] == "Overview text"

    def test_none_extra_fields_ignored(self):
        """create_agent_result should ignore None extra fields."""
        result = create_agent_result(
            agent_name="test_agent",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            notes=None
        )

        assert "notes" not in result


class TestMergeAgentResults:
    """Tests for merge_agent_results function."""

    def test_merge_single_result(self):
        """merge_agent_results with single result should return same."""
        result = create_agent_result(
            agent_name="agent1",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        merged = merge_agent_results(result)

        assert "agent1" in merged["agent_outputs"]
        assert merged["total_cost"] == 0.01
        assert merged["total_tokens"]["input"] == 100

    def test_merge_two_results(self):
        """merge_agent_results should combine two results."""
        result1 = create_agent_result(
            agent_name="agent1",
            analysis="Analysis 1",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )
        result2 = create_agent_result(
            agent_name="agent2",
            analysis="Analysis 2",
            input_tokens=200,
            output_tokens=100,
            cost=0.02
        )

        merged = merge_agent_results(result1, result2)

        assert "agent1" in merged["agent_outputs"]
        assert "agent2" in merged["agent_outputs"]
        assert merged["total_cost"] == pytest.approx(0.03)
        assert merged["total_tokens"]["input"] == 300
        assert merged["total_tokens"]["output"] == 150

    def test_merge_multiple_results(self):
        """merge_agent_results should combine multiple results."""
        results = [
            create_agent_result(
                agent_name=f"agent{i}",
                analysis=f"Analysis {i}",
                input_tokens=100,
                output_tokens=50,
                cost=0.01
            )
            for i in range(5)
        ]

        merged = merge_agent_results(*results)

        assert len(merged["agent_outputs"]) == 5
        assert merged["total_cost"] == pytest.approx(0.05)
        assert merged["total_tokens"]["input"] == 500

    def test_merge_preserves_analyses(self):
        """merge_agent_results should preserve all analyses."""
        result1 = create_agent_result(
            agent_name="agent1",
            analysis="First analysis",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )
        result2 = create_agent_result(
            agent_name="agent2",
            analysis="Second analysis",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        merged = merge_agent_results(result1, result2)

        assert merged["agent_outputs"]["agent1"]["analysis"] == "First analysis"
        assert merged["agent_outputs"]["agent2"]["analysis"] == "Second analysis"

    def test_merge_optional_fields(self):
        """merge_agent_results should carry forward optional fields."""
        result1 = create_agent_result(
            agent_name="agent1",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            company_overview="Overview"
        )
        result2 = create_agent_result(
            agent_name="agent2",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )

        merged = merge_agent_results(result1, result2)

        assert merged.get("company_overview") == "Overview"

    def test_merge_later_optional_fields_win(self):
        """merge_agent_results should use later optional fields."""
        result1 = create_agent_result(
            agent_name="agent1",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            quality_score=0.5
        )
        result2 = create_agent_result(
            agent_name="agent2",
            analysis="Test",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            quality_score=0.8
        )

        merged = merge_agent_results(result1, result2)

        assert merged.get("quality_score") == 0.8

    def test_merge_empty_results(self):
        """merge_agent_results should handle empty results."""
        result1 = create_empty_result("agent1")
        result2 = create_empty_result("agent2")

        merged = merge_agent_results(result1, result2)

        assert "agent1" in merged["agent_outputs"]
        assert "agent2" in merged["agent_outputs"]
        assert merged["total_cost"] == 0.0


class TestTokenUsageTypedDict:
    """Tests for TokenUsage TypedDict structure."""

    def test_token_usage_structure(self):
        """TokenUsage should have input and output fields."""
        usage: TokenUsage = {"input": 100, "output": 50}
        assert usage["input"] == 100
        assert usage["output"] == 50


class TestAgentOutputTypedDict:
    """Tests for AgentOutput TypedDict structure."""

    def test_required_fields(self):
        """AgentOutput should have required fields."""
        output: AgentOutput = {
            "analysis": "Test analysis",
            "data_extracted": True,
            "cost": 0.01,
            "tokens": {"input": 100, "output": 50}
        }
        assert output["analysis"] == "Test analysis"
        assert output["data_extracted"] is True

    def test_optional_fields(self):
        """AgentOutput should accept optional fields."""
        output: AgentOutput = {
            "analysis": "Test",
            "data_extracted": True,
            "cost": 0.01,
            "tokens": {"input": 100, "output": 50},
            "status": "success",
            "error": "",
            "sources_used": 5,
            "confidence": 0.85
        }
        assert output["status"] == "success"
        assert output["confidence"] == 0.85


class TestSearchResultTypedDict:
    """Tests for SearchResult TypedDict structure."""

    def test_required_fields(self):
        """SearchResult should have required fields."""
        result: SearchResult = {
            "title": "Test Title",
            "url": "http://example.com",
            "content": "Test content"
        }
        assert result["title"] == "Test Title"
        assert result["url"] == "http://example.com"

    def test_optional_score(self):
        """SearchResult should accept optional score."""
        result: SearchResult = {
            "title": "Test",
            "url": "http://example.com",
            "content": "Test",
            "score": 0.95
        }
        assert result["score"] == 0.95
