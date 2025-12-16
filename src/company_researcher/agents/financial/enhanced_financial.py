"""
Enhanced Financial Agent with Real Financial Data APIs (Phase 7).

Integrates multiple data sources for comprehensive financial analysis:
- Alpha Vantage (stock data and fundamentals)
- SEC EDGAR (official filings)
- Web search results (supplementary)

Provides:
- Revenue analysis (trends, growth rates)
- Profitability metrics (margins, EBITDA)
- Financial health indicators (debt, cash flow, ratios)
- Stock performance (for public companies)
- Funding analysis (for private companies)
"""

from typing import Any, Callable, Dict, Optional

from ...utils import get_logger

logger = get_logger(__name__)

from ...config import get_config
from ...llm.client_factory import calculate_cost, get_anthropic_client, safe_extract_text
from ...state import OverallState
from ...tools.alpha_vantage_client import AlphaVantageClient, extract_key_metrics
from ...tools.sec_edgar_parser import (
    SECEdgarParser,
    extract_financial_health,
    extract_profitability_metrics,
    extract_revenue_trends,
    is_public_company,
)


class EnhancedFinancialAgent:
    """Enhanced financial analysis agent with API integrations."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(self, company_name: str, search_results: list = None) -> Dict[str, Any]:
        """Perform enhanced financial analysis for a company."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return enhanced_financial_agent_node(state)


def create_enhanced_financial_agent(
    search_tool: Callable = None, llm_client: Any = None
) -> EnhancedFinancialAgent:
    """Factory function to create an EnhancedFinancialAgent."""
    return EnhancedFinancialAgent(search_tool=search_tool, llm_client=llm_client)


# ==============================================================================
# Prompts
# ==============================================================================

ENHANCED_FINANCIAL_PROMPT = """You are an expert financial analyst with access to comprehensive financial data.

Company: {company_name}

**DATA SOURCES:**

{financial_data_summary}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide comprehensive financial analysis combining all available data sources.

**STRUCTURE YOUR ANALYSIS:**

### 1. Revenue Analysis
- Annual revenue (last 3-5 years)
- Revenue growth rates (YoY, CAGR)
- Revenue breakdown (if available: by segment, geography)
- Growth trajectory and trends

### 2. Profitability Metrics
- Gross margin
- Operating margin
- Net profit margin
- EBITDA and EBITDA margin
- Trend analysis

### 3. Financial Health
- Cash and cash equivalents
- Total debt and debt-to-equity ratio
- Current ratio and quick ratio
- Free cash flow
- Overall financial stability assessment

### 4. Stock Performance (if public company)
- Current stock price and market cap
- 52-week performance
- Key valuation ratios (P/E, P/B, etc.)
- Analyst ratings or price targets

### 5. Funding Information (if private company)
- Total funding raised
- Latest funding round details
- Key investors
- Estimated valuation

**REQUIREMENTS:**
- Use specific numbers with dates
- Cite sources for each data point
- Highlight gaps where data is unavailable
- Provide context and interpretation
- Note any concerning trends or positive indicators

Begin your analysis:"""


# ==============================================================================
# Enhanced Financial Agent
# ==============================================================================


def enhanced_financial_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced Financial Agent Node: Comprehensive financial analysis.

    Uses multiple data sources:
    1. Alpha Vantage API for stock data (if available)
    2. SEC EDGAR for official filings (if public company)
    3. Web search results (supplementary)

    Args:
        state: Current workflow state

    Returns:
        State update with enhanced financial analysis
    """
    logger.info("Enhanced Financial agent starting - comprehensive analysis")

    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    # Initialize clients
    alpha_vantage = AlphaVantageClient()
    sec_parser = SECEdgarParser()

    # Determine company type and fetch appropriate data
    financial_data = gather_financial_data(company_name, alpha_vantage, sec_parser)

    # Create comprehensive analysis prompt
    prompt = create_financial_analysis_prompt(company_name, financial_data, search_results)

    # Call LLM for analysis
    client = get_anthropic_client()
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.enhanced_financial_max_tokens,
        temperature=config.financial_temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    financial_analysis = safe_extract_text(response, agent_name="enhanced_financial")
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

    logger.info(f"Enhanced Financial analysis complete - cost: ${cost:.4f}")

    # Create agent output
    agent_output = {
        "analysis": financial_analysis,
        "data_sources_used": {
            "alpha_vantage": financial_data.get("alpha_vantage", {}).get("available", False),
            "sec_edgar": financial_data.get("sec_edgar", {}).get("available", False),
            "search_results": len(search_results) > 0,
        },
        "data_extracted": True,
        "cost": cost,
        "tokens": {"input": response.usage.input_tokens, "output": response.usage.output_tokens},
    }

    return {
        "agent_outputs": {"financial": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
    }


# ==============================================================================
# Helper Functions
# ==============================================================================


def gather_financial_data(
    company_name: str, alpha_vantage: AlphaVantageClient, sec_parser: SECEdgarParser
) -> Dict[str, Any]:
    """
    Gather financial data from all available sources.

    Args:
        company_name: Name of company to research
        alpha_vantage: Alpha Vantage client
        sec_parser: SEC EDGAR parser

    Returns:
        Dictionary with all available financial data
    """
    logger.info("Gathering data from multiple sources")

    financial_data = {}

    # Try to determine stock ticker symbol
    # (In production, would have a ticker lookup service)
    ticker = infer_ticker_symbol(company_name)

    # 1. Try Alpha Vantage (for stock data)
    if alpha_vantage.is_available() and ticker:
        logger.debug(f"Fetching Alpha Vantage data for {ticker}")
        try:
            av_data = alpha_vantage.get_company_financials(ticker)
            financial_data["alpha_vantage"] = av_data

            if av_data.get("available"):
                # Extract key metrics
                metrics = extract_key_metrics(av_data)
                financial_data["key_metrics"] = metrics
                logger.debug("Alpha Vantage data fetched successfully")
            else:
                logger.debug("Alpha Vantage data unavailable")
        except Exception as e:
            logger.warning(f"Alpha Vantage error: {e}")
            financial_data["alpha_vantage"] = {"available": False, "error": str(e)}
    else:
        logger.debug("Alpha Vantage skipped (no API key or ticker)")
        financial_data["alpha_vantage"] = {"available": False, "reason": "No API key or ticker"}

    # 2. Try SEC EDGAR (for official filings)
    if is_public_company(company_name):
        logger.debug("Fetching SEC EDGAR filings")
        try:
            sec_data = sec_parser.get_company_financials(company_name)
            financial_data["sec_edgar"] = sec_data

            if sec_data.get("available"):
                # Extract trends and metrics
                financial_data["revenue_trends"] = extract_revenue_trends(sec_data)
                financial_data["profitability"] = extract_profitability_metrics(sec_data)
                financial_data["financial_health"] = extract_financial_health(sec_data)
                logger.debug("SEC EDGAR data fetched successfully")
            else:
                logger.debug("SEC EDGAR data unavailable")
        except Exception as e:
            logger.warning(f"SEC EDGAR error: {e}")
            financial_data["sec_edgar"] = {"available": False, "error": str(e)}
    else:
        logger.debug("SEC EDGAR skipped (private company)")
        financial_data["sec_edgar"] = {
            "available": False,
            "reason": "Private company - no SEC filings",
        }

    return financial_data


def create_financial_analysis_prompt(
    company_name: str, financial_data: Dict[str, Any], search_results: list
) -> str:
    """
    Create comprehensive financial analysis prompt.

    Args:
        company_name: Name of company
        financial_data: Gathered financial data
        search_results: Web search results

    Returns:
        Formatted prompt string
    """
    # Summarize available data sources
    data_summary = []

    # Alpha Vantage summary
    av_data = financial_data.get("alpha_vantage", {})
    if av_data.get("available"):
        data_summary.append("✓ **Alpha Vantage**: Stock data and fundamentals available")

        key_metrics = financial_data.get("key_metrics", {})
        if key_metrics.get("available"):
            metrics_str = []
            if key_metrics.get("market_cap"):
                metrics_str.append(f"Market Cap: {key_metrics['market_cap']}")
            if key_metrics.get("revenue_ttm"):
                metrics_str.append(f"Revenue (TTM): {key_metrics['revenue_ttm']}")
            if key_metrics.get("profit_margin"):
                metrics_str.append(f"Profit Margin: {key_metrics['profit_margin']}")

            if metrics_str:
                data_summary.append(f"  Key Metrics: {', '.join(metrics_str)}")
    else:
        data_summary.append(f"✗ **Alpha Vantage**: {av_data.get('reason', 'Not available')}")

    # SEC EDGAR summary
    sec_data = financial_data.get("sec_edgar", {})
    if sec_data.get("available"):
        data_summary.append("✓ **SEC EDGAR**: Official filings available")

        if sec_data.get("latest_10k"):
            data_summary.append(
                f"  Latest 10-K: {sec_data['latest_10k'].get('filing_date', 'N/A')}"
            )
        if sec_data.get("latest_10q"):
            data_summary.append(
                f"  Latest 10-Q: {sec_data['latest_10q'].get('filing_date', 'N/A')}"
            )
    else:
        data_summary.append(f"✗ **SEC EDGAR**: {sec_data.get('reason', 'Not available')}")

    # Search results summary
    if search_results:
        data_summary.append(f"✓ **Web Search**: {len(search_results)} sources available")
    else:
        data_summary.append("✗ **Web Search**: No search results")

    data_summary_text = "\n".join(data_summary)

    # Format search results
    formatted_results = "\n\n".join(
        [
            f"Source {i+1}: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')[:400]}..."
            for i, result in enumerate(search_results[:10])
        ]
    )

    # Create prompt
    prompt = ENHANCED_FINANCIAL_PROMPT.format(
        company_name=company_name,
        financial_data_summary=data_summary_text,
        search_results=formatted_results if formatted_results else "No search results available.",
    )

    return prompt


def infer_ticker_symbol(company_name: str) -> Optional[str]:
    """
    Infer stock ticker symbol from company name.

    This is a simple heuristic mapping. In production, would use:
    - Ticker lookup API
    - Company database with ticker mappings
    - Symbol search service

    Args:
        company_name: Company name

    Returns:
        Ticker symbol or None if not found
    """
    # Simple heuristic mapping for common companies
    ticker_map = {
        "tesla": "TSLA",
        "microsoft": "MSFT",
        "apple": "AAPL",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "salesforce": "CRM",
        "adobe": "ADBE",
        "oracle": "ORCL",
        "intel": "INTC",
        "amd": "AMD",
        "ibm": "IBM",
        "cisco": "CSCO",
        "qualcomm": "QCOM",
        "paypal": "PYPL",
        "square": "SQ",
        "shopify": "SHOP",
        "zoom": "ZM",
        "slack": "WORK",
        "twitter": "TWTR",
        "snap": "SNAP",
        "uber": "UBER",
        "lyft": "LYFT",
        "airbnb": "ABNB",
        "doordash": "DASH",
        "coinbase": "COIN",
        "robinhood": "HOOD",
        "snowflake": "SNOW",
        "databricks": None,  # Private
        "stripe": None,  # Private
        "openai": None,  # Private
        "anthropic": None,  # Private
        "spacex": None,  # Private
    }

    company_lower = company_name.lower().strip()

    for key, ticker in ticker_map.items():
        if key in company_lower:
            return ticker

    # Not found in map
    return None
