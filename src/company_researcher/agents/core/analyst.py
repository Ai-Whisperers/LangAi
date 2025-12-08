"""
Analyst Agent - Extracts structured insights from sources.

This agent is responsible for:
- Analyzing search results from Researcher
- Extracting structured data (overview, metrics, products, competitors)
- Generating comprehensive notes
- Formatting insights for report generation
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ...state import OverallState
from ...prompts import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    format_search_results_for_analysis,
    format_sources_for_extraction
)


class AnalystAgent:
    """Analyst agent for extracting structured insights from sources."""

    def __init__(
        self,
        llm_client: Optional[Any] = None
    ):
        self.llm_client = llm_client or get_anthropic_client()

    def analyze(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]] = None,
        sources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze search results and extract structured insights.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        state = {
            "company_name": company_name,
            "search_results": search_results or [],
            "sources": sources or []
        }
        return analyst_agent_node(state)


def create_analyst_agent(llm_client: Any = None) -> AnalystAgent:
    """Factory function to create an AnalystAgent."""
    return AnalystAgent(llm_client=llm_client)


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
    logger.info("Analyst agent starting - analyzing sources")

    config = get_config()
    client = get_anthropic_client()

    company_name = state["company_name"]
    search_results = state.get("search_results", [])  # Full results with content
    sources = state.get("sources", [])  # Metadata for tracking

    if not search_results:
        logger.warning("No search results to analyze")
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

    logger.info(f"Analyzing {len(search_results)} search results")

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

    notes = safe_extract_text(analysis_response, agent_name="analyst")
    analysis_cost = calculate_cost(
        analysis_response.usage.input_tokens,
        analysis_response.usage.output_tokens
    )

    logger.debug("Analysis complete")

    # Step 2: Extract structured data from notes
    logger.debug("Extracting structured data")

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

    extracted_data = safe_extract_text(extraction_response, agent_name="analyst")
    extraction_cost = calculate_cost(
        extraction_response.usage.input_tokens,
        extraction_response.usage.output_tokens
    )

    logger.debug("Data extraction complete")

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

    logger.info(f"Analyst agent complete - cost: ${total_cost:.4f}")

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
