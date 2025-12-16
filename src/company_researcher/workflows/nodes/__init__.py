"""
Workflow Nodes Package

This package contains modular node functions for LangGraph workflows.
Each module groups related nodes by functionality.

Modules:
    - search_nodes: Query generation, web search, SEC EDGAR, website scraping
    - analysis_nodes: Claude analysis, data extraction, quality checking
    - enrichment_nodes: News sentiment, competitive analysis, risk assessment
    - output_nodes: Investment thesis generation, report saving
    - data_collection_nodes: Financial and news data fetching (comprehensive workflow)
    - comprehensive_analysis_nodes: Multi-faceted company analysis (financial, market, ESG, brand)
    - comprehensive_output_nodes: Comprehensive report generation

Usage:
    from company_researcher.workflows.nodes import (
        generate_queries_node,
        search_node,
        sec_edgar_node,
        website_scraping_node,
        analyze_node,
        extract_data_node,
        check_quality_node,
        news_sentiment_node,
        competitive_analysis_node,
        risk_assessment_node,
        investment_thesis_node,
        save_report_node,
        # Comprehensive workflow nodes
        core_analysis_node,
        financial_analysis_node,
        market_analysis_node,
        esg_analysis_node,
        brand_analysis_node,
        fetch_financial_data_node,
        fetch_news_node,
        save_comprehensive_report_node,
    )
"""

from .analysis_nodes import (
    analyze_node,
    check_quality_node,
    extract_data_node,
    should_continue_research,
)
from .comprehensive_analysis_nodes import (
    brand_analysis_node,
    core_analysis_node,
    esg_analysis_node,
    financial_analysis_node,
    market_analysis_node,
)
from .comprehensive_output_nodes import (
    enrich_executive_summary_node,
    save_comprehensive_report_node,
)
from .data_collection_nodes import fetch_financial_data_node, fetch_news_node
from .enrichment_nodes import (
    competitive_analysis_node,
    financial_comparison_node,
    news_sentiment_node,
    risk_assessment_node,
)
from .output_nodes import investment_thesis_node, save_report_node
from .search_nodes import (  # Integration availability flags
    JINA_AVAILABLE,
    SEC_EDGAR_AVAILABLE,
    WIKIPEDIA_AVAILABLE,
    generate_queries_node,
    search_node,
    sec_edgar_node,
    website_scraping_node,
)

__all__ = [
    # Search nodes
    "generate_queries_node",
    "search_node",
    "sec_edgar_node",
    "website_scraping_node",
    # Analysis nodes
    "analyze_node",
    "extract_data_node",
    "check_quality_node",
    "should_continue_research",
    # Enrichment nodes
    "news_sentiment_node",
    "competitive_analysis_node",
    "risk_assessment_node",
    "financial_comparison_node",
    # Output nodes
    "investment_thesis_node",
    "save_report_node",
    # Comprehensive analysis nodes
    "core_analysis_node",
    "financial_analysis_node",
    "market_analysis_node",
    "esg_analysis_node",
    "brand_analysis_node",
    # Data collection nodes
    "fetch_financial_data_node",
    "fetch_news_node",
    # Comprehensive output nodes
    "enrich_executive_summary_node",
    "save_comprehensive_report_node",
    # Flags
    "SEC_EDGAR_AVAILABLE",
    "JINA_AVAILABLE",
    "WIKIPEDIA_AVAILABLE",
]
