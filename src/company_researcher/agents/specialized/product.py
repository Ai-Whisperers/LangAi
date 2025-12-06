"""
Product Agent - Analyzes products, services, and technology.

This agent specializes in:
- Product lineup and offerings
- Key features and capabilities
- Technology stack and innovations
- Recent product launches
- Product strategy and roadmap
"""

from typing import Dict, Any
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState


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


def product_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Product Agent Node: Analyze products and technology.

    This specialized agent focuses solely on products and technology,
    providing deeper analysis of offerings and capabilities.

    Args:
        state: Current workflow state

    Returns:
        State update with product analysis
    """
    print("\n" + "=" * 60)
    print("[AGENT: Product] Analyzing products and technology...")
    print("=" * 60)

    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Product] WARNING: No search results to analyze!")
        return {
            "agent_outputs": {
                "product": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[Product] Analyzing {len(search_results)} sources for product data...")

    # Format search results for analysis
    formatted_results = "\n\n".join([
        f"Source {i+1}: {result.get('title', 'N/A')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"Content: {result.get('content', 'N/A')[:500]}..."
        for i, result in enumerate(search_results[:15])
    ])

    # Create product analysis prompt
    prompt = PRODUCT_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude for product analysis
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    product_analysis = response.content[0].text
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[Product] Analysis complete")
    print(f"[Product] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # Track agent output
    agent_output = {
        "analysis": product_analysis,
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
        "agent_outputs": {"product": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
