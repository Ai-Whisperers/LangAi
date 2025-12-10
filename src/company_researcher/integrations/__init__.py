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
from .base_client import BaseAPIClient, RateLimitError, APIError

# =============================================================================
# Unified Providers (Recommended)
# =============================================================================

from .financial_provider import (
    FinancialDataProvider,
    FinancialData,
    ProviderStatus,
    ProviderState,
    create_financial_provider,
)

from .news_provider import (
    NewsProvider,
    NewsArticle,
    NewsResult,
    NewsProviderStatus,
    create_news_provider,
)

# =============================================================================
# Financial Data Clients
# =============================================================================

from .financial_modeling_prep import (
    FMPClient,
    CompanyProfile,
    IncomeStatement,
    BalanceSheet,
    KeyMetrics,
    DCFValue,
)

from .finnhub import (
    FinnhubClient,
)

from .polygon import (
    PolygonClient,
)

# =============================================================================
# News Clients
# =============================================================================

from .news_api import (
    NewsAPIClient,
)

from .gnews import (
    GNewsClient,
)

from .mediastack import (
    MediastackClient,
)

# =============================================================================
# Company Data Clients
# =============================================================================

from .hunter_io import (
    HunterClient,
)

from .domainsdb import (
    DomainsDBClient,
)

from .github_client import (
    GitHubClient,
)

from .reddit_client import (
    RedditClient,
)

# =============================================================================
# Search & Scraping Clients
# =============================================================================

from .firecrawl_client import (
    FirecrawlClient,
)

from .scrapegraph_client import (
    ScrapeGraphClient,
)

# =============================================================================
# FREE Alternatives (Cost Optimization)
# =============================================================================

from .crawl4ai_client import (
    Crawl4AIClient,
    CrawlResult,
    get_crawl4ai,
    scrape_url_sync,
    scrape_to_markdown,
)

from .jina_reader import (
    JinaReader,
    JinaResult,
    get_jina_reader,
    read_url,
)

from .google_news_rss import (
    GoogleNewsRSS,
    NewsArticle as GoogleNewsArticle,
    NewsSearchResult as GoogleNewsSearchResult,
    get_google_news,
    search_news,
)

from .wikipedia_client import (
    WikipediaClient,
    WikipediaArticle,
    WikipediaInfobox,
    WikipediaSearchResult,
    get_wikipedia_client,
    get_company_summary,
)

from .search_router import (
    SearchRouter,
    SearchResult,
    SearchResponse,
    get_search_router,
    smart_search,
    free_search,
)

from .serper_client import (
    SerperClient,
    SerperResult,
    SerperResponse,
    get_serper_client,
    serper_search,
    serper_news,
)

from .cost_tracker import (
    CostTracker,
    ProviderCategory,
    CostTier,
    ProviderConfig,
    UsageRecord,
    CostAlert,
    PROVIDER_CONFIGS,
    get_cost_tracker,
    track_cost,
    get_daily_cost,
    get_monthly_cost,
    print_cost_summary,
)

from .scraping_router import (
    ScrapingRouter,
    ScrapingProvider,
    ScrapingQuality,
    ScrapeResult,
    get_scraping_router,
    smart_scrape,
    smart_scrape_sync,
)

from .news_router import (
    NewsRouter,
    NewsProvider as NewsRouterProvider,
    NewsQuality,
    NewsArticle as NewsRouterArticle,
    NewsSearchResult as NewsRouterSearchResult,
    get_news_router,
    smart_news_search,
    smart_news_search_sync,
)

# Result Cache (Cost Optimization)
from .result_cache import (
    ResultCache,
    CacheEntry,
    get_result_cache,
    cache_search,
    get_cached_search,
    cache_scrape,
    get_cached_scrape,
    cache_classification,
    get_cached_classification,
    cache_financial,
    get_cached_financial,
    cache_news,
    get_cached_news,
    cache_wikipedia,
    get_cached_wikipedia,
    print_cache_stats,
)

# =============================================================================
# Geocoding Clients
# =============================================================================

from .opencage import (
    OpenCageClient,
)

from .nominatim import (
    NominatimClient,
)

# =============================================================================
# Regulatory & Research Clients
# =============================================================================

from .sec_edgar import (
    SECEdgarClient,
    SECCompany,
    SECFiling,
    SECSearchResult,
    get_sec_edgar,
    get_company_filings,
    search_sec_filings,
)

from .crunchbase import (
    CrunchbaseClient,
)

# =============================================================================
# ML/AI Clients
# =============================================================================

from .huggingface import (
    HuggingFaceClient,
)

# =============================================================================
# Health Check
# =============================================================================

from .health_check import (
    IntegrationHealthChecker,
    IntegrationHealth,
    HealthReport,
    HealthStatus,
    check_integration_health,
)

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
