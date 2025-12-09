"""
Financial Data Provider using free APIs.

Primary source: Yahoo Finance (yfinance) - No API key required
Fallback source: Alpha Vantage (free tier: 25 requests/day)

Data available:
- Market capitalization
- Stock price (current, 52-week high/low)
- P/E ratio
- EPS
- Dividend yield
- Revenue, net income
- And more...
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Alpha Vantage free API key (get your own at https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")


@dataclass
class FinancialData:
    """Financial data for a company."""
    ticker: str
    company_name: str = ""

    # Stock data
    current_price: Optional[float] = None
    currency: str = "USD"
    market_cap: Optional[float] = None
    market_cap_formatted: str = ""

    # 52-week range
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

    # Valuation metrics
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None

    # Financials
    revenue: Optional[float] = None
    revenue_formatted: str = ""
    net_income: Optional[float] = None
    eps: Optional[float] = None

    # Dividends
    dividend_yield: Optional[float] = None
    dividend_rate: Optional[float] = None

    # Company info
    sector: str = ""
    industry: str = ""
    employees: Optional[int] = None
    website: str = ""
    description: str = ""

    # Metadata
    exchange: str = ""
    fetch_timestamp: datetime = field(default_factory=datetime.now)
    data_source: str = "yahoo_finance"

    def to_context_string(self) -> str:
        """Convert to a string suitable for LLM context."""
        lines = [
            f"## Financial Data for {self.company_name} ({self.ticker})",
            f"Data Source: Yahoo Finance (as of {self.fetch_timestamp.strftime('%Y-%m-%d %H:%M')})",
            "",
            "### Stock Information",
            f"- Current Price: ${self.current_price:.2f} {self.currency}" if self.current_price else "- Current Price: N/A",
            f"- Market Cap: {self.market_cap_formatted}" if self.market_cap_formatted else "- Market Cap: N/A",
            f"- 52-Week High: ${self.fifty_two_week_high:.2f}" if self.fifty_two_week_high else "- 52-Week High: N/A",
            f"- 52-Week Low: ${self.fifty_two_week_low:.2f}" if self.fifty_two_week_low else "- 52-Week Low: N/A",
            "",
            "### Valuation Metrics",
            f"- P/E Ratio (TTM): {self.pe_ratio:.2f}" if self.pe_ratio else "- P/E Ratio: N/A",
            f"- Forward P/E: {self.forward_pe:.2f}" if self.forward_pe else "- Forward P/E: N/A",
            f"- PEG Ratio: {self.peg_ratio:.2f}" if self.peg_ratio else "- PEG Ratio: N/A",
            f"- Price/Book: {self.price_to_book:.2f}" if self.price_to_book else "- Price/Book: N/A",
            f"- Price/Sales: {self.price_to_sales:.2f}" if self.price_to_sales else "- Price/Sales: N/A",
            "",
            "### Financial Performance",
            f"- Revenue (TTM): {self.revenue_formatted}" if self.revenue_formatted else "- Revenue: N/A",
            f"- EPS (TTM): ${self.eps:.2f}" if self.eps else "- EPS: N/A",
            f"- Dividend Yield: {self.dividend_yield*100:.2f}%" if self.dividend_yield else "- Dividend Yield: N/A",
            "",
            "### Company Info",
            f"- Sector: {self.sector}" if self.sector else "- Sector: N/A",
            f"- Industry: {self.industry}" if self.industry else "- Industry: N/A",
            f"- Employees: {self.employees:,}" if self.employees else "- Employees: N/A",
            f"- Exchange: {self.exchange}" if self.exchange else "- Exchange: N/A",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "current_price": self.current_price,
            "currency": self.currency,
            "market_cap": self.market_cap,
            "market_cap_formatted": self.market_cap_formatted,
            "fifty_two_week_high": self.fifty_two_week_high,
            "fifty_two_week_low": self.fifty_two_week_low,
            "pe_ratio": self.pe_ratio,
            "forward_pe": self.forward_pe,
            "peg_ratio": self.peg_ratio,
            "price_to_book": self.price_to_book,
            "price_to_sales": self.price_to_sales,
            "revenue": self.revenue,
            "revenue_formatted": self.revenue_formatted,
            "net_income": self.net_income,
            "eps": self.eps,
            "dividend_yield": self.dividend_yield,
            "sector": self.sector,
            "industry": self.industry,
            "employees": self.employees,
            "exchange": self.exchange,
            "data_source": self.data_source,
            "fetch_timestamp": self.fetch_timestamp.isoformat()
        }


def _format_large_number(num: Optional[float]) -> str:
    """Format large numbers with B/M/K suffixes."""
    if num is None:
        return ""
    if num >= 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"


class FinancialDataProvider:
    """
    Provider for financial data using free APIs.

    Primary source: Yahoo Finance (via yfinance library)
    - Completely free
    - No API key required
    - Real-time stock data
    - Historical data available
    """

    def __init__(self):
        """Initialize the financial data provider."""
        self._yfinance_available = False
        try:
            import yfinance
            self._yfinance_available = True
        except ImportError:
            logger.warning("yfinance not installed. Install with: pip install yfinance")

    def get_financial_data(self, ticker: str, retries: int = 3, delay: float = 2.0) -> Optional[FinancialData]:
        """
        Fetch financial data for a ticker symbol with retry logic.

        Args:
            ticker: Stock ticker symbol (e.g., "MSFT", "AAPL")
            retries: Number of retry attempts on rate limiting
            delay: Delay between retries in seconds

        Returns:
            FinancialData object or None if not found
        """
        if not self._yfinance_available:
            logger.error("yfinance not available")
            return None

        if not ticker:
            logger.warning("No ticker provided")
            return None

        import time
        import yfinance as yf

        last_error = None
        for attempt in range(retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry {attempt}/{retries} for {ticker} after {delay}s delay...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff

                # Fetch ticker data
                stock = yf.Ticker(ticker)
                info = stock.info

                if not info or info.get("regularMarketPrice") is None:
                    logger.warning(f"No data found for ticker: {ticker}")
                    return None

                # Extract market cap
                market_cap = info.get("marketCap")

                # Extract revenue
                revenue = info.get("totalRevenue")

                # Build financial data object
                data = FinancialData(
                    ticker=ticker.upper(),
                    company_name=info.get("longName", info.get("shortName", ticker)),

                    # Stock data
                    current_price=info.get("regularMarketPrice") or info.get("currentPrice"),
                    currency=info.get("currency", "USD"),
                    market_cap=market_cap,
                    market_cap_formatted=_format_large_number(market_cap),

                    # 52-week range
                    fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                    fifty_two_week_low=info.get("fiftyTwoWeekLow"),

                    # Valuation
                    pe_ratio=info.get("trailingPE"),
                    forward_pe=info.get("forwardPE"),
                    peg_ratio=info.get("pegRatio"),
                    price_to_book=info.get("priceToBook"),
                    price_to_sales=info.get("priceToSalesTrailing12Months"),

                    # Financials
                    revenue=revenue,
                    revenue_formatted=_format_large_number(revenue),
                    net_income=info.get("netIncomeToCommon"),
                    eps=info.get("trailingEps"),

                    # Dividends
                    dividend_yield=info.get("dividendYield"),
                    dividend_rate=info.get("dividendRate"),

                    # Company info
                    sector=info.get("sector", ""),
                    industry=info.get("industry", ""),
                    employees=info.get("fullTimeEmployees"),
                    website=info.get("website", ""),
                    description=info.get("longBusinessSummary", "")[:500] if info.get("longBusinessSummary") else "",

                    # Metadata
                    exchange=info.get("exchange", ""),
                )

                logger.info(f"Successfully fetched financial data for {ticker}")
                return data

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                # Check for rate limiting errors (429) or JSON parse errors that follow rate limits
                if "429" in str(e) or "too many requests" in error_str or "expecting value" in error_str:
                    logger.warning(f"Rate limited on attempt {attempt + 1}/{retries} for {ticker}")
                    continue
                # Non-rate-limit errors should fail immediately
                logger.error(f"Error fetching financial data for {ticker}: {e}")
                return None

        logger.error(f"All {retries} attempts failed for {ticker}: {last_error}")

        # Try Alpha Vantage as fallback
        if ALPHA_VANTAGE_API_KEY:
            logger.info(f"Trying Alpha Vantage fallback for {ticker}...")
            return self._fetch_from_alpha_vantage(ticker)

        return None

    def _fetch_from_alpha_vantage(self, ticker: str) -> Optional[FinancialData]:
        """Fetch financial data from Alpha Vantage (free tier: 25 requests/day)."""
        import requests

        if not ALPHA_VANTAGE_API_KEY:
            return None

        try:
            # Get company overview
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url, timeout=10)
            info = response.json()

            if not info or "Symbol" not in info:
                logger.warning(f"Alpha Vantage: No data for {ticker}")
                return None

            # Parse market cap
            market_cap = None
            if info.get("MarketCapitalization"):
                try:
                    market_cap = float(info["MarketCapitalization"])
                except (ValueError, TypeError):
                    pass

            # Parse revenue
            revenue = None
            if info.get("RevenueTTM"):
                try:
                    revenue = float(info["RevenueTTM"])
                except (ValueError, TypeError):
                    pass

            data = FinancialData(
                ticker=ticker.upper(),
                company_name=info.get("Name", ticker),
                market_cap=market_cap,
                market_cap_formatted=_format_large_number(market_cap),
                pe_ratio=float(info["PERatio"]) if info.get("PERatio") and info["PERatio"] != "None" else None,
                forward_pe=float(info["ForwardPE"]) if info.get("ForwardPE") and info["ForwardPE"] != "None" else None,
                peg_ratio=float(info["PEGRatio"]) if info.get("PEGRatio") and info["PEGRatio"] != "None" else None,
                price_to_book=float(info["PriceToBookRatio"]) if info.get("PriceToBookRatio") and info["PriceToBookRatio"] != "None" else None,
                revenue=revenue,
                revenue_formatted=_format_large_number(revenue),
                eps=float(info["EPS"]) if info.get("EPS") and info["EPS"] != "None" else None,
                dividend_yield=float(info["DividendYield"]) if info.get("DividendYield") and info["DividendYield"] != "None" else None,
                fifty_two_week_high=float(info["52WeekHigh"]) if info.get("52WeekHigh") and info["52WeekHigh"] != "None" else None,
                fifty_two_week_low=float(info["52WeekLow"]) if info.get("52WeekLow") and info["52WeekLow"] != "None" else None,
                sector=info.get("Sector", ""),
                industry=info.get("Industry", ""),
                exchange=info.get("Exchange", ""),
                description=info.get("Description", "")[:500] if info.get("Description") else "",
                data_source="alpha_vantage"
            )

            logger.info(f"Alpha Vantage: Got data for {ticker}")
            return data

        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {e}")
            return None

    def get_multiple_tickers(self, tickers: List[str]) -> Dict[str, Optional[FinancialData]]:
        """
        Fetch financial data for multiple tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to FinancialData
        """
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_financial_data(ticker)
        return results

    def is_available(self) -> bool:
        """Check if the provider is available."""
        return self._yfinance_available


# Module-level convenience functions
_provider = None

def get_provider() -> FinancialDataProvider:
    """Get or create the singleton provider instance."""
    global _provider
    if _provider is None:
        _provider = FinancialDataProvider()
    return _provider


def fetch_financial_data(ticker: str) -> Optional[FinancialData]:
    """
    Convenience function to fetch financial data for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        FinancialData object or None
    """
    return get_provider().get_financial_data(ticker)
