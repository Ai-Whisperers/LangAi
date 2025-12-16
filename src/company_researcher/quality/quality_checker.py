"""
Quality checker for research output (cost-optimized).

This module evaluates the quality of research and identifies gaps.
Uses smart routing to select cheapest appropriate model for classification.
"""

import json
import re
from typing import Any, Dict, List, Set

from ..prompts import QUALITY_CHECK_PROMPT, format_sources_for_extraction
from ..utils import get_logger

logger = get_logger(__name__)

# Required fields for comprehensive research (field name -> patterns to search for)
REQUIRED_FIELDS = {
    # Core company info
    "company_name": ["company name", "legal name", "trading as"],
    "headquarters": ["headquarters", "headquarter", "based in", "located in"],
    "founded": ["founded", "established", "incorporated"],
    "industry": ["industry", "sector", "business segment"],
    "employees": ["employees", "workforce", "staff count", "headcount"],
    # Leadership
    "ceo": ["ceo", "chief executive", "managing director", "general manager"],
    "leadership_team": ["leadership", "management team", "board", "executives"],
    # Financial metrics
    "revenue": ["revenue", "sales", "turnover", "annual revenue"],
    "profit_margin": ["profit margin", "net margin", "operating margin"],
    "market_cap": ["market cap", "market capitalization", "valuation"],
    # Market position
    "market_share": ["market share", "share of market", "% of market"],
    "subscribers": ["subscribers", "customers", "users", "client base"],
    "competitors": ["competitor", "rival", "competing", "market player"],
    # Operational
    "products_services": ["product", "service", "offering", "solution"],
    "geographic_presence": ["geographic", "countries", "regions", "operations in"],
}


def check_field_completeness(extracted_data: str) -> Dict[str, Any]:
    """
    Check which required fields are present/missing in extracted data.

    Args:
        extracted_data: The extracted research content

    Returns:
        Dictionary with field_scores, missing_fields, present_fields
    """
    data_lower = extracted_data.lower()
    present_fields: Set[str] = set()
    missing_fields: Set[str] = set()

    for field_name, patterns in REQUIRED_FIELDS.items():
        field_found = False
        for pattern in patterns:
            if pattern.lower() in data_lower:
                field_found = True
                break

        if field_found:
            present_fields.add(field_name)
        else:
            missing_fields.add(field_name)

    # Calculate field completion score (0-100)
    total_fields = len(REQUIRED_FIELDS)
    present_count = len(present_fields)
    field_score = (present_count / total_fields) * 100 if total_fields > 0 else 0

    # Categorize missing fields by priority
    critical_fields = {"company_name", "revenue", "ceo", "market_share"}
    important_fields = {"headquarters", "employees", "competitors", "subscribers"}

    critical_missing = missing_fields & critical_fields
    important_missing = missing_fields & important_fields
    other_missing = missing_fields - critical_fields - important_fields

    return {
        "field_score": field_score,
        "present_fields": list(present_fields),
        "missing_fields": list(missing_fields),
        "critical_missing": list(critical_missing),
        "important_missing": list(important_missing),
        "other_missing": list(other_missing),
        "field_counts": {
            "total": total_fields,
            "present": present_count,
            "missing": len(missing_fields),
        },
    }


def check_research_quality(
    company_name: str, extracted_data: str, sources: List[Dict[str, str]]
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
            - quality_score: Float 0-100 (composite of LLM + field scores)
            - llm_quality_score: Float 0-100 (LLM assessment)
            - field_score: Float 0-100 (field completeness)
            - missing_information: List of missing items
            - missing_fields: List of missing field names
            - critical_missing: List of critical missing fields
            - important_missing: List of important missing fields
            - strengths: List of research strengths
            - recommended_queries: List of search queries to fill gaps
    """
    # Import smart_completion for cost-optimized routing
    from ..llm.smart_client import smart_completion

    # First, check field-level completeness (fast, no LLM call)
    field_results = check_field_completeness(extracted_data)
    field_score = field_results["field_score"]

    logger.debug(
        f"Field completeness: {field_score:.1f}% "
        f"({field_results['field_counts']['present']}/{field_results['field_counts']['total']} fields)"
    )

    # Log critical missing fields
    if field_results["critical_missing"]:
        logger.warning(f"Critical fields missing: {field_results['critical_missing']}")

    # Format sources
    formatted_sources = format_sources_for_extraction(sources)

    # Create quality check prompt
    prompt = QUALITY_CHECK_PROMPT.format(
        company_name=company_name, extracted_data=extracted_data, sources=formatted_sources
    )

    # Use smart_completion - routes to DeepSeek V3 for classification tasks
    result = smart_completion(
        prompt=prompt,
        task_type="classification",  # Routes to DeepSeek V3 ($0.14/1M)
        max_tokens=1500,
        temperature=0.0,
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
        start_idx = content.find("{")
        end_idx = content.rfind("}")

        if start_idx >= 0 and end_idx >= 0:
            json_str = content[start_idx : end_idx + 1]
            quality_data = json.loads(json_str)
        else:
            quality_data = json.loads(content)

        # Get LLM quality score
        llm_quality_score = float(quality_data.get("quality_score", 0))

        # Calculate composite quality score (60% LLM assessment, 40% field completeness)
        # Field score matters more when critical fields are missing
        critical_penalty = (
            len(field_results["critical_missing"]) * 5
        )  # -5 points per critical field
        composite_score = (llm_quality_score * 0.6) + (field_score * 0.4) - critical_penalty
        composite_score = max(0, min(100, composite_score))  # Clamp to 0-100

        # Generate recommended queries based on missing fields
        field_based_queries = _generate_queries_for_missing_fields(
            company_name, field_results["critical_missing"], field_results["important_missing"]
        )

        # Merge with LLM recommended queries (deduplicate)
        llm_queries = quality_data.get("recommended_queries", [])
        all_queries = field_based_queries + [q for q in llm_queries if q not in field_based_queries]

        # Validate structure with field-level results
        quality_result = {
            "quality_score": composite_score,
            "llm_quality_score": llm_quality_score,
            "field_score": field_score,
            "missing_information": quality_data.get("missing_information", []),
            "missing_fields": field_results["missing_fields"],
            "critical_missing": field_results["critical_missing"],
            "important_missing": field_results["important_missing"],
            "present_fields": field_results["present_fields"],
            "field_counts": field_results["field_counts"],
            "strengths": quality_data.get("strengths", []),
            "recommended_queries": all_queries,
            "cost": cost,
            "tokens": {"input": result.input_tokens, "output": result.output_tokens},
        }

        logger.debug(
            f"Quality check complete - composite: {composite_score:.1f}, "
            f"llm: {llm_quality_score:.1f}, field: {field_score:.1f}, model: {result.model}"
        )
        return quality_result

    except json.JSONDecodeError as e:
        # Fallback: return quality based on field completeness if LLM parsing fails
        logger.warning(
            f"Failed to parse quality response as JSON: {type(e).__name__}. "
            "Using field-based quality score as fallback."
        )

        # Generate recommended queries based on missing fields
        field_based_queries = _generate_queries_for_missing_fields(
            company_name, field_results["critical_missing"], field_results["important_missing"]
        )

        # Critical penalty applies even in fallback
        critical_penalty = len(field_results["critical_missing"]) * 5
        fallback_score = max(0, min(100, field_score - critical_penalty))

        return {
            "quality_score": fallback_score,
            "llm_quality_score": None,  # LLM failed
            "field_score": field_score,
            "missing_information": ["Unable to parse quality assessment response"],
            "missing_fields": field_results["missing_fields"],
            "critical_missing": field_results["critical_missing"],
            "important_missing": field_results["important_missing"],
            "present_fields": field_results["present_fields"],
            "field_counts": field_results["field_counts"],
            "strengths": [],
            "recommended_queries": field_based_queries,
            "cost": cost,
            "tokens": {"input": result.input_tokens, "output": result.output_tokens},
        }


def _generate_queries_for_missing_fields(
    company_name: str, critical_missing: List[str], important_missing: List[str]
) -> List[str]:
    """
    Generate targeted search queries based on missing fields.

    Args:
        company_name: Name of the company
        critical_missing: List of critical missing field names
        important_missing: List of important missing field names

    Returns:
        List of search queries to fill gaps
    """
    queries = []

    # Query templates for each field type
    query_templates = {
        # Critical fields
        "company_name": ["{company} official name legal entity"],
        "revenue": [
            "{company} annual revenue financial results",
            "{company} revenue earnings report",
        ],
        "ceo": [
            "{company} CEO chief executive officer name",
            "{company} leadership management team",
        ],
        "market_share": [
            "{company} market share industry position",
            "{company} market position competitors",
        ],
        # Important fields
        "headquarters": ["{company} headquarters location address"],
        "employees": ["{company} number of employees workforce size", "{company} headcount staff"],
        "competitors": ["{company} competitors competitive landscape", "{company} industry rivals"],
        "subscribers": ["{company} customers subscribers users base", "{company} customer count"],
        # Other fields
        "founded": ["{company} founded established history"],
        "industry": ["{company} industry sector business segment"],
        "leadership_team": ["{company} leadership team executives board directors"],
        "profit_margin": ["{company} profit margin profitability net income"],
        "market_cap": ["{company} market cap valuation market capitalization"],
        "products_services": ["{company} products services offerings"],
        "geographic_presence": ["{company} geographic presence operations countries"],
    }

    # Add queries for critical fields first (highest priority)
    for field in critical_missing:
        if field in query_templates:
            for template in query_templates[field][:1]:  # Take first template for critical
                queries.append(template.format(company=company_name))

    # Add queries for important fields
    for field in important_missing:
        if field in query_templates:
            for template in query_templates[field][:1]:  # Take first template
                queries.append(template.format(company=company_name))

    return queries[:10]  # Limit to 10 queries
