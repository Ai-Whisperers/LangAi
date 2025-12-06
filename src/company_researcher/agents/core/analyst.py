"""
Analyst Agent - Extracts structured insights from sources.

This agent is responsible for:
- Analyzing search results from Researcher
- Extracting structured data (overview, metrics, products, competitors)
- Generating comprehensive notes
- Formatting insights for report generation
"""

from typing import Dict, Any
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState
from ..prompts import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    format_search_results_for_analysis,
    format_sources_for_extraction
)


def analyst_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Analyst Agent Node: Extract structured insights from sources.

    This agent receives sources from the Researcher agent and
    performs deep analysis to extract all required information.

    Args:
        state: Current workflow state

    Returns:
        State update with analysis, extracted data, and agent metrics
    """
    print("\n" + "=" * 60)
    print("[AGENT: Analyst] Analyzing sources...")
    print("=" * 60)

    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    company_name = state["company_name"]
    search_results = state.get("search_results", [])  # Full results with content
    sources = state.get("sources", [])  # Metadata for tracking

    if not search_results:
        print("[Analyst] WARNING: No search results to analyze!")
        return {
            "notes": ["No search results available for analysis."],
            "company_overview": "Not available in research",
            "agent_outputs": {
                "analyst": {
                    "sources_analyzed": 0,
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[Analyst] Analyzing {len(search_results)} search results...")

    # Step 1: Analyze search results to create notes (using full content)
    formatted_results = format_search_results_for_analysis(search_results)

    analysis_prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    analysis_response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    notes = analysis_response.content[0].text
    analysis_cost = config.calculate_llm_cost(
        analysis_response.usage.input_tokens,
        analysis_response.usage.output_tokens
    )

    print("[Analyst] Analysis complete")

    # Step 2: Extract structured data from notes
    print("[Analyst] Extracting structured data...")

    # Combine with previous notes if iterating
    previous_notes = state.get("notes", [])
    all_notes = previous_notes + [notes]
    combined_notes = "\n\n---\n\n".join(all_notes)

    formatted_sources = format_sources_for_extraction(sources)

    extraction_prompt = EXTRACT_DATA_PROMPT.format(
        company_name=company_name,
        notes=combined_notes,
        sources=formatted_sources
    )

    extraction_response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    extracted_data = extraction_response.content[0].text
    extraction_cost = config.calculate_llm_cost(
        extraction_response.usage.input_tokens,
        extraction_response.usage.output_tokens
    )

    print("[Analyst] Data extraction complete")

    # Calculate total cost
    total_cost = analysis_cost + extraction_cost

    # Track agent output
    agent_output = {
        "sources_analyzed": len(sources),
        "notes_length": len(notes),
        "data_extracted": True,
        "cost": total_cost,
        "tokens": {
            "input": analysis_response.usage.input_tokens + extraction_response.usage.input_tokens,
            "output": analysis_response.usage.output_tokens + extraction_response.usage.output_tokens
        }
    }

    print(f"[Analyst] Agent complete - ${total_cost:.4f}")
    print("=" * 60)

    # Return only this agent's contribution
    # Reducers will handle merging/accumulation automatically
    return {
        "notes": [notes],
        "company_overview": extracted_data,
        "agent_outputs": {"analyst": agent_output},
        "total_cost": total_cost,
        "total_tokens": {
            "input": agent_output["tokens"]["input"],
            "output": agent_output["tokens"]["output"]
        }
    }
