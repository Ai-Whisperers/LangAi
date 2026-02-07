"""
Comprehensive Analysis Nodes for Multi-Faceted Company Research.

This module contains specialized analysis nodes for comprehensive research:
- Core company analysis
- Financial analysis
- Market position analysis
- ESG (Environmental, Social, Governance) analysis
- Brand and reputation analysis

Each node focuses on a specific aspect of company intelligence.

Uses SmartLLMClient for automatic provider fallback:
- Primary: Anthropic Claude
- Fallback 1: Groq (llama-3.3-70b-versatile) on rate limit
- Fallback 2: DeepSeek on rate limit
"""

import json
from typing import Any, Dict, List, Optional

from ...config import get_config
from ...llm.smart_client import TaskType, get_smart_client
from ...prompts import ANALYZE_RESULTS_PROMPT, BRAND_AUDIT_PROMPT
from ...quality.models import MarketShareValidator
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

    logger.info("[NODE] Running core analysis...")

    # Format search results
    formatted_results = _format_search_results(state["search_results"])

    prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=state["company_name"], search_results=formatted_results
    )

    result = _create_completion(
        prompt=prompt, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature
    )

    notes = result["content"]
    cost = result["cost"]

    logger.info(f"[OK] Core analysis complete (via {result['provider']})")

    return {
        "notes": [notes],
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {}).get("input", 0) + result["input_tokens"],
            "output": state.get("total_tokens", {}).get("output", 0) + result["output_tokens"],
        },
    }


def financial_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Financial analysis using available financial data.
    """
    logger.info("[NODE] Running financial analysis...")

    # Combine financial data from provider and search results
    financial_context = ""
    if state.get("financial_data"):
        financial_context = (
            f"Financial Data from APIs:\n{json.dumps(state['financial_data'], indent=2)}\n\n"
        )

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

    result = _create_completion(prompt=prompt, max_tokens=1500, temperature=0.1)

    analysis = result["content"]
    cost = result["cost"]

    logger.info(f"[OK] Financial analysis complete (via {result['provider']})")

    return {
        "agent_outputs": {"financial": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {}).get("input", 0) + result["input_tokens"],
            "output": state.get("total_tokens", {}).get("output", 0) + result["output_tokens"],
        },
    }


def market_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Market position and competitive analysis with market share validation.
    """
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

    result = _create_completion(prompt=prompt, max_tokens=1200, temperature=0.1)

    analysis = result["content"]
    cost = result["cost"]

    # Validate market share data if present in the analysis
    validator = MarketShareValidator(tolerance=5.0)
    validation_result, extracted_shares = validator.validate_from_text(
        text=analysis, company_name=state["company_name"]
    )

    # Add validation warnings to the analysis if issues found
    if extracted_shares and not validation_result.is_valid:
        validation_warning = "\n\n⚠️ **Market Share Data Quality Warning**\n"
        validation_warning += f"- Total market shares: {validation_result.total_percentage:.1f}%\n"
        validation_warning += (
            f"- Deviation from 100%: {validation_result.deviation_from_100:.1f}%\n"
        )
        for issue in validation_result.issues:
            validation_warning += f"- Issue: {issue}\n"
        if validation_result.corrected_shares:
            validation_warning += (
                f"- Suggested normalized shares: {validation_result.corrected_shares}\n"
            )
        analysis += validation_warning
        logger.warning(f"[VALIDATION] Market share validation issues: {validation_result.issues}")
    elif extracted_shares and validation_result.warnings:
        for warning in validation_result.warnings:
            logger.info(f"[VALIDATION] Market share note: {warning}")

    logger.info(f"[OK] Market analysis complete (via {result['provider']})")

    return {
        "agent_outputs": {"market": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {}).get("input", 0) + result["input_tokens"],
            "output": state.get("total_tokens", {}).get("output", 0) + result["output_tokens"],
        },
    }


def esg_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    ESG (Environmental, Social, Governance) analysis.
    """
    logger.info("[NODE] Running ESG analysis...")

    # Extract ESG-related info
    esg_context = _extract_esg_from_search(state["search_results"])

    prompt = ESG_ANALYSIS_PROMPT.format(
        company_name=state["company_name"],
        context=esg_context or "Limited ESG data available from search results.",
    )

    result = _create_completion(prompt=prompt, max_tokens=1200, temperature=0.1)

    analysis = result["content"]
    cost = result["cost"]

    logger.info(f"[OK] ESG analysis complete (via {result['provider']})")

    return {
        "agent_outputs": {"esg": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {}).get("input", 0) + result["input_tokens"],
            "output": state.get("total_tokens", {}).get("output", 0) + result["output_tokens"],
        },
    }


def brand_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Brand perception and reputation analysis.
    """
    logger.info("[NODE] Running brand analysis...")

    # Extract brand-related info
    brand_context = _extract_brand_from_search(state["search_results"])

    prompt = BRAND_AUDIT_PROMPT.format(
        company_name=state["company_name"],
        search_results=brand_context or "Limited brand data available from search results.",
    )

    result = _create_completion(prompt=prompt, max_tokens=1000, temperature=0.1)

    analysis = result["content"]
    cost = result["cost"]

    logger.info(f"[OK] Brand analysis complete (via {result['provider']})")

    return {
        "agent_outputs": {"brand": analysis},
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {}).get("input", 0) + result["input_tokens"],
            "output": state.get("total_tokens", {}).get("output", 0) + result["output_tokens"],
        },
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
    current = state.get("total_tokens") or {}
    return {
        "input": current.get("input", 0) + usage.input_tokens,
        "output": current.get("output", 0) + usage.output_tokens,
    }


def _extract_financial_from_search(results: List[Dict]) -> str:
    """Extract financial information from search results."""
    financial_keywords = [
        "revenue",
        "profit",
        "earnings",
        "financial",
        "billion",
        "million",
        "growth",
    ]
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
    esg_keywords = [
        "esg",
        "sustainability",
        "environmental",
        "social",
        "governance",
        "carbon",
        "diversity",
    ]
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
