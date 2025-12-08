"""
Quality checker for research output.

This module evaluates the quality of research and identifies gaps.
"""

import json
import logging
from typing import Dict, Any, List

from ..config import get_config
from ..llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ..prompts import QUALITY_CHECK_PROMPT, format_sources_for_extraction

logger = logging.getLogger(__name__)


def check_research_quality(
    company_name: str,
    extracted_data: str,
    sources: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Check the quality of research output.

    Args:
        company_name: Name of the company
        extracted_data: Extracted and formatted research data
        sources: List of source dictionaries

    Returns:
        Dictionary with:
            - quality_score: Float 0-100
            - missing_information: List of missing items
            - strengths: List of research strengths
            - recommended_queries: List of search queries to fill gaps
    """
    config = get_config()
    client = get_anthropic_client()

    # Format sources
    formatted_sources = format_sources_for_extraction(sources)

    # Create quality check prompt
    prompt = QUALITY_CHECK_PROMPT.format(
        company_name=company_name,
        extracted_data=extracted_data,
        sources=formatted_sources
    )

    # Call Claude for quality assessment
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1500,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response safely
    content = safe_extract_text(response, agent_name="quality_checker")
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

    try:
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Find JSON object in content (handles extra text before/after)
        content = content.strip()

        # Try to find the JSON object boundaries
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx >= 0 and end_idx >= 0:
            json_str = content[start_idx:end_idx+1]
            quality_data = json.loads(json_str)
        else:
            quality_data = json.loads(content)

        # Validate structure
        result = {
            "quality_score": float(quality_data.get("quality_score", 0)),
            "missing_information": quality_data.get("missing_information", []),
            "strengths": quality_data.get("strengths", []),
            "recommended_queries": quality_data.get("recommended_queries", []),
            "cost": cost,
            "tokens": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }

        logger.debug(f"Quality check complete - score: {result['quality_score']}")
        return result

    except json.JSONDecodeError as e:
        # Fallback: return low quality score if parsing fails
        logger.warning(
            f"Failed to parse quality response as JSON: {type(e).__name__}. "
            "Returning default quality score."
        )
        return {
            "quality_score": 50.0,  # Default to medium-low quality
            "missing_information": ["Unable to parse quality assessment response"],
            "strengths": [],
            "recommended_queries": [],
            "cost": cost,
            "tokens": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }
