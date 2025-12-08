"""
Integrations Module for Company Researcher.

Provides:
- News API integration
- Crunchbase integration for funding/company data
- SEC EDGAR integration for financial filings
- External data source connectors
- Third-party service integrations
"""

from .news_api import (
    NewsAPIClient,
    NewsArticle,
    NewsSearchResult,
    NewsMonitor,
    NewsSummarizer,
    NewsSentiment,
    NewsCategory,
    SimpleSentimentAnalyzer,
    create_news_client,
    search_company_news,
    create_news_monitor,
)

from .crunchbase import (
    CrunchbaseClient,
    CompanyProfile,
    FundingHistory,
    FundingRound,
    FundingType,
    create_crunchbase_client,
)

from .sec_edgar import (
    SECEdgarClient,
    CompanyInfo,
    Filing,
    FilingType,
    FinancialFact,
    CompanyFinancials,
    create_sec_client,
)

__all__ = [
    # News API
    "NewsAPIClient",
    "NewsArticle",
    "NewsSearchResult",
    "NewsMonitor",
    "NewsSummarizer",
    "NewsSentiment",
    "NewsCategory",
    "SimpleSentimentAnalyzer",
    "create_news_client",
    "search_company_news",
    "create_news_monitor",
    # Crunchbase
    "CrunchbaseClient",
    "CompanyProfile",
    "FundingHistory",
    "FundingRound",
    "FundingType",
    "create_crunchbase_client",
    # SEC EDGAR
    "SECEdgarClient",
    "CompanyInfo",
    "Filing",
    "FilingType",
    "FinancialFact",
    "CompanyFinancials",
    "create_sec_client",
]
