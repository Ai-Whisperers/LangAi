"""
Analysis Nodes for Research Workflow

This module contains nodes responsible for data analysis:
- analyze_node: Analyze search results with Claude
- extract_data_node: Extract structured data from notes
- check_quality_node: Assess research quality
- should_continue_research: Decision function for iteration
"""

from typing import Dict, Any

from anthropic import Anthropic

from ...state import OverallState
from ...config import get_config
from ...llm.client_factory import safe_extract_text
from ...prompts import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    format_search_results_for_analysis,
    format_sources_for_extraction,
)
from ...quality import check_research_quality


def analyze_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 3: Analyze search results with Claude.

    Args:
        state: Current workflow state

    Returns:
        State update with analysis notes
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    print("\n[NODE] Analyzing search results...")

    # Format search results for prompt
    formatted_results = format_search_results_for_analysis(state["search_results"])

    # Create prompt
    prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=state["company_name"],
        search_results=formatted_results
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    notes = safe_extract_text(response, agent_name="analyze")

    # Update cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[OK] Analysis complete")

    return {
        "notes": [notes],
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + response.usage.input_tokens,
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + response.usage.output_tokens
        }
    }


def extract_data_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 4: Extract structured data from notes.

    Args:
        state: Current workflow state

    Returns:
        State update with extracted structured data
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    print("\n[NODE] Extracting structured data...")

    # Combine all notes
    combined_notes = "\n\n".join(state["notes"])

    # Format sources
    formatted_sources = format_sources_for_extraction(state["sources"])

    # Create prompt
    prompt = EXTRACT_DATA_PROMPT.format(
        company_name=state["company_name"],
        notes=combined_notes,
        sources=formatted_sources
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    extracted_text = safe_extract_text(response, agent_name="extract_data")

    # Update cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[OK] Data extraction complete")

    # Store extracted text as-is (it's already formatted markdown)
    return {
        "company_overview": extracted_text,
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + response.usage.input_tokens,
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + response.usage.output_tokens
        }
    }


def check_quality_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 5: Check research quality.

    Args:
        state: Current workflow state

    Returns:
        State update with quality assessment
    """
    print("\n[NODE] Checking research quality...")

    # Check quality
    quality_result = check_research_quality(
        company_name=state["company_name"],
        extracted_data=state.get("company_overview", ""),
        sources=state.get("sources", [])
    )

    quality_score = quality_result["quality_score"]
    print(f"[QUALITY] Score: {quality_score:.1f}/100")

    if quality_score < 85:
        print("[QUALITY] Below threshold (85). Missing information:")
        for item in quality_result["missing_information"][:3]:
            print(f"  - {item}")

    return {
        "quality_score": quality_score,
        "missing_info": quality_result["missing_information"],
        "iteration_count": state.get("iteration_count", 0) + 1,
        "total_cost": state.get("total_cost", 0.0) + quality_result["cost"],
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + quality_result["tokens"]["input"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + quality_result["tokens"]["output"]
        }
    }


def should_continue_research(state: OverallState) -> str:
    """
    Decision function: Should we iterate or finish?

    Args:
        state: Current workflow state

    Returns:
        "iterate" to continue research, "finish" to complete
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 2  # Maximum 2 iterations

    # Finish if quality is good enough OR max iterations reached
    if quality_score >= 85:
        print(f"[DECISION] Quality sufficient ({quality_score:.1f} >= 85). Proceeding to report.")
        return "finish"
    elif iteration_count >= max_iterations:
        print(f"[DECISION] Max iterations reached ({iteration_count}/{max_iterations}). Proceeding to report.")
        return "finish"
    else:
        print(f"[DECISION] Quality low ({quality_score:.1f} < 85), iteration {iteration_count}/{max_iterations}. Re-searching.")
        return "iterate"
