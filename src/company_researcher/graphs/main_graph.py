"""
Main Orchestration Graph - Phase 11

This module creates the main research workflow by composing subgraphs.
It provides multiple workflow variants for different use cases:

Workflow Variants:
    - create_research_workflow(): Standard research with all phases
    - create_quick_workflow(): Fast research with minimal agents
    - create_comprehensive_workflow(): Full research with all agents
    - create_adaptive_workflow(): Dynamic routing based on company type

Architecture:
    Main Graph
    ├── Data Collection Subgraph
    │   ├── Classify Company
    │   ├── Generate Queries
    │   ├── Search (routed by company type)
    │   ├── SEC EDGAR (US public only)
    │   └── Website Scraping
    ├── Analysis Subgraph
    │   ├── Financial Agent (parallel)
    │   ├── Market Agent (parallel)
    │   ├── Product Agent (parallel)
    │   ├── Competitor Agent (parallel)
    │   ├── [Optional: ESG, Brand, Social] (parallel)
    │   ├── Merge Outputs
    │   └── Synthesizer
    ├── Quality Subgraph
    │   ├── Extract Facts
    │   ├── Detect Contradictions
    │   ├── Identify Gaps
    │   ├── Logic Critic
    │   ├── Calculate Score
    │   └── Should Iterate?
    └── Output Subgraph
        ├── Prepare Data
        ├── Generate Markdown
        └── Save Files
"""

from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass
from langgraph.graph import StateGraph, START, END

from ..state.workflow import (
    OverallState,
    InputState,
    OutputState,
    create_initial_state,
    create_output_state,
)
from .subgraphs import (
    create_data_collection_subgraph,
    create_analysis_subgraph,
    create_quality_subgraph,
    create_output_subgraph,
    DataCollectionConfig,
    AnalysisConfig,
    QualityConfig,
    OutputConfig,
)
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class WorkflowConfig:
    """Configuration for main research workflow."""

    # Depth level
    depth: Literal["quick", "standard", "comprehensive"] = "standard"

    # Subgraph configurations
    data_collection: Optional[DataCollectionConfig] = None
    analysis: Optional[AnalysisConfig] = None
    quality: Optional[QualityConfig] = None
    output: Optional[OutputConfig] = None

    # Iteration settings
    max_iterations: int = 2
    min_quality_score: float = 85.0
    enable_iteration: bool = True

    # Checkpointing
    enable_checkpointing: bool = False
    checkpoint_db_path: str = "data/checkpoints.db"

    @classmethod
    def quick(cls) -> "WorkflowConfig":
        """Quick research configuration."""
        return cls(
            depth="quick",
            analysis=AnalysisConfig.quick(),
            max_iterations=1,
            enable_iteration=False,
        )

    @classmethod
    def standard(cls) -> "WorkflowConfig":
        """Standard research configuration."""
        return cls(
            depth="standard",
            analysis=AnalysisConfig.standard(),
            max_iterations=2,
        )

    @classmethod
    def comprehensive(cls) -> "WorkflowConfig":
        """Comprehensive research configuration."""
        return cls(
            depth="comprehensive",
            analysis=AnalysisConfig.comprehensive(),
            max_iterations=3,
        )


# ============================================================================
# Routing Functions
# ============================================================================

def should_iterate(state: OverallState) -> str:
    """
    Determine if workflow should iterate for better quality.

    Args:
        state: Current workflow state

    Returns:
        "iterate" to loop back, "complete" to proceed to output
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    should_iterate_flag = state.get("should_iterate", False)

    # Get config values (defaults)
    min_quality = 85.0
    max_iterations = 2

    if quality_score >= min_quality:
        logger.info(f"[ROUTE] Quality sufficient ({quality_score:.1f} >= {min_quality})")
        return "complete"
    elif iteration_count >= max_iterations:
        logger.info(f"[ROUTE] Max iterations reached ({iteration_count}/{max_iterations})")
        return "complete"
    elif should_iterate_flag:
        logger.info(f"[ROUTE] Quality low ({quality_score:.1f}), iterating...")
        return "iterate"
    else:
        return "complete"


# ============================================================================
# Main Workflow Creation
# ============================================================================

def create_research_workflow(
    config: Optional[WorkflowConfig] = None
) -> StateGraph:
    """
    Create the main research workflow using subgraphs.

    This is the primary workflow that:
    1. Collects data (with company-type routing)
    2. Analyzes data (parallel agents)
    3. Validates quality (with iteration loop)
    4. Generates output

    Args:
        config: Optional workflow configuration

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = WorkflowConfig.standard()

    logger.info(f"[WORKFLOW] Creating {config.depth} research workflow")

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    # ========================================
    # Create and Add Subgraphs as Nodes
    # ========================================

    # Data Collection Subgraph
    data_config = config.data_collection or DataCollectionConfig()
    data_collection = create_data_collection_subgraph(data_config)
    graph.add_node("data_collection", data_collection)

    # Analysis Subgraph
    analysis_config = config.analysis or AnalysisConfig.standard()
    analysis = create_analysis_subgraph(analysis_config)
    graph.add_node("analysis", analysis)

    # Quality Subgraph
    quality_config = config.quality or QualityConfig()
    quality = create_quality_subgraph(quality_config)
    graph.add_node("quality", quality)

    # Output Subgraph
    output_config = config.output or OutputConfig()
    output = create_output_subgraph(output_config)
    graph.add_node("output", output)

    # ========================================
    # Define Main Workflow Edges
    # ========================================

    # Entry: Start with data collection
    graph.set_entry_point("data_collection")

    # Data Collection → Analysis
    graph.add_edge("data_collection", "analysis")

    # Analysis → Quality Check
    graph.add_edge("analysis", "quality")

    # Quality Check → Conditional (iterate or complete)
    if config.enable_iteration:
        graph.add_conditional_edges(
            "quality",
            should_iterate,
            {
                "iterate": "data_collection",  # Loop back
                "complete": "output",  # Proceed to output
            }
        )
    else:
        graph.add_edge("quality", "output")

    # Output → END
    graph.add_edge("output", END)

    return graph.compile()


def create_quick_workflow() -> StateGraph:
    """
    Create a quick research workflow for fast results.

    Uses minimal agents and no iteration.

    Returns:
        Compiled StateGraph
    """
    return create_research_workflow(WorkflowConfig.quick())


def create_comprehensive_workflow() -> StateGraph:
    """
    Create a comprehensive research workflow.

    Uses all agents and allows multiple iterations.

    Returns:
        Compiled StateGraph
    """
    return create_research_workflow(WorkflowConfig.comprehensive())


# ============================================================================
# Adaptive Workflow (Phase 14)
# ============================================================================

def create_adaptive_workflow(
    config: Optional[WorkflowConfig] = None
) -> StateGraph:
    """
    Create an adaptive workflow that adjusts based on company type.

    This workflow:
    1. Classifies company first
    2. Routes to appropriate data collection strategy
    3. Selects agents based on company type
    4. Adjusts quality thresholds

    Args:
        config: Optional workflow configuration

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = WorkflowConfig.standard()

    logger.info("[WORKFLOW] Creating adaptive research workflow")

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    # ========================================
    # Add Classification Node
    # ========================================

    from ..agents.core.company_classifier import classify_company_node
    graph.add_node("classify", classify_company_node)

    # ========================================
    # Create Type-Specific Analysis Subgraphs
    # ========================================

    # Public US companies: Full financial analysis
    public_us_analysis = create_analysis_subgraph(AnalysisConfig(
        enable_financial=True,
        enable_market=True,
        enable_product=True,
        enable_competitor=True,
        enable_esg=True,  # ESG for public companies
        enable_brand=False,
        enable_social_media=False,
        enable_sales_intelligence=False,
    ))
    graph.add_node("analysis_public_us", public_us_analysis)

    # Public international: Similar but different data sources
    public_intl_analysis = create_analysis_subgraph(AnalysisConfig(
        enable_financial=True,
        enable_market=True,
        enable_product=True,
        enable_competitor=True,
        enable_esg=True,
        enable_brand=False,
        enable_social_media=False,
        enable_sales_intelligence=False,
    ))
    graph.add_node("analysis_public_intl", public_intl_analysis)

    # Private companies: Focus on market and competitive
    private_analysis = create_analysis_subgraph(AnalysisConfig(
        enable_financial=True,
        enable_market=True,
        enable_product=True,
        enable_competitor=True,
        enable_esg=False,  # Less ESG data for private
        enable_brand=True,  # Brand matters more
        enable_social_media=True,  # Social presence
        enable_sales_intelligence=True,  # Sales intel
    ))
    graph.add_node("analysis_private", private_analysis)

    # Startups: Different focus
    startup_analysis = create_analysis_subgraph(AnalysisConfig(
        enable_financial=True,
        enable_market=True,
        enable_product=True,
        enable_competitor=True,
        enable_esg=False,
        enable_brand=True,
        enable_social_media=True,
        enable_sales_intelligence=False,
    ))
    graph.add_node("analysis_startup", startup_analysis)

    # ========================================
    # Data Collection (same for all)
    # ========================================

    data_collection = create_data_collection_subgraph(
        DataCollectionConfig(route_by_company_type=True)
    )
    graph.add_node("data_collection", data_collection)

    # ========================================
    # Quality and Output (same for all)
    # ========================================

    quality = create_quality_subgraph(QualityConfig())
    graph.add_node("quality", quality)

    output = create_output_subgraph(OutputConfig())
    graph.add_node("output", output)

    # ========================================
    # Define Edges with Routing
    # ========================================

    def route_to_analysis(state: OverallState) -> str:
        """Route to appropriate analysis based on company type."""
        classification = state.get("company_classification", {})
        is_public = classification.get("is_public_company", False)
        exchange = classification.get("exchange", "")
        company_type = classification.get("company_type", "private")

        us_exchanges = {"NYSE", "NASDAQ", "AMEX", "OTC"}

        if is_public and exchange in us_exchanges:
            return "analysis_public_us"
        elif is_public:
            return "analysis_public_intl"
        elif company_type in ("startup", "venture-backed"):
            return "analysis_startup"
        else:
            return "analysis_private"

    # Entry: Classify first
    graph.set_entry_point("classify")

    # Classify → Data Collection
    graph.add_edge("classify", "data_collection")

    # Data Collection → Route to Analysis
    graph.add_conditional_edges(
        "data_collection",
        route_to_analysis,
        {
            "analysis_public_us": "analysis_public_us",
            "analysis_public_intl": "analysis_public_intl",
            "analysis_private": "analysis_private",
            "analysis_startup": "analysis_startup",
        }
    )

    # All analysis paths → Quality
    graph.add_edge("analysis_public_us", "quality")
    graph.add_edge("analysis_public_intl", "quality")
    graph.add_edge("analysis_private", "quality")
    graph.add_edge("analysis_startup", "quality")

    # Quality → Output (no iteration for adaptive to keep simple)
    graph.add_edge("quality", "output")
    graph.add_edge("output", END)

    return graph.compile()


# ============================================================================
# Research Functions
# ============================================================================

def research_company(
    company_name: str,
    depth: Literal["quick", "standard", "comprehensive"] = "standard",
    config: Optional[WorkflowConfig] = None,
) -> OutputState:
    """
    Research a company using the main workflow.

    Args:
        company_name: Name of company to research
        depth: Research depth ("quick", "standard", "comprehensive")
        config: Optional custom configuration

    Returns:
        OutputState with results and metrics
    """
    print(f"\n{'='*60}")
    print(f"[WORKFLOW] Phase 11 Research: {company_name}")
    print(f"[WORKFLOW] Depth: {depth}")
    print(f"{'='*60}")

    # Create workflow based on depth
    if config:
        workflow = create_research_workflow(config)
    elif depth == "quick":
        workflow = create_quick_workflow()
    elif depth == "comprehensive":
        workflow = create_comprehensive_workflow()
    else:
        workflow = create_research_workflow()

    # Create initial state
    initial_state = create_initial_state(company_name)

    # Run workflow
    final_state = workflow.invoke(initial_state)

    # Convert to output
    output = create_output_state(final_state)

    # Print summary
    print(f"\n{'='*60}")
    print("[RESULTS] Research Complete")
    print(f"{'='*60}")
    print(f"Report: {output['report_path']}")
    print(f"Duration: {output['metrics']['duration_seconds']:.1f}s")
    print(f"Cost: ${output['metrics']['cost_usd']:.4f}")
    print(f"Quality: {output['metrics']['quality_score']:.1f}/100")
    print(f"Iterations: {output['metrics']['iterations']}")
    print(f"{'='*60}\n")

    return output


def research_company_adaptive(company_name: str) -> OutputState:
    """
    Research a company using the adaptive workflow.

    The workflow automatically adjusts based on company type.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with results and metrics
    """
    print(f"\n{'='*60}")
    print(f"[WORKFLOW] Adaptive Research: {company_name}")
    print(f"{'='*60}")

    workflow = create_adaptive_workflow()
    initial_state = create_initial_state(company_name)
    final_state = workflow.invoke(initial_state)
    output = create_output_state(final_state)

    print(f"\n{'='*60}")
    print("[RESULTS] Adaptive Research Complete")
    print(f"Report: {output['report_path']}")
    print(f"{'='*60}\n")

    return output


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Configurations
    "WorkflowConfig",
    # Workflow creation
    "create_research_workflow",
    "create_quick_workflow",
    "create_comprehensive_workflow",
    "create_adaptive_workflow",
    # Research functions
    "research_company",
    "research_company_adaptive",
]
