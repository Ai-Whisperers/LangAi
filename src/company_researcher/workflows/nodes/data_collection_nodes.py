"""
Data Collection Nodes for Comprehensive Research Workflow.

This module contains nodes that fetch data from external sources:
- Financial data providers (with fallback chain)
- News providers (with fallback chain)
"""

import logging
from typing import Dict, Any, Optional

from ...state import OverallState
from ...config import get_config
from ...integrations import (
    create_financial_provider,
    create_news_provider,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Data Collection Nodes
# =============================================================================

def fetch_financial_data_node(state: OverallState) -> Dict[str, Any]:
    """
    Fetch financial data using the unified provider with fallback chain.
    """
    config = get_config()
    company_name = state["company_name"]

    logger.info(f"[NODE] Fetching financial data for: {company_name}")

    # Try to identify ticker from company name
    ticker = _guess_ticker(company_name)

    if not ticker:
        logger.info("[INFO] Could not identify ticker, skipping financial data fetch")
        return {"financial_data": None}

    try:
        provider = create_financial_provider(config)
        financial_data = provider.get_financial_data(ticker)

        if financial_data:
            logger.info(f"[OK] Got {financial_data.data_quality} financial data from {', '.join(financial_data.data_sources)}")
            return {
                "financial_data": financial_data.to_dict(),
                "ticker": ticker
            }
    except Exception as e:
        logger.warning(f"Financial data fetch failed: {e}")

    return {"financial_data": None, "ticker": ticker}


def fetch_news_node(state: OverallState) -> Dict[str, Any]:
    """
    Fetch recent news using the unified news provider.
    """
    config = get_config()
    company_name = state["company_name"]

    logger.info(f"[NODE] Fetching news for: {company_name}")

    try:
        provider = create_news_provider(config)
        news_result = provider.get_company_news(company_name, max_results=15, days_back=30)

        if news_result.articles:
            logger.info(f"[OK] Got {len(news_result.articles)} articles from {', '.join(news_result.sources_used)}")
            return {
                "news_articles": news_result.to_dict(),
                "news_count": len(news_result.articles)
            }
    except Exception as e:
        logger.warning(f"News fetch failed: {e}")

    return {"news_articles": None, "news_count": 0}


# =============================================================================
# Helper Functions
# =============================================================================

def _guess_ticker(company_name: str) -> Optional[str]:
    """Try to guess ticker from company name."""
    # Common company name to ticker mappings
    common_tickers = {
        "microsoft": "MSFT",
        "apple": "AAPL",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "netflix": "NFLX",
    }

    name_lower = company_name.lower()
    for key, ticker in common_tickers.items():
        if key in name_lower:
            return ticker

    # If company name looks like a ticker (all caps, 1-5 chars), use it
    if company_name.isupper() and 1 <= len(company_name) <= 5:
        return company_name

    return None
