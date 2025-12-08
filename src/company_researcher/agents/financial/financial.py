"""
Financial Agent - Extracts financial metrics and data.

This agent specializes in:
- Revenue figures (annual, quarterly)
- Funding rounds and total raised
- Valuation or market capitalization
- Profitability metrics
- Financial trends and growth
"""

from typing import Dict, Any, Optional, Callable

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost
from ...state import OverallState


class FinancialAgent:
    """Financial analysis agent for extracting financial metrics."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(self, company_name: str, search_results: list = None) -> Dict[str, Any]:
        """Analyze financial data for a company."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return financial_agent_node(state)


def create_financial_agent(search_tool: Callable = None, llm_client: Any = None) -> FinancialAgent:
    """Factory function to create a FinancialAgent."""
    return FinancialAgent(search_tool=search_tool, llm_client=llm_client)


FINANCIAL_ANALYSIS_PROMPT = """You are a financial analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL financial data and metrics from these search results.

Focus on:
1. **Revenue**: Annual revenue, quarterly revenue, revenue growth
2. **Funding**: Total funding raised, valuation, recent rounds
3. **Profitability**: Operating income, net income, profit margins
4. **Market Value**: Market cap (if public), valuation (if private)
5. **Financial Metrics**: R&D spending, cash flow, any other metrics

Requirements:
- Be specific with numbers and dates
- Include sources for each data point
- Note if data is missing or unavailable
- Format as bullet points

Output format:
- Revenue: [specific figures with years]
- Funding: [total raised, rounds, investors if mentioned]
- Valuation/Market Cap: [amount and date]
- Profitability: [operating income, net income, etc.]
- Other Metrics: [any additional financial data]

Extract the financial data now:"""


def financial_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Financial Agent Node: Extract financial metrics and data.

    This specialized agent focuses solely on financial information,
    providing deeper analysis of revenue, funding, and metrics.

    Args:
        state: Current workflow state

    Returns:
        State update with financial analysis
    """
    print("\n" + "=" * 60)
    print("[AGENT: Financial] Analyzing financial data...")
    print("=" * 60)

    config = get_config()
    client = get_anthropic_client()

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Financial] WARNING: No search results to analyze!")
        return {
            "agent_outputs": {
                "financial": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[Financial] Analyzing {len(search_results)} sources for financial data...")

    # Format search results for analysis
    formatted_results = "\n\n".join([
        f"Source {i+1}: {result.get('title', 'N/A')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"Content: {result.get('content', 'N/A')[:500]}..."
        for i, result in enumerate(search_results[:15])
    ])

    # Create financial analysis prompt
    prompt = FINANCIAL_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude for financial analysis
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    financial_analysis = response.content[0].text
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[Financial] Analysis complete")
    print(f"[Financial] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # Track agent output
    agent_output = {
        "analysis": financial_analysis,
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
        "agent_outputs": {"financial": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
