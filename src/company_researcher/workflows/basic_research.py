"""
Basic Research Workflow - Phase 1

This module implements a single-agent LangGraph workflow for company research.

Workflow:
    Input → Generate Queries → Search → Analyze → Extract Data → Save Report → Output
"""

from langgraph.graph import END, StateGraph

from ..agents.core.company_classifier import classify_company_node
from ..state import InputState, OutputState, OverallState, create_initial_state, create_output_state

# Import all workflow nodes from the nodes package
from .nodes import (  # Search nodes; Analysis nodes; Enrichment nodes; Output nodes
    analyze_node,
    check_quality_node,
    competitive_analysis_node,
    extract_data_node,
    generate_queries_node,
    investment_thesis_node,
    news_sentiment_node,
    risk_assessment_node,
    save_report_node,
    search_node,
    sec_edgar_node,
    should_continue_research,
    website_scraping_node,
)

# ============================================================================
# Workflow Graph Construction
# ============================================================================


def create_research_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for basic research.

    Workflow:
        classify_company → generate_queries → search → sec_edgar → website_scraping →
        analyze → news_sentiment → extract_data → check_quality →
        (if quality OK) → competitive_analysis → risk_assessment → investment_thesis → save_report

    Data Sources (FREE):
        - Web search (Brave/Tavily)
        - SEC EDGAR (US company filings)
        - Wikipedia (company overviews, infobox data)
        - Jina Reader (website scraping via r.jina.ai)

    Returns:
        Compiled StateGraph workflow
    """
    # Create graph
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add nodes
    workflow.add_node("classify_company", classify_company_node)  # First node - classify company
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", search_node)
    workflow.add_node("sec_edgar", sec_edgar_node)  # FREE SEC filings for US companies
    workflow.add_node(
        "website_scraping", website_scraping_node
    )  # FREE Wikipedia + Jina website scraping
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("check_quality", check_quality_node)
    # Enhanced analysis nodes
    workflow.add_node("news_sentiment", news_sentiment_node)
    workflow.add_node("competitive_analysis", competitive_analysis_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("investment_thesis", investment_thesis_node)
    workflow.add_node("save_report", save_report_node)

    # Define edges - classify_company is the entry point
    workflow.set_entry_point("classify_company")
    workflow.add_edge("classify_company", "generate_queries")  # Classify → Generate queries
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "sec_edgar")  # Fetch SEC filings after web search
    workflow.add_edge("sec_edgar", "website_scraping")  # Scrape Wikipedia + company websites (FREE)
    workflow.add_edge("website_scraping", "analyze")
    workflow.add_edge("analyze", "news_sentiment")  # Add sentiment analysis after search
    workflow.add_edge("news_sentiment", "extract_data")
    workflow.add_edge("extract_data", "check_quality")

    # Conditional edge from check_quality
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {
            "iterate": "generate_queries",  # Loop back to improve
            "finish": "competitive_analysis",  # Quality is good, proceed to analysis
        },
    )

    # Enhanced analysis pipeline
    workflow.add_edge("competitive_analysis", "risk_assessment")
    workflow.add_edge("risk_assessment", "investment_thesis")
    workflow.add_edge("investment_thesis", "save_report")
    workflow.add_edge("save_report", END)

    return workflow.compile()


# ============================================================================
# Main Research Function
# ============================================================================


def research_company(company_name: str) -> OutputState:
    """
    Research a company using the basic workflow.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with results and metrics
    """
    print(f"\n{'='*60}")
    print(f"[WORKFLOW] Researching: {company_name}")
    print(f"{'='*60}")

    # Create workflow
    workflow = create_research_workflow()

    # Create initial state
    initial_state = create_initial_state(company_name)

    # Run workflow
    final_state = workflow.invoke(initial_state)

    # Convert to output state
    output = create_output_state(final_state)

    # Print summary
    print(f"\n{'='*60}")
    print("[RESULTS] Research Complete")
    print(f"{'='*60}")
    print(f"Report: {output['report_path']}")
    print(f"Duration: {output['metrics']['duration_seconds']:.1f}s")
    print(f"Cost: ${output['metrics']['cost_usd']:.4f}")
    print(
        f"Tokens: {output['metrics']['tokens']['input']:,} in, {output['metrics']['tokens']['output']:,} out"
    )
    print(f"Sources: {output['metrics']['sources_count']}")
    print(f"{'='*60}\n")

    return output
