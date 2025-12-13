"""
Analyst Agent - Extracts structured insights from sources.

This agent is responsible for:
- Analyzing search results from Researcher
- Extracting structured data (overview, metrics, products, competitors)
- Generating comprehensive notes
- Formatting insights for report generation
- VALIDATING data quality before report generation
"""

from typing import Any, Dict, List, Optional
from ...utils import get_logger

logger = get_logger(__name__)

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ...state import OverallState
from ...prompts import (
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    format_search_results_for_analysis,
    format_sources_for_extraction
)

# Import quality validation modules
try:
    from ..research.metrics_validator import (
        create_metrics_validator,
    )
    from ..research.quality_enforcer import (
        create_quality_enforcer,
    )
    QUALITY_MODULES_AVAILABLE = True
except ImportError:
    QUALITY_MODULES_AVAILABLE = False
    logger.warning("Quality validation modules not available")


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
    NOW INCLUDES QUALITY VALIDATION.

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
            "data_quality": {
                "score": 0,
                "passes_threshold": False,
                "issues": ["No search results provided"]
            },
            "agent_outputs": {
                "analyst": {
                    "sources_analyzed": 0,
                    "data_extracted": False,
                    "quality_score": 0,
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

    # Step 3: QUALITY VALIDATION (NEW)
    quality_result = None
    quality_score = 0
    quality_warnings = []
    can_generate_report = True
    retry_recommended = False
    recommended_queries = []

    if QUALITY_MODULES_AVAILABLE:
        logger.info("Running quality validation on extracted data")

        # Initialize validators
        metrics_validator = create_metrics_validator(
            min_score=30.0,
            critical_threshold=0.4
        )
        quality_enforcer = create_quality_enforcer(
            min_score=30.0,
            block_on_empty=True,
            strict=False
        )

        # Validate metrics in extracted data
        validation_result = metrics_validator.validate_metrics(
            content=extracted_data,
            company_name=company_name
        )

        quality_score = validation_result.score
        quality_warnings = validation_result.warnings
        retry_recommended = validation_result.retry_recommended
        recommended_queries = validation_result.recommended_queries

        # Check quality gate for report generation
        quality_gate = quality_enforcer.check_quality(
            report_content=extracted_data,
            company_name=company_name,
            validation_score=validation_result.score
        )

        can_generate_report = quality_gate.can_generate

        quality_result = {
            "score": quality_score,
            "passes_threshold": validation_result.is_valid,
            "can_generate_report": can_generate_report,
            "metrics_found": list(validation_result.metrics_found.keys()),
            "metrics_missing": validation_result.metrics_missing,
            "critical_missing": validation_result.critical_missing,
            "warnings": quality_warnings,
            "retry_recommended": retry_recommended,
            "recommended_queries": recommended_queries,
            "company_type": validation_result.company_type.value,
            "quality_gate_status": quality_gate.status.value,
        }

        logger.info(
            f"Quality validation: score={quality_score:.1f}, "
            f"can_generate={can_generate_report}, "
            f"metrics_found={len(validation_result.metrics_found)}, "
            f"missing={len(validation_result.metrics_missing)}"
        )

        # Add quality warnings to notes if significant issues
        if quality_warnings:
            quality_note = "\n\n**Data Quality Warnings:**\n" + "\n".join(f"- {w}" for w in quality_warnings[:3])
            notes += quality_note

    else:
        # Basic quality check without modules
        quality_result = {
            "score": 50.0,  # Default score
            "passes_threshold": True,
            "can_generate_report": True,
            "warnings": [],
            "note": "Quality modules not available - using defaults"
        }

    # Calculate total cost
    total_cost = analysis_cost + extraction_cost

    # Track agent output with quality metrics
    agent_output = {
        "sources_analyzed": len(sources),
        "notes_length": len(notes),
        "data_extracted": True,
        "quality_score": quality_score,
        "can_generate_report": can_generate_report,
        "retry_recommended": retry_recommended,
        "cost": total_cost,
        "tokens": {
            "input": analysis_response.usage.input_tokens + extraction_response.usage.input_tokens,
            "output": analysis_response.usage.output_tokens + extraction_response.usage.output_tokens
        }
    }

    logger.info(f"Analyst agent complete - cost: ${total_cost:.4f}, quality: {quality_score:.1f}")

    # Return with quality data
    return {
        "notes": [notes],
        "company_overview": extracted_data,
        "data_quality": quality_result,
        "agent_outputs": {"analyst": agent_output},
        "total_cost": total_cost,
        "total_tokens": {
            "input": agent_output["tokens"]["input"],
            "output": agent_output["tokens"]["output"]
        }
    }
