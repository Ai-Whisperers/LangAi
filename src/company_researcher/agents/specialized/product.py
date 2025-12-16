"""
Product Agent - Analyzes products, services, and technology.

This agent specializes in:
- Product lineup and offerings
- Key features and capabilities
- Technology stack and innovations
- Recent product launches
- Product strategy and roadmap

Refactored to use @agent_node decorator for reduced boilerplate.
"""

from typing import Any, Callable, Dict, List, Optional

from ...config import ResearchConfig
from ...state import OverallState
from ..base import AgentResult, agent_node


class ProductAgent:
    """Product analysis agent for product/service analysis."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client

    def analyze(
        self, company_name: str, search_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze products and services for a company.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return product_agent_node(state)


def create_product_agent(
    search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None
) -> ProductAgent:
    """Factory function to create a ProductAgent."""
    return ProductAgent(search_tool=search_tool, llm_client=llm_client)


PRODUCT_ANALYSIS_PROMPT = """You are a product analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL product, service, and technology information from these search results.

Focus on:
1. **Products/Services**: Complete list of main products or services offered
2. **Key Features**: Important features, capabilities, or differentiators
3. **Technology**: Technology stack, innovations, patents, R&D focus
4. **Recent Launches**: New products, updates, or announcements
5. **Strategy**: Product strategy, target markets, future direction

Requirements:
- List all products/services specifically
- Describe key features and capabilities
- Include technology details when available
- Note recent developments
- Format as bullet points

Output format:
- Main Products/Services: [complete list with descriptions]
- Key Features: [notable features or capabilities]
- Technology: [tech stack, innovations, R&D]
- Recent Launches: [new products or updates]
- Product Strategy: [target markets, direction]

Extract the product data now:"""


@agent_node(
    agent_name="product",
    max_tokens=1000,
    temperature=0.0,
    max_sources=15,
    content_truncate_length=500,
)
def product_agent_node(
    state: OverallState,
    logger,
    client,
    config: ResearchConfig,
    node_config,
    formatted_results: str,
    company_name: str,
) -> AgentResult:
    """
    Product Agent Node: Analyze products and technology.

    This specialized agent focuses solely on products and technology,
    providing deeper analysis of offerings and capabilities.

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
    prompt = PRODUCT_ANALYSIS_PROMPT.format(
        company_name=company_name, search_results=formatted_results
    )

    # Call Claude for product analysis
    # Return the response - decorator handles cost calculation and result wrapping
    return client.messages.create(
        model=config.llm_model,
        max_tokens=node_config.max_tokens,
        temperature=node_config.temperature,
        messages=[{"role": "user", "content": prompt}],
    )
