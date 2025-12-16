"""
Constants - Centralized magic numbers and configuration defaults.

This module eliminates scattered hardcoded values across agent files.
All agents should import these constants rather than using inline values.

Usage:
    from company_researcher.agents.constants import (
        FormattingConstants,
        ExtractionConstants,
        AgentDefaults,
    )

    # In formatting
    content = text[:FormattingConstants.CONTENT_TRUNCATE_LENGTH]

    # In extraction
    if len(item) > ExtractionConstants.LIST_ITEM_MAX_LENGTH:
        item = item[:ExtractionConstants.LIST_ITEM_MAX_LENGTH]
"""

from typing import Final

# ==============================================================================
# Formatting Constants
# ==============================================================================


class FormattingConstants:
    """Constants for search result and content formatting."""

    # Content truncation
    CONTENT_TRUNCATE_LENGTH: Final[int] = 500
    """Default length to truncate content in search results."""

    CONTENT_TRUNCATE_SHORT: Final[int] = 300
    """Short truncation for summaries."""

    CONTENT_TRUNCATE_LONG: Final[int] = 800
    """Long truncation for detailed analysis."""

    # Source limits
    MAX_SOURCES_DEFAULT: Final[int] = 15
    """Default maximum sources to include in prompts."""

    MAX_SOURCES_DETAILED: Final[int] = 20
    """Maximum sources for detailed analysis."""

    MAX_SOURCES_QUICK: Final[int] = 10
    """Maximum sources for quick analysis."""

    # Output formatting
    SEPARATOR_WIDTH: Final[int] = 70
    """Width of separator lines in output."""

    SEPARATOR_CHAR: Final[str] = "="
    """Character used for separator lines."""


# ==============================================================================
# Extraction Constants
# ==============================================================================


class ExtractionConstants:
    """Constants for text extraction and parsing."""

    # Section extraction
    SECTION_MAX_LENGTH: Final[int] = 500
    """Maximum length for extracted sections."""

    SECTION_CONTEXT_LENGTH: Final[int] = 200
    """Context window around keywords."""

    # Line/item extraction
    LINE_MAX_LENGTH: Final[int] = 200
    """Maximum length for extracted lines."""

    LIST_ITEM_MAX_LENGTH: Final[int] = 150
    """Maximum length for list items."""

    LIST_MAX_ITEMS: Final[int] = 5
    """Default maximum items to extract from lists."""

    # Validation
    MIN_CONTENT_LENGTH: Final[int] = 10
    """Minimum length for valid content."""

    MIN_ITEM_LENGTH: Final[int] = 5
    """Minimum length for valid list items."""

    # Score extraction
    DEFAULT_SCORE: Final[float] = 50.0
    """Default score when extraction fails."""

    MAX_SCORE: Final[float] = 100.0
    """Maximum score value."""


# ==============================================================================
# Agent Defaults
# ==============================================================================


class AgentDefaults:
    """Default configuration values for agents."""

    # LLM parameters
    DEFAULT_MAX_TOKENS: Final[int] = 1000
    """Default max tokens for LLM calls."""

    DEFAULT_TEMPERATURE: Final[float] = 0.0
    """Default temperature (deterministic)."""

    CREATIVE_TEMPERATURE: Final[float] = 0.3
    """Temperature for creative tasks."""

    # Timeouts
    DEFAULT_TIMEOUT: Final[int] = 30
    """Default timeout in seconds."""

    LONG_TIMEOUT: Final[int] = 60
    """Timeout for complex operations."""

    # Retry settings
    DEFAULT_RETRIES: Final[int] = 3
    """Default number of retries."""

    RETRY_DELAY: Final[float] = 1.0
    """Delay between retries in seconds."""


# ==============================================================================
# Quality Constants
# ==============================================================================


class QualityConstants:
    """Constants for quality assessment."""

    # Thresholds
    HIGH_CONFIDENCE_THRESHOLD: Final[float] = 0.8
    """Threshold for high confidence classification."""

    MEDIUM_CONFIDENCE_THRESHOLD: Final[float] = 0.5
    """Threshold for medium confidence."""

    QUALITY_PASS_THRESHOLD: Final[float] = 75.0
    """Minimum quality score to pass."""

    # Weights
    FACT_SCORE_WEIGHT: Final[float] = 0.25
    """Weight for fact coverage in quality score."""

    CONTRADICTION_SCORE_WEIGHT: Final[float] = 0.30
    """Weight for contradiction score."""

    GAP_SCORE_WEIGHT: Final[float] = 0.25
    """Weight for gap coverage."""

    CONFIDENCE_SCORE_WEIGHT: Final[float] = 0.20
    """Weight for confidence distribution."""

    # Counts
    MIN_FACTS_HIGH_QUALITY: Final[int] = 50
    """Minimum facts for high quality score."""

    MIN_FACTS_MEDIUM_QUALITY: Final[int] = 30
    """Minimum facts for medium quality."""

    MIN_FACTS_PER_SECTION: Final[int] = 3
    """Minimum facts per research section."""


# ==============================================================================
# Search Constants
# ==============================================================================


class SearchConstants:
    """Constants for search operations."""

    # Result limits
    MAX_RESULTS_PER_QUERY: Final[int] = 3
    """Maximum results per search query."""

    MAX_QUERIES_DEFAULT: Final[int] = 5
    """Default number of queries to generate."""

    MAX_QUERIES_DEEP: Final[int] = 10
    """Maximum queries for deep research."""

    # Relevance scoring
    BOOST_SCORE: Final[int] = 3
    """Extra points for high-priority keyword matches."""

    MIN_RELEVANCE_SCORE: Final[int] = 0
    """Minimum relevance score."""


# ==============================================================================
# Display Constants
# ==============================================================================


class DisplayConstants:
    """Constants for display and output formatting."""

    # Agent prefixes
    PREFIX_FORMAT: Final[str] = "[{agent_name}]"
    """Format string for agent log prefixes."""

    # Status indicators
    STATUS_OK: Final[str] = "OK"
    STATUS_ERROR: Final[str] = "ERROR"
    STATUS_WARNING: Final[str] = "WARNING"

    # Relevance labels
    MARKET_RELEVANCE_LABEL: Final[str] = "Market Relevance"
    COMPETITOR_RELEVANCE_LABEL: Final[str] = "Competitor Relevance"
    FINANCIAL_RELEVANCE_LABEL: Final[str] = "Financial Relevance"


# ==============================================================================
# Convenience Aliases
# ==============================================================================

# Common formatting values
CONTENT_LENGTH = FormattingConstants.CONTENT_TRUNCATE_LENGTH
MAX_SOURCES = FormattingConstants.MAX_SOURCES_DEFAULT
SEPARATOR = FormattingConstants.SEPARATOR_CHAR * FormattingConstants.SEPARATOR_WIDTH

# Common extraction values
MAX_ITEM_LEN = ExtractionConstants.LIST_ITEM_MAX_LENGTH
MAX_ITEMS = ExtractionConstants.LIST_MAX_ITEMS

# Common agent values
DEFAULT_TOKENS = AgentDefaults.DEFAULT_MAX_TOKENS
DEFAULT_TEMP = AgentDefaults.DEFAULT_TEMPERATURE
