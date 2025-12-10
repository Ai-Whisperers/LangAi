"""
Mediastack News API Client.

Free tier: 500 requests/month (15-min delay)
Provides: Live news from 7,500+ sources in 50+ countries

Documentation: https://mediastack.com/documentation
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class MediastackArticle:
    """News article from Mediastack."""
    author: Optional[str]
    title: str
    description: str
    url: str
    source: str
    image: Optional[str]
    category: str
    language: str
    country: str
    published_at: str

    @classmethod
    def from_dict(cls, data: Dict) -> "MediastackArticle":
        return cls(
            author=data.get("author"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            source=data.get("source", ""),
            image=data.get("image"),
            category=data.get("category", ""),
            language=data.get("language", ""),
            country=data.get("country", ""),
            published_at=data.get("published_at", "")
        )


class MediastackClient(BaseAPIClient):
    """
    Mediastack News API Client.

    Free tier: 500 requests/month, 15-min delay
    Basic: $12.99/mo (10,000 requests)
    Standard: $49.99/mo (50,000 requests)

    Features:
    - Live news from 7,500+ sources
    - 50+ countries
    - Category filtering
    - Historical news (paid only)
    """

    BASE_URL = "http://api.mediastack.com/v1"  # Note: HTTP for free tier

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="MEDIASTACK_API_KEY",
            cache_ttl=900,  # 15 min cache matches delay
            rate_limit_calls=500,
            rate_limit_period=2592000.0  # Monthly limit
        )

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ):
        """Override to add API key to all requests."""
        params = params or {}
        params["access_key"] = self.api_key
        return await super()._request(endpoint, params, **kwargs)

    async def get_live_news(
        self,
        keywords: Optional[str] = None,
        sources: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> List[MediastackArticle]:
        """
        Get live news articles.

        Args:
            keywords: Search keywords
            sources: List of source domains (e.g., ["cnn", "bbc"])
            categories: Categories (general, business, technology, etc.)
            countries: Country codes (us, gb, de, etc.)
            languages: Language codes (en, es, de, etc.)
            limit: Max results (1-100)
            offset: Pagination offset

        Returns:
            List of MediastackArticle objects

        Categories:
            - general, business, technology, science
            - health, sports, entertainment
        """
        params = {
            "limit": min(limit, 100),
            "offset": offset
        }

        if keywords:
            params["keywords"] = keywords
        if sources:
            params["sources"] = ",".join(sources)
        if categories:
            params["categories"] = ",".join(categories)
        if countries:
            params["countries"] = ",".join(countries)
        if languages:
            params["languages"] = ",".join(languages)

        data = await self._request("news", params)
        articles = data.get("data", []) if data else []
        return [MediastackArticle.from_dict(article) for article in articles]

    async def get_business_news(
        self,
        countries: Optional[List[str]] = None,
        limit: int = 25
    ) -> List[MediastackArticle]:
        """
        Get business news.

        Args:
            countries: Country codes to filter
            limit: Max results

        Returns:
            List of MediastackArticle objects
        """
        return await self.get_live_news(
            categories=["business"],
            countries=countries,
            limit=limit
        )

    async def get_tech_news(
        self,
        countries: Optional[List[str]] = None,
        limit: int = 25
    ) -> List[MediastackArticle]:
        """
        Get technology news.

        Args:
            countries: Country codes to filter
            limit: Max results

        Returns:
            List of MediastackArticle objects
        """
        return await self.get_live_news(
            categories=["technology"],
            countries=countries,
            limit=limit
        )

    async def search_news(
        self,
        keywords: str,
        categories: Optional[List[str]] = None,
        limit: int = 25
    ) -> List[MediastackArticle]:
        """
        Search for news by keywords.

        Args:
            keywords: Search keywords
            categories: Optional category filter
            limit: Max results

        Returns:
            List of MediastackArticle objects
        """
        return await self.get_live_news(
            keywords=keywords,
            categories=categories,
            limit=limit
        )

    async def get_company_news(
        self,
        company_name: str,
        limit: int = 20
    ) -> List[MediastackArticle]:
        """
        Get news about a company.

        Args:
            company_name: Company name to search
            limit: Max results

        Returns:
            List of MediastackArticle objects
        """
        return await self.search_news(
            keywords=company_name,
            categories=["business", "technology"],
            limit=limit
        )
