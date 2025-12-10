"""
State definitions for the Company Researcher workflow.

This module defines the state schemas used by LangGraph to manage
the research workflow state transitions.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
from operator import add


def merge_dicts(left: Optional[Dict], right: Optional[Dict]) -> Dict:
    """
    Merge two dictionaries (used for concurrent updates in parallel execution).

    Args:
        left: Existing dictionary (or None)
        right: New dictionary to merge (or None)

    Returns:
        Merged dictionary
    """
    if left is None:
        left = {}
    if right is None:
        right = {}
    return {**left, **right}


def add_tokens(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """
    Add token counts from two dictionaries (used for concurrent updates).

    Args:
        left: Existing token counts
        right: New token counts to add

    Returns:
        Combined token counts
    """
    return {
        "input": left.get("input", 0) + right.get("input", 0),
        "output": left.get("output", 0) + right.get("output", 0)
    }


# ============================================================================
# Input State
# ============================================================================

class InputState(TypedDict):
    """
    Initial input to the research workflow.

    Attributes:
        company_name: Name of the company to research
    """
    company_name: str


# ============================================================================
# Overall State
# ============================================================================

class OverallState(TypedDict):
    """
    Complete state maintained throughout the workflow.

    This state is passed between all nodes in the graph.
    Uses Annotated types with operators to control how updates are merged.
    """

    # Input
    company_name: str

    # Query Generation
    search_queries: List[str]

    # Search Results
    # Using 'add' operator means each node appends to the list
    search_results: Annotated[List[Dict[str, Any]], add]

    # Analysis
    notes: List[str]  # LLM summaries of search results

    # Extracted Data
    company_overview: Optional[str]
    key_metrics: Optional[Dict[str, Any]]
    products_services: Optional[List[str]]
    competitors: Optional[List[str]]
    key_insights: Optional[List[str]]

    # Metadata
    sources: Annotated[List[Dict[str, str]], add]  # URL, title, relevance

    # Quality (Phase 2)
    quality_score: Optional[float]  # Quality score 0-100
    iteration_count: int  # Number of research iterations
    missing_info: Optional[List[str]]  # Missing information to research

    # Company Classification (First node)
    company_classification: Optional[Dict[str, Any]]  # Full classification result
    is_public_company: Optional[bool]  # True if publicly traded
    stock_ticker: Optional[str]  # Stock ticker symbol
    available_data_sources: Optional[List[str]]  # Available data sources
    sec_data: Optional[Dict[str, Any]]  # SEC EDGAR data

    # Scraped Content (Website scraping node)
    scraped_content: Optional[Dict[str, Any]]  # Content scraped from websites

    # Enhanced Analysis (Phase 2+)
    competitive_matrix: Optional[Dict[str, Any]]  # Competitive analysis data
    risk_profile: Optional[Dict[str, Any]]  # Risk assessment data
    investment_thesis: Optional[Dict[str, Any]]  # Investment thesis data
    news_sentiment: Optional[Dict[str, Any]]  # News sentiment analysis
    detected_region: Optional[str]  # Detected geographic region
    detected_language: Optional[str]  # Primary language for searches

    # Agent Coordination (Phase 3+)
    # Using merge_dicts allows concurrent updates from parallel agents (Phase 4)
    agent_outputs: Annotated[Optional[Dict[str, Any]], merge_dicts]  # Track agent contributions

    # Metrics
    start_time: datetime
    total_cost: Annotated[float, add]  # Using add allows concurrent cost accumulation
    total_tokens: Annotated[Dict[str, int], add_tokens]  # {"input": X, "output": Y}

    # Report
    report_path: Optional[str]


# ============================================================================
# Output State
# ============================================================================

class OutputState(TypedDict):
    """
    Final output from the research workflow.

    Attributes:
        company_name: Name of researched company
        report_path: Path to generated markdown report
        metrics: Performance metrics (time, cost, tokens)
        success: Whether research completed successfully
    """
    company_name: str
    report_path: str
    metrics: Dict[str, Any]
    success: bool


# ============================================================================
# Helper Functions
# ============================================================================

def create_initial_state(company_name: str) -> OverallState:
    """
    Create initial state for a new research workflow.

    Args:
        company_name: Name of company to research

    Returns:
        Initialized OverallState
    """
    return {
        "company_name": company_name,
        "search_queries": [],
        "search_results": [],
        "notes": [],
        "company_overview": None,
        "key_metrics": None,
        "products_services": None,
        "competitors": None,
        "key_insights": None,
        "sources": [],
        "quality_score": None,
        "iteration_count": 0,
        "missing_info": None,
        # Company Classification
        "company_classification": None,
        "is_public_company": None,
        "stock_ticker": None,
        "available_data_sources": None,
        "sec_data": None,
        "scraped_content": None,
        # Enhanced Analysis
        "competitive_matrix": None,
        "risk_profile": None,
        "investment_thesis": None,
        "news_sentiment": None,
        "detected_region": None,
        "detected_language": None,
        "agent_outputs": {},
        "start_time": datetime.now(),
        "total_cost": 0.0,
        "total_tokens": {"input": 0, "output": 0},
        "report_path": None
    }


def create_output_state(state: OverallState) -> OutputState:
    """
    Convert OverallState to OutputState.

    Args:
        state: Complete workflow state

    Returns:
        OutputState with results and metrics
    """
    duration = (datetime.now() - state.get("start_time", datetime.now())).total_seconds()

    return {
        "company_name": state.get("company_name", ""),
        "report_path": state.get("report_path", ""),
        "metrics": {
            "duration_seconds": duration,
            "cost_usd": state.get("total_cost", 0.0),
            "tokens": state.get("total_tokens", {"input": 0, "output": 0}),
            "sources_count": len(state.get("sources", [])),
            "quality_score": state.get("quality_score", 0.0),
            "iterations": state.get("iteration_count", 0)
        },
        "success": state.get("report_path") is not None
    }
