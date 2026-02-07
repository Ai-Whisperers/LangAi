"""
Unified Financial Data Provider with Fallback Chain.

Implements a priority-based fallback strategy:
    1. yfinance (free, best for public companies)
    2. Financial Modeling Prep (250 req/day free)
    3. Finnhub (60 req/min free)
    4. Polygon (5 req/min free)

Each provider is tried in order until data is successfully retrieved.
Failed providers are logged and skipped for subsequent calls during the session.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class ProviderStatus(Enum):
    """Provider availability status."""

    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ProviderState:
    """Tracks state of a financial data provider."""

    name: str
    status: ProviderStatus = ProviderStatus.AVAILABLE
    last_call: Optional[datetime] = None
    last_error: Optional[str] = None
    calls_today: int = 0
    daily_limit: Optional[int] = None
    reset_time: Optional[datetime] = None

    def can_call(self) -> bool:
        """Check if provider can be called."""
        if self.status == ProviderStatus.DISABLED:
            return False
        if self.status == ProviderStatus.RATE_LIMITED:
            if self.reset_time and utc_now() > self.reset_time:
                self.status = ProviderStatus.AVAILABLE
                self.calls_today = 0
                return True
            return False
        if self.daily_limit and self.calls_today >= self.daily_limit:
            self.status = ProviderStatus.RATE_LIMITED
            self.reset_time = utc_now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            return False
        return True

    def record_call(self, success: bool, error: Optional[str] = None):
        """Record a call attempt."""
        self.last_call = utc_now()
        self.calls_today += 1
        if not success:
            self.last_error = error
            if "rate limit" in (error or "").lower():
                self.status = ProviderStatus.RATE_LIMITED


@dataclass
class FinancialData:
    """Unified financial data structure."""

    ticker: str
    company_name: Optional[str] = None

    # Basic Info
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employees: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = None
    ceo: Optional[str] = None

    # Price Data
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    previous_close: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None

    # Valuation Metrics
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    ev_to_revenue: Optional[float] = None

    # Financials
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    gross_profit: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_income: Optional[float] = None
    operating_margin: Optional[float] = None
    net_income: Optional[float] = None
    profit_margin: Optional[float] = None
    ebitda: Optional[float] = None
    eps: Optional[float] = None
    eps_growth: Optional[float] = None

    # Balance Sheet
    total_cash: Optional[float] = None
    total_debt: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    book_value: Optional[float] = None

    # Dividends
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    ex_dividend_date: Optional[str] = None

    # Performance
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    beta: Optional[float] = None

    # Analyst Data
    target_price: Optional[float] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    analyst_recommendation: Optional[str] = None
    num_analyst_opinions: Optional[int] = None

    # Meta
    data_sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=utc_now)
    data_quality: str = "partial"  # complete, partial, minimal

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    result[key] = value
                else:
                    result[key] = value
        return result

    def merge(self, other: "FinancialData") -> "FinancialData":
        """Merge with another FinancialData, preferring non-None values."""
        for key in self.__dataclass_fields__:
            if key in ("data_sources", "last_updated", "data_quality"):
                continue
            self_val = getattr(self, key)
            other_val = getattr(other, key)
            if self_val is None and other_val is not None:
                setattr(self, key, other_val)

        # Merge sources
        for source in other.data_sources:
            if source not in self.data_sources:
                self.data_sources.append(source)

        # Update quality assessment
        self._assess_quality()
        return self

    def _assess_quality(self):
        """Assess data completeness."""
        critical_fields = ["current_price", "market_cap", "revenue", "net_income", "pe_ratio"]
        important_fields = ["employees", "sector", "industry", "gross_margin", "profit_margin"]

        critical_count = sum(1 for f in critical_fields if getattr(self, f) is not None)
        important_count = sum(1 for f in important_fields if getattr(self, f) is not None)

        if critical_count >= 4 and important_count >= 3:
            self.data_quality = "complete"
        elif critical_count >= 2 or important_count >= 2:
            self.data_quality = "partial"
        else:
            self.data_quality = "minimal"


class FinancialDataProvider:
    """
    Unified financial data provider with automatic fallback.

    Usage:
        provider = FinancialDataProvider(config)
        data = provider.get_financial_data("AAPL")

        # Or with specific providers only
        provider = FinancialDataProvider(config, providers=["yfinance", "fmp"])
    """

    def __init__(
        self, config: Any, providers: Optional[List[str]] = None, enable_caching: bool = True
    ):
        """
        Initialize the financial data provider.

        Args:
            config: Application configuration
            providers: List of provider names to use (default: all available)
            enable_caching: Whether to cache results
        """
        self.config = config
        self.enable_caching = enable_caching
        self._cache: Dict[str, FinancialData] = {}
        self._cache_ttl = timedelta(minutes=15)

        # Initialize provider states
        self.providers: Dict[str, ProviderState] = {}
        self._provider_funcs: Dict[str, Callable] = {}

        # Register available providers
        self._register_providers(providers)

    def _register_providers(self, providers: Optional[List[str]] = None):
        """Register available providers based on configuration."""
        all_providers = [
            ("yfinance", self._fetch_yfinance, None),  # No limit for yfinance
            ("fmp", self._fetch_fmp, 250),
            ("finnhub", self._fetch_finnhub, 60),
            ("polygon", self._fetch_polygon, 5),
        ]

        for name, func, daily_limit in all_providers:
            # Skip if not in requested providers list
            if providers and name not in providers:
                continue

            # Skip if API key required but not configured
            if name == "fmp" and not getattr(self.config, "fmp_api_key", None):
                logger.debug(f"FMP API key not configured, skipping")
                continue
            if name == "finnhub" and not getattr(self.config, "finnhub_api_key", None):
                logger.debug(f"Finnhub API key not configured, skipping")
                continue
            if name == "polygon" and not getattr(self.config, "polygon_api_key", None):
                logger.debug(f"Polygon API key not configured, skipping")
                continue

            self.providers[name] = ProviderState(name=name, daily_limit=daily_limit)
            self._provider_funcs[name] = func
            logger.info(f"Registered financial provider: {name}")

    def get_financial_data(
        self, ticker: str, force_refresh: bool = False
    ) -> Optional[FinancialData]:
        """
        Get financial data for a ticker using fallback chain.

        Args:
            ticker: Stock ticker symbol
            force_refresh: Bypass cache if True

        Returns:
            FinancialData object or None if all providers fail
        """
        ticker = ticker.upper().strip()

        # Check cache
        if self.enable_caching and not force_refresh:
            cached = self._get_cached(ticker)
            if cached:
                logger.debug(f"Returning cached data for {ticker}")
                return cached

        # Try providers in order
        result = FinancialData(ticker=ticker)
        successful_providers = []

        for name, state in self.providers.items():
            if not state.can_call():
                logger.debug(f"Skipping {name}: {state.status.value}")
                continue

            try:
                logger.info(f"Fetching {ticker} from {name}...")
                fetch_func = self._provider_funcs[name]
                provider_data = fetch_func(ticker)

                if provider_data:
                    result = result.merge(provider_data)
                    successful_providers.append(name)
                    state.record_call(success=True)
                    logger.info(f"Got data from {name} for {ticker}")
                else:
                    state.record_call(success=False, error="No data returned")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"{name} failed for {ticker}: {error_msg}")
                state.record_call(success=False, error=error_msg)
                continue

        if not successful_providers:
            logger.error(f"All providers failed for {ticker}")
            return None

        result.data_sources = successful_providers
        result._assess_quality()

        # Cache result
        if self.enable_caching:
            self._cache[ticker] = result

        logger.info(
            f"Got {result.data_quality} data for {ticker} "
            f"from {', '.join(successful_providers)}"
        )
        return result

    def _get_cached(self, ticker: str) -> Optional[FinancialData]:
        """Get cached data if valid."""
        if ticker not in self._cache:
            return None
        cached = self._cache[ticker]
        if utc_now() - cached.last_updated > self._cache_ttl:
            del self._cache[ticker]
            return None
        return cached

    def _fetch_yfinance(self, ticker: str) -> Optional[FinancialData]:
        """Fetch data from yfinance."""
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed")
            return None

        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            return None

        return FinancialData(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName"),
            exchange=info.get("exchange"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            country=info.get("country"),
            employees=info.get("fullTimeEmployees"),
            description=info.get("longBusinessSummary"),
            website=info.get("website"),
            current_price=info.get("regularMarketPrice") or info.get("currentPrice"),
            market_cap=info.get("marketCap"),
            previous_close=info.get("previousClose"),
            day_high=info.get("dayHigh"),
            day_low=info.get("dayLow"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            volume=info.get("volume"),
            avg_volume=info.get("averageVolume"),
            pe_ratio=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            peg_ratio=info.get("pegRatio"),
            price_to_book=info.get("priceToBook"),
            price_to_sales=info.get("priceToSalesTrailing12Months"),
            ev_to_ebitda=info.get("enterpriseToEbitda"),
            ev_to_revenue=info.get("enterpriseToRevenue"),
            revenue=info.get("totalRevenue"),
            revenue_growth=info.get("revenueGrowth"),
            gross_profit=info.get("grossProfits"),
            gross_margin=info.get("grossMargins"),
            operating_income=info.get("operatingIncome") or info.get("ebit"),
            operating_margin=info.get("operatingMargins"),
            net_income=info.get("netIncomeToCommon"),
            profit_margin=info.get("profitMargins"),
            ebitda=info.get("ebitda"),
            eps=info.get("trailingEps"),
            total_cash=info.get("totalCash"),
            total_debt=info.get("totalDebt"),
            debt_to_equity=info.get("debtToEquity"),
            current_ratio=info.get("currentRatio"),
            book_value=info.get("bookValue"),
            dividend_rate=info.get("dividendRate"),
            dividend_yield=info.get("dividendYield"),
            payout_ratio=info.get("payoutRatio"),
            return_on_equity=info.get("returnOnEquity"),
            return_on_assets=info.get("returnOnAssets"),
            beta=info.get("beta"),
            target_price=info.get("targetMeanPrice"),
            target_high=info.get("targetHighPrice"),
            target_low=info.get("targetLowPrice"),
            analyst_recommendation=info.get("recommendationKey"),
            num_analyst_opinions=info.get("numberOfAnalystOpinions"),
            data_sources=["yfinance"],
        )

    def _fetch_fmp(self, ticker: str) -> Optional[FinancialData]:
        """Fetch data from Financial Modeling Prep."""
        from .financial_modeling_prep import FMPClient

        client = FMPClient(self.config.fmp_api_key)

        # Get company profile
        profile = client.get_company_profile(ticker)
        if not profile:
            return None

        # Get financial ratios
        ratios = client.get_financial_ratios(ticker)

        # Get income statement
        income = client.get_income_statement(ticker)

        data = FinancialData(
            ticker=ticker,
            company_name=profile.company_name if profile else None,
            exchange=profile.exchange if profile else None,
            sector=profile.sector if profile else None,
            industry=profile.industry if profile else None,
            country=profile.country if profile else None,
            employees=profile.employees if profile else None,
            description=profile.description if profile else None,
            website=profile.website if profile else None,
            ceo=profile.ceo if profile else None,
            current_price=profile.price if profile else None,
            market_cap=profile.market_cap if profile else None,
            data_sources=["fmp"],
        )

        # Add income statement data
        if income and len(income) > 0:
            latest = income[0]
            data.revenue = latest.revenue
            data.gross_profit = latest.gross_profit
            data.operating_income = latest.operating_income
            data.net_income = latest.net_income
            data.ebitda = latest.ebitda
            data.eps = latest.eps
            data.gross_margin = latest.gross_profit_ratio
            data.operating_margin = latest.operating_income_ratio
            data.profit_margin = latest.net_income_ratio

        # Add ratios
        if ratios and len(ratios) > 0:
            latest = ratios[0]
            data.pe_ratio = getattr(latest, "pe_ratio", None)
            data.price_to_book = getattr(latest, "price_to_book", None)
            data.debt_to_equity = getattr(latest, "debt_to_equity", None)
            data.current_ratio = getattr(latest, "current_ratio", None)
            data.return_on_equity = getattr(latest, "return_on_equity", None)
            data.return_on_assets = getattr(latest, "return_on_assets", None)

        return data

    def _fetch_finnhub(self, ticker: str) -> Optional[FinancialData]:
        """Fetch data from Finnhub."""
        from .finnhub import FinnhubClient

        client = FinnhubClient(self.config.finnhub_api_key)

        # Get company profile
        profile = client.get_company_profile(ticker)
        if not profile:
            return None

        # Get quote
        quote = client.get_quote(ticker)

        # Get basic financials
        metrics = client.get_basic_financials(ticker)

        data = FinancialData(
            ticker=ticker,
            company_name=profile.get("name"),
            exchange=profile.get("exchange"),
            industry=profile.get("finnhubIndustry"),
            country=profile.get("country"),
            website=profile.get("weburl"),
            market_cap=profile.get("marketCapitalization"),
            data_sources=["finnhub"],
        )

        # Add quote data
        if quote:
            data.current_price = quote.get("c")
            data.day_high = quote.get("h")
            data.day_low = quote.get("l")
            data.previous_close = quote.get("pc")

        # Add metrics
        if metrics and "metric" in metrics:
            m = metrics["metric"]
            data.pe_ratio = m.get("peBasicExclExtraTTM")
            data.eps = m.get("epsBasicExclExtraItemsTTM")
            data.revenue = m.get("revenuePerShareTTM")
            data.fifty_two_week_high = m.get("52WeekHigh")
            data.fifty_two_week_low = m.get("52WeekLow")
            data.beta = m.get("beta")
            data.dividend_yield = m.get("dividendYieldIndicatedAnnual")
            data.return_on_equity = m.get("roeTTM")
            data.return_on_assets = m.get("roaTTM")

        return data

    def _fetch_polygon(self, ticker: str) -> Optional[FinancialData]:
        """Fetch data from Polygon."""
        from .polygon import PolygonClient

        client = PolygonClient(self.config.polygon_api_key)

        # Get ticker details
        details = client.get_ticker_details(ticker)
        if not details:
            return None

        # Get previous close
        previous = client.get_previous_close(ticker)

        data = FinancialData(
            ticker=ticker,
            company_name=details.get("name"),
            description=details.get("description"),
            sector=details.get("sic_description"),
            employees=details.get("total_employees"),
            market_cap=details.get("market_cap"),
            website=details.get("homepage_url"),
            data_sources=["polygon"],
        )

        # Add price data
        if previous and "results" in previous and len(previous["results"]) > 0:
            p = previous["results"][0]
            data.previous_close = p.get("c")
            data.volume = p.get("v")
            data.day_high = p.get("h")
            data.day_low = p.get("l")

        return data

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            name: {
                "status": state.status.value,
                "calls_today": state.calls_today,
                "daily_limit": state.daily_limit,
                "last_call": state.last_call.isoformat() if state.last_call else None,
                "last_error": state.last_error,
            }
            for name, state in self.providers.items()
        }

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()

    def reset_provider(self, name: str):
        """Reset a provider's state."""
        if name in self.providers:
            self.providers[name].status = ProviderStatus.AVAILABLE
            self.providers[name].calls_today = 0
            self.providers[name].last_error = None


# Factory function
def create_financial_provider(config: Any) -> FinancialDataProvider:
    """Create a configured financial data provider."""
    return FinancialDataProvider(config)
