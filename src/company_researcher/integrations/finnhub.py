"""
Finnhub Stock API Client.

Free tier: 60 API calls/minute
Provides: Real-time quotes, fundamentals, news, sentiment

Documentation: https://finnhub.io/docs/api
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional

from .base_client import BaseAPIClient
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class CompanyNews:
    """News article for a company."""
    category: str
    datetime: int
    headline: str
    id: int
    image: str
    related: str
    source: str
    summary: str
    url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "CompanyNews":
        return cls(
            category=data.get("category", ""),
            datetime=data.get("datetime", 0),
            headline=data.get("headline", ""),
            id=data.get("id", 0),
            image=data.get("image", ""),
            related=data.get("related", ""),
            source=data.get("source", ""),
            summary=data.get("summary", ""),
            url=data.get("url", "")
        )


@dataclass
class Quote:
    """Stock quote data."""
    current_price: float
    change: float
    percent_change: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: int

    @classmethod
    def from_dict(cls, data: Dict) -> "Quote":
        return cls(
            current_price=data.get("c", 0),
            change=data.get("d", 0),
            percent_change=data.get("dp", 0),
            high=data.get("h", 0),
            low=data.get("l", 0),
            open=data.get("o", 0),
            previous_close=data.get("pc", 0),
            timestamp=data.get("t", 0)
        )


@dataclass
class CompanyProfile:
    """Company profile from Finnhub."""
    country: str
    currency: str
    exchange: str
    ipo: str
    market_cap: float
    name: str
    phone: str
    shares_outstanding: float
    ticker: str
    weburl: str
    logo: str
    industry: str

    @classmethod
    def from_dict(cls, data: Dict) -> "CompanyProfile":
        return cls(
            country=data.get("country", ""),
            currency=data.get("currency", ""),
            exchange=data.get("exchange", ""),
            ipo=data.get("ipo", ""),
            market_cap=data.get("marketCapitalization", 0),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            shares_outstanding=data.get("shareOutstanding", 0),
            ticker=data.get("ticker", ""),
            weburl=data.get("weburl", ""),
            logo=data.get("logo", ""),
            industry=data.get("finnhubIndustry", "")
        )


class FinnhubClient(BaseAPIClient):
    """
    Finnhub Stock API Client.

    Free tier: 60 API calls/minute
    Rate limit enforced by client.

    Features:
    - Real-time stock quotes
    - Company profiles
    - Company news
    - News sentiment
    - Social sentiment (Reddit, Twitter)
    - Basic financials/metrics
    - Earnings calendar
    - Stock peers
    - Analyst recommendations
    - Price targets
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="FINNHUB_API_KEY",
            cache_ttl=300,  # 5 min cache for real-time data
            rate_limit_calls=60,
            rate_limit_period=60.0
        )

    def _get_headers(self) -> Dict[str, str]:
        """Add API key to headers."""
        headers = super()._get_headers()
        if self.api_key:
            headers["X-Finnhub-Token"] = self.api_key
        return headers

    # =========================================================================
    # Quote & Price
    # =========================================================================

    async def get_quote(self, symbol: str) -> Quote:
        """
        Get real-time stock quote.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Quote object with price data
        """
        data = await self._request("quote", {"symbol": symbol})
        return Quote.from_dict(data)

    # =========================================================================
    # Company Info
    # =========================================================================

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """
        Get company profile.

        Args:
            symbol: Stock ticker symbol

        Returns:
            CompanyProfile or None
        """
        data = await self._request("stock/profile2", {"symbol": symbol})
        if data:
            return CompanyProfile.from_dict(data)
        return None

    async def get_peers(self, symbol: str) -> List[str]:
        """
        Get company peers/competitors.

        Args:
            symbol: Stock ticker symbol

        Returns:
            List of peer ticker symbols
        """
        return await self._request("stock/peers", {"symbol": symbol}) or []

    # =========================================================================
    # News
    # =========================================================================

    async def get_company_news(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[CompanyNews]:
        """
        Get company news in date range.

        Args:
            symbol: Stock ticker symbol
            from_date: Start date (YYYY-MM-DD), defaults to 7 days ago
            to_date: End date (YYYY-MM-DD), defaults to today

        Returns:
            List of CompanyNews objects
        """
        if not from_date:
            from_date = (utc_now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = utc_now().strftime("%Y-%m-%d")

        data = await self._request("company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        return [CompanyNews.from_dict(item) for item in (data or [])]

    async def get_market_news(self, category: str = "general") -> List[Dict]:
        """
        Get market news by category.

        Args:
            category: News category (general, forex, crypto, merger)

        Returns:
            List of news article dicts
        """
        return await self._request("news", {"category": category}) or []

    # =========================================================================
    # Sentiment
    # =========================================================================

    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get news sentiment analysis.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with sentiment scores and article analysis
        """
        return await self._request("news-sentiment", {"symbol": symbol}) or {}

    async def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get social media sentiment (Reddit, Twitter).

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with social sentiment data
        """
        return await self._request("stock/social-sentiment", {"symbol": symbol}) or {}

    # =========================================================================
    # Fundamentals
    # =========================================================================

    async def get_basic_financials(
        self,
        symbol: str,
        metric: str = "all"
    ) -> Dict[str, Any]:
        """
        Get basic financial metrics.

        Args:
            symbol: Stock ticker symbol
            metric: Metric type ("all", "price", "valuation", "margin")

        Returns:
            Dict with metric data and series
        """
        return await self._request("stock/metric", {
            "symbol": symbol,
            "metric": metric
        }) or {}

    # =========================================================================
    # Earnings
    # =========================================================================

    async def get_earnings_calendar(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """
        Get earnings calendar.

        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            symbol: Filter by symbol (optional)

        Returns:
            List of earnings events
        """
        if not from_date:
            from_date = utc_now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (utc_now() + timedelta(days=30)).strftime("%Y-%m-%d")

        params = {"from": from_date, "to": to_date}
        if symbol:
            params["symbol"] = symbol

        data = await self._request("calendar/earnings", params)
        return data.get("earningsCalendar", []) if data else []

    # =========================================================================
    # Analyst Data
    # =========================================================================

    async def get_recommendations(self, symbol: str) -> List[Dict]:
        """
        Get analyst recommendations.

        Args:
            symbol: Stock ticker symbol

        Returns:
            List of recommendation dicts with buy/hold/sell counts
        """
        return await self._request("stock/recommendation", {"symbol": symbol}) or []

    async def get_price_target(self, symbol: str) -> Dict[str, Any]:
        """
        Get analyst price targets.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with target high, low, mean, median
        """
        return await self._request("stock/price-target", {"symbol": symbol}) or {}

    # =========================================================================
    # Search
    # =========================================================================

    async def search_symbol(self, query: str) -> List[Dict]:
        """
        Search for stock symbols.

        Args:
            query: Search query

        Returns:
            List of matching symbols with descriptions
        """
        data = await self._request("search", {"q": query})
        return data.get("result", []) if data else []

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive company overview with all available data.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with profile, quote, news, sentiment, and recommendations
        """
        result = {
            "symbol": symbol,
            "profile": None,
            "quote": None,
            "news": [],
            "sentiment": {},
            "social_sentiment": {},
            "financials": {},
            "recommendations": [],
            "price_target": {},
            "peers": []
        }

        result["profile"] = await self.get_company_profile(symbol)
        result["quote"] = await self.get_quote(symbol)
        result["news"] = await self.get_company_news(symbol)
        result["sentiment"] = await self.get_news_sentiment(symbol)
        result["social_sentiment"] = await self.get_social_sentiment(symbol)
        result["financials"] = await self.get_basic_financials(symbol)
        result["recommendations"] = await self.get_recommendations(symbol)
        result["price_target"] = await self.get_price_target(symbol)
        result["peers"] = await self.get_peers(symbol)

        return result
