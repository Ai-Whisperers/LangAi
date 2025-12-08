"""
Market Agent - Analyzes market position and competitive landscape.

This agent specializes in:
- Market share (domestic and global)
- Main competitors and positioning
- Competitive advantages
- Market trends
- Industry dynamics
"""

from typing import Dict, Any, Optional, Callable

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost
from ...state import OverallState


class MarketAgent:
    """Market analysis agent for competitive landscape."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(self, company_name: str, search_results: list = None) -> Dict[str, Any]:
        """Analyze market position for a company."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return market_agent_node(state)


def create_market_agent(search_tool: Callable = None, llm_client: Any = None) -> MarketAgent:
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
- Name specific competitors
- Include market context (growing/declining, etc.)
- Format as bullet points

Output format:
- Market Share: [domestic %, global %, ranking]
- Main Competitors: [list competitors with their positions]
- Positioning: [how company positions itself]
- Market Trends: [key trends affecting the company]
- Competitive Advantages: [unique strengths]

Extract the market data now:"""


def market_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Market Agent Node: Analyze market position and competition.

    This specialized agent focuses solely on market dynamics,
    providing deeper analysis of competitors and positioning.

    Args:
        state: Current workflow state

    Returns:
        State update with market analysis
    """
    print("\n" + "=" * 60)
    print("[AGENT: Market] Analyzing market position...")
    print("=" * 60)

    config = get_config()
    client = get_anthropic_client()

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Market] WARNING: No search results to analyze!")
        return {
            "agent_outputs": {
                "market": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[Market] Analyzing {len(search_results)} sources for market data...")

    # Format search results for analysis
    formatted_results = "\n\n".join([
        f"Source {i+1}: {result.get('title', 'N/A')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"Content: {result.get('content', 'N/A')[:500]}..."
        for i, result in enumerate(search_results[:15])
    ])

    # Create market analysis prompt
    prompt = MARKET_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude for market analysis
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    market_analysis = response.content[0].text
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[Market] Analysis complete")
    print(f"[Market] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # Track agent output
    agent_output = {
        "analysis": market_analysis,
        "data_extracted": True,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    # Return only this agent's contribution
    # Reducers will handle merging/accumulation automatically
    return {
        "agent_outputs": {"market": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
