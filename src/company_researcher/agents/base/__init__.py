"""
Base Agent Infrastructure.

Provides common functionality for all agents:
- Standardized types (AgentResult, AgentOutput, etc.)
- Centralized logging (AgentLogger)
- Base node class and decorator (BaseAgentNode, @agent_node)
- Utility functions for common operations

This module eliminates code duplication across 19+ agent files.

Usage:
    from company_researcher.agents.base import (
        # Types
        AgentResult,
        AgentOutput,
        AgentConfig,
        AgentStatus,
        create_agent_result,
        create_empty_result,
        merge_agent_results,

        # Logging
        AgentLogger,
        get_agent_logger,
        configure_agent_logging,

        # Node infrastructure
        BaseAgentNode,
        agent_node,
        format_search_results,
    )

Example - Using decorator:
    @agent_node("financial", max_tokens=800)
    def financial_agent_node(state, logger, client, config, node_config, formatted_results, company_name):
        prompt = PROMPT.format(company_name=company_name, results=formatted_results)
        return client.messages.create(
            model=config.llm_model,
            max_tokens=node_config.max_tokens,
            temperature=node_config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

Example - Using class:
    class FinancialAgentNode(BaseAgentNode):
        agent_name = "financial"
        max_tokens = 800

        def get_prompt(self, company_name, formatted_results, **kwargs):
            return PROMPT.format(...)
"""

# Error handling
from .errors import (  # Exceptions; Severity; Helpers; Retry; Context manager; Validation
    AgentError,
    AgentErrorContext,
    ConfigurationError,
    ErrorSeverity,
    ExtractionError,
    LLMError,
    ParsingError,
    RetryConfig,
    SearchError,
    ValidationError,
    create_empty_result_with_reason,
    create_error_result,
    handle_agent_error,
    validate_company_name,
    validate_search_results,
    with_retry,
)

# Logger
from .logger import AgentLogContext, AgentLogger, configure_agent_logging, get_agent_logger

# Node infrastructure
from .node import BaseAgentNode, NodeConfig, agent_node, format_search_results

# Query generation
from .query_generation import (  # Date-aware queries; Spanish templates
    SPANISH_DOMAIN_TEMPLATES,
    QueryConfig,
    QueryDomain,
    clean_query,
    generate_targeted_queries,
    get_bilingual_queries,
    get_comprehensive_dated_queries,
    get_comprehensive_queries,
    get_date_filtered_queries,
    get_domain_queries,
    get_fallback_queries,
    get_gap_queries,
    get_leadership_queries,
    get_market_data_queries,
    parse_query_response,
    validate_queries,
)

# Search result formatting
from .search_formatting import (  # Core formatter; Domain-specific formatters; Convenience functions
    BrandSearchFormatter,
    CompetitorSearchFormatter,
    FinancialSearchFormatter,
    FormatterConfig,
    MarketSearchFormatter,
    ProductSearchFormatter,
    SalesSearchFormatter,
    SearchResultFormatter,
    SearchResultMixin,
    format_brand_results,
    format_competitor_results,
    format_financial_results,
    format_market_results,
    format_product_results,
    format_sales_results,
)

# Specialist agent infrastructure
from .specialist import AnalysisMetrics, BaseSpecialistAgent, ParsingMixin

# Types
from .types import (  # Enums; TypedDicts; Dataclasses; Factory functions
    AgentConfig,
    AgentContext,
    AgentOutput,
    AgentResult,
    AgentStatus,
    SearchResult,
    TokenUsage,
    create_agent_result,
    create_empty_result,
    merge_agent_results,
)

__all__ = [
    # Types - Enums
    "AgentStatus",
    # Types - TypedDicts
    "TokenUsage",
    "AgentOutput",
    "AgentResult",
    "SearchResult",
    # Types - Dataclasses
    "AgentConfig",
    "AgentContext",
    # Types - Factory functions
    "create_empty_result",
    "create_agent_result",
    "merge_agent_results",
    # Logger
    "AgentLogger",
    "AgentLogContext",
    "get_agent_logger",
    "configure_agent_logging",
    # Node
    "BaseAgentNode",
    "NodeConfig",
    "agent_node",
    "format_search_results",
    # Specialist
    "BaseSpecialistAgent",
    "ParsingMixin",
    "AnalysisMetrics",
    # Search formatting
    "SearchResultFormatter",
    "FormatterConfig",
    "SearchResultMixin",
    "MarketSearchFormatter",
    "CompetitorSearchFormatter",
    "FinancialSearchFormatter",
    "ProductSearchFormatter",
    "SalesSearchFormatter",
    "BrandSearchFormatter",
    "format_market_results",
    "format_competitor_results",
    "format_financial_results",
    "format_product_results",
    "format_sales_results",
    "format_brand_results",
    # Query generation
    "QueryDomain",
    "QueryConfig",
    "get_fallback_queries",
    "get_domain_queries",
    "get_gap_queries",
    "get_comprehensive_queries",
    "clean_query",
    "validate_queries",
    "parse_query_response",
    # Date-aware queries
    "get_date_filtered_queries",
    "get_leadership_queries",
    "get_market_data_queries",
    "get_bilingual_queries",
    "get_comprehensive_dated_queries",
    "generate_targeted_queries",
    "SPANISH_DOMAIN_TEMPLATES",
    # Error handling
    "AgentError",
    "ParsingError",
    "LLMError",
    "SearchError",
    "ConfigurationError",
    "ValidationError",
    "ExtractionError",
    "ErrorSeverity",
    "create_error_result",
    "create_empty_result_with_reason",
    "handle_agent_error",
    "RetryConfig",
    "with_retry",
    "AgentErrorContext",
    "validate_search_results",
    "validate_company_name",
]
