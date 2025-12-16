"""
Analysis Subgraph - Phase 11

Handles parallel execution of specialist agents:
- Financial Agent: Revenue, profitability, financial health
- Market Agent: Competitive landscape, market position
- Product Agent: Products/services, technology stack
- Competitor Agent: Competitive intelligence
- ESG Agent: Environmental, social, governance (optional)
- Brand Agent: Brand perception and sentiment (optional)

LangGraph automatically parallelizes agents that have no dependencies
between them, maximizing throughput.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langgraph.graph import END, START, StateGraph

from ...agents import (  # Core specialist agents; Optional agents; Synthesizer
    brand_auditor_agent_node,
    competitor_scout_agent_node,
    esg_agent_node,
    financial_agent_node,
    market_agent_node,
    product_agent_node,
    sales_intelligence_agent_node,
    social_media_agent_node,
    synthesizer_agent_node,
)
from ...state.workflow import OverallState
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class AnalysisConfig:
    """Configuration for analysis subgraph."""

    # Core agents (always enabled)
    enable_financial: bool = True
    enable_market: bool = True
    enable_product: bool = True
    enable_competitor: bool = True

    # Optional specialist agents
    enable_esg: bool = False
    enable_brand: bool = False
    enable_social_media: bool = False
    enable_sales_intelligence: bool = False

    # Synthesis settings
    enable_synthesizer: bool = True
    synthesizer_detailed: bool = True

    # Parallel execution settings
    max_parallel_agents: int = 6

    # Agent selection based on research depth
    depth: str = "standard"  # "quick", "standard", "comprehensive"

    @classmethod
    def quick(cls) -> "AnalysisConfig":
        """Quick analysis - minimal agents."""
        return cls(
            enable_financial=True,
            enable_market=True,
            enable_product=False,
            enable_competitor=False,
            enable_esg=False,
            enable_brand=False,
            enable_social_media=False,
            enable_sales_intelligence=False,
            depth="quick",
        )

    @classmethod
    def standard(cls) -> "AnalysisConfig":
        """Standard analysis - core agents."""
        return cls(
            enable_financial=True,
            enable_market=True,
            enable_product=True,
            enable_competitor=True,
            enable_esg=False,
            enable_brand=False,
            enable_social_media=False,
            enable_sales_intelligence=False,
            depth="standard",
        )

    @classmethod
    def comprehensive(cls) -> "AnalysisConfig":
        """Comprehensive analysis - all agents."""
        return cls(
            enable_financial=True,
            enable_market=True,
            enable_product=True,
            enable_competitor=True,
            enable_esg=True,
            enable_brand=True,
            enable_social_media=True,
            enable_sales_intelligence=True,
            depth="comprehensive",
        )


# ============================================================================
# Helper Nodes
# ============================================================================


def prepare_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Prepare state for parallel analysis.

    This node:
    1. Validates that required data is present
    2. Formats search results for agents
    3. Sets up tracking for agent outputs

    Args:
        state: Current workflow state

    Returns:
        State update with prepared data
    """
    logger.info("[NODE] Preparing for parallel analysis...")

    search_results = state.get("search_results", [])
    sources = state.get("sources", [])

    if not search_results:
        logger.warning("[WARN] No search results available for analysis")

    # Ensure agent_outputs exists
    agent_outputs = state.get("agent_outputs", {})

    return {
        "agent_outputs": agent_outputs,
        "analysis_started": True,
    }


def merge_agent_outputs_node(state: OverallState) -> Dict[str, Any]:
    """
    Merge outputs from all parallel agents.

    This node runs after all parallel agents complete and:
    1. Combines agent outputs into unified structure
    2. Resolves conflicts between agent findings
    3. Calculates aggregate metrics

    Args:
        state: Current workflow state with all agent outputs

    Returns:
        State update with merged analysis
    """
    logger.info("[NODE] Merging agent outputs...")

    agent_outputs = state.get("agent_outputs", {})

    # Count successful agents
    successful_agents = sum(
        1
        for output in agent_outputs.values()
        if output.get("status") == "success" or output.get("data_extracted", False)
    )

    total_agents = len(agent_outputs)

    # Calculate total analysis cost
    total_analysis_cost = sum(output.get("cost", 0.0) for output in agent_outputs.values())

    # Calculate total tokens
    total_analysis_tokens = {
        "input": sum(output.get("tokens", {}).get("input", 0) for output in agent_outputs.values()),
        "output": sum(
            output.get("tokens", {}).get("output", 0) for output in agent_outputs.values()
        ),
    }

    logger.info(f"[MERGE] {successful_agents}/{total_agents} agents successful")
    logger.info(f"[MERGE] Analysis cost: ${total_analysis_cost:.4f}")

    return {
        "analysis_complete": True,
        "analysis_metrics": {
            "successful_agents": successful_agents,
            "total_agents": total_agents,
            "success_rate": successful_agents / total_agents if total_agents > 0 else 0,
            "total_cost": total_analysis_cost,
            "total_tokens": total_analysis_tokens,
        },
    }


# ============================================================================
# Subgraph Creation
# ============================================================================


def create_analysis_subgraph(config: Optional[AnalysisConfig] = None) -> StateGraph:
    """
    Create the analysis subgraph with parallel agent execution.

    This subgraph:
    1. Prepares data for analysis
    2. Runs specialist agents in parallel (LangGraph handles parallelization)
    3. Merges agent outputs
    4. Optionally runs synthesizer to create unified overview

    Args:
        config: Optional configuration for the subgraph

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = AnalysisConfig.standard()

    graph = StateGraph(OverallState)

    # ========================================
    # Add Nodes
    # ========================================

    # Preparation
    graph.add_node("prepare", prepare_analysis_node)

    # Core specialist agents
    if config.enable_financial:
        graph.add_node("financial", financial_agent_node)

    if config.enable_market:
        graph.add_node("market", market_agent_node)

    if config.enable_product:
        graph.add_node("product", product_agent_node)

    if config.enable_competitor:
        graph.add_node("competitor", competitor_scout_agent_node)

    # Optional specialist agents
    if config.enable_esg:
        graph.add_node("esg", esg_agent_node)

    if config.enable_brand:
        graph.add_node("brand", brand_auditor_agent_node)

    if config.enable_social_media:
        graph.add_node("social_media", social_media_agent_node)

    if config.enable_sales_intelligence:
        graph.add_node("sales", sales_intelligence_agent_node)

    # Merge results
    graph.add_node("merge", merge_agent_outputs_node)

    # Synthesizer (optional)
    if config.enable_synthesizer:
        graph.add_node("synthesize", synthesizer_agent_node)

    # ========================================
    # Define Edges (Fan-out / Fan-in Pattern)
    # ========================================

    # Entry
    graph.set_entry_point("prepare")

    # Fan-out: All agents start from prepare (PARALLEL EXECUTION)
    # LangGraph automatically runs these in parallel since they
    # all depend on "prepare" and don't depend on each other

    enabled_agents = []

    if config.enable_financial:
        graph.add_edge("prepare", "financial")
        enabled_agents.append("financial")

    if config.enable_market:
        graph.add_edge("prepare", "market")
        enabled_agents.append("market")

    if config.enable_product:
        graph.add_edge("prepare", "product")
        enabled_agents.append("product")

    if config.enable_competitor:
        graph.add_edge("prepare", "competitor")
        enabled_agents.append("competitor")

    if config.enable_esg:
        graph.add_edge("prepare", "esg")
        enabled_agents.append("esg")

    if config.enable_brand:
        graph.add_edge("prepare", "brand")
        enabled_agents.append("brand")

    if config.enable_social_media:
        graph.add_edge("prepare", "social_media")
        enabled_agents.append("social_media")

    if config.enable_sales_intelligence:
        graph.add_edge("prepare", "sales")
        enabled_agents.append("sales")

    # Fan-in: All agents merge into merge node
    for agent in enabled_agents:
        graph.add_edge(agent, "merge")

    # After merge
    if config.enable_synthesizer:
        graph.add_edge("merge", "synthesize")
        graph.add_edge("synthesize", END)
    else:
        graph.add_edge("merge", END)

    return graph.compile()


def create_parallel_analysis_subgraph(agents: Optional[List[str]] = None) -> StateGraph:
    """
    Create a custom parallel analysis subgraph with specified agents.

    This is a more flexible version that allows specifying exactly
    which agents to run.

    Args:
        agents: List of agent names to include. Options:
            - "financial"
            - "market"
            - "product"
            - "competitor"
            - "esg"
            - "brand"
            - "social_media"
            - "sales"

    Returns:
        Compiled StateGraph
    """
    if agents is None:
        agents = ["financial", "market", "product", "competitor"]

    # Map agent names to node functions
    agent_map = {
        "financial": financial_agent_node,
        "market": market_agent_node,
        "product": product_agent_node,
        "competitor": competitor_scout_agent_node,
        "esg": esg_agent_node,
        "brand": brand_auditor_agent_node,
        "social_media": social_media_agent_node,
        "sales": sales_intelligence_agent_node,
    }

    graph = StateGraph(OverallState)

    # Add prepare node
    graph.add_node("prepare", prepare_analysis_node)

    # Add requested agents
    valid_agents = []
    for agent_name in agents:
        if agent_name in agent_map:
            graph.add_node(agent_name, agent_map[agent_name])
            valid_agents.append(agent_name)
        else:
            logger.warning(f"Unknown agent: {agent_name}")

    # Add merge and synthesize
    graph.add_node("merge", merge_agent_outputs_node)
    graph.add_node("synthesize", synthesizer_agent_node)

    # Entry
    graph.set_entry_point("prepare")

    # Fan-out to all agents
    for agent_name in valid_agents:
        graph.add_edge("prepare", agent_name)

    # Fan-in to merge
    for agent_name in valid_agents:
        graph.add_edge(agent_name, "merge")

    # Merge to synthesize to end
    graph.add_edge("merge", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


# ============================================================================
# Specialized Analysis Subgraphs
# ============================================================================


def create_financial_focus_subgraph() -> StateGraph:
    """
    Create a subgraph focused on financial analysis.

    Includes: financial, market (for context), synthesizer

    Returns:
        Compiled StateGraph
    """
    return create_parallel_analysis_subgraph(agents=["financial", "market"])


def create_competitive_focus_subgraph() -> StateGraph:
    """
    Create a subgraph focused on competitive analysis.

    Includes: market, competitor, product, synthesizer

    Returns:
        Compiled StateGraph
    """
    return create_parallel_analysis_subgraph(agents=["market", "competitor", "product"])


def create_esg_focus_subgraph() -> StateGraph:
    """
    Create a subgraph focused on ESG analysis.

    Includes: esg, brand, social_media, synthesizer

    Returns:
        Compiled StateGraph
    """
    return create_parallel_analysis_subgraph(agents=["esg", "brand", "social_media"])
