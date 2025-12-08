"""
Conditional Routing for Research Workflows.

Provides intelligent workflow routing based on company type and
characteristics using LangGraph's conditional edges.

Features:
- Company type classification (public, private, startup)
- Dynamic agent selection based on available data
- Cost-optimized routing
- Quality-based iteration control

Usage:
    from company_researcher.orchestration import create_conditional_workflow

    workflow = create_conditional_workflow()
    result = workflow.invoke({"company_name": "Tesla"})
"""

from typing import Dict, Any, Literal, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None


class CompanyType(str, Enum):
    """Classification of company types."""
    PUBLIC = "public"
    PRIVATE = "private"
    STARTUP = "startup"
    UNKNOWN = "unknown"


class ResearchDepth(str, Enum):
    """Depth of research required."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


@dataclass
class RoutingDecision:
    """Decision made by the router."""
    company_type: CompanyType
    research_depth: ResearchDepth
    agents_to_run: List[str]
    skip_agents: List[str]
    use_enhanced_financial: bool
    use_batch_api: bool
    estimated_cost: float


# =============================================================================
# Classification Functions
# =============================================================================

def classify_company_type(
    company_name: str,
    search_results: List[Dict[str, Any]] = None
) -> CompanyType:
    """
    Classify company type based on available information.

    Args:
        company_name: Company name
        search_results: Optional search results for hints

    Returns:
        CompanyType classification
    """
    # Common public company indicators
    public_indicators = [
        "nasdaq", "nyse", "stock", "ticker", "sec filing",
        "quarterly earnings", "market cap", "publicly traded",
        "ipo", "shareholders", "10-k", "10-q"
    ]

    # Startup indicators
    startup_indicators = [
        "series a", "series b", "series c", "seed round",
        "venture capital", "vc", "startup", "founded 202",
        "pre-revenue", "early stage", "accelerator"
    ]

    # Combine text for analysis
    combined_text = company_name.lower()
    if search_results:
        for result in search_results[:10]:
            content = result.get("content", "") or result.get("snippet", "")
            title = result.get("title", "")
            combined_text += f" {content} {title}".lower()

    # Score indicators
    public_score = sum(1 for ind in public_indicators if ind in combined_text)
    startup_score = sum(1 for ind in startup_indicators if ind in combined_text)

    # Well-known public companies
    known_public = [
        "apple", "microsoft", "google", "amazon", "tesla", "meta",
        "nvidia", "netflix", "salesforce", "adobe", "oracle", "intel"
    ]
    if any(company in company_name.lower() for company in known_public):
        return CompanyType.PUBLIC

    # Classification logic
    if public_score >= 3:
        return CompanyType.PUBLIC
    elif startup_score >= 2:
        return CompanyType.STARTUP
    elif public_score >= 1:
        return CompanyType.PRIVATE  # Might be public, but not confident
    else:
        return CompanyType.UNKNOWN


def determine_research_depth(
    company_name: str,
    requested_depth: Optional[str] = None,
    source_count: int = 0
) -> ResearchDepth:
    """
    Determine appropriate research depth.

    Args:
        company_name: Company name
        requested_depth: User-requested depth
        source_count: Number of sources found

    Returns:
        ResearchDepth level
    """
    if requested_depth:
        depth_map = {
            "quick": ResearchDepth.QUICK,
            "standard": ResearchDepth.STANDARD,
            "deep": ResearchDepth.DEEP
        }
        return depth_map.get(requested_depth.lower(), ResearchDepth.STANDARD)

    # Auto-determine based on source availability
    if source_count < 5:
        return ResearchDepth.QUICK
    elif source_count < 15:
        return ResearchDepth.STANDARD
    else:
        return ResearchDepth.DEEP


def make_routing_decision(
    company_name: str,
    search_results: List[Dict[str, Any]] = None,
    config: Dict[str, Any] = None
) -> RoutingDecision:
    """
    Make comprehensive routing decision.

    Args:
        company_name: Company to research
        search_results: Available search results
        config: Optional configuration

    Returns:
        RoutingDecision with all routing parameters
    """
    config = config or {}
    search_results = search_results or []

    # Classify company
    company_type = classify_company_type(company_name, search_results)

    # Determine depth
    research_depth = determine_research_depth(
        company_name,
        config.get("research_depth"),
        len(search_results)
    )

    # Determine agents to run
    base_agents = ["researcher", "analyst"]

    if company_type == CompanyType.PUBLIC:
        agents_to_run = base_agents + ["enhanced_financial", "market", "product"]
        skip_agents = ["basic_financial"]
        use_enhanced_financial = True
    elif company_type == CompanyType.STARTUP:
        agents_to_run = base_agents + ["financial", "market", "product"]
        skip_agents = ["enhanced_financial"]  # No SEC data
        use_enhanced_financial = False
    else:
        agents_to_run = base_agents + ["financial", "market", "product"]
        skip_agents = []
        use_enhanced_financial = False

    # Add optional agents based on depth
    if research_depth == ResearchDepth.DEEP:
        agents_to_run.extend(["investment_analyst", "competitor_scout"])

    # Add synthesizer at end
    agents_to_run.append("synthesizer")

    # Batch API decision
    use_batch = config.get("use_batch_api", False)
    if not use_batch and len(search_results) > 20:
        use_batch = True  # Large research, use batch for cost savings

    # Estimate cost
    cost_per_agent = 0.02 if use_batch else 0.04
    estimated_cost = len(agents_to_run) * cost_per_agent

    return RoutingDecision(
        company_type=company_type,
        research_depth=research_depth,
        agents_to_run=agents_to_run,
        skip_agents=skip_agents,
        use_enhanced_financial=use_enhanced_financial,
        use_batch_api=use_batch,
        estimated_cost=estimated_cost
    )


# =============================================================================
# LangGraph Conditional Router
# =============================================================================

if LANGGRAPH_AVAILABLE:

    def create_company_type_router():
        """
        Create a router function for LangGraph.

        Returns:
            Router function for conditional edges
        """
        def router(state: Dict[str, Any]) -> str:
            """Route based on company type."""
            company_name = state.get("company_name", "")
            search_results = state.get("search_results", [])

            company_type = classify_company_type(company_name, search_results)

            if company_type == CompanyType.PUBLIC:
                return "public_flow"
            elif company_type == CompanyType.STARTUP:
                return "startup_flow"
            else:
                return "private_flow"

        return router

    def create_quality_checker():
        """
        Create a quality check router.

        Determines if research is complete or needs iteration.
        """
        def checker(state: Dict[str, Any]) -> str:
            """Check research quality and decide next step."""
            iterations = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 2)

            # Check if we have enough data
            agent_outputs = state.get("agent_outputs", {})
            missing_critical = []

            # Check for critical data
            financial = agent_outputs.get("financial", {})
            if not financial.get("analysis"):
                missing_critical.append("financial")

            market = agent_outputs.get("market", {})
            if not market.get("analysis"):
                missing_critical.append("market")

            # Quality score
            quality_score = state.get("quality_score", 0)

            # Decision logic
            if iterations >= max_iterations:
                return "finalize"  # Max iterations reached
            elif missing_critical and iterations < max_iterations:
                return "iterate"  # Need more data
            elif quality_score < 0.7 and iterations < max_iterations:
                return "iterate"  # Quality too low
            else:
                return "finalize"  # Good enough

        return checker

    def create_conditional_research_graph(config: Dict[str, Any] = None):
        """
        Create a research graph with conditional routing.

        Args:
            config: Optional configuration

        Returns:
            Compiled LangGraph workflow
        """
        from ..state import OverallState
        from ..agents.core.researcher import researcher_agent_node
        from ..agents.core.analyst import analyst_agent_node
        from ..agents.core.synthesizer import synthesizer_agent_node
        from ..agents.financial.financial import financial_agent_node
        from ..agents.financial.enhanced_financial import enhanced_financial_agent_node
        from ..agents.market.market import market_agent_node
        from ..agents.specialized.product import product_agent_node

        # Create graph
        workflow = StateGraph(OverallState)

        # Add nodes
        workflow.add_node("researcher", researcher_agent_node)
        workflow.add_node("analyst", analyst_agent_node)
        workflow.add_node("financial_basic", financial_agent_node)
        workflow.add_node("financial_enhanced", enhanced_financial_agent_node)
        workflow.add_node("market", market_agent_node)
        workflow.add_node("product", product_agent_node)
        workflow.add_node("synthesizer", synthesizer_agent_node)

        # Classification node
        def classify_node(state: OverallState) -> Dict[str, Any]:
            """Classify company and set routing."""
            company_name = state["company_name"]
            search_results = state.get("search_results", [])

            decision = make_routing_decision(company_name, search_results, config)

            return {
                "company_type": decision.company_type.value,
                "use_enhanced_financial": decision.use_enhanced_financial,
                "routing_decision": {
                    "agents": decision.agents_to_run,
                    "depth": decision.research_depth.value,
                    "estimated_cost": decision.estimated_cost
                }
            }

        workflow.add_node("classify", classify_node)

        # Define edges
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "classify")

        # Conditional routing based on classification
        def financial_router(state: OverallState) -> str:
            """Route to appropriate financial agent."""
            if state.get("use_enhanced_financial", False):
                return "financial_enhanced"
            return "financial_basic"

        workflow.add_conditional_edges(
            "classify",
            financial_router,
            {
                "financial_enhanced": "financial_enhanced",
                "financial_basic": "financial_basic"
            }
        )

        # Both financial paths continue to market
        workflow.add_edge("financial_basic", "market")
        workflow.add_edge("financial_enhanced", "market")

        # Continue to product and synthesizer
        workflow.add_edge("market", "product")
        workflow.add_edge("product", "synthesizer")
        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    def create_iterative_research_graph(max_iterations: int = 2):
        """
        Create a research graph with quality-based iteration.

        Args:
            max_iterations: Maximum research iterations

        Returns:
            Compiled LangGraph workflow with iteration support
        """
        from ..state import OverallState

        workflow = StateGraph(OverallState)

        # Import agent nodes
        from ..agents.core.researcher import researcher_agent_node
        from ..agents.core.synthesizer import synthesizer_agent_node
        from ..agents.quality.logic_critic import logic_critic_agent_node

        # Add nodes
        workflow.add_node("research", researcher_agent_node)
        workflow.add_node("synthesize", synthesizer_agent_node)
        workflow.add_node("quality_check", logic_critic_agent_node)

        # Counter node
        def increment_iteration(state: OverallState) -> Dict[str, Any]:
            return {"iteration_count": state.get("iteration_count", 0) + 1}

        workflow.add_node("increment", increment_iteration)

        # Define flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "synthesize")
        workflow.add_edge("synthesize", "quality_check")
        workflow.add_edge("quality_check", "increment")

        # Quality-based routing
        quality_checker = create_quality_checker()
        workflow.add_conditional_edges(
            "increment",
            quality_checker,
            {
                "iterate": "research",  # Loop back
                "finalize": END
            }
        )

        return workflow.compile()

else:
    # LangGraph not available - provide stub functions

    def create_conditional_research_graph(config=None):
        raise ImportError(
            "LangGraph is required for conditional routing. "
            "Install with: pip install langgraph"
        )

    def create_iterative_research_graph(max_iterations=2):
        raise ImportError(
            "LangGraph is required for iterative workflows. "
            "Install with: pip install langgraph"
        )

    def create_company_type_router():
        raise ImportError("LangGraph is required")

    def create_quality_checker():
        raise ImportError("LangGraph is required")


# =============================================================================
# Simple Router (No LangGraph Required)
# =============================================================================

class SimpleRouter:
    """
    Simple router without LangGraph dependency.

    Provides basic conditional routing logic that can be used
    with any workflow system.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def route_research(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Get routing decision for a company.

        Args:
            company_name: Company to research
            search_results: Optional search results

        Returns:
            RoutingDecision
        """
        return make_routing_decision(
            company_name,
            search_results,
            self.config
        )

    def get_agent_sequence(
        self,
        decision: RoutingDecision
    ) -> List[Callable]:
        """
        Get ordered list of agent functions to run.

        Args:
            decision: Routing decision

        Returns:
            List of agent functions
        """
        from ..agents.core.researcher import researcher_agent_node
        from ..agents.core.analyst import analyst_agent_node
        from ..agents.core.synthesizer import synthesizer_agent_node
        from ..agents.financial.financial import financial_agent_node
        from ..agents.financial.enhanced_financial import enhanced_financial_agent_node
        from ..agents.market.market import market_agent_node
        from ..agents.specialized.product import product_agent_node

        agent_map = {
            "researcher": researcher_agent_node,
            "analyst": analyst_agent_node,
            "financial": financial_agent_node,
            "enhanced_financial": enhanced_financial_agent_node,
            "market": market_agent_node,
            "product": product_agent_node,
            "synthesizer": synthesizer_agent_node
        }

        sequence = []
        for agent_name in decision.agents_to_run:
            if agent_name in agent_map and agent_name not in decision.skip_agents:
                sequence.append(agent_map[agent_name])

        return sequence

    def run_sequential(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run research with simple sequential routing.

        Args:
            company_name: Company to research
            search_results: Optional search results

        Returns:
            Research results
        """
        # Get routing decision
        decision = self.route_research(company_name, search_results)

        # Initialize state
        state = {
            "company_name": company_name,
            "search_results": search_results or [],
            "agent_outputs": {},
            "routing": decision.__dict__
        }

        # Run agents in sequence
        agents = self.get_agent_sequence(decision)

        for agent_fn in agents:
            result = agent_fn(state)
            # Merge result into state
            for key, value in result.items():
                if key == "agent_outputs":
                    state["agent_outputs"].update(value)
                else:
                    state[key] = value

        return state
