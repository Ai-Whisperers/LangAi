"""
Market Agent - Analyzes market position and competitive landscape.

This agent specializes in:
- Market share (domestic and global)
- Main competitors and positioning
- Competitive advantages
- Market trends
- Industry dynamics
- Competitive matrix generation

Refactored to use @agent_node decorator for reduced boilerplate.
"""

from typing import Any, Callable, Dict, List, Optional

from ...config import ResearchConfig
from ...state import OverallState
from ...utils import get_logger
from ..base import AgentResult, agent_node

logger = get_logger(__name__)

# Import competitive matrix with fallback
try:
    COMPETITIVE_MATRIX_AVAILABLE = True
except ImportError:
    COMPETITIVE_MATRIX_AVAILABLE = False
    logger.warning("Competitive matrix not available")


class MarketAgent:
    """Market analysis agent for competitive landscape."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client

    def analyze(
        self, company_name: str, search_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market position for a company.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return market_agent_node(state)


def create_market_agent(
    search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None
) -> MarketAgent:
    """Factory function to create a MarketAgent."""
    return MarketAgent(search_tool=search_tool, llm_client=llm_client)


MARKET_ANALYSIS_PROMPT = """You are a market analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL market position and competitive information from these search results.

Focus on:
1. **Market Share**: Domestic market share, global market share, market position
2. **Competitors**: Main competitors, their market shares, competitive dynamics
3. **Positioning**: How the company positions itself, unique value proposition
4. **Market Trends**: Industry trends, market growth, shifts in competition
5. **Competitive Advantages**: What makes the company different or better

Requirements:
- Be specific with percentages and rankings
- Name specific competitors with their market shares if available
- Include market context (growing/declining, etc.)
- Format as bullet points

Output format:
## Market Position
- Market Share: [domestic %, global %, ranking]
- Market Size: [total addressable market if available]
- Position: [leader/challenger/follower/niche player]

## Competitive Landscape
- Main Competitors: [list top 3-5 competitors]
  - [Competitor 1]: [market share %, strengths]
  - [Competitor 2]: [market share %, strengths]
  - [Competitor 3]: [market share %, strengths]
- Competitive Intensity: [high/medium/low]
- Barriers to Entry: [key barriers]

## Strategic Positioning
- Value Proposition: [how company positions itself]
- Target Segments: [key customer segments]
- Differentiation: [what makes them unique]

## Market Trends
- Growth Rate: [market growth rate %]
- Key Trends: [list 3-5 trends]
- Disruption Risks: [emerging threats]

## Competitive Advantages
- Core Strengths: [list main advantages]
- Weaknesses: [areas where competitors may be stronger]

Extract the market data now:"""


COMPETITIVE_MATRIX_PROMPT = """Based on the market analysis above, create a competitive comparison matrix.

For each competitor identified, estimate scores (1-10) for:
- Market Share: Current market position
- Product Range: Breadth of offerings
- Technology: Technical capabilities
- Brand Strength: Brand recognition and trust
- Geographic Reach: International presence
- Innovation: R&D and new product development

Format as:
| Competitor | Market Share | Product Range | Technology | Brand | Reach | Innovation |
|------------|--------------|---------------|------------|-------|-------|------------|
| [Company]  | [1-10]       | [1-10]        | [1-10]     | [1-10]| [1-10]| [1-10]     |
"""


@agent_node(
    agent_name="market",
    max_tokens=1000,
    temperature=0.0,
    max_sources=15,
    content_truncate_length=500,
)
def market_agent_node(
    state: OverallState,
    logger,
    client,
    config: ResearchConfig,
    node_config,
    formatted_results: str,
    company_name: str,
) -> AgentResult:
    """
    Market Agent Node: Analyze market position and competition.

    This specialized agent focuses solely on market dynamics,
    providing deeper analysis of competitors and positioning.

    Uses @agent_node decorator which handles:
    - Logging (start/end with cost)
    - Search result validation
    - Search result formatting
    - Cost calculation and token tracking
    - Error handling

    Args:
        state: Current workflow state
        logger: Agent logger instance
        client: Anthropic client
        config: Application config
        node_config: Node-specific config
        formatted_results: Pre-formatted search results
        company_name: Company being analyzed

    Returns:
        LLM response (decorator wraps into AgentResult)
    """
    # Create prompt with pre-formatted results
    prompt = MARKET_ANALYSIS_PROMPT.format(
        company_name=company_name, search_results=formatted_results
    )

    # Call Claude for market analysis
    # Return the response - decorator handles cost calculation and result wrapping
    return client.messages.create(
        model=config.llm_model,
        max_tokens=node_config.max_tokens,
        temperature=node_config.temperature,
        messages=[{"role": "user", "content": prompt}],
    )
