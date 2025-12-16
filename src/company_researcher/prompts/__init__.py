"""
Prompt management system for versioned, testable prompts.

This module provides organized access to all prompts used in the research workflow:
- Core workflow prompts (query generation, analysis, extraction, quality)
- Financial analysis prompts
- Market and competitive analysis prompts
- Research and reasoning prompts
- Specialty prompts (brand, social, sales)
- Prompt management system

Usage:
    from company_researcher.prompts import get_prompt, register_prompt
    from company_researcher.prompts import GENERATE_QUERIES_PROMPT

    # Use prompt constants directly
    prompt = GENERATE_QUERIES_PROMPT.format(company_name="Apple", num_queries=5)

    # Or use the prompt management system
    prompt = get_prompt("financial_analysis", company_name="Apple Inc.")
"""

from .analysis import LOGIC_CRITIC_PROMPT, SYNTHESIS_PROMPT

# Import all prompt constants from categorized modules
from .core import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    GENERATE_QUERIES_PROMPT,
    GENERATE_REPORT_TEMPLATE,
    QUALITY_CHECK_PROMPT,
)
from .financial import (
    ENHANCED_FINANCIAL_PROMPT,
    FINANCIAL_ANALYSIS_PROMPT,
    INVESTMENT_ANALYSIS_PROMPT,
)
from .formatters import (
    format_search_results_for_analysis,
    format_sources_for_extraction,
    format_sources_for_report,
)
from .market import (
    COMPETITOR_SCOUT_PROMPT,
    ENHANCED_MARKET_PROMPT,
    MARKET_ANALYSIS_PROMPT,
    PRODUCT_ANALYSIS_PROMPT,
)
from .prompt_manager import (  # Core classes; Singleton access; Convenience functions
    PromptCategory,
    PromptMetrics,
    PromptRegistry,
    PromptVersion,
    get_prompt,
    get_prompt_registry,
    register_prompt,
)
from .research import (
    DEEP_RESEARCH_PROMPT,
    DEEP_RESEARCH_QUERY_PROMPT,
    HYPOTHESIS_TESTING_PROMPT,
    REASONING_PROMPT,
    STRATEGIC_INFERENCE_PROMPT,
)
from .specialty import BRAND_AUDIT_PROMPT, SALES_INTELLIGENCE_PROMPT, SOCIAL_MEDIA_PROMPT

__all__ = [
    # Prompt Management System
    "PromptRegistry",
    "PromptVersion",
    "PromptMetrics",
    "PromptCategory",
    "get_prompt_registry",
    "get_prompt",
    "register_prompt",
    # Core Workflow Prompts
    "GENERATE_QUERIES_PROMPT",
    "ANALYZE_RESULTS_PROMPT",
    "EXTRACT_DATA_PROMPT",
    "GENERATE_REPORT_TEMPLATE",
    "QUALITY_CHECK_PROMPT",
    # Helper Functions
    "format_search_results_for_analysis",
    "format_sources_for_extraction",
    "format_sources_for_report",
    # Financial Analysis Prompts
    "FINANCIAL_ANALYSIS_PROMPT",
    "ENHANCED_FINANCIAL_PROMPT",
    "INVESTMENT_ANALYSIS_PROMPT",
    # Market & Competitive Analysis Prompts
    "MARKET_ANALYSIS_PROMPT",
    "ENHANCED_MARKET_PROMPT",
    "COMPETITOR_SCOUT_PROMPT",
    "PRODUCT_ANALYSIS_PROMPT",
    # Analysis & Synthesis Prompts
    "SYNTHESIS_PROMPT",
    "LOGIC_CRITIC_PROMPT",
    # Research & Reasoning Prompts
    "DEEP_RESEARCH_PROMPT",
    "DEEP_RESEARCH_QUERY_PROMPT",
    "REASONING_PROMPT",
    "HYPOTHESIS_TESTING_PROMPT",
    "STRATEGIC_INFERENCE_PROMPT",
    # Specialty Analysis Prompts
    "BRAND_AUDIT_PROMPT",
    "SOCIAL_MEDIA_PROMPT",
    "SALES_INTELLIGENCE_PROMPT",
]
