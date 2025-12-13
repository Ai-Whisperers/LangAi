"""
Data Collection Subgraph - Phase 11

Handles all data gathering operations:
- Company classification (public/private/startup)
- Query generation (multilingual support)
- Web search (multi-provider with fallback)
- SEC EDGAR filings (US public companies)
- Website scraping (Wikipedia + company sites)

This subgraph routes dynamically based on company type to optimize
data source selection and reduce unnecessary API calls.
"""

from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, START, END

from ...state.workflow import OverallState
from ...agents.core.company_classifier import classify_company_node
from ...workflows.nodes import (
    generate_queries_node,
    search_node,
    sec_edgar_node,
    website_scraping_node,
    SEC_EDGAR_AVAILABLE,
)
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class DataCollectionConfig:
    """Configuration for data collection subgraph."""

    # Search settings
    max_queries: int = 5
    results_per_query: int = 10
    enable_multilingual: bool = True

    # Data source toggles
    enable_sec_edgar: bool = True
    enable_website_scraping: bool = True
    enable_news_fetch: bool = True

    # Company type routing
    route_by_company_type: bool = True

    # Fallback settings
    fallback_on_error: bool = True
    max_retries: int = 2


# ============================================================================
# Routing Functions
# ============================================================================

def route_by_company_type(state: OverallState) -> str:
    """
    Route to appropriate data collection strategy based on company type.

    Routes:
        - public_us: SEC EDGAR + Web Search + Website Scraping
        - public_intl: Web Search + Website Scraping (no SEC)
        - private: Web Search + Website Scraping
        - startup: Web Search + Crunchbase + GitHub

    Args:
        state: Current workflow state with company_classification

    Returns:
        Route key for next node
    """
    classification = state.get("company_classification", {})
    is_public = classification.get("is_public_company", False)
    exchange = classification.get("exchange", "")
    company_type = classification.get("company_type", "unknown")

    # US public companies have SEC filings
    us_exchanges = {"NYSE", "NASDAQ", "AMEX", "OTC"}

    if is_public and exchange in us_exchanges:
        logger.info(f"[ROUTE] Public US company detected (exchange: {exchange})")
        return "public_us"
    elif is_public:
        logger.info(f"[ROUTE] Public international company detected")
        return "public_intl"
    elif company_type in ("startup", "venture-backed"):
        logger.info(f"[ROUTE] Startup/venture company detected")
        return "startup"
    else:
        logger.info(f"[ROUTE] Private company detected")
        return "private"


def route_after_search(state: OverallState) -> str:
    """
    Route after search based on whether SEC data should be fetched.

    Args:
        state: Current workflow state

    Returns:
        "sec_edgar" if US public company, else "website_scraping"
    """
    classification = state.get("company_classification", {})
    is_public = classification.get("is_public_company", False)
    exchange = classification.get("exchange", "")

    us_exchanges = {"NYSE", "NASDAQ", "AMEX", "OTC"}

    if is_public and exchange in us_exchanges and SEC_EDGAR_AVAILABLE:
        return "sec_edgar"
    else:
        return "website_scraping"


# ============================================================================
# Enhanced Nodes for Specific Company Types
# ============================================================================

def startup_search_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced search for startups - includes Crunchbase and GitHub queries.

    Args:
        state: Current workflow state

    Returns:
        State update with search results
    """
    logger.info("[NODE] Startup-focused search...")

    company_name = state.get("company_name", "Unknown")

    # Add startup-specific queries
    startup_queries = [
        f"{company_name} funding rounds investors",
        f"{company_name} crunchbase profile",
        f"{company_name} github repository",
        f"{company_name} founders team background",
        f"{company_name} product launch news",
    ]

    # Merge with existing queries
    existing_queries = state.get("search_queries", [])
    all_queries = list(set(existing_queries + startup_queries))[:10]

    # Update state with enhanced queries then call regular search
    enhanced_state = {**state, "search_queries": all_queries}

    # Call the regular search node
    result = search_node(enhanced_state)

    return {
        **result,
        "search_queries": all_queries,
    }


def international_search_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced search for international companies - includes regional sources.

    Args:
        state: Current workflow state

    Returns:
        State update with search results
    """
    logger.info("[NODE] International company search...")

    company_name = state.get("company_name", "Unknown")
    detected_region = state.get("detected_region", "")

    # Add region-specific queries
    regional_queries = []
    if detected_region:
        regional_queries = [
            f"{company_name} {detected_region} market",
            f"{company_name} annual report {detected_region}",
        ]

    # Merge with existing queries
    existing_queries = state.get("search_queries", [])
    all_queries = list(set(existing_queries + regional_queries))[:10]

    # Update state and call regular search
    enhanced_state = {**state, "search_queries": all_queries}
    result = search_node(enhanced_state)

    return {
        **result,
        "search_queries": all_queries,
    }


# ============================================================================
# Subgraph Creation
# ============================================================================

def create_data_collection_subgraph(
    config: Optional[DataCollectionConfig] = None
) -> StateGraph:
    """
    Create the data collection subgraph.

    This subgraph handles:
    1. Company classification (determines routing)
    2. Query generation (multilingual support)
    3. Web search (with provider fallback)
    4. SEC EDGAR data (US public companies only)
    5. Website scraping (Wikipedia + company sites)

    The subgraph uses conditional routing to optimize data collection
    based on company type.

    Args:
        config: Optional configuration for the subgraph

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = DataCollectionConfig()

    graph = StateGraph(OverallState)

    # ========================================
    # Add Nodes
    # ========================================

    # Classification (entry point)
    graph.add_node("classify", classify_company_node)

    # Query generation
    graph.add_node("generate_queries", generate_queries_node)

    # Search nodes (type-specific)
    graph.add_node("search_standard", search_node)
    graph.add_node("search_startup", startup_search_node)
    graph.add_node("search_international", international_search_node)

    # Data enrichment
    if config.enable_sec_edgar:
        graph.add_node("sec_edgar", sec_edgar_node)

    if config.enable_website_scraping:
        graph.add_node("website_scraping", website_scraping_node)

    # Merge node to combine results
    graph.add_node("merge_results", merge_data_results_node)

    # ========================================
    # Define Edges
    # ========================================

    # Entry point
    graph.set_entry_point("classify")
    graph.add_edge("classify", "generate_queries")

    if config.route_by_company_type:
        # Dynamic routing based on company type
        graph.add_conditional_edges(
            "generate_queries",
            route_by_company_type,
            {
                "public_us": "search_standard",
                "public_intl": "search_international",
                "startup": "search_startup",
                "private": "search_standard",
            }
        )

        # After search, route to SEC or skip
        graph.add_conditional_edges(
            "search_standard",
            route_after_search,
            {
                "sec_edgar": "sec_edgar" if config.enable_sec_edgar else "website_scraping",
                "website_scraping": "website_scraping" if config.enable_website_scraping else "merge_results",
            }
        )

        # International and startup routes skip SEC
        if config.enable_website_scraping:
            graph.add_edge("search_international", "website_scraping")
            graph.add_edge("search_startup", "website_scraping")
        else:
            graph.add_edge("search_international", "merge_results")
            graph.add_edge("search_startup", "merge_results")
    else:
        # Simple linear flow without type-based routing
        graph.add_edge("generate_queries", "search_standard")
        if config.enable_sec_edgar:
            graph.add_edge("search_standard", "sec_edgar")
            if config.enable_website_scraping:
                graph.add_edge("sec_edgar", "website_scraping")
                graph.add_edge("website_scraping", "merge_results")
            else:
                graph.add_edge("sec_edgar", "merge_results")
        elif config.enable_website_scraping:
            graph.add_edge("search_standard", "website_scraping")
            graph.add_edge("website_scraping", "merge_results")
        else:
            graph.add_edge("search_standard", "merge_results")

    # SEC and website scraping lead to merge
    if config.enable_sec_edgar:
        if config.enable_website_scraping:
            graph.add_edge("sec_edgar", "website_scraping")
        else:
            graph.add_edge("sec_edgar", "merge_results")

    if config.enable_website_scraping:
        graph.add_edge("website_scraping", "merge_results")

    # Exit
    graph.add_edge("merge_results", END)

    return graph.compile()


def merge_data_results_node(state: OverallState) -> Dict[str, Any]:
    """
    Merge all data collection results into a unified format.

    This node:
    1. Deduplicates search results by URL
    2. Combines sources from all data providers
    3. Calculates data coverage metrics

    Args:
        state: Current workflow state with all collected data

    Returns:
        State update with merged and deduplicated data
    """
    logger.info("[NODE] Merging data collection results...")

    search_results = state.get("search_results", [])
    sources = state.get("sources", [])
    sec_data = state.get("sec_data", {})
    scraped_content = state.get("scraped_content", {})

    # Deduplicate search results by URL
    seen_urls = set()
    unique_results = []
    for result in search_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    # Calculate data coverage
    data_coverage = {
        "search_results": len(unique_results),
        "unique_sources": len(seen_urls),
        "has_sec_data": bool(sec_data),
        "has_scraped_content": bool(scraped_content),
        "sec_filings_count": len(sec_data.get("filings", [])) if sec_data else 0,
        "scraped_pages_count": len(scraped_content.get("pages", [])) if scraped_content else 0,
    }

    logger.info(f"[MERGE] Data coverage: {data_coverage}")

    return {
        "search_results": unique_results,
        "data_coverage": data_coverage,
    }


# ============================================================================
# Simple Linear Subgraph (Alternative)
# ============================================================================

def create_simple_data_collection_subgraph() -> StateGraph:
    """
    Create a simple linear data collection subgraph without routing.

    Workflow: classify → queries → search → sec_edgar → scrape → END

    Use this for simpler workflows or testing.

    Returns:
        Compiled StateGraph
    """
    graph = StateGraph(OverallState)

    graph.add_node("classify", classify_company_node)
    graph.add_node("generate_queries", generate_queries_node)
    graph.add_node("search", search_node)
    graph.add_node("sec_edgar", sec_edgar_node)
    graph.add_node("website_scraping", website_scraping_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "generate_queries")
    graph.add_edge("generate_queries", "search")
    graph.add_edge("search", "sec_edgar")
    graph.add_edge("sec_edgar", "website_scraping")
    graph.add_edge("website_scraping", END)

    return graph.compile()
