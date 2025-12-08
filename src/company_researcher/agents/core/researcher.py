"""
Researcher Agent - Finds and gathers sources.

This agent is responsible for:
- Generating targeted search queries
- Executing web searches
- Collecting and ranking results
- Returning quality sources for analysis
"""

import json
from typing import Dict, Any, List

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, get_tavily_client, calculate_cost
from ...state import OverallState
from ...prompts import GENERATE_QUERIES_PROMPT


def researcher_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Researcher Agent Node: Find and gather quality sources.

    This agent combines query generation and search execution into
    a single specialized agent focused on finding the best sources.

    Args:
        state: Current workflow state

    Returns:
        State update with sources and agent metrics
    """
    print("\n" + "=" * 60)
    print("[AGENT: Researcher] Gathering sources...")
    print("=" * 60)

    config = get_config()
    client = get_anthropic_client()
    company_name = state["company_name"]

    # Step 1: Generate search queries
    print("[Researcher] Generating targeted queries...")

    # Check if we're iterating with missing info
    missing_info = state.get("missing_info", [])
    if missing_info:
        # Generate queries based on gaps
        num_queries = 3
        query_context = f"""
Previous research had gaps. Focus queries on:
{chr(10).join(f'- {info}' for info in missing_info[:3])}
"""
    else:
        num_queries = 5
        query_context = ""

    prompt = GENERATE_QUERIES_PROMPT.format(
        company_name=company_name,
        num_queries=num_queries
    )
    if query_context:
        prompt += f"\n\n{query_context}"

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=500,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text

    # Parse queries
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        queries = json.loads(content.strip())
    except json.JSONDecodeError:
        # Fallback
        queries = [
            f"{company_name} company overview",
            f"{company_name} revenue financial performance",
            f"{company_name} products services",
            f"{company_name} competitors market position",
            f"{company_name} recent news developments"
        ]

    query_cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print(f"[Researcher] Generated {len(queries)} queries")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Step 2: Execute searches
    print(f"\n[Researcher] Searching for sources...")

    tavily_client = get_tavily_client()
    all_results = []
    sources = []

    for query in queries:
        print(f"  [SEARCH] {query}")
        search_response = tavily_client.search(
            query=query,
            max_results=3
        )

        # Extract results and sources
        for result in search_response.get("results", []):
            all_results.append(result)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0.0)
            })

    # Calculate Tavily cost (approximate)
    search_cost = len(queries) * 0.001

    print(f"[Researcher] Found {len(all_results)} total results")

    # Calculate total cost
    total_cost = query_cost + search_cost

    # Track agent output
    agent_output = {
        "queries_generated": len(queries),
        "queries": queries,
        "sources_found": len(sources),
        "cost": total_cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    print(f"[Researcher] Agent complete - ${total_cost:.4f}")
    print("=" * 60)

    # Return only this agent's contribution
    # Reducers will handle merging/accumulation automatically
    return {
        "search_results": all_results,  # Full results with content for Analyst
        "sources": sources,  # Metadata for tracking
        "agent_outputs": {"researcher": agent_output},
        "total_cost": total_cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
