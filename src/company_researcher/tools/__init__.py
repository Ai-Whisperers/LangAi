"""
Tools Module for Company Researcher.

Contains utility tools for various operations:
- Alpha Vantage client for stock data
- Competitor analysis utilities
- SEC EDGAR parser for regulatory filings
"""

from .alpha_vantage_client import (
    AlphaVantageClient,
    extract_key_metrics,
)
from .competitor_analysis_utils import (
    CompetitorType,
    ThreatLevel,
    TechStackAnalyzer,
    GitHubMetrics,
    classify_competitor,
    assess_threat_level,
    analyze_competitive_positioning,
    analyze_patent_portfolio,
    aggregate_review_sentiment,
)
from .sec_edgar_parser import (
    SECEdgarParser,
    extract_revenue_trends,
    extract_profitability_metrics,
    extract_financial_health,
    is_public_company,
)

__all__ = [
    # Alpha Vantage
    "AlphaVantageClient",
    "extract_key_metrics",
    # Competitor Analysis
    "CompetitorType",
    "ThreatLevel",
    "TechStackAnalyzer",
    "GitHubMetrics",
    "classify_competitor",
    "assess_threat_level",
    "analyze_competitive_positioning",
    "analyze_patent_portfolio",
    "aggregate_review_sentiment",
    # SEC EDGAR
    "SECEdgarParser",
    "extract_revenue_trends",
    "extract_profitability_metrics",
    "extract_financial_health",
    "is_public_company",
]
