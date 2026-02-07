"""
Cost Tracking Data Models and Provider Configurations.

This module contains:
- ProviderCategory enum
- CostTier enum
- ProviderConfig dataclass
- PROVIDER_CONFIGS dictionary (40+ providers)
- UsageRecord, DailyUsage, CostAlert dataclasses
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class ProviderCategory(str, Enum):
    """Categories of API providers."""

    LLM = "llm"
    SEARCH = "search"
    SCRAPING = "scraping"
    NEWS = "news"
    FINANCIAL = "financial"
    GEOCODING = "geocoding"
    COMPANY_DATA = "company_data"


class CostTier(str, Enum):
    """Cost tiers for providers."""

    FREE = "free"  # $0/query
    CHEAP = "cheap"  # <$0.001/query
    STANDARD = "standard"  # $0.001-$0.01/query
    PREMIUM = "premium"  # >$0.01/query


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""

    name: str
    category: ProviderCategory
    tier: CostTier
    cost_per_unit: float  # Cost per request/token/query
    unit_type: str  # "request", "1k_tokens", "query"
    free_tier_limit: int = 0  # Free tier limit per month
    rate_limit: int = 0  # Requests per minute
    is_enabled: bool = True


# Provider cost configurations
PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    # LLM Providers
    "claude-3-5-sonnet": ProviderConfig(
        name="Claude 3.5 Sonnet",
        category=ProviderCategory.LLM,
        tier=CostTier.PREMIUM,
        cost_per_unit=0.015,  # $15/1M tokens avg (input + output)
        unit_type="1k_tokens",
    ),
    "claude-3-haiku": ProviderConfig(
        name="Claude 3 Haiku",
        category=ProviderCategory.LLM,
        tier=CostTier.STANDARD,
        cost_per_unit=0.00125,  # $1.25/1M tokens
        unit_type="1k_tokens",
    ),
    "gpt-4o": ProviderConfig(
        name="GPT-4o",
        category=ProviderCategory.LLM,
        tier=CostTier.PREMIUM,
        cost_per_unit=0.015,
        unit_type="1k_tokens",
    ),
    "gpt-4o-mini": ProviderConfig(
        name="GPT-4o Mini",
        category=ProviderCategory.LLM,
        tier=CostTier.CHEAP,
        cost_per_unit=0.00015,  # $0.15/1M tokens
        unit_type="1k_tokens",
    ),
    "deepseek-chat": ProviderConfig(
        name="DeepSeek Chat",
        category=ProviderCategory.LLM,
        tier=CostTier.CHEAP,
        cost_per_unit=0.00014,  # $0.14/1M tokens
        unit_type="1k_tokens",
    ),
    "gemini-1.5-flash": ProviderConfig(
        name="Gemini 1.5 Flash",
        category=ProviderCategory.LLM,
        tier=CostTier.CHEAP,
        cost_per_unit=0.000075,  # $0.075/1M tokens
        unit_type="1k_tokens",
    ),
    "gemini-1.5-pro": ProviderConfig(
        name="Gemini 1.5 Pro",
        category=ProviderCategory.LLM,
        tier=CostTier.STANDARD,
        cost_per_unit=0.00125,  # $1.25/1M tokens
        unit_type="1k_tokens",
    ),
    "groq-llama-70b": ProviderConfig(
        name="Groq Llama 70B",
        category=ProviderCategory.LLM,
        tier=CostTier.CHEAP,
        cost_per_unit=0.00059,  # $0.59/1M tokens
        unit_type="1k_tokens",
    ),
    "groq-llama-8b": ProviderConfig(
        name="Groq Llama 8B",
        category=ProviderCategory.LLM,
        tier=CostTier.CHEAP,
        cost_per_unit=0.00005,  # $0.05/1M tokens
        unit_type="1k_tokens",
    ),
    # Search Providers
    "tavily": ProviderConfig(
        name="Tavily",
        category=ProviderCategory.SEARCH,
        tier=CostTier.STANDARD,
        cost_per_unit=0.005,  # ~$0.005/query
        unit_type="query",
        free_tier_limit=1000,  # 1000 free queries/month
    ),
    "serper": ProviderConfig(
        name="Serper.dev",
        category=ProviderCategory.SEARCH,
        tier=CostTier.CHEAP,
        cost_per_unit=0.001,  # $0.001/query
        unit_type="query",
    ),
    "duckduckgo": ProviderConfig(
        name="DuckDuckGo",
        category=ProviderCategory.SEARCH,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="query",
        rate_limit=30,  # ~30/min to avoid blocks
    ),
    # Scraping Providers
    "firecrawl": ProviderConfig(
        name="Firecrawl",
        category=ProviderCategory.SCRAPING,
        tier=CostTier.PREMIUM,
        cost_per_unit=0.01,  # ~$0.01/page
        unit_type="page",
        free_tier_limit=500,  # 500 free credits/month
    ),
    "scrapegraph": ProviderConfig(
        name="ScrapeGraph",
        category=ProviderCategory.SCRAPING,
        tier=CostTier.PREMIUM,
        cost_per_unit=0.01,
        unit_type="page",
    ),
    "crawl4ai": ProviderConfig(
        name="Crawl4AI",
        category=ProviderCategory.SCRAPING,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="page",
    ),
    "jina-reader": ProviderConfig(
        name="Jina Reader",
        category=ProviderCategory.SCRAPING,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="page",
        free_tier_limit=1000000,  # 1M tokens/month free
    ),
    # News Providers
    "newsapi": ProviderConfig(
        name="NewsAPI",
        category=ProviderCategory.NEWS,
        tier=CostTier.STANDARD,
        cost_per_unit=0.003,  # ~$0.003/request
        unit_type="request",
        free_tier_limit=100,  # 100/day dev only
    ),
    "gnews": ProviderConfig(
        name="GNews",
        category=ProviderCategory.NEWS,
        tier=CostTier.STANDARD,
        cost_per_unit=0.003,
        unit_type="request",
        free_tier_limit=100,  # 100/day
    ),
    "mediastack": ProviderConfig(
        name="Mediastack",
        category=ProviderCategory.NEWS,
        tier=CostTier.STANDARD,
        cost_per_unit=0.002,
        unit_type="request",
        free_tier_limit=500,  # 500/month
    ),
    "google-news-rss": ProviderConfig(
        name="Google News RSS",
        category=ProviderCategory.NEWS,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="request",
    ),
    # Financial Providers
    "fmp": ProviderConfig(
        name="Financial Modeling Prep",
        category=ProviderCategory.FINANCIAL,
        tier=CostTier.STANDARD,
        cost_per_unit=0.004,
        unit_type="request",
        free_tier_limit=250,  # 250/day
    ),
    "finnhub": ProviderConfig(
        name="Finnhub",
        category=ProviderCategory.FINANCIAL,
        tier=CostTier.STANDARD,
        cost_per_unit=0.0,  # Free tier
        unit_type="request",
        free_tier_limit=60,  # 60/min
        rate_limit=60,
    ),
    "polygon": ProviderConfig(
        name="Polygon.io",
        category=ProviderCategory.FINANCIAL,
        tier=CostTier.STANDARD,
        cost_per_unit=0.0,
        unit_type="request",
        free_tier_limit=5,  # 5/min
        rate_limit=5,
    ),
    "yfinance": ProviderConfig(
        name="Yahoo Finance",
        category=ProviderCategory.FINANCIAL,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="request",
    ),
    "sec-edgar": ProviderConfig(
        name="SEC EDGAR",
        category=ProviderCategory.FINANCIAL,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="request",
        rate_limit=10,  # Be nice to SEC
    ),
    # Company Data
    "hunter-io": ProviderConfig(
        name="Hunter.io",
        category=ProviderCategory.COMPANY_DATA,
        tier=CostTier.STANDARD,
        cost_per_unit=0.04,  # ~$0.04/search
        unit_type="search",
        free_tier_limit=25,  # 25/month
    ),
    "wikipedia": ProviderConfig(
        name="Wikipedia",
        category=ProviderCategory.COMPANY_DATA,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="request",
    ),
    # Geocoding
    "opencage": ProviderConfig(
        name="OpenCage",
        category=ProviderCategory.GEOCODING,
        tier=CostTier.STANDARD,
        cost_per_unit=0.0004,
        unit_type="request",
        free_tier_limit=2500,  # 2500/day
    ),
    "nominatim": ProviderConfig(
        name="Nominatim",
        category=ProviderCategory.GEOCODING,
        tier=CostTier.FREE,
        cost_per_unit=0.0,
        unit_type="request",
        rate_limit=1,  # 1/sec
    ),
}


@dataclass
class UsageRecord:
    """Single usage record."""

    provider: str
    category: str
    timestamp: datetime
    units: float
    cost: float
    metadata: dict = field(default_factory=dict)


@dataclass
class DailyUsage:
    """Daily usage summary."""

    date: str
    total_cost: float
    by_category: dict[str, float]
    by_provider: dict[str, float]
    request_count: int


@dataclass
class CostAlert:
    """Cost alert configuration."""

    name: str
    threshold: float
    category: Optional[ProviderCategory] = None
    provider: Optional[str] = None
    period: str = "daily"  # "daily", "monthly", "total"
    callback: Optional[Callable[[float, float], None]] = None
