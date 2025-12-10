"""
Cache-Aware Research Workflow.

Integrates the Research Cache system with workflows to:
1. Check existing data before starting research
2. Filter out known-useless URLs during search
3. Store all research results persistently
4. Only research missing data sections (incremental research)
5. Never lose data between runs

Usage:
    from company_researcher.workflows.cache_aware_workflow import (
        research_with_cache,
        research_gaps_only,
        get_cached_report,
    )

    # Full research (checks cache first)
    result = research_with_cache("Apple Inc")

    # Only research missing sections
    result = research_gaps_only("Apple Inc")

    # Get existing data without new research
    existing = get_cached_report("Apple Inc")
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from ..cache import (
    ResearchCache,
    get_cache,
    CachedCompanyData,
    DataSection,
    URLStatus,
    CompletenessReport,
)
from ..state import OverallState, InputState, OutputState, create_initial_state, create_output_state
from ..config import get_config

# Import base workflows
from .basic_research import (
    create_research_workflow,
    generate_queries_node,
    search_node as base_search_node,
    analyze_node,
    extract_data_node,
    check_quality_node,
    news_sentiment_node,
    competitive_analysis_node,
    risk_assessment_node,
    investment_thesis_node,
    save_report_node,
)

logger = logging.getLogger(__name__)

# Global cache instance
_workflow_cache: Optional[ResearchCache] = None


def get_workflow_cache() -> ResearchCache:
    """Get or create the workflow cache instance."""
    global _workflow_cache
    if _workflow_cache is None:
        _workflow_cache = get_cache()
    return _workflow_cache


# =============================================================================
# Cache-Aware Workflow Nodes
# =============================================================================

def check_cache_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 0: Check cache for existing data before starting research.

    Returns cached data if available and determines what needs to be researched.
    """
    cache = get_workflow_cache()
    company_name = state["company_name"]

    logger.info(f"[CACHE] Checking existing data for: {company_name}")

    # Check if we should research
    decision = cache.should_research(company_name)

    if not decision["needs_research"]:
        logger.info(f"[CACHE] Data is complete! No research needed.")
        logger.info(f"[CACHE] Reason: {decision['reason']}")

        # Load existing data into state
        existing = cache.get_company_data(company_name)
        if existing:
            return {
                "cache_hit": True,
                "needs_research": False,
                "cached_data": existing,
                "company_overview": _format_cached_overview(existing),
                "sources": existing.all_sources,
                "skip_to_report": True,
            }

    logger.info(f"[CACHE] Research needed: {decision['reason']}")
    logger.info(f"[CACHE] Priority sections: {decision['priority_sections'][:5]}")

    # Get existing data to merge with
    existing = cache.get_company_data(company_name)

    return {
        "cache_hit": existing is not None,
        "needs_research": True,
        "cached_data": existing,
        "priority_sections": decision["priority_sections"],
        "existing_completeness": decision.get("completeness", 0),
        "skip_to_report": False,
    }


def cache_aware_search_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced search node that filters out known-useless URLs.
    """
    cache = get_workflow_cache()

    logger.info(f"[SEARCH] Executing {len(state['search_queries'])} searches...")

    # Run base search
    search_result = base_search_node(state)

    # Filter URLs
    urls = [s.get("url", "") for s in search_result.get("sources", [])]
    filtered = cache.filter_urls(urls)

    logger.info(f"[CACHE] URL filtering: {len(filtered['new'])} new, {len(filtered['useful'])} useful, {len(filtered['useless'])} blocked")

    # Remove useless URLs from results
    useless_urls = set(filtered["useless"])
    filtered_results = [
        r for r in search_result.get("search_results", [])
        if r.get("url", "") not in useless_urls
    ]
    filtered_sources = [
        s for s in search_result.get("sources", [])
        if s.get("url", "") not in useless_urls
    ]

    # Add priority for useful URLs
    for source in filtered_sources:
        if source.get("url") in filtered["useful"]:
            source["priority"] = "high"
            source["cached_quality"] = "verified_useful"

    logger.info(f"[SEARCH] {len(filtered_results)} results after filtering (removed {len(useless_urls)} known useless)")

    return {
        "search_results": filtered_results,
        "sources": filtered_sources,
        "urls_filtered_out": len(useless_urls),
        "total_cost": search_result.get("total_cost", 0.0),
    }


def store_results_node(state: OverallState) -> Dict[str, Any]:
    """
    Store research results in the cache after analysis.

    This node runs after quality check to persist all collected data.
    """
    cache = get_workflow_cache()
    company_name = state["company_name"]

    logger.info(f"[CACHE] Storing results for: {company_name}")

    # Store in sections
    sections_stored = []

    # Overview
    if state.get("company_overview"):
        cache.store_company_data(
            company_name=company_name,
            section="overview",
            data={
                "content": state["company_overview"],
                "company_name": company_name,
                "description": _extract_description(state["company_overview"]),
            },
            sources=state.get("sources", []),
        )
        sections_stored.append("overview")

    # Key metrics
    if state.get("key_metrics"):
        cache.store_company_data(
            company_name=company_name,
            section="financials",
            data=state["key_metrics"],
        )
        sections_stored.append("financials")

    # Competitors
    if state.get("competitors"):
        cache.store_company_data(
            company_name=company_name,
            section="competitors",
            data={"competitors": state["competitors"]},
        )
        sections_stored.append("competitors")

    # Products/services
    if state.get("products_services"):
        cache.store_company_data(
            company_name=company_name,
            section="products",
            data={"products_services": state["products_services"]},
        )
        sections_stored.append("products")

    # Risk profile
    if state.get("risk_profile"):
        cache.store_company_data(
            company_name=company_name,
            section="risks",
            data=state["risk_profile"],
        )
        sections_stored.append("risks")

    # News sentiment
    if state.get("news_sentiment"):
        cache.store_company_data(
            company_name=company_name,
            section="news",
            data=state["news_sentiment"],
        )
        sections_stored.append("news")

    # Investment thesis
    if state.get("investment_thesis"):
        cache.store_company_data(
            company_name=company_name,
            section="investment",
            data=state["investment_thesis"],
        )
        sections_stored.append("investment")

    # Competitive matrix
    if state.get("competitive_matrix"):
        cache.store_company_data(
            company_name=company_name,
            section="competitive",
            data=state["competitive_matrix"],
        )
        sections_stored.append("competitive")

    # Mark URLs as useful or useless based on source quality
    _classify_source_urls(cache, state.get("sources", []), company_name)

    logger.info(f"[CACHE] Stored {len(sections_stored)} sections: {', '.join(sections_stored)}")

    return {"sections_cached": sections_stored}


def merge_with_cached_node(state: OverallState) -> Dict[str, Any]:
    """
    Merge newly researched data with existing cached data.

    This ensures we never lose existing information.
    """
    cached_data = state.get("cached_data")
    if not cached_data:
        return {}

    logger.info("[CACHE] Merging new data with cached data...")

    updates = {}

    # Merge sources (don't duplicate)
    existing_urls = {s.get("url") for s in cached_data.all_sources}
    new_sources = [
        s for s in state.get("sources", [])
        if s.get("url") not in existing_urls
    ]
    if new_sources:
        updates["sources"] = cached_data.all_sources + new_sources
        logger.info(f"[CACHE] Added {len(new_sources)} new sources")

    # Use cached data for sections we didn't research
    if not state.get("key_metrics") and cached_data.financials:
        updates["key_metrics"] = cached_data.financials
        logger.info("[CACHE] Using cached financials")

    if not state.get("competitors") and cached_data.competitors:
        updates["competitors"] = cached_data.competitors.get("competitors", [])
        logger.info("[CACHE] Using cached competitors")

    return updates


# =============================================================================
# Helper Functions
# =============================================================================

def _format_cached_overview(data: CachedCompanyData) -> str:
    """Format cached data as overview text."""
    sections = []

    sections.append(f"# {data.company_name}\n")

    if data.overview:
        if isinstance(data.overview, dict):
            if data.overview.get("content"):
                sections.append(data.overview["content"])
            elif data.overview.get("description"):
                sections.append(f"**Description:** {data.overview['description']}")
        else:
            sections.append(str(data.overview))

    if data.financials:
        sections.append("\n## Financial Summary\n")
        for key, value in data.financials.items():
            if isinstance(value, (int, float)) and value > 1000000:
                sections.append(f"- **{key}:** ${value:,.0f}")
            else:
                sections.append(f"- **{key}:** {value}")

    if data.competitors:
        competitors = data.competitors.get("competitors", [])
        if competitors:
            sections.append("\n## Competitors\n")
            for comp in competitors[:5]:
                sections.append(f"- {comp}")

    return "\n".join(sections)


def _extract_description(overview: str) -> str:
    """Extract description from overview text."""
    if not overview:
        return ""
    # Get first paragraph
    lines = overview.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("*"):
            return line[:500]
    return overview[:500]


def _classify_source_urls(cache: ResearchCache, sources: List[Dict], company_name: str):
    """Classify source URLs as useful or useless based on quality."""
    for source in sources:
        url = source.get("url", "")
        if not url:
            continue

        score = source.get("score", 0.5)
        title = source.get("title", "")

        # High score = useful
        if score >= 0.6:
            cache.url_registry.mark_useful(
                url=url,
                quality_score=score,
                content_summary=title[:200],
                company_name=company_name,
                title=title,
            )
        # Very low score = useless
        elif score < 0.2:
            cache.url_registry.mark_useless(
                url=url,
                reason=f"Low relevance score: {score:.2f}",
                status=URLStatus.LOW_QUALITY,
            )


# =============================================================================
# Main Research Functions
# =============================================================================

def research_with_cache(company_name: str, force: bool = False) -> OutputState:
    """
    Research a company using the cache-aware workflow.

    This function:
    1. Checks the cache for existing data
    2. Only researches if data is missing/stale
    3. Filters out known-useless URLs
    4. Stores all results for future use

    Args:
        company_name: Name of company to research
        force: If True, research even if cache is complete

    Returns:
        OutputState with results and metrics
    """
    from langgraph.graph import StateGraph, END

    cache = get_workflow_cache()

    logger.info(f"\n{'='*60}")
    logger.info(f"[CACHE-AWARE WORKFLOW] Researching: {company_name}")
    logger.info(f"{'='*60}")

    # Check cache first
    decision = cache.should_research(company_name, force=force)

    if not decision["needs_research"]:
        logger.info("[CACHE] Using cached data (no new research needed)")
        return _create_output_from_cache(company_name, cache)

    # Create cache-aware workflow
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add nodes
    workflow.add_node("check_cache", check_cache_node)
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", cache_aware_search_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("news_sentiment", news_sentiment_node)
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("merge_cached", merge_with_cached_node)
    workflow.add_node("store_results", store_results_node)
    workflow.add_node("competitive_analysis", competitive_analysis_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("investment_thesis", investment_thesis_node)
    workflow.add_node("save_report", save_report_node)

    # Define edges
    workflow.set_entry_point("check_cache")
    workflow.add_edge("check_cache", "generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", "news_sentiment")
    workflow.add_edge("news_sentiment", "extract_data")
    workflow.add_edge("extract_data", "check_quality")
    workflow.add_edge("check_quality", "merge_cached")
    workflow.add_edge("merge_cached", "store_results")
    workflow.add_edge("store_results", "competitive_analysis")
    workflow.add_edge("competitive_analysis", "risk_assessment")
    workflow.add_edge("risk_assessment", "investment_thesis")
    workflow.add_edge("investment_thesis", "save_report")
    workflow.add_edge("save_report", END)

    # Compile and run
    compiled = workflow.compile()
    initial_state = create_initial_state(company_name)
    final_state = compiled.invoke(initial_state)

    output = create_output_state(final_state)

    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("[RESULTS] Cache-Aware Research Complete")
    logger.info(f"{'='*60}")
    logger.info(f"Report: {output['report_path']}")
    logger.info(f"Cache hit: {final_state.get('cache_hit', False)}")
    logger.info(f"URLs filtered: {final_state.get('urls_filtered_out', 0)}")
    logger.info(f"Sections cached: {final_state.get('sections_cached', [])}")
    logger.info(f"{'='*60}\n")

    return output


def research_gaps_only(company_name: str) -> OutputState:
    """
    Only research missing sections for a company.

    This is more efficient than full research when we already have
    partial data cached.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with results
    """
    cache = get_workflow_cache()

    # Get gap analysis
    gaps_report = cache.identify_gaps(company_name)

    if not gaps_report.needs_research:
        logger.info(f"[GAPS] No gaps found for {company_name} - data is complete!")
        return _create_output_from_cache(company_name, cache)

    logger.info(f"[GAPS] Found {len(gaps_report.gaps)} gaps to fill")
    logger.info(f"[GAPS] Priority sections: {gaps_report.priority_sections[:5]}")

    # For now, run full research but it will merge with existing data
    return research_with_cache(company_name)


def get_cached_report(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Get existing cached data without running new research.

    Args:
        company_name: Name of company

    Returns:
        Cached data dict or None if not found
    """
    cache = get_workflow_cache()
    data = cache.get_company_data(company_name)

    if not data:
        return None

    return {
        "company_name": data.company_name,
        "overview": data.overview,
        "financials": data.financials,
        "competitors": data.competitors,
        "products": data.products,
        "news": data.news,
        "risks": data.risks,
        "completeness": data.completeness.value,
        "sources": data.all_sources,
        "last_updated": data.last_updated.isoformat() if data.last_updated else None,
    }


def list_cached_companies() -> List[str]:
    """List all companies with cached data."""
    cache = get_workflow_cache()
    return cache.list_companies()


def get_cache_summary() -> Dict[str, Any]:
    """Get summary of cached data."""
    cache = get_workflow_cache()

    companies = cache.list_companies()
    url_stats = cache.url_registry.get_statistics()

    return {
        "total_companies": len(companies),
        "companies": companies,
        "url_registry": {
            "total_urls": url_stats["total_urls"],
            "useful_urls": url_stats["useful_urls"],
            "useless_urls": url_stats["useless_urls"],
            "blocked_domains": url_stats["blocked_domains"],
        },
        "storage_path": str(cache.storage_path),
    }


def _create_output_from_cache(company_name: str, cache: ResearchCache) -> OutputState:
    """Create OutputState from cached data without running workflow."""
    data = cache.get_company_data(company_name)

    if not data:
        raise ValueError(f"No cached data found for {company_name}")

    config = get_config()
    output_dir = Path(config.output_dir) / company_name.replace(" ", "_").lower()

    # Check for existing report
    report_path = output_dir / "00_full_report.md"
    if not report_path.exists():
        report_path = None

    return {
        "company_name": company_name,
        "report_path": str(report_path) if report_path else "",
        "success": True,
        "metrics": {
            "duration_seconds": 0.0,
            "cost_usd": 0.0,
            "tokens": {"input": 0, "output": 0},
            "sources_count": len(data.all_sources),
            "quality_score": _estimate_quality_from_completeness(data),
            "from_cache": True,
        },
    }


def _estimate_quality_from_completeness(data: CachedCompanyData) -> float:
    """Estimate quality score from cached data completeness."""
    from ..cache.data_completeness import DataCompleteness

    scores = {
        DataCompleteness.COMPLETE: 95,
        DataCompleteness.MOSTLY_COMPLETE: 85,
        DataCompleteness.PARTIAL: 65,
        DataCompleteness.MINIMAL: 40,
        DataCompleteness.EMPTY: 0,
    }
    return scores.get(data.completeness, 50)
