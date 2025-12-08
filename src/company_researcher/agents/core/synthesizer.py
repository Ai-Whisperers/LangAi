"""
Synthesizer Agent - Aggregates insights from all specialized agents.

This agent is responsible for:
- Combining outputs from Financial, Market, and Product agents
- Resolving conflicts between agents
- Generating comprehensive company overview
- Formatting structured data for final report
"""

from typing import Dict, Any

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost
from ...state import OverallState


SYNTHESIS_PROMPT = """You are a senior research analyst synthesizing insights from multiple specialized analysts.

Company: {company_name}

You have received analysis from three specialist teams:

## Financial Analysis
{financial_analysis}

## Market Analysis
{market_analysis}

## Product Analysis
{product_analysis}

Task: Create a comprehensive, well-structured research report by synthesizing these specialized analyses.

Generate the following sections:

## Company Overview
A 2-3 sentence summary combining insights from all analysts about what the company does and its significance.

## Key Metrics
Extract and list all financial metrics in bullet format:
- Revenue: [from financial analysis]
- Founded: [if mentioned]
- Market Share: [from market analysis]
- Employees: [if mentioned]
- Valuation/Market Cap: [from financial analysis]
- Any other relevant metrics

## Main Products/Services
List the company's products/services from the product analysis (bullet points)

## Competitors
List main competitors from market analysis

## Key Insights
List 3-4 most important insights combining perspectives from all three analyses:
- Financial health/performance
- Market position
- Product/technology strengths
- Strategic positioning

Requirements:
- Synthesize, don't just concatenate
- Resolve any contradictions intelligently
- Maintain factual accuracy
- Keep formatting clean and consistent
- If information is missing, note "Not available in research"

Generate the synthesized report now:"""


def synthesizer_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Synthesizer Agent Node: Aggregate all specialized agent outputs.

    This agent combines insights from Financial, Market, and Product
    specialists into a comprehensive, coherent research report.

    Args:
        state: Current workflow state

    Returns:
        State update with synthesized overview
    """
    print("\n" + "=" * 60)
    print("[AGENT: Synthesizer] Aggregating specialist insights...")
    print("=" * 60)

    config = get_config()
    client = get_anthropic_client()

    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})

    # Get outputs from each specialist
    financial = agent_outputs.get("financial", {}).get("analysis", "No financial analysis available")
    market = agent_outputs.get("market", {}).get("analysis", "No market analysis available")
    product = agent_outputs.get("product", {}).get("analysis", "No product analysis available")

    print("[Synthesizer] Combining insights from specialists...")
    print(f"  - Financial: {len(financial)} chars")
    print(f"  - Market: {len(market)} chars")
    print(f"  - Product: {len(product)} chars")

    # Create synthesis prompt
    prompt = SYNTHESIS_PROMPT.format(
        company_name=company_name,
        financial_analysis=financial,
        market_analysis=market,
        product_analysis=product
    )

    # Call Claude for synthesis
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1500,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    synthesized_overview = response.content[0].text
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[Synthesizer] Synthesis complete")
    print(f"[Synthesizer] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # Track agent output
    agent_output = {
        "synthesis": synthesized_overview,
        "specialists_combined": 3,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    # Return only this agent's contribution
    # Reducers will handle merging/accumulation automatically
    return {
        "company_overview": synthesized_overview,
        "notes": [synthesized_overview],  # For quality check
        "agent_outputs": {"synthesizer": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
