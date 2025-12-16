"""
Analysis Nodes for Research Workflow

This module contains nodes responsible for data analysis:
- analyze_node: Analyze search results with Claude
- extract_data_node: Extract structured data from notes
- check_quality_node: Assess research quality
- should_continue_research: Decision function for iteration

Uses SmartLLMClient for automatic provider fallback:
- Primary: Anthropic Claude
- Fallback 1: Groq (llama-3.3-70b-versatile) on rate limit
- Fallback 2: DeepSeek on rate limit
"""

from typing import Any, Dict, Optional

from ...config import get_config
from ...llm.smart_client import TaskType, get_smart_client
from ...prompts import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    format_search_results_for_analysis,
    format_sources_for_extraction,
)
from ...quality import check_research_quality
from ...state import OverallState
from ...utils import get_logger

logger = get_logger(__name__)


def _create_completion(
    prompt: str, system: Optional[str] = None, max_tokens: int = 2000, temperature: float = 0.1
):
    """Create a completion using SmartLLMClient with automatic provider fallback."""
    smart_client = get_smart_client()

    # Combine system and user prompt if system is provided
    full_prompt = prompt
    if system:
        full_prompt = f"{system}\n\n{prompt}"

    result = smart_client.complete(
        prompt=full_prompt,
        task_type=TaskType.REASONING,
        complexity="medium",
        max_tokens=max_tokens,
        temperature=temperature,
    )

    logger.info(f"[LLM] Provider: {result.provider}/{result.model} ({result.routing_reason})")

    return {
        "content": result.content,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "provider": result.provider,
        "cost": result.cost,
    }


def analyze_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 3: Analyze search results with LLM.

    Args:
        state: Current workflow state

    Returns:
        State update with analysis notes
    """
    config = get_config()

    print("\n[NODE] Analyzing search results...")

    # Format search results for prompt
    formatted_results = format_search_results_for_analysis(state["search_results"])

    # Create prompt
    prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=state["company_name"], search_results=formatted_results
    )

    # Call LLM (Groq first, Anthropic fallback)
    result = _create_completion(
        prompt=prompt, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature
    )

    notes = result["content"]
    cost = result["cost"]

    print(f"[OK] Analysis complete (via {result['provider']})")

    return {
        "notes": [notes],
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"]
            + result["input_tokens"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"]
            + result["output_tokens"],
        },
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

    print("\n[NODE] Extracting structured data...")

    # Combine all notes
    combined_notes = "\n\n".join(state["notes"])

    # Format sources
    formatted_sources = format_sources_for_extraction(state["sources"])

    # Create prompt
    prompt = EXTRACT_DATA_PROMPT.format(
        company_name=state["company_name"], notes=combined_notes, sources=formatted_sources
    )

    # Call LLM (Groq first, Anthropic fallback)
    result = _create_completion(
        prompt=prompt, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature
    )

    extracted_text = result["content"]
    cost = result["cost"]

    print(f"[OK] Data extraction complete (via {result['provider']})")

    # Store extracted text as-is (it's already formatted markdown)
    return {
        "company_overview": extracted_text,
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"]
            + result["input_tokens"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"]
            + result["output_tokens"],
        },
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
        sources=state.get("sources", []),
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
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"]
            + quality_result["tokens"]["input"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"]
            + quality_result["tokens"]["output"],
        },
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
        print(
            f"[DECISION] Max iterations reached ({iteration_count}/{max_iterations}). Proceeding to report."
        )
        return "finish"
    else:
        print(
            f"[DECISION] Quality low ({quality_score:.1f} < 85), iteration {iteration_count}/{max_iterations}. Re-searching."
        )
        return "iterate"
