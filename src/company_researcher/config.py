"""
Configuration management for Company Researcher.

This module handles all configuration settings including API keys,
model selection, and research parameters.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ResearchConfig(BaseSettings):
    """
    Configuration for the research workflow.

    All settings can be overridden via environment variables.
    """

    # ========================================================================
    # API Keys
    # ========================================================================

    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key for Claude models"
    )

    tavily_api_key: str = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY", ""),
        description="Tavily API key for web search"
    )

    # ========================================================================
    # Model Configuration
    # ========================================================================

    llm_model: str = Field(
        default="claude-3-5-haiku-20241022",
        description="Claude model to use for analysis"
    )

    llm_temperature: float = Field(
        default=0.0,
        description="Temperature for LLM (0.0 = deterministic)"
    )

    llm_max_tokens: int = Field(
        default=4000,
        description="Maximum tokens for LLM output"
    )

    # ========================================================================
    # Search Configuration
    # ========================================================================

    num_search_queries: int = Field(
        default=5,
        description="Number of search queries to generate"
    )

    search_results_per_query: int = Field(
        default=3,
        description="Number of results per search query"
    )

    max_search_results: int = Field(
        default=15,
        description="Maximum total search results to process"
    )

    # ========================================================================
    # Research Parameters
    # ========================================================================

    max_research_time_seconds: int = Field(
        default=300,
        description="Maximum time for research (5 minutes)"
    )

    target_cost_usd: float = Field(
        default=0.30,
        description="Target cost per research"
    )

    # ========================================================================
    # Output Configuration
    # ========================================================================

    output_dir: str = Field(
        default="outputs",
        description="Directory for research reports"
    )

    report_format: str = Field(
        default="markdown",
        description="Report output format (markdown only for Phase 1)"
    )

    # ========================================================================
    # Validation
    # ========================================================================

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env

    def validate_api_keys(self) -> None:
        """
        Validate that required API keys are present.

        Raises:
            ValueError: If required API keys are missing
        """
        if not self.anthropic_api_key:
            raise ValueError(
                "Missing ANTHROPIC_API_KEY. "
                "Get your key at: https://console.anthropic.com/"
            )

        if not self.tavily_api_key:
            raise ValueError(
                "Missing TAVILY_API_KEY. "
                "Get your key at: https://tavily.com/"
            )

    def get_model_pricing(self) -> dict:
        """
        Get pricing information for the configured model.

        Returns:
            Dictionary with input and output token costs per 1M tokens
        """
        # Pricing as of December 2024
        pricing = {
            "claude-3-5-haiku-20241022": {
                "input": 0.80,
                "output": 4.00
            },
            "claude-3-5-sonnet-20241022": {
                "input": 3.00,
                "output": 15.00
            },
            "claude-3-haiku-20240307": {
                "input": 0.25,
                "output": 1.25
            }
        }

        return pricing.get(
            self.llm_model,
            {"input": 3.00, "output": 15.00}  # Default to Sonnet pricing
        )

    def calculate_llm_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for LLM usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        pricing = self.get_model_pricing()
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


# ============================================================================
# Global Config Instance
# ============================================================================

_config: Optional[ResearchConfig] = None


def get_config() -> ResearchConfig:
    """
    Get or create the global configuration instance.

    Returns:
        ResearchConfig instance
    """
    global _config
    if _config is None:
        _config = ResearchConfig()
        _config.validate_api_keys()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (useful for testing)."""
    global _config
    _config = None
