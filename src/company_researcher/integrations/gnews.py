"""
GNews API Client.

Free tier: 100 requests/day
Provides: News articles from 60,000+ sources worldwide

Documentation: https://gnews.io/docs/
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class GNewsArticle:
    """News article from GNews."""
    title: str
    description: str
    content: str
    url: str
    image: Optional[str]
    published_at: str
    source_name: str
    source_url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "GNewsArticle":
        source = data.get("source", {})
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            content=data.get("content", ""),
            url=data.get("url", ""),
            image=data.get("image"),
            published_at=data.get("publishedAt", ""),
            source_name=source.get("name", ""),
            source_url=source.get("url", "")
        )


class GNewsClient(BaseAPIClient):
    """
    GNews API Client.

    Free tier: 100 requests/day
    Basic: $29/mo (1,000 req/day)
    Pro: $79/mo (10,000 req/day)

    Features:
    - Search news articles
    - Top headlines by topic/country
    - 60,000+ sources worldwide
    - Multiple languages
    """

    BASE_URL = "https://gnews.io/api/v4"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="GNEWS_API_KEY",
            cache_ttl=1800,  # 30 min cache for news
            rate_limit_calls=100,
            rate_limit_period=86400.0  # Daily limit
        )

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ):
        """Override to add API key to all requests."""
        params = params or {}
        params["apikey"] = self.api_key
        return await super()._request(endpoint, params, **kwargs)

    async def search(
        self,
        query: str,
        lang: str = "en",
        country: Optional[str] = None,
        max_results: int = 10,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        sort_by: str = "publishedAt"
    ) -> List[GNewsArticle]:
        """
        Search for news articles.

        Args:
            query: Search query (supports AND, OR, NOT, exact phrases)
            lang: Language code (en, es, fr, de, etc.)
            country: Country code (us, gb, ca, etc.)
            max_results: Max articles to return (1-100)
            from_date: Start date (YYYY-MM-DDThh:mm:ssZ)
            to_date: End date (YYYY-MM-DDThh:mm:ssZ)
            sort_by: Sort order (publishedAt, relevance)

        Returns:
            List of GNewsArticle objects

        Query operators:
            - AND: "apple AND iphone"
            - OR: "apple OR google"
            - NOT: "apple NOT fruit"
            - Exact phrase: '"company name"'
            - Exclude: -word
        """
        params = {
            "q": query,
            "lang": lang,
            "max": min(max_results, 100),
            "sortby": sort_by
        }

        if country:
            params["country"] = country
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = await self._request("search", params)
        articles = data.get("articles", []) if data else []
        return [GNewsArticle.from_dict(article) for article in articles]

    async def get_top_headlines(
        self,
        topic: Optional[str] = None,
        country: str = "us",
        lang: str = "en",
        max_results: int = 10
    ) -> List[GNewsArticle]:
        """
        Get top headlines by topic.

        Args:
            topic: Topic (business, technology, science, health, sports, entertainment)
            country: Country code (us, gb, ca, etc.)
            lang: Language code
            max_results: Max articles

        Returns:
            List of GNewsArticle objects
        """
        params = {
            "country": country,
            "lang": lang,
            "max": min(max_results, 100)
        }

        if topic:
            params["topic"] = topic

        data = await self._request("top-headlines", params)
        articles = data.get("articles", []) if data else []
        return [GNewsArticle.from_dict(article) for article in articles]

    async def get_company_news(
        self,
        company_name: str,
        days_back: int = 7,
        max_results: int = 20,
        lang: str = "en"
    ) -> List[GNewsArticle]:
        """
        Get recent news about a company.

        Args:
            company_name: Company name to search
            days_back: Number of days to look back
            max_results: Max articles to return
            lang: Language code

        Returns:
            List of GNewsArticle objects
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")

        return await self.search(
            query=f'"{company_name}"',
            lang=lang,
            from_date=from_date,
            max_results=max_results,
            sort_by="relevance"
        )

    async def get_business_headlines(
        self,
        country: str = "us",
        max_results: int = 10
    ) -> List[GNewsArticle]:
        """
        Get business news headlines.

        Args:
            country: Country code
            max_results: Max articles

        Returns:
            List of GNewsArticle objects
        """
        return await self.get_top_headlines(
            topic="business",
            country=country,
            max_results=max_results
        )

    async def get_tech_headlines(
        self,
        country: str = "us",
        max_results: int = 10
    ) -> List[GNewsArticle]:
        """
        Get technology news headlines.

        Args:
            country: Country code
            max_results: Max articles

        Returns:
            List of GNewsArticle objects
        """
        return await self.get_top_headlines(
            topic="technology",
            country=country,
            max_results=max_results
        )
