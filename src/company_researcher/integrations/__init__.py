"""
Company Researcher API Integrations.

Unified access to all external API integrations with fallback chains.

Categories:
- Financial Data: yfinance, FMP, Finnhub, Polygon
- News Data: NewsAPI, GNews, Mediastack
- Company Data: Hunter.io, DomainsDB, GitHub, Reddit
- Search: Tavily, DuckDuckGo (via tavily fallback)
- Geocoding: OpenCage, Nominatim
- Scraping: Firecrawl, ScrapeGraph
- Regulatory: SEC Edgar, Crunchbase
- ML/AI: HuggingFace

Usage:
    # Use unified providers (recommended)
    from company_researcher.integrations import (
        FinancialDataProvider,
        NewsProvider,
        create_financial_provider,
        create_news_provider
    )

    provider = create_financial_provider(config)
    data = provider.get_financial_data("AAPL")

    # Or use individual clients
    from company_researcher.integrations import FMPClient, FinnhubClient
"""

# Base client and errors
from .base_client import APIError, BaseAPIClient, RateLimitError
from .cost_tracker import (
    PROVIDER_CONFIGS,
    CostAlert,
    CostTier,
    CostTracker,
    ProviderCategory,
    ProviderConfig,
    UsageRecord,
    get_cost_tracker,
    get_daily_cost,
    get_monthly_cost,
    print_cost_summary,
    track_cost,
)
from .crawl4ai_client import (
    Crawl4AIClient,
    CrawlResult,
    get_crawl4ai,
    scrape_to_markdown,
    scrape_url_sync,
)
from .crunchbase import CrunchbaseClient
from .domainsdb import DomainsDBClient
from .financial_modeling_prep import (
    BalanceSheet,
    CompanyProfile,
    DCFValue,
    FMPClient,
    IncomeStatement,
    KeyMetrics,
)
from .financial_provider import (
    FinancialData,
    FinancialDataProvider,
    ProviderState,
    ProviderStatus,
    create_financial_provider,
)
from .finnhub import FinnhubClient
from .firecrawl_client import FirecrawlClient
from .github_client import GitHubClient
from .gnews import GNewsClient
from .google_news_rss import GoogleNewsRSS
from .google_news_rss import NewsArticle as GoogleNewsArticle
from .google_news_rss import NewsSearchResult as GoogleNewsSearchResult
from .google_news_rss import get_google_news, search_news
from .health_check import (
    HealthReport,
    HealthStatus,
    IntegrationHealth,
    IntegrationHealthChecker,
    check_integration_health,
)
from .huggingface import HuggingFaceClient
from .hunter_io import HunterClient
from .jina_reader import JinaReader, JinaResult, get_jina_reader, read_url
from .mediastack import MediastackClient
from .news_api import NewsAPIClient
from .news_provider import (
    NewsArticle,
    NewsProvider,
    NewsProviderStatus,
    NewsResult,
    create_news_provider,
)
from .news_router import NewsArticle as NewsRouterArticle
from .news_router import NewsProvider as NewsRouterProvider
from .news_router import NewsQuality, NewsRouter
from .news_router import NewsSearchResult as NewsRouterSearchResult
from .news_router import get_news_router, smart_news_search, smart_news_search_sync
from .nominatim import NominatimClient
from .opencage import OpenCageClient
from .polygon import PolygonClient
from .reddit_client import RedditClient

# Result Cache (Cost Optimization)
from .result_cache import (
    CacheEntry,
    ResultCache,
    cache_classification,
    cache_financial,
    cache_news,
    cache_scrape,
    cache_search,
    cache_wikipedia,
    get_cached_classification,
    get_cached_financial,
    get_cached_news,
    get_cached_scrape,
    get_cached_search,
    get_cached_wikipedia,
    get_result_cache,
    print_cache_stats,
)
from .scrapegraph_client import ScrapeGraphClient
from .scraping_router import (
    ScrapeResult,
    ScrapingProvider,
    ScrapingQuality,
    ScrapingRouter,
    get_scraping_router,
    smart_scrape,
    smart_scrape_sync,
)
from .search_router import (
    SearchResponse,
    SearchResult,
    SearchRouter,
    free_search,
    get_search_router,
    smart_search,
)
from .sec_edgar import (
    SECCompany,
    SECEdgarClient,
    SECFiling,
    SECSearchResult,
    get_company_filings,
    get_sec_edgar,
    search_sec_filings,
)
from .serper_client import (
    SerperClient,
    SerperResponse,
    SerperResult,
    get_serper_client,
    serper_news,
    serper_search,
)
from .wikipedia_client import (
    WikipediaArticle,
    WikipediaClient,
    WikipediaInfobox,
    WikipediaSearchResult,
    get_company_summary,
    get_wikipedia_client,
)

# =============================================================================
# Unified Providers (Recommended)
# =============================================================================


# =============================================================================
# Financial Data Clients
# =============================================================================


# =============================================================================
# News Clients
# =============================================================================


# =============================================================================
# Company Data Clients
# =============================================================================


# =============================================================================
# Search & Scraping Clients
# =============================================================================


# =============================================================================
# FREE Alternatives (Cost Optimization)
# =============================================================================


# =============================================================================
# Geocoding Clients
# =============================================================================


# =============================================================================
# Regulatory & Research Clients
# =============================================================================


# =============================================================================
# ML/AI Clients
# =============================================================================


# =============================================================================
# Health Check
# =============================================================================


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Base
    "BaseAPIClient",
    "RateLimitError",
    "APIError",
    # Unified Providers
    "FinancialDataProvider",
    "FinancialData",
    "ProviderStatus",
    "ProviderState",
    "create_financial_provider",
    "NewsProvider",
    "NewsArticle",
    "NewsResult",
    "NewsProviderStatus",
    "create_news_provider",
    # Financial Clients
    "FMPClient",
    "CompanyProfile",
    "IncomeStatement",
    "BalanceSheet",
    "KeyMetrics",
    "DCFValue",
    "FinnhubClient",
    "PolygonClient",
    # News Clients
    "NewsAPIClient",
    "GNewsClient",
    "MediastackClient",
    # Company Data Clients
    "HunterClient",
    "DomainsDBClient",
    "GitHubClient",
    "RedditClient",
    # Search & Scraping (Paid)
    "FirecrawlClient",
    "ScrapeGraphClient",
    # FREE Alternatives (Cost Optimization)
    "Crawl4AIClient",
    "CrawlResult",
    "get_crawl4ai",
    "scrape_url_sync",
    "scrape_to_markdown",
    "JinaReader",
    "JinaResult",
    "get_jina_reader",
    "read_url",
    "GoogleNewsRSS",
    "GoogleNewsArticle",
    "GoogleNewsSearchResult",
    "get_google_news",
    "search_news",
    "WikipediaClient",
    "WikipediaArticle",
    "WikipediaInfobox",
    "WikipediaSearchResult",
    "get_wikipedia_client",
    "get_company_summary",
    "SearchRouter",
    "SearchResult",
    "SearchResponse",
    "get_search_router",
    "smart_search",
    "free_search",
    # Serper (10x cheaper than Tavily)
    "SerperClient",
    "SerperResult",
    "SerperResponse",
    "get_serper_client",
    "serper_search",
    "serper_news",
    # Cost Tracking
    "CostTracker",
    "ProviderCategory",
    "CostTier",
    "ProviderConfig",
    "UsageRecord",
    "CostAlert",
    "PROVIDER_CONFIGS",
    "get_cost_tracker",
    "track_cost",
    "get_daily_cost",
    "get_monthly_cost",
    "print_cost_summary",
    # Smart Routers (Free → Paid fallback)
    "ScrapingRouter",
    "ScrapingProvider",
    "ScrapingQuality",
    "ScrapeResult",
    "get_scraping_router",
    "smart_scrape",
    "smart_scrape_sync",
    "NewsRouter",
    "NewsRouterProvider",
    "NewsQuality",
    "NewsRouterArticle",
    "NewsRouterSearchResult",
    "get_news_router",
    "smart_news_search",
    "smart_news_search_sync",
    # Result Cache (Cost Optimization)
    "ResultCache",
    "CacheEntry",
    "get_result_cache",
    "cache_search",
    "get_cached_search",
    "cache_scrape",
    "get_cached_scrape",
    "cache_classification",
    "get_cached_classification",
    "cache_financial",
    "get_cached_financial",
    "cache_news",
    "get_cached_news",
    "cache_wikipedia",
    "get_cached_wikipedia",
    "print_cache_stats",
    # Geocoding
    "OpenCageClient",
    "NominatimClient",
    # Regulatory
    "SECEdgarClient",
    "SECCompany",
    "SECFiling",
    "SECSearchResult",
    "get_sec_edgar",
    "get_company_filings",
    "search_sec_filings",
    "CrunchbaseClient",
    # ML/AI
    "HuggingFaceClient",
    # Health Check
    "IntegrationHealthChecker",
    "IntegrationHealth",
    "HealthReport",
    "HealthStatus",
    "check_integration_health",
]
