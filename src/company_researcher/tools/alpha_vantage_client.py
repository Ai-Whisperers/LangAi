"""
Alpha Vantage API Client for Financial Data (Phase 7).

Fetches stock quotes, fundamentals, and financial statements for public companies.

API Documentation: https://www.alphavantage.co/documentation/
Free Tier: 25 API calls per day
"""

from typing import Dict, Optional, Any
from datetime import timedelta
from ..utils import get_config, utc_now


class AlphaVantageClient:
    """
    Client for Alpha Vantage financial data API.

    Provides methods to fetch:
    - Stock quotes (real-time and historical)
    - Company fundamentals (overview)
    - Income statements
    - Balance sheets
    - Cash flow statements
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client.

        Args:
            api_key: Alpha Vantage API key (defaults to env var)
        """
        self.api_key = api_key or get_config("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = timedelta(hours=6)  # Cache for 6 hours

    def is_available(self) -> bool:
        """Check if Alpha Vantage API is available (API key set)."""
        return bool(self.api_key)

    def _make_request(self, function: str, symbol: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request to Alpha Vantage.

        Args:
            function: API function name
            symbol: Stock ticker symbol
            **kwargs: Additional query parameters

        Returns:
            JSON response as dictionary
        """
        # Check cache first
        cache_key = f"{function}_{symbol}"
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if utc_now() - cached_time < self._cache_ttl:
                return cached_data

        # Make API call (placeholder - would use requests library)
        # In production, would use: requests.get(self.base_url, params=params)
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
            **kwargs
        }

        # For now, return mock data structure
        # In production implementation, this would make actual HTTP request
        mock_response = self._get_mock_data(function, symbol)

        # Cache the response
        self._cache[cache_key] = (mock_response, utc_now())

        return mock_response

    def _get_mock_data(self, function: str, symbol: str) -> Dict[str, Any]:
        """
        Get mock data for testing (Phase 7 initial implementation).

        In production, this would be replaced with actual API calls.
        """
        # This is a placeholder - actual implementation would make HTTP requests
        return {
            "Information": f"Mock data for {function} - {symbol}. "
                          "Replace with actual HTTP request in production.",
            "symbol": symbol,
            "function": function,
            "note": "This is mock data. Set up requests library for production use."
        }

    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company overview and fundamentals.

        Returns data including:
        - Market cap
        - P/E ratio
        - Dividend yield
        - 52-week high/low
        - Revenue, EBITDA
        - Profit margin
        - etc.

        Args:
            symbol: Stock ticker (e.g., "TSLA", "MSFT")

        Returns:
            Company overview data or None if error
        """
        if not self.is_available():
            return None

        try:
            data = self._make_request("OVERVIEW", symbol)
            return data
        except Exception as e:
            print(f"[Alpha Vantage] Error fetching overview for {symbol}: {e}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current stock quote.

        Returns:
        - Current price
        - Open, high, low
        - Volume
        - Latest trading day
        - Change/change percent

        Args:
            symbol: Stock ticker

        Returns:
            Quote data or None if error
        """
        if not self.is_available():
            return None

        try:
            data = self._make_request("GLOBAL_QUOTE", symbol)
            return data
        except Exception as e:
            print(f"[Alpha Vantage] Error fetching quote for {symbol}: {e}")
            return None

    def get_income_statement(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get annual and quarterly income statements.

        Returns:
        - Revenue
        - Gross profit
        - Operating income
        - Net income
        - EPS
        - etc.

        Args:
            symbol: Stock ticker

        Returns:
            Income statement data or None if error
        """
        if not self.is_available():
            return None

        try:
            data = self._make_request("INCOME_STATEMENT", symbol)
            return data
        except Exception as e:
            print(f"[Alpha Vantage] Error fetching income statement for {symbol}: {e}")
            return None

    def get_balance_sheet(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get annual and quarterly balance sheets.

        Returns:
        - Total assets
        - Total liabilities
        - Shareholder equity
        - Current assets/liabilities
        - Long-term debt
        - etc.

        Args:
            symbol: Stock ticker

        Returns:
            Balance sheet data or None if error
        """
        if not self.is_available():
            return None

        try:
            data = self._make_request("BALANCE_SHEET", symbol)
            return data
        except Exception as e:
            print(f"[Alpha Vantage] Error fetching balance sheet for {symbol}: {e}")
            return None

    def get_cash_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get annual and quarterly cash flow statements.

        Returns:
        - Operating cash flow
        - Investing cash flow
        - Financing cash flow
        - Free cash flow
        - etc.

        Args:
            symbol: Stock ticker

        Returns:
            Cash flow data or None if error
        """
        if not self.is_available():
            return None

        try:
            data = self._make_request("CASH_FLOW", symbol)
            return data
        except Exception as e:
            print(f"[Alpha Vantage] Error fetching cash flow for {symbol}: {e}")
            return None

    def get_company_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a company.

        Fetches all available financial data:
        - Company overview
        - Current quote
        - Income statement
        - Balance sheet
        - Cash flow

        Args:
            symbol: Stock ticker

        Returns:
            Dictionary with all financial data
        """
        if not self.is_available():
            return {
                "available": False,
                "reason": "Alpha Vantage API key not set"
            }

        print(f"[Alpha Vantage] Fetching comprehensive data for {symbol}...")

        financials = {
            "available": True,
            "symbol": symbol,
            "fetched_at": utc_now().isoformat(),
            "overview": self.get_company_overview(symbol),
            "quote": self.get_quote(symbol),
            "income_statement": self.get_income_statement(symbol),
            "balance_sheet": self.get_balance_sheet(symbol),
            "cash_flow": self.get_cash_flow(symbol)
        }

        print(f"[Alpha Vantage] Data fetched for {symbol}")

        return financials


# ==============================================================================
# Helper Functions
# ==============================================================================

def extract_key_metrics(financials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key financial metrics from Alpha Vantage data.

    Args:
        financials: Output from get_company_financials()

    Returns:
        Dictionary of key metrics in standardized format
    """
    if not financials.get("available"):
        return {"available": False}

    # Extract from overview
    overview = financials.get("overview", {})

    # Extract from income statement
    income = financials.get("income_statement", {})

    # Extract from balance sheet
    balance = financials.get("balance_sheet", {})

    # Extract from cash flow
    cash_flow = financials.get("cash_flow", {})

    # Compile key metrics
    # (In production, would parse actual API response structure)
    metrics = {
        "available": True,
        "symbol": financials["symbol"],

        # Valuation
        "market_cap": overview.get("MarketCapitalization"),
        "pe_ratio": overview.get("PERatio"),
        "peg_ratio": overview.get("PEGRatio"),

        # Profitability
        "revenue_ttm": overview.get("RevenueTTM"),
        "gross_profit_ttm": overview.get("GrossProfitTTM"),
        "ebitda": overview.get("EBITDA"),
        "profit_margin": overview.get("ProfitMargin"),
        "operating_margin": overview.get("OperatingMarginTTM"),

        # Financial Health
        "book_value": overview.get("BookValue"),
        "debt_to_equity": overview.get("DebtToEquity"),
        "return_on_equity": overview.get("ReturnOnEquityTTM"),
        "current_ratio": overview.get("CurrentRatio"),

        # Growth
        "revenue_growth_yoy": overview.get("QuarterlyRevenueGrowthYOY"),
        "earnings_growth_yoy": overview.get("QuarterlyEarningsGrowthYOY"),

        # Dividends
        "dividend_yield": overview.get("DividendYield"),
        "dividend_per_share": overview.get("DividendPerShare"),

        # Stock Price
        "52_week_high": overview.get("52WeekHigh"),
        "52_week_low": overview.get("52WeekLow"),
        "50_day_ma": overview.get("50DayMovingAverage"),
        "200_day_ma": overview.get("200DayMovingAverage")
    }

    return metrics
