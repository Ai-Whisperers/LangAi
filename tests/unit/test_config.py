"""
Tests for config module.

Tests the configuration management including agent-specific settings.
"""

import pytest
import os
from unittest.mock import patch

from src.company_researcher.config import ResearchConfig, reset_config


class TestResearchConfig:
    """Tests for ResearchConfig class."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def test_default_model_config(self):
        """Test default model configuration."""
        config = ResearchConfig()
        assert config.llm_model == "claude-3-5-haiku-20241022"
        assert config.llm_temperature == 0.0
        assert config.llm_max_tokens == 4000

    def test_default_search_config(self):
        """Test default search configuration."""
        config = ResearchConfig()
        assert config.num_search_queries == 5
        assert config.search_results_per_query == 3
        assert config.max_search_results == 15

    def test_default_output_config(self):
        """Test default output configuration."""
        config = ResearchConfig()
        assert config.output_dir == "outputs"
        assert config.report_format == "markdown"


class TestAgentSpecificConfig:
    """Tests for agent-specific configuration values."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def test_researcher_config(self):
        """Test researcher agent config values."""
        config = ResearchConfig()
        assert config.researcher_max_tokens == 500
        assert config.researcher_temperature == 0.7

    def test_analyst_config(self):
        """Test analyst agent config values."""
        config = ResearchConfig()
        assert config.analyst_max_tokens == 1000
        assert config.analyst_temperature == 0.1

    def test_synthesizer_config(self):
        """Test synthesizer agent config values."""
        config = ResearchConfig()
        assert config.synthesizer_max_tokens == 1500
        assert config.synthesizer_temperature == 0.1

    def test_financial_config(self):
        """Test financial agent config values."""
        config = ResearchConfig()
        assert config.financial_max_tokens == 800
        assert config.financial_temperature == 0.0
        assert config.enhanced_financial_max_tokens == 1200
        assert config.investment_analyst_max_tokens == 2500

    def test_market_config(self):
        """Test market agent config values."""
        config = ResearchConfig()
        assert config.market_max_tokens == 800
        assert config.market_temperature == 0.0
        assert config.enhanced_market_max_tokens == 1200
        assert config.competitor_scout_max_tokens == 1500

    def test_specialized_agent_config(self):
        """Test specialized agent config values."""
        config = ResearchConfig()
        assert config.brand_auditor_max_tokens == 2000
        assert config.social_media_max_tokens == 1500
        assert config.sales_intelligence_max_tokens == 1800
        assert config.product_max_tokens == 1000

    def test_research_agent_config(self):
        """Test research agent config values."""
        config = ResearchConfig()
        assert config.deep_research_max_tokens == 3000
        assert config.reasoning_max_tokens == 2000

    def test_quality_agent_config(self):
        """Test quality agent config values."""
        config = ResearchConfig()
        assert config.logic_critic_max_tokens == 800

    def test_esg_agent_config(self):
        """Test ESG agent config values."""
        config = ResearchConfig()
        assert config.esg_max_tokens == 1500

    def test_processing_limits(self):
        """Test processing limit config values."""
        config = ResearchConfig()
        assert config.max_sources_per_agent == 15
        assert config.content_truncate_length == 500


class TestModelPricing:
    """Tests for model pricing functionality."""

    def test_haiku_pricing(self):
        """Test Haiku model pricing."""
        config = ResearchConfig()
        config.llm_model = "claude-3-5-haiku-20241022"
        pricing = config.get_model_pricing()
        assert pricing["input"] == 0.80
        assert pricing["output"] == 4.00

    def test_sonnet_pricing(self):
        """Test Sonnet model pricing."""
        config = ResearchConfig()
        config.llm_model = "claude-3-5-sonnet-20241022"
        pricing = config.get_model_pricing()
        assert pricing["input"] == 3.00
        assert pricing["output"] == 15.00

    def test_unknown_model_defaults_to_sonnet(self):
        """Test unknown model defaults to Sonnet pricing."""
        config = ResearchConfig()
        config.llm_model = "unknown-model"
        pricing = config.get_model_pricing()
        assert pricing["input"] == 3.00
        assert pricing["output"] == 15.00


class TestCostCalculation:
    """Tests for cost calculation functionality."""

    def test_cost_calculation_haiku(self):
        """Test cost calculation for Haiku model."""
        config = ResearchConfig()
        config.llm_model = "claude-3-5-haiku-20241022"

        # 1000 input tokens, 500 output tokens
        cost = config.calculate_llm_cost(1000, 500)

        # Input: (1000 / 1M) * 0.80 = 0.0008
        # Output: (500 / 1M) * 4.00 = 0.002
        # Total: 0.0028
        assert cost == pytest.approx(0.0028, rel=1e-6)

    def test_cost_calculation_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        config = ResearchConfig()
        cost = config.calculate_llm_cost(0, 0)
        assert cost == 0.0
