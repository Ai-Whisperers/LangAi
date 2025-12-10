"""
Quality checker for research output (cost-optimized).

This module evaluates the quality of research and identifies gaps.
Uses smart routing to select cheapest appropriate model for classification.
"""

import json
import logging
from typing import Dict, Any, List

from ..prompts import QUALITY_CHECK_PROMPT, format_sources_for_extraction

logger = logging.getLogger(__name__)


def check_research_quality(
    company_name: str,
    extracted_data: str,
    sources: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Check the quality of research output (cost-optimized).

    Uses smart_completion to route to cheapest model for classification tasks:
    - DeepSeek V3 ($0.14/1M) - primary choice
    - Falls back to GPT-4o-mini if needed

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
    # Import smart_completion for cost-optimized routing
    from ..llm.smart_client import smart_completion

    # Format sources
    formatted_sources = format_sources_for_extraction(sources)

    # Create quality check prompt
    prompt = QUALITY_CHECK_PROMPT.format(
        company_name=company_name,
        extracted_data=extracted_data,
        sources=formatted_sources
    )

    # Use smart_completion - routes to DeepSeek V3 for classification tasks
    result = smart_completion(
        prompt=prompt,
        task_type="classification",  # Routes to DeepSeek V3 ($0.14/1M)
        max_tokens=1500,
        temperature=0.0
    )

    content = result.content
    cost = result.cost

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
        quality_result = {
            "quality_score": float(quality_data.get("quality_score", 0)),
            "missing_information": quality_data.get("missing_information", []),
            "strengths": quality_data.get("strengths", []),
            "recommended_queries": quality_data.get("recommended_queries", []),
            "cost": cost,
            "tokens": {
                "input": result.input_tokens,
                "output": result.output_tokens
            }
        }

        logger.debug(f"Quality check complete - score: {quality_result['quality_score']}, model: {result.model}")
        return quality_result

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
                "input": result.input_tokens,
                "output": result.output_tokens
            }
        }
