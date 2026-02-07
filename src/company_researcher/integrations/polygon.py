"""
Polygon.io Stock Market API Client.

Free tier: 5 API calls/minute (delayed data)
Provides: Historical stock data, company details, news

Documentation: https://polygon.io/docs
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional

from ..utils import get_logger, utc_now
from .base_client import BaseAPIClient

logger = get_logger(__name__)


@dataclass
class StockBar:
    """OHLCV bar data."""

    ticker: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    num_transactions: int

    @classmethod
    def from_dict(cls, ticker: str, data: Dict) -> "StockBar":
        return cls(
            ticker=ticker,
            timestamp=data.get("t", 0),
            open=data.get("o", 0),
            high=data.get("h", 0),
            low=data.get("l", 0),
            close=data.get("c", 0),
            volume=data.get("v", 0),
            vwap=data.get("vw", 0),
            num_transactions=data.get("n", 0),
        )


@dataclass
class TickerDetails:
    """Detailed ticker information."""

    ticker: str
    name: str
    market: str
    locale: str
    primary_exchange: str
    type: str
    currency: str
    cik: Optional[str]
    composite_figi: Optional[str]
    description: str
    homepage_url: Optional[str]
    total_employees: Optional[int]
    list_date: Optional[str]
    sic_code: Optional[str]
    sic_description: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "TickerDetails":
        results = data.get("results", data)
        return cls(
            ticker=results.get("ticker", ""),
            name=results.get("name", ""),
            market=results.get("market", ""),
            locale=results.get("locale", ""),
            primary_exchange=results.get("primary_exchange", ""),
            type=results.get("type", ""),
            currency=results.get("currency_name", ""),
            cik=results.get("cik"),
            composite_figi=results.get("composite_figi"),
            description=results.get("description", ""),
            homepage_url=results.get("homepage_url"),
            total_employees=results.get("total_employees"),
            list_date=results.get("list_date"),
            sic_code=results.get("sic_code"),
            sic_description=results.get("sic_description"),
        )


@dataclass
class NewsArticle:
    """News article from Polygon."""

    id: str
    publisher: Dict[str, str]
    title: str
    author: str
    published_utc: str
    article_url: str
    tickers: List[str]
    description: str
    keywords: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "NewsArticle":
        return cls(
            id=data.get("id", ""),
            publisher=data.get("publisher", {}),
            title=data.get("title", ""),
            author=data.get("author", ""),
            published_utc=data.get("published_utc", ""),
            article_url=data.get("article_url", ""),
            tickers=data.get("tickers", []),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
        )


class PolygonClient(BaseAPIClient):
    """
    Polygon.io Stock Market API Client.

    Free tier: 5 API calls/minute, delayed data
    Paid tiers start at $29/month for unlimited.

    Features:
    - Historical aggregate bars (OHLCV)
    - Ticker details and company info
    - Related companies
    - Stock news
    - Financial data (paid only)
    """

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="POLYGON_API_KEY",
            cache_ttl=3600,  # 1 hour for historical data
            rate_limit_calls=5,
            rate_limit_period=60.0,  # Free tier: 5/minute
        )

    async def _request(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Any:
        """Override to add API key to all requests."""
        params = params or {}
        params["apiKey"] = self.api_key
        return await super()._request(endpoint, params, **kwargs)

    # =========================================================================
    # Aggregates (Historical Bars)
    # =========================================================================

    async def get_aggregates(
        self,
        ticker: str,
        multiplier: int = 1,
        timespan: str = "day",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 120,
    ) -> List[StockBar]:
        """
        Get aggregate bars for a stock.

        Args:
            ticker: Stock ticker symbol
            multiplier: Size of timespan multiplier
            timespan: minute, hour, day, week, month, quarter, year
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Max results (default 120)

        Returns:
            List of StockBar objects
        """
        if not from_date:
            from_date = (utc_now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = utc_now().strftime("%Y-%m-%d")

        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        data = await self._request(endpoint, {"limit": limit})

        bars = []
        for bar in data.get("results", []):
            bars.append(StockBar.from_dict(ticker, bar))
        return bars

    async def get_daily_bars(self, ticker: str, days: int = 30) -> List[StockBar]:
        """
        Get daily bars for recent period.

        Args:
            ticker: Stock ticker symbol
            days: Number of days to retrieve

        Returns:
            List of StockBar objects
        """
        from_date = (utc_now() - timedelta(days=days)).strftime("%Y-%m-%d")
        to_date = utc_now().strftime("%Y-%m-%d")
        return await self.get_aggregates(ticker, 1, "day", from_date, to_date, days)

    # =========================================================================
    # Ticker Details
    # =========================================================================

    async def get_ticker_details(self, ticker: str) -> Optional[TickerDetails]:
        """
        Get detailed info about a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            TickerDetails or None
        """
        data = await self._request(f"/v3/reference/tickers/{ticker}")
        if data and data.get("results"):
            return TickerDetails.from_dict(data)
        return None

    async def search_tickers(
        self, search: str, type: str = "CS", market: str = "stocks", limit: int = 10  # Common Stock
    ) -> List[Dict]:
        """
        Search for tickers.

        Args:
            search: Search query
            type: Ticker type (CS=common stock, ETF, etc.)
            market: Market type (stocks, crypto, fx)
            limit: Max results

        Returns:
            List of matching tickers
        """
        data = await self._request(
            "/v3/reference/tickers",
            {"search": search, "type": type, "market": market, "limit": limit},
        )
        return data.get("results", []) if data else []

    # =========================================================================
    # Related Companies
    # =========================================================================

    async def get_related_companies(self, ticker: str) -> List[str]:
        """
        Get related companies/tickers.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of related ticker symbols
        """
        data = await self._request(f"/v1/related-companies/{ticker}")
        return [item.get("ticker") for item in data.get("results", [])] if data else []

    # =========================================================================
    # News
    # =========================================================================

    async def get_ticker_news(
        self, ticker: Optional[str] = None, limit: int = 10, order: str = "desc"
    ) -> List[NewsArticle]:
        """
        Get news for a ticker or general market news.

        Args:
            ticker: Stock ticker symbol (optional)
            limit: Max articles
            order: Sort order (asc, desc)

        Returns:
            List of NewsArticle objects
        """
        params = {"limit": limit, "order": order}
        if ticker:
            params["ticker"] = ticker

        data = await self._request("/v2/reference/news", params)
        return [NewsArticle.from_dict(item) for item in data.get("results", [])] if data else []

    # =========================================================================
    # Previous Close
    # =========================================================================

    async def get_previous_close(self, ticker: str) -> Optional[Dict]:
        """
        Get previous day's close data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with previous close OHLCV data
        """
        data = await self._request(f"/v2/aggs/ticker/{ticker}/prev")
        results = data.get("results", []) if data else []
        return results[0] if results else None

    # =========================================================================
    # Grouped Daily
    # =========================================================================

    async def get_grouped_daily(self, date: str, adjusted: bool = True) -> List[Dict]:
        """
        Get daily bars for all stocks on a given date.

        Args:
            date: Date (YYYY-MM-DD)
            adjusted: Whether to adjust for splits

        Returns:
            List of bars for all stocks
        """
        data = await self._request(
            f"/v2/aggs/grouped/locale/us/market/stocks/{date}", {"adjusted": str(adjusted).lower()}
        )
        return data.get("results", []) if data else []

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def get_stock_overview(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock overview.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with details, bars, news, and related companies
        """
        result = {
            "ticker": ticker,
            "details": None,
            "previous_close": None,
            "daily_bars": [],
            "news": [],
            "related": [],
        }

        result["details"] = await self.get_ticker_details(ticker)
        result["previous_close"] = await self.get_previous_close(ticker)
        result["daily_bars"] = await self.get_daily_bars(ticker, days=30)
        result["news"] = await self.get_ticker_news(ticker, limit=5)
        result["related"] = await self.get_related_companies(ticker)

        return result
