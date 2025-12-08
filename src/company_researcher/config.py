"""
Configuration management for Company Researcher.

This module handles all configuration settings including API keys,
model selection, and research parameters.
"""

import logging
import os
import re
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


# API Key validation patterns
API_KEY_PATTERNS = {
    "anthropic": re.compile(r"^sk-ant-api\d{2}-[\w-]{20,}$"),
    "tavily": re.compile(r"^tvly-[\w-]{20,}$"),
    "langsmith": re.compile(r"^ls[pk]t?-[\w-]{20,}$"),
}


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
    # Financial Data APIs (Phase 7)
    # ========================================================================

    alpha_vantage_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALPHA_VANTAGE_API_KEY"),
        description="Alpha Vantage API key for stock data and fundamentals"
    )

    # ========================================================================
    # Observability & Monitoring (Phase 4)
    # ========================================================================

    agentops_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("AGENTOPS_API_KEY"),
        description="AgentOps API key for agent monitoring"
    )

    langsmith_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGSMITH_API_KEY"),
        description="LangSmith API key for LangChain tracing"
    )

    langchain_tracing_v2: bool = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        description="Enable LangSmith tracing"
    )

    langchain_project: str = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_PROJECT", "langai-research"),
        description="LangSmith project name"
    )

    langchain_endpoint: str = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        description="LangSmith API endpoint"
    )

    @property
    def observability_enabled(self) -> bool:
        """Check if any observability tool is configured."""
        return bool(self.agentops_api_key) or (bool(self.langsmith_api_key) and self.langchain_tracing_v2)

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
    # Display/Limit Configuration
    # These control how many items are shown in reports and summaries
    # ========================================================================

    report_sources_per_domain: int = Field(
        default=3,
        description="Max sources to display per domain in report"
    )

    report_max_results: int = Field(
        default=10,
        description="Max search results to include in reports"
    )

    summary_max_items: int = Field(
        default=5,
        description="Max items per category in summaries"
    )

    insights_max_count: int = Field(
        default=10,
        description="Max insights to generate"
    )

    recommendations_max_count: int = Field(
        default=5,
        description="Max recommendations to generate"
    )

    # ========================================================================
    # Agent-Specific Configuration
    # These centralize previously hardcoded values from 19 agent files
    # ========================================================================

    # Core Agents
    researcher_max_tokens: int = Field(
        default=500,
        description="Max tokens for researcher query generation"
    )
    researcher_temperature: float = Field(
        default=0.7,
        description="Temperature for creative query generation"
    )

    analyst_max_tokens: int = Field(
        default=1000,
        description="Max tokens for analyst summarization"
    )
    analyst_temperature: float = Field(
        default=0.1,
        description="Semi-deterministic analysis"
    )

    synthesizer_max_tokens: int = Field(
        default=1500,
        description="Max tokens for synthesizer overview"
    )
    synthesizer_temperature: float = Field(
        default=0.1,
        description="Semi-deterministic synthesis"
    )

    # Financial Agents
    financial_max_tokens: int = Field(
        default=800,
        description="Max tokens for basic financial analysis"
    )
    financial_temperature: float = Field(
        default=0.0,
        description="Deterministic financial extraction"
    )

    enhanced_financial_max_tokens: int = Field(
        default=1200,
        description="Max tokens for enhanced financial analysis"
    )

    investment_analyst_max_tokens: int = Field(
        default=2500,
        description="Max tokens for investment analyst (detailed reports)"
    )

    # Market Agents
    market_max_tokens: int = Field(
        default=800,
        description="Max tokens for market analysis"
    )
    market_temperature: float = Field(
        default=0.0,
        description="Deterministic market analysis"
    )

    enhanced_market_max_tokens: int = Field(
        default=1200,
        description="Max tokens for enhanced market analysis"
    )

    competitor_scout_max_tokens: int = Field(
        default=1500,
        description="Max tokens for competitor analysis"
    )

    # Specialized Agents
    brand_auditor_max_tokens: int = Field(
        default=2000,
        description="Max tokens for brand audit reports"
    )

    social_media_max_tokens: int = Field(
        default=1500,
        description="Max tokens for social media analysis"
    )

    sales_intelligence_max_tokens: int = Field(
        default=1800,
        description="Max tokens for sales intelligence"
    )

    product_max_tokens: int = Field(
        default=1000,
        description="Max tokens for product analysis"
    )

    # Research Agents
    deep_research_max_tokens: int = Field(
        default=3000,
        description="Max tokens for deep research (comprehensive)"
    )

    reasoning_max_tokens: int = Field(
        default=2000,
        description="Max tokens for reasoning agent"
    )

    # Quality Agents
    logic_critic_max_tokens: int = Field(
        default=800,
        description="Max tokens for logic critic evaluation"
    )

    # ESG Agent
    esg_max_tokens: int = Field(
        default=1500,
        description="Max tokens for ESG analysis"
    )

    # ========================================================================
    # Processing Limits
    # ========================================================================

    max_sources_per_agent: int = Field(
        default=15,
        description="Maximum sources each agent processes"
    )

    content_truncate_length: int = Field(
        default=500,
        description="Length to truncate content snippets"
    )

    # ========================================================================
    # API Timeouts (Security: Prevent hanging on external services)
    # ========================================================================

    api_timeout_seconds: float = Field(
        default=60.0,
        description="Default timeout for API calls in seconds"
    )

    api_connect_timeout_seconds: float = Field(
        default=10.0,
        description="Connection timeout for API calls in seconds"
    )

    search_timeout_seconds: float = Field(
        default=30.0,
        description="Timeout for search API calls in seconds"
    )

    webhook_timeout_seconds: float = Field(
        default=10.0,
        description="Timeout for webhook delivery calls in seconds"
    )

    # ========================================================================
    # Validation
    # ========================================================================

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env

    def validate_api_keys(self, strict: bool = None) -> List[str]:
        """
        Validate that required API keys are present and properly formatted.

        Args:
            strict: If True, raise exception on validation failure.
                   Defaults to True in production, False otherwise.

        Returns:
            List of warning/error messages

        Raises:
            ConfigurationError: If required API keys are missing (in strict mode)
        """
        if strict is None:
            strict = os.getenv("ENVIRONMENT", "development") == "production"

        issues: List[str] = []

        # Validate required keys
        issues.extend(self._validate_required_key(
            "ANTHROPIC_API_KEY", self.anthropic_api_key, "anthropic",
            "https://console.anthropic.com/", "sk-ant-api##-..."
        ))
        issues.extend(self._validate_required_key(
            "TAVILY_API_KEY", self.tavily_api_key, "tavily",
            "https://tavily.com/", "tvly-..."
        ))

        # Validate optional keys
        if self.langsmith_api_key and not self._validate_key_format("langsmith", self.langsmith_api_key):
            issues.append(
                "WARNING: LANGSMITH_API_KEY format looks suspicious. "
                "Expected format: lspt-... or lsk-..."
            )

        # Log and handle issues
        self._log_and_raise_issues(issues, strict)
        return issues

    def _validate_required_key(
        self, key_name: str, key_value: str, key_type: str, url: str, expected_format: str
    ) -> List[str]:
        """Validate a required API key and check for placeholders."""
        issues: List[str] = []

        if not key_value:
            issues.append(f"CRITICAL: Missing {key_name}. Get your key at: {url}")
            return issues

        if not self._validate_key_format(key_type, key_value):
            issues.append(
                f"WARNING: {key_name} format looks suspicious. "
                f"Expected format: {expected_format}"
            )

        if self._is_placeholder_value(key_value):
            issues.append(
                f"CRITICAL: {key_name} appears to be a placeholder value. "
                "Please set a valid API key."
            )

        return issues

    def _is_placeholder_value(self, value: str) -> bool:
        """Check if a value looks like a placeholder."""
        placeholder_patterns = ["your-api-key", "xxx", "placeholder", "changeme", "test"]
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in placeholder_patterns)

    def _log_and_raise_issues(self, issues: List[str], strict: bool) -> None:
        """Log issues and raise exception if in strict mode."""
        critical_issues = [i for i in issues if i.startswith("CRITICAL")]

        for issue in issues:
            if issue.startswith("CRITICAL"):
                logger.error(issue)
            else:
                logger.warning(issue)

        if critical_issues and strict:
            raise ConfigurationError(
                "Configuration validation failed:\n" +
                "\n".join(f"  - {i}" for i in critical_issues)
            )

    def _validate_key_format(self, key_type: str, key_value: str) -> bool:
        """
        Validate API key format against known patterns.

        Args:
            key_type: Type of key (anthropic, tavily, langsmith)
            key_value: The API key value

        Returns:
            True if format appears valid, False otherwise
        """
        if not key_value:
            return False

        pattern = API_KEY_PATTERNS.get(key_type)
        if pattern:
            return bool(pattern.match(key_value))

        # For unknown key types, just check minimum length
        return len(key_value) >= 20

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
