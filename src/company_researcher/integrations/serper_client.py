"""
Serper.dev Integration - 10x Cheaper Than Tavily.

Google search results via API at $0.001/query ($50 for 50,000 queries).
High quality Google results at a fraction of Tavily's cost.

Features:
- Web search (Google results)
- News search
- Image search
- Places search
- Scholar search
- Cost tracking

Cost: $0.001/query ($50/50K queries)
Comparison: Tavily $0.005/query (5x more expensive)

Usage:
    from company_researcher.integrations.serper_client import get_serper_client

    serper = get_serper_client()

    # Web search
    results = serper.search("Tesla Q4 earnings 2024")

    # News search
    news = serper.search_news("Apple announcement")

    # Get cost stats
    stats = serper.get_stats()
"""

import os
import requests
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
import logging

logger = logging.getLogger(__name__)


SearchType = Literal["search", "news", "images", "places", "scholar"]


@dataclass
class SerperResult:
    """A single search result from Serper."""
    title: str
    link: str
    snippet: str
    position: int = 0
    date: Optional[str] = None
    source: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "position": self.position,
            "date": self.date,
            "source": self.source,
            "image_url": self.image_url
        }


@dataclass
class SerperResponse:
    """Response from Serper search."""
    query: str
    search_type: str
    results: List[SerperResult] = field(default_factory=list)
    answer_box: Optional[Dict[str, Any]] = None
    knowledge_graph: Optional[Dict[str, Any]] = None
    related_searches: List[str] = field(default_factory=list)
    credits_used: int = 1
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "search_type": self.search_type,
            "results": [r.to_dict() for r in self.results],
            "answer_box": self.answer_box,
            "knowledge_graph": self.knowledge_graph,
            "related_searches": self.related_searches,
            "credits_used": self.credits_used,
            "success": self.success,
            "error": self.error
        }


class SerperClient:
    """
    Serper.dev API client - Google search at 10x lower cost than Tavily.

    Pricing: $50 for 50,000 queries = $0.001/query
    """

    BASE_URL = "https://google.serper.dev"

    # Cost per query in USD
    COST_PER_QUERY = 0.001

    # Endpoint mapping
    ENDPOINTS = {
        "search": "/search",
        "news": "/news",
        "images": "/images",
        "places": "/places",
        "scholar": "/scholar",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 10,
        default_country: str = "us",
        default_language: str = "en"
    ):
        """
        Initialize Serper client.

        Args:
            api_key: Serper API key (or set SERPER_API_KEY env var)
            timeout: Request timeout in seconds
            default_country: Default country code for results
            default_language: Default language for results
        """
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.timeout = timeout
        self.default_country = default_country
        self.default_language = default_language

        if not self.api_key:
            logger.warning("Serper API key not configured. Set SERPER_API_KEY environment variable.")

        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        # Usage tracking
        self._total_queries = 0
        self._total_cost = 0.0
        self._queries_by_type: Dict[str, int] = {}
        self._lock = Lock()

    def _make_request(
        self,
        search_type: SearchType,
        query: str,
        num_results: int = 10,
        country: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> SerperResponse:
        """Make request to Serper API."""
        if not self.api_key:
            return SerperResponse(
                query=query,
                search_type=search_type,
                success=False,
                error="Serper API key not configured"
            )

        try:
            endpoint = self.ENDPOINTS.get(search_type, "/search")
            url = f"{self.BASE_URL}{endpoint}"

            payload = {
                "q": query,
                "num": num_results,
                "gl": country or self.default_country,
                "hl": language or self.default_language,
            }

            # Add any additional parameters
            payload.update(kwargs)

            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            # Parse results based on search type
            results = []

            if search_type == "search":
                organic = data.get("organic", [])
                for i, item in enumerate(organic):
                    results.append(SerperResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        position=item.get("position", i + 1),
                        date=item.get("date"),
                    ))

            elif search_type == "news":
                news = data.get("news", [])
                for i, item in enumerate(news):
                    results.append(SerperResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        position=i + 1,
                        date=item.get("date"),
                        source=item.get("source"),
                        image_url=item.get("imageUrl"),
                    ))

            elif search_type == "images":
                images = data.get("images", [])
                for i, item in enumerate(images):
                    results.append(SerperResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet="",
                        position=i + 1,
                        image_url=item.get("imageUrl"),
                    ))

            elif search_type == "places":
                places = data.get("places", [])
                for i, item in enumerate(places):
                    results.append(SerperResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("address", ""),
                        position=i + 1,
                    ))

            elif search_type == "scholar":
                organic = data.get("organic", [])
                for i, item in enumerate(organic):
                    results.append(SerperResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        position=i + 1,
                        date=item.get("year"),
                    ))

            # Extract additional data
            answer_box = data.get("answerBox")
            knowledge_graph = data.get("knowledgeGraph")
            related_searches = [
                item.get("query", "")
                for item in data.get("relatedSearches", [])
            ]

            # Track usage
            with self._lock:
                self._total_queries += 1
                self._total_cost += self.COST_PER_QUERY
                self._queries_by_type[search_type] = self._queries_by_type.get(search_type, 0) + 1

            return SerperResponse(
                query=query,
                search_type=search_type,
                results=results,
                answer_box=answer_box,
                knowledge_graph=knowledge_graph,
                related_searches=related_searches,
                credits_used=1,
                success=True
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Serper request error for '{query}': {e}")
            return SerperResponse(
                query=query,
                search_type=search_type,
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Serper error for '{query}': {e}")
            return SerperResponse(
                query=query,
                search_type=search_type,
                success=False,
                error=str(e)
            )

    def search(
        self,
        query: str,
        num_results: int = 10,
        country: Optional[str] = None,
        language: Optional[str] = None
    ) -> SerperResponse:
        """
        Perform web search.

        Args:
            query: Search query
            num_results: Number of results (max 100)
            country: Country code (e.g., 'us', 'uk', 'de')
            language: Language code (e.g., 'en', 'es', 'de')

        Returns:
            SerperResponse with search results
        """
        return self._make_request(
            "search",
            query,
            num_results=min(num_results, 100),
            country=country,
            language=language
        )

    def search_news(
        self,
        query: str,
        num_results: int = 10,
        country: Optional[str] = None,
        language: Optional[str] = None
    ) -> SerperResponse:
        """
        Search news articles.

        Args:
            query: Search query
            num_results: Number of results
            country: Country code
            language: Language code

        Returns:
            SerperResponse with news results
        """
        return self._make_request(
            "news",
            query,
            num_results=min(num_results, 100),
            country=country,
            language=language
        )

    def search_images(
        self,
        query: str,
        num_results: int = 10,
        country: Optional[str] = None
    ) -> SerperResponse:
        """
        Search images.

        Args:
            query: Search query
            num_results: Number of results
            country: Country code

        Returns:
            SerperResponse with image results
        """
        return self._make_request(
            "images",
            query,
            num_results=min(num_results, 100),
            country=country
        )

    def search_places(
        self,
        query: str,
        num_results: int = 10,
        country: Optional[str] = None
    ) -> SerperResponse:
        """
        Search places/local businesses.

        Args:
            query: Search query (e.g., "coffee shops near me")
            num_results: Number of results
            country: Country code

        Returns:
            SerperResponse with place results
        """
        return self._make_request(
            "places",
            query,
            num_results=min(num_results, 20),
            country=country
        )

    def search_scholar(
        self,
        query: str,
        num_results: int = 10
    ) -> SerperResponse:
        """
        Search academic papers (Google Scholar).

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            SerperResponse with scholar results
        """
        return self._make_request(
            "scholar",
            query,
            num_results=min(num_results, 100)
        )

    def search_company(
        self,
        company_name: str,
        search_type: str = "general",
        num_results: int = 10
    ) -> SerperResponse:
        """
        Search for company information.

        Args:
            company_name: Company name
            search_type: Type of search (general, financials, news, competitors)
            num_results: Number of results

        Returns:
            SerperResponse with company results
        """
        query_templates = {
            "general": f'"{company_name}" company overview',
            "financials": f'"{company_name}" financials revenue earnings annual report',
            "news": f'"{company_name}" news latest',
            "competitors": f'"{company_name}" competitors market share',
            "products": f'"{company_name}" products services',
            "leadership": f'"{company_name}" CEO executives leadership team',
            "stock": f'"{company_name}" stock price ticker symbol',
        }

        query = query_templates.get(search_type, f'"{company_name}"')

        if search_type == "news":
            return self.search_news(query, num_results)
        else:
            return self.search(query, num_results)

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_queries": self._total_queries,
                "total_cost": round(self._total_cost, 4),
                "cost_per_query": self.COST_PER_QUERY,
                "queries_by_type": self._queries_by_type.copy(),
                "api_configured": bool(self.api_key)
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_queries = 0
            self._total_cost = 0.0
            self._queries_by_type.clear()

    @property
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)


# Singleton instance
_serper_client: Optional[SerperClient] = None
_client_lock = Lock()


def get_serper_client(api_key: Optional[str] = None) -> SerperClient:
    """Get singleton Serper client instance."""
    global _serper_client
    if _serper_client is None:
        with _client_lock:
            if _serper_client is None:
                _serper_client = SerperClient(api_key=api_key)
    return _serper_client


def reset_serper_client() -> None:
    """Reset Serper client instance."""
    global _serper_client
    _serper_client = None


# Convenience functions
def serper_search(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function to search via Serper."""
    client = get_serper_client()
    result = client.search(query, num_results)
    return [r.to_dict() for r in result.results] if result.success else []


def serper_news(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function to search news via Serper."""
    client = get_serper_client()
    result = client.search_news(query, num_results)
    return [r.to_dict() for r in result.results] if result.success else []
