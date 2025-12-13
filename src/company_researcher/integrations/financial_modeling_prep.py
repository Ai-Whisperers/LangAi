"""
Financial Modeling Prep (FMP) API Client.

Free tier: 250 requests/day
Provides: Financial statements, ratios, DCF valuations, company profiles

Documentation: https://site.financialmodelingprep.com/developer/docs
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base_client import BaseAPIClient
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class CompanyProfile:
    """Company profile data."""
    symbol: str
    company_name: str
    exchange: str
    industry: str
    sector: str
    country: str
    description: str
    ceo: str
    employees: Optional[int]
    website: str
    ipo_date: str
    market_cap: Optional[float]
    price: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict) -> "CompanyProfile":
        return cls(
            symbol=data.get("symbol", ""),
            company_name=data.get("companyName", ""),
            exchange=data.get("exchange", ""),
            industry=data.get("industry", ""),
            sector=data.get("sector", ""),
            country=data.get("country", ""),
            description=data.get("description", ""),
            ceo=data.get("ceo", ""),
            employees=data.get("fullTimeEmployees"),
            website=data.get("website", ""),
            ipo_date=data.get("ipoDate", ""),
            market_cap=data.get("mktCap"),
            price=data.get("price")
        )


@dataclass
class IncomeStatement:
    """Income statement data."""
    date: str
    symbol: str
    revenue: float
    cost_of_revenue: float
    gross_profit: float
    gross_profit_ratio: float
    operating_expenses: float
    operating_income: float
    operating_income_ratio: float
    ebitda: float
    ebitda_ratio: float
    net_income: float
    net_income_ratio: float
    eps: float
    eps_diluted: float

    @classmethod
    def from_dict(cls, data: Dict) -> "IncomeStatement":
        return cls(
            date=data.get("date", ""),
            symbol=data.get("symbol", ""),
            revenue=data.get("revenue", 0),
            cost_of_revenue=data.get("costOfRevenue", 0),
            gross_profit=data.get("grossProfit", 0),
            gross_profit_ratio=data.get("grossProfitRatio", 0),
            operating_expenses=data.get("operatingExpenses", 0),
            operating_income=data.get("operatingIncome", 0),
            operating_income_ratio=data.get("operatingIncomeRatio", 0),
            ebitda=data.get("ebitda", 0),
            ebitda_ratio=data.get("ebitdaratio", 0),
            net_income=data.get("netIncome", 0),
            net_income_ratio=data.get("netIncomeRatio", 0),
            eps=data.get("eps", 0),
            eps_diluted=data.get("epsdiluted", 0)
        )


@dataclass
class BalanceSheet:
    """Balance sheet data."""
    date: str
    symbol: str
    total_assets: float
    total_liabilities: float
    total_equity: float
    cash_and_equivalents: float
    short_term_investments: float
    net_receivables: float
    inventory: float
    total_current_assets: float
    total_current_liabilities: float
    long_term_debt: float
    total_debt: float

    @classmethod
    def from_dict(cls, data: Dict) -> "BalanceSheet":
        return cls(
            date=data.get("date", ""),
            symbol=data.get("symbol", ""),
            total_assets=data.get("totalAssets", 0),
            total_liabilities=data.get("totalLiabilities", 0),
            total_equity=data.get("totalStockholdersEquity", 0),
            cash_and_equivalents=data.get("cashAndCashEquivalents", 0),
            short_term_investments=data.get("shortTermInvestments", 0),
            net_receivables=data.get("netReceivables", 0),
            inventory=data.get("inventory", 0),
            total_current_assets=data.get("totalCurrentAssets", 0),
            total_current_liabilities=data.get("totalCurrentLiabilities", 0),
            long_term_debt=data.get("longTermDebt", 0),
            total_debt=data.get("totalDebt", 0)
        )


@dataclass
class KeyMetrics:
    """Key financial metrics."""
    symbol: str
    date: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    price_to_sales: Optional[float]
    price_to_book: Optional[float]
    enterprise_value: Optional[float]
    ev_to_ebitda: Optional[float]
    ev_to_revenue: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    roic: Optional[float]
    revenue_growth: Optional[float]
    earnings_growth: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict) -> "KeyMetrics":
        return cls(
            symbol=data.get("symbol", ""),
            date=data.get("date", ""),
            market_cap=data.get("marketCap"),
            pe_ratio=data.get("peRatio"),
            price_to_sales=data.get("priceToSalesRatio"),
            price_to_book=data.get("pbRatio"),
            enterprise_value=data.get("enterpriseValue"),
            ev_to_ebitda=data.get("enterpriseValueOverEBITDA"),
            ev_to_revenue=data.get("evToSales"),
            debt_to_equity=data.get("debtToEquity"),
            current_ratio=data.get("currentRatio"),
            roe=data.get("roe"),
            roa=data.get("roa"),
            roic=data.get("roic"),
            revenue_growth=data.get("revenueGrowth"),
            earnings_growth=data.get("netIncomeGrowth")
        )


@dataclass
class DCFValue:
    """Discounted Cash Flow valuation."""
    symbol: str
    date: str
    dcf: float
    stock_price: float

    @classmethod
    def from_dict(cls, data: Dict) -> "DCFValue":
        return cls(
            symbol=data.get("symbol", ""),
            date=data.get("date", ""),
            dcf=data.get("dcf", 0),
            stock_price=data.get("Stock Price", 0)
        )


class FMPClient(BaseAPIClient):
    """
    Financial Modeling Prep API Client.

    Free tier: 250 requests/day
    Rate limit: ~5 requests/second

    Features:
    - Company profiles and search
    - Financial statements (income, balance sheet, cash flow)
    - Key metrics and ratios
    - DCF valuations
    - Stock peers/competitors
    - News
    """

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="FMP_API_KEY",
            cache_ttl=3600,  # 1 hour cache
            rate_limit_calls=5,
            rate_limit_period=1.0
        )

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """Override to add API key to all requests."""
        params = params or {}
        params["apikey"] = self.api_key
        return await super()._request(endpoint, params, **kwargs)

    # =========================================================================
    # Company Profile
    # =========================================================================

    async def get_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """
        Get company profile and basic info.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")

        Returns:
            CompanyProfile or None if not found
        """
        data = await self._request(f"profile/{symbol}")
        if data and len(data) > 0:
            return CompanyProfile.from_dict(data[0])
        return None

    async def search_company(
        self,
        query: str,
        limit: int = 10,
        exchange: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for companies by name.

        Args:
            query: Search query (company name)
            limit: Max results (default 10)
            exchange: Filter by exchange (e.g., "NASDAQ")

        Returns:
            List of matching companies with symbol and name
        """
        params = {"query": query, "limit": limit}
        if exchange:
            params["exchange"] = exchange
        return await self._request("search", params)

    async def search_ticker(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for ticker symbols.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching tickers
        """
        return await self._request("search-ticker", {"query": query, "limit": limit})

    # =========================================================================
    # Financial Statements
    # =========================================================================

    async def get_income_statement(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[IncomeStatement]:
        """
        Get income statement history.

        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve

        Returns:
            List of IncomeStatement objects
        """
        data = await self._request(
            f"income-statement/{symbol}",
            {"period": period, "limit": limit}
        )
        return [IncomeStatement.from_dict(item) for item in (data or [])]

    async def get_balance_sheet(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[BalanceSheet]:
        """
        Get balance sheet history.

        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve

        Returns:
            List of BalanceSheet objects
        """
        data = await self._request(
            f"balance-sheet-statement/{symbol}",
            {"period": period, "limit": limit}
        )
        return [BalanceSheet.from_dict(item) for item in (data or [])]

    async def get_cash_flow(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict]:
        """
        Get cash flow statement history.

        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve

        Returns:
            List of cash flow statement dicts
        """
        return await self._request(
            f"cash-flow-statement/{symbol}",
            {"period": period, "limit": limit}
        ) or []

    # =========================================================================
    # Valuation & Metrics
    # =========================================================================

    async def get_key_metrics(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[KeyMetrics]:
        """
        Get key financial metrics and ratios.

        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve

        Returns:
            List of KeyMetrics objects
        """
        data = await self._request(
            f"key-metrics/{symbol}",
            {"period": period, "limit": limit}
        )
        return [KeyMetrics.from_dict(item) for item in (data or [])]

    async def get_dcf(self, symbol: str) -> Optional[DCFValue]:
        """
        Get discounted cash flow valuation.

        Args:
            symbol: Stock ticker symbol

        Returns:
            DCFValue or None
        """
        data = await self._request(f"discounted-cash-flow/{symbol}")
        if data and len(data) > 0:
            return DCFValue.from_dict(data[0])
        return None

    async def get_rating(self, symbol: str) -> Optional[Dict]:
        """
        Get company rating (buy/hold/sell).

        Args:
            symbol: Stock ticker symbol

        Returns:
            Rating dict with score and recommendation
        """
        data = await self._request(f"rating/{symbol}")
        return data[0] if data else None

    async def get_financial_ratios(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict]:
        """
        Get comprehensive financial ratios.

        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods

        Returns:
            List of financial ratio dicts
        """
        return await self._request(
            f"ratios/{symbol}",
            {"period": period, "limit": limit}
        ) or []

    # =========================================================================
    # Peers & Competitors
    # =========================================================================

    async def get_stock_peers(self, symbol: str) -> List[str]:
        """
        Get list of peer/competitor symbols.

        Args:
            symbol: Stock ticker symbol

        Returns:
            List of peer ticker symbols
        """
        data = await self._request(f"stock_peers", {"symbol": symbol})
        if data and len(data) > 0:
            return data[0].get("peersList", [])
        return []

    # =========================================================================
    # News
    # =========================================================================

    async def get_stock_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get stock-related news.

        Args:
            symbol: Stock ticker symbol (optional)
            limit: Max articles to return

        Returns:
            List of news article dicts
        """
        params = {"limit": limit}
        if symbol:
            params["tickers"] = symbol
        return await self._request("stock_news", params) or []

    # =========================================================================
    # Quote
    # =========================================================================

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time stock quote.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Quote dict with price, change, volume, etc.
        """
        data = await self._request(f"quote/{symbol}")
        return data[0] if data else None

    async def get_quote_batch(self, symbols: List[str]) -> List[Dict]:
        """
        Get quotes for multiple symbols.

        Args:
            symbols: List of ticker symbols

        Returns:
            List of quote dicts
        """
        symbols_str = ",".join(symbols)
        return await self._request(f"quote/{symbols_str}") or []

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def get_company_financials(
        self,
        symbol: str,
        include_ratios: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a company.

        Args:
            symbol: Stock ticker symbol
            include_ratios: Include financial ratios

        Returns:
            Dict with profile, financials, metrics, and valuation
        """
        result = {
            "symbol": symbol,
            "profile": None,
            "quote": None,
            "income_statement": [],
            "balance_sheet": [],
            "cash_flow": [],
            "key_metrics": [],
            "dcf": None,
            "rating": None,
            "peers": [],
            "ratios": []
        }

        # Fetch all data
        result["profile"] = await self.get_profile(symbol)
        result["quote"] = await self.get_quote(symbol)
        result["income_statement"] = await self.get_income_statement(symbol)
        result["balance_sheet"] = await self.get_balance_sheet(symbol)
        result["cash_flow"] = await self.get_cash_flow(symbol)
        result["key_metrics"] = await self.get_key_metrics(symbol)
        result["dcf"] = await self.get_dcf(symbol)
        result["rating"] = await self.get_rating(symbol)
        result["peers"] = await self.get_stock_peers(symbol)

        if include_ratios:
            result["ratios"] = await self.get_financial_ratios(symbol)

        return result
