"""
Research Workflow Templates (Phase 17.3).

Pre-built workflow configurations for company research:
- Quick research (basic info)
- Standard research (balanced)
- Comprehensive research (full analysis)
- Custom workflow builder

Integrates all agents into cohesive workflows.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .workflow_engine import (
    WorkflowEngine,
    WorkflowState,
    NodeConfig,
    NodeType,
    RouteCondition,
    ExecutionStatus,
    create_workflow_engine,
)


# ============================================================================
# Research Depth Configuration
# ============================================================================

class ResearchDepth(str, Enum):
    """Research depth levels."""
    QUICK = "quick"            # Basic company info only
    STANDARD = "standard"      # Core analysis agents
    COMPREHENSIVE = "comprehensive"  # Full analysis suite
    CUSTOM = "custom"          # User-defined


@dataclass
class ResearchConfig:
    """Research workflow configuration."""
    depth: ResearchDepth = ResearchDepth.STANDARD
    include_financial: bool = True
    include_market: bool = True
    include_competitive: bool = True
    include_news: bool = True
    include_brand: bool = False
    include_social: bool = False
    include_sales: bool = False
    include_investment: bool = False
    include_deep_research: bool = False
    max_parallel: int = 4
    enable_quality_check: bool = True


# ============================================================================
# Agent Node Handlers (Stubs - Connect to actual agents)
# ============================================================================

def _create_search_node() -> Callable:
    """Create search agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Search] Searching for: {company_name}")

        # In production, this would call the actual search agent
        return {
            "search_results": [
                {"title": f"{company_name} Overview", "content": f"Information about {company_name}..."},
                {"title": f"{company_name} News", "content": f"Recent news about {company_name}..."},
            ],
            "agent_outputs": {
                "search": {"status": "completed", "result_count": 2}
            },
            "total_cost": 0.001
        }
    return handler


def _create_financial_node() -> Callable:
    """Create financial agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Financial] Analyzing: {company_name}")

        return {
            "agent_outputs": {
                "financial": {
                    "analysis": f"Financial analysis for {company_name}",
                    "health_score": 75.0,
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_market_node() -> Callable:
    """Create market analysis agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Market] Analyzing market for: {company_name}")

        return {
            "agent_outputs": {
                "market": {
                    "analysis": f"Market analysis for {company_name}",
                    "market_score": 70.0,
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_competitive_node() -> Callable:
    """Create competitive analysis agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Competitive] Analyzing competitors for: {company_name}")

        return {
            "agent_outputs": {
                "competitive": {
                    "analysis": f"Competitive analysis for {company_name}",
                    "competitors": ["Competitor A", "Competitor B"],
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_news_node() -> Callable:
    """Create news analysis agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[News] Analyzing news for: {company_name}")

        return {
            "agent_outputs": {
                "news": {
                    "analysis": f"News analysis for {company_name}",
                    "sentiment": "positive",
                    "cost": 0.008
                }
            },
            "total_cost": 0.008
        }
    return handler


def _create_brand_node() -> Callable:
    """Create brand auditor agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Brand] Auditing brand for: {company_name}")

        return {
            "agent_outputs": {
                "brand": {
                    "analysis": f"Brand audit for {company_name}",
                    "brand_score": 72.0,
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_social_node() -> Callable:
    """Create social media agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Social] Analyzing social presence for: {company_name}")

        return {
            "agent_outputs": {
                "social_media": {
                    "analysis": f"Social media analysis for {company_name}",
                    "social_score": 65.0,
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_sales_node() -> Callable:
    """Create sales intelligence agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Sales] Generating sales intel for: {company_name}")

        return {
            "agent_outputs": {
                "sales": {
                    "analysis": f"Sales intelligence for {company_name}",
                    "lead_score": "warm",
                    "cost": 0.01
                }
            },
            "total_cost": 0.01
        }
    return handler


def _create_investment_node() -> Callable:
    """Create investment analyst agent node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        print(f"[Investment] Analyzing investment potential for: {company_name}")

        return {
            "agent_outputs": {
                "investment": {
                    "analysis": f"Investment analysis for {company_name}",
                    "rating": "BUY",
                    "cost": 0.015
                }
            },
            "total_cost": 0.015
        }
    return handler


def _create_quality_node() -> Callable:
    """Create quality checker node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        print("[Quality] Running quality checks...")

        agent_outputs = state.get("agent_outputs", {})
        quality_score = 0.8 if len(agent_outputs) > 3 else 0.6

        return {
            "quality_score": quality_score,
            "agent_outputs": {
                "quality": {
                    "score": quality_score,
                    "checks_passed": len(agent_outputs),
                    "cost": 0.005
                }
            },
            "total_cost": 0.005
        }
    return handler


def _create_synthesis_node() -> Callable:
    """Create synthesis node handler."""
    def handler(state: Dict[str, Any]) -> Dict[str, Any]:
        company_name = state.get("company_name", "Unknown")
        agent_outputs = state.get("agent_outputs", {})

        print(f"[Synthesis] Synthesizing research for: {company_name}")

        # Aggregate all agent analyses
        synthesis = {
            "company_name": company_name,
            "agents_completed": list(agent_outputs.keys()),
            "summary": f"Comprehensive research synthesis for {company_name}"
        }

        return {
            "synthesis": synthesis,
            "agent_outputs": {
                "synthesis": synthesis
            },
            "total_cost": 0.01
        }
    return handler


# ============================================================================
# Workflow Builders
# ============================================================================

def create_research_workflow(
    config: Optional[ResearchConfig] = None,
    use_actual_agents: bool = False
) -> WorkflowEngine:
    """
    Create a research workflow based on configuration.

    Args:
        config: Research configuration
        use_actual_agents: Whether to use actual agent implementations

    Returns:
        Configured WorkflowEngine
    """
    cfg = config or ResearchConfig()

    engine = create_workflow_engine(
        max_parallel=cfg.max_parallel,
        enable_retries=True
    )

    # Start with search
    engine.add_node(NodeConfig(
        name="search",
        node_type=NodeType.AGENT,
        handler=_create_search_node(),
        children=["parallel_analysis"]
    ))

    # Parallel analysis group
    parallel_children = []

    if cfg.include_financial:
        engine.add_node(NodeConfig(
            name="financial",
            node_type=NodeType.AGENT,
            handler=_create_financial_node()
        ))
        parallel_children.append("financial")

    if cfg.include_market:
        engine.add_node(NodeConfig(
            name="market",
            node_type=NodeType.AGENT,
            handler=_create_market_node()
        ))
        parallel_children.append("market")

    if cfg.include_competitive:
        engine.add_node(NodeConfig(
            name="competitive",
            node_type=NodeType.AGENT,
            handler=_create_competitive_node()
        ))
        parallel_children.append("competitive")

    if cfg.include_news:
        engine.add_node(NodeConfig(
            name="news",
            node_type=NodeType.AGENT,
            handler=_create_news_node()
        ))
        parallel_children.append("news")

    if cfg.include_brand:
        engine.add_node(NodeConfig(
            name="brand",
            node_type=NodeType.AGENT,
            handler=_create_brand_node()
        ))
        parallel_children.append("brand")

    if cfg.include_social:
        engine.add_node(NodeConfig(
            name="social",
            node_type=NodeType.AGENT,
            handler=_create_social_node()
        ))
        parallel_children.append("social")

    if cfg.include_sales:
        engine.add_node(NodeConfig(
            name="sales",
            node_type=NodeType.AGENT,
            handler=_create_sales_node()
        ))
        parallel_children.append("sales")

    if cfg.include_investment:
        engine.add_node(NodeConfig(
            name="investment",
            node_type=NodeType.AGENT,
            handler=_create_investment_node()
        ))
        parallel_children.append("investment")

    # Add parallel execution node
    engine.add_node(NodeConfig(
        name="parallel_analysis",
        node_type=NodeType.PARALLEL,
        children=parallel_children
    ))
    engine.connect("parallel_analysis", "quality" if cfg.enable_quality_check else "synthesis")

    # Quality check
    if cfg.enable_quality_check:
        engine.add_node(NodeConfig(
            name="quality",
            node_type=NodeType.AGENT,
            handler=_create_quality_node(),
            children=["synthesis"]
        ))

    # Final synthesis
    engine.add_node(NodeConfig(
        name="synthesis",
        node_type=NodeType.AGENT,
        handler=_create_synthesis_node(),
        children=["end"]
    ))

    # End node
    engine.add_node(NodeConfig(
        name="end",
        node_type=NodeType.END
    ))

    return engine


def create_quick_research_workflow() -> WorkflowEngine:
    """Create a quick research workflow (basic info only)."""
    config = ResearchConfig(
        depth=ResearchDepth.QUICK,
        include_financial=True,
        include_market=False,
        include_competitive=False,
        include_news=True,
        include_brand=False,
        include_social=False,
        include_sales=False,
        include_investment=False,
        enable_quality_check=False,
        max_parallel=2
    )
    return create_research_workflow(config)


def create_comprehensive_research_workflow() -> WorkflowEngine:
    """Create a comprehensive research workflow (full analysis)."""
    config = ResearchConfig(
        depth=ResearchDepth.COMPREHENSIVE,
        include_financial=True,
        include_market=True,
        include_competitive=True,
        include_news=True,
        include_brand=True,
        include_social=True,
        include_sales=True,
        include_investment=True,
        include_deep_research=True,
        enable_quality_check=True,
        max_parallel=6
    )
    return create_research_workflow(config)


# ============================================================================
# Convenience Functions
# ============================================================================

def execute_research(
    company_name: str,
    depth: ResearchDepth = ResearchDepth.STANDARD,
    config: Optional[ResearchConfig] = None
) -> WorkflowState:
    """
    Execute research for a company.

    Args:
        company_name: Company to research
        depth: Research depth level
        config: Optional custom configuration

    Returns:
        Workflow execution state with results
    """
    if config is None:
        if depth == ResearchDepth.QUICK:
            workflow = create_quick_research_workflow()
        elif depth == ResearchDepth.COMPREHENSIVE:
            workflow = create_comprehensive_research_workflow()
        else:
            workflow = create_research_workflow()
    else:
        workflow = create_research_workflow(config)

    print(f"\n{'='*60}")
    print(f"Starting {depth.value} research for: {company_name}")
    print(f"{'='*60}\n")

    result = workflow.execute(
        initial_data={"company_name": company_name}
    )

    print(f"\n{'='*60}")
    print(f"Research completed: {result.status.value}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Total cost: ${result.total_cost:.4f}")
    print(f"Nodes completed: {len(result.completed_nodes)}")
    print(f"{'='*60}\n")

    return result


# ============================================================================
# Workflow Templates for Specific Use Cases
# ============================================================================

def create_due_diligence_workflow() -> WorkflowEngine:
    """Create workflow for investment due diligence."""
    config = ResearchConfig(
        depth=ResearchDepth.COMPREHENSIVE,
        include_financial=True,
        include_market=True,
        include_competitive=True,
        include_news=True,
        include_brand=True,
        include_social=False,
        include_sales=False,
        include_investment=True,
        enable_quality_check=True,
        max_parallel=4
    )
    return create_research_workflow(config)


def create_sales_prospecting_workflow() -> WorkflowEngine:
    """Create workflow for sales prospecting."""
    config = ResearchConfig(
        depth=ResearchDepth.STANDARD,
        include_financial=True,
        include_market=True,
        include_competitive=True,
        include_news=True,
        include_brand=False,
        include_social=True,
        include_sales=True,
        include_investment=False,
        enable_quality_check=False,
        max_parallel=4
    )
    return create_research_workflow(config)


def create_competitive_intelligence_workflow() -> WorkflowEngine:
    """Create workflow focused on competitive intelligence."""
    config = ResearchConfig(
        depth=ResearchDepth.STANDARD,
        include_financial=True,
        include_market=True,
        include_competitive=True,
        include_news=True,
        include_brand=True,
        include_social=True,
        include_sales=False,
        include_investment=False,
        enable_quality_check=True,
        max_parallel=4
    )
    return create_research_workflow(config)
