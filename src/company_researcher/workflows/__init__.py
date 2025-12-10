"""
Workflows package for Company Researcher.

This package contains all LangGraph workflows for different research phases.

Available Workflows:
- basic_research: Standard research workflow (faster, lower cost)
- comprehensive_research: Full feature workflow (all agents, quality modules)
- cache_aware_workflow: Persistent cache-aware workflow (recommended for production)

Usage:
    # Standard research
    from company_researcher.workflows import research_company
    result = research_company("Microsoft")

    # Comprehensive research (all features)
    from company_researcher.workflows import research_company_comprehensive
    result = research_company_comprehensive("Microsoft")

    # Cache-aware research (recommended - never loses data)
    from company_researcher.workflows import research_with_cache
    result = research_with_cache("Microsoft")

    # Check cached data
    from company_researcher.workflows import get_cached_report, list_cached_companies
    existing = get_cached_report("Microsoft")
    companies = list_cached_companies()
"""

from .basic_research import research_company, create_research_workflow

from .comprehensive_research import (
    research_company_comprehensive,
    create_comprehensive_workflow,
)

from .cache_aware_workflow import (
    research_with_cache,
    research_gaps_only,
    get_cached_report,
    list_cached_companies,
    get_cache_summary,
    get_workflow_cache,
)

__all__ = [
    # Basic workflow
    "research_company",
    "create_research_workflow",

    # Comprehensive workflow
    "research_company_comprehensive",
    "create_comprehensive_workflow",

    # Cache-aware workflow (recommended)
    "research_with_cache",
    "research_gaps_only",
    "get_cached_report",
    "list_cached_companies",
    "get_cache_summary",
    "get_workflow_cache",
]
