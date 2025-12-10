"""
Comprehensive Analysis Nodes for Multi-Faceted Company Research.

This module contains specialized analysis nodes for comprehensive research:
- Core company analysis
- Financial analysis
- Market position analysis
- ESG (Environmental, Social, Governance) analysis
- Brand and reputation analysis

Each node focuses on a specific aspect of company intelligence.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from anthropic import Anthropic

from ...state import OverallState
from ...config import get_config
from ...llm.client_factory import safe_extract_text
from ...prompts import (
    ANALYZE_RESULTS_PROMPT,
    BRAND_AUDIT_PROMPT,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ESG Analysis Prompt (Comprehensive-specific)
# =============================================================================

ESG_ANALYSIS_PROMPT = """You are an ESG (Environmental, Social, Governance) analyst.

Analyze the following information about {company_name}:

{context}

Provide a comprehensive ESG analysis covering:

## Environmental
- Carbon emissions and climate initiatives
- Energy efficiency and renewable energy use
- Waste management and recycling programs
- Environmental compliance and violations

## Social
- Employee diversity and inclusion
- Labor practices and worker safety
- Community engagement and impact
- Supply chain ethics

## Governance
- Board composition and independence
- Executive compensation practices
- Shareholder rights and activism
- Anti-corruption policies and compliance

## ESG Rating
Provide an overall ESG score (0-100) and rating (STRONG/MODERATE/WEAK)

Be specific with data points and cite sources when available.
"""


# =============================================================================
# Analysis Nodes
# =============================================================================

def core_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Core analysis of search results - company overview, products, etc.
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    logger.info("[NODE] Running core analysis...")

    # Format search results
    formatted_results = _format_search_results(state["search_results"])

    prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=state["company_name"],
        search_results=formatted_results
    )

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    notes = safe_extract_text(response, agent_name="core_analysis")
    cost = config.calculate_llm_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info("[OK] Core analysis complete")

    return {
        "notes": [notes],
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": _update_tokens(state, response.usage)
    }


def financial_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Financial analysis using available financial data.
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    logger.info("[NODE] Running financial analysis...")

    # Combine financial data from provider and search results
    financial_context = ""
    if state.get("financial_data"):
        financial_context = f"Financial Data from APIs:\n{json.dumps(state['financial_data'], indent=2)}\n\n"

    # Extract financial info from search results
    search_financial = _extract_financial_from_search(state["search_results"])
    if search_financial:
        financial_context += f"Financial Info from Web Search:\n{search_financial}\n\n"

    if not financial_context:
        logger.info("[INFO] No financial data available, skipping")
        return {"agent_outputs": {"financial": None}}

    prompt = f"""You are an expert financial analyst.

Analyze the following financial data for {state['company_name']}:

{financial_context}

Provide a comprehensive financial analysis including:
1. Revenue and Growth Analysis
2. Profitability Metrics
3. Financial Health Indicators
4. Valuation Assessment
5. Key Financial Risks
6. Summary and Outlook

Be specific with numbers and cite your sources.
"""

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1500,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = safe_extract_text(response, agent_name="financial_analysis")
    cost = config.calculate_llm_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info("[OK] Financial analysis complete")

    return {
        "agent_outputs": {"financial": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": _update_tokens(state, response.usage)
    }


def market_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Market position and competitive analysis.
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    logger.info("[NODE] Running market analysis...")

    # Extract market-related info
    market_context = _extract_market_from_search(state["search_results"])

    prompt = f"""You are an expert market analyst.

Analyze the market position of {state['company_name']}:

{market_context}

Provide analysis of:
1. Market Size and Growth
2. Market Share and Position
3. Key Competitors
4. Competitive Advantages
5. Market Trends
6. Strategic Positioning

Be specific and cite sources where possible.
"""

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1200,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = safe_extract_text(response, agent_name="market_analysis")
    cost = config.calculate_llm_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info("[OK] Market analysis complete")

    return {
        "agent_outputs": {"market": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": _update_tokens(state, response.usage)
    }


def esg_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    ESG (Environmental, Social, Governance) analysis.
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    logger.info("[NODE] Running ESG analysis...")

    # Extract ESG-related info
    esg_context = _extract_esg_from_search(state["search_results"])

    prompt = ESG_ANALYSIS_PROMPT.format(
        company_name=state["company_name"],
        context=esg_context or "Limited ESG data available from search results."
    )

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1200,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = safe_extract_text(response, agent_name="esg_analysis")
    cost = config.calculate_llm_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info("[OK] ESG analysis complete")

    return {
        "agent_outputs": {"esg": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": _update_tokens(state, response.usage)
    }


def brand_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Brand perception and reputation analysis.
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    logger.info("[NODE] Running brand analysis...")

    # Extract brand-related info
    brand_context = _extract_brand_from_search(state["search_results"])

    prompt = BRAND_AUDIT_PROMPT.format(
        company_name=state["company_name"],
        search_results=brand_context or "Limited brand data available from search results."
    )

    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1000,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = safe_extract_text(response, agent_name="brand_analysis")
    cost = config.calculate_llm_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info("[OK] Brand analysis complete")

    return {
        "agent_outputs": {"brand": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": _update_tokens(state, response.usage)
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _format_search_results(results: List[Dict]) -> str:
    """Format search results for prompt."""
    formatted = []
    for i, r in enumerate(results[:15], 1):
        formatted.append(f"[{i}] {r.get('title', 'No title')}")
        formatted.append(f"    URL: {r.get('url', 'No URL')}")
        content = r.get("content", "")[:500]
        if content:
            formatted.append(f"    Content: {content}...")
        formatted.append("")
    return "\n".join(formatted)


def _update_tokens(state: OverallState, usage) -> Dict[str, int]:
    """Update token counts."""
    current = state.get("total_tokens", {"input": 0, "output": 0})
    return {
        "input": current["input"] + usage.input_tokens,
        "output": current["output"] + usage.output_tokens
    }


def _extract_financial_from_search(results: List[Dict]) -> str:
    """Extract financial information from search results."""
    financial_keywords = ["revenue", "profit", "earnings", "financial", "billion", "million", "growth"]
    relevant = []
    for r in results:
        content = (r.get("content", "") or "").lower()
        if any(kw in content for kw in financial_keywords):
            relevant.append(r.get("content", "")[:500])
    return "\n\n".join(relevant[:5])


def _extract_market_from_search(results: List[Dict]) -> str:
    """Extract market information from search results."""
    market_keywords = ["market", "competitor", "industry", "share", "position", "leader"]
    relevant = []
    for r in results:
        content = (r.get("content", "") or "").lower()
        if any(kw in content for kw in market_keywords):
            relevant.append(r.get("content", "")[:500])
    return "\n\n".join(relevant[:5])


def _extract_esg_from_search(results: List[Dict]) -> str:
    """Extract ESG information from search results."""
    esg_keywords = ["esg", "sustainability", "environmental", "social", "governance", "carbon", "diversity"]
    relevant = []
    for r in results:
        content = (r.get("content", "") or "").lower()
        if any(kw in content for kw in esg_keywords):
            relevant.append(r.get("content", "")[:500])
    return "\n\n".join(relevant[:5])


def _extract_brand_from_search(results: List[Dict]) -> str:
    """Extract brand information from search results."""
    brand_keywords = ["brand", "reputation", "customer", "review", "perception", "trust"]
    relevant = []
    for r in results:
        content = (r.get("content", "") or "").lower()
        if any(kw in content for kw in brand_keywords):
            relevant.append(r.get("content", "")[:500])
    return "\n\n".join(relevant[:5])
