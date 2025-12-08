"""
Financial Agent - Extracts financial metrics and data.

This agent specializes in:
- Revenue figures (annual, quarterly)
- Funding rounds and total raised
- Valuation or market capitalization
- Profitability metrics
- Financial trends and growth

Refactored to use @agent_node decorator for reduced boilerplate.
"""

from typing import Any, Callable, Dict, List, Optional

from ..base import agent_node, AgentResult
from ...config import ResearchConfig
from ...state import OverallState


class FinancialAgent:
    """Financial analysis agent for extracting financial metrics."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client

    def analyze(self, company_name: str, search_results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze financial data for a company.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return financial_agent_node(state)


def create_financial_agent(search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None) -> FinancialAgent:
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


@agent_node(
    agent_name="financial",
    max_tokens=1000,
    temperature=0.0,
    max_sources=15,
    content_truncate_length=500
)
def financial_agent_node(
    state: OverallState,
    logger,
    client,
    config: ResearchConfig,
    node_config,
    formatted_results: str,
    company_name: str
) -> AgentResult:
    """
    Financial Agent Node: Extract financial metrics and data.

    This specialized agent focuses solely on financial information,
    providing deeper analysis of revenue, funding, and metrics.

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
    prompt = FINANCIAL_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude for financial analysis
    # Return the response - decorator handles cost calculation and result wrapping
    return client.messages.create(
        model=config.llm_model,
        max_tokens=node_config.max_tokens,
        temperature=node_config.temperature,
        messages=[{"role": "user", "content": prompt}]
    )
