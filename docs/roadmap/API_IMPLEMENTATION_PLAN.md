# Company Researcher API Implementation Plan

> **Comprehensive guide for integrating 25+ APIs to enhance the Company Researcher platform**
> Generated: December 2024 | Based on project analysis and API research

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Implementation Priority Matrix](#implementation-priority-matrix)
3. [Category 1: Business & Company Data APIs](#category-1-business--company-data-apis)
4. [Category 2: Finance APIs](#category-2-finance-apis)
5. [Category 3: News APIs](#category-3-news-apis)
6. [Category 4: Data Enrichment & Validation APIs](#category-4-data-enrichment--validation-apis)
7. [Category 5: Geocoding & Location APIs](#category-5-geocoding--location-apis)
8. [Category 6: ML & AI Enhancement APIs](#category-6-ml--ai-enhancement-apis)
9. [Category 7: Social & Community Data APIs](#category-7-social--community-data-apis)
8. [Architecture Patterns](#architecture-patterns)
9. [Configuration & Environment Setup](#configuration--environment-setup)
10. [Cost Analysis](#cost-analysis)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

### Current State
The Company Researcher already has solid foundations:
- **Existing integrations**: Tavily, NewsAPI, SEC EDGAR, Alpha Vantage, Yahoo Finance, Crunchbase (mock)
- **Architecture**: Multi-provider cascade with circuit breakers, rate limiting, and fallbacks
- **Patterns**: Dataclass models, Pydantic config, singleton clients, LangGraph workflows

### Recommended Additions
| Priority | Category | APIs | Impact |
|----------|----------|------|--------|
| **P0 - Critical** | Finance | Financial Modeling Prep, Finnhub | Complete financial data coverage |
| **P1 - High** | Company Data | Hunter.io, Domainsdb.info | Lead generation & domain intelligence |
| **P2 - Medium** | News | GNews, Mediastack | News source redundancy |
| **P3 - Enhancement** | Geocoding | OpenCage, Nominatim | LATAM market research |
| **P4 - Future** | ML/Social | Hugging Face, Reddit/PRAW | Sentiment & community analysis |

---

## Implementation Priority Matrix

```
                    HIGH IMPACT
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    │  P0: CRITICAL      │  P1: HIGH VALUE    │
    │  - FMP API         │  - Hunter.io       │
    │  - Finnhub         │  - GNews           │
    │  - Polygon.io      │  - OpenCage        │
    │                    │                    │
LOW ├────────────────────┼────────────────────┤ HIGH
EFFORT                   │                    EFFORT
    │                    │                    │
    │  P2: QUICK WINS    │  P3: STRATEGIC     │
    │  - Domainsdb.info  │  - IBM Watson NLU  │
    │  - Nominatim       │  - Hugging Face    │
    │  - Abstract Email  │  - Reddit/PRAW     │
    │  - Mediastack      │  - GitHub API      │
    │                    │                    │
    └────────────────────┴────────────────────┘
                    LOW IMPACT
```

---

## Category 1: Business & Company Data APIs

### 1.1 Clearbit Logo API ⚠️ DEPRECATED

> **STATUS**: Sunsetting December 1, 2025 - DO NOT IMPLEMENT

**Migration Path**: Use [Logo.dev](https://logo.dev) as replacement
- Free tier: 10,000 requests/month
- Simple URL pattern: `https://img.logo.dev/{domain}`

### 1.2 Hunter.io - Email Finder

**Purpose**: Find decision-maker contacts for sales intelligence

| Attribute | Details |
|-----------|---------|
| **Pricing** | Free: 25 searches/month, Starter: $34/mo (500), Growth: $104/mo (5,000) |
| **Rate Limits** | 10 requests/second |
| **Auth** | API Key |
| **Free Tier** | 50 credits/month for development |

**Implementation Plan**:

```
src/company_researcher/integrations/hunter_io.py
```

```python
# Data Models
@dataclass
class EmailResult:
    email: str
    first_name: str
    last_name: str
    position: str
    department: str
    linkedin: Optional[str]
    twitter: Optional[str]
    phone: Optional[str]
    confidence: int  # 0-100
    sources: List[str]

@dataclass
class DomainSearchResult:
    domain: str
    organization: str
    emails: List[EmailResult]
    total_emails: int
    webmail: bool
    pattern: Optional[str]  # e.g., "{first}.{last}"

# Client Implementation
class HunterClient:
    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUNTER_API_KEY")
        self._session: Optional[aiohttp.ClientSession] = None

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def domain_search(
        self,
        domain: str,
        department: Optional[str] = None,  # executive, finance, sales, etc.
        limit: int = 10
    ) -> DomainSearchResult:
        """Find all emails associated with a domain"""

    async def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str
    ) -> Optional[EmailResult]:
        """Find specific person's email"""

    async def email_verifier(self, email: str) -> Dict[str, Any]:
        """Verify if email is deliverable"""
```

**Agent Integration**:
```python
# In sales_intelligence.py agent
from ...integrations.hunter_io import HunterClient

async def enrich_with_contacts(company_domain: str) -> Dict:
    client = HunterClient()
    if client.is_available():
        result = await client.domain_search(
            domain=company_domain,
            department="executive",
            limit=5
        )
        return {
            "key_contacts": [
                {
                    "name": f"{e.first_name} {e.last_name}",
                    "position": e.position,
                    "email": e.email,
                    "confidence": e.confidence
                }
                for e in result.emails
            ],
            "email_pattern": result.pattern
        }
    return {}
```

**Files to Create/Modify**:
1. `src/company_researcher/integrations/hunter_io.py` - Client implementation
2. `src/company_researcher/config.py` - Add `hunter_api_key` field
3. `src/company_researcher/agents/specialized/sales_intelligence.py` - Integrate
4. `env.example` - Add `HUNTER_API_KEY=`

---

### 1.3 Tomba.io - B2B Email Finder

**Purpose**: Alternative/complement to Hunter.io for email discovery

| Attribute | Details |
|-----------|---------|
| **Pricing** | Free: 25 searches/month, Starter: $39/mo (1,000) |
| **Rate Limits** | 1 request/second (free), 5/second (paid) |
| **Auth** | API Key + Secret |

**Implementation Plan**:

```python
# src/company_researcher/integrations/tomba_io.py

@dataclass
class TombaEmailResult:
    email: str
    type: str  # personal, generic
    confidence: int
    first_name: str
    last_name: str
    full_name: str
    position: str
    department: str
    linkedin: Optional[str]
    twitter: Optional[str]
    sources: List[Dict]
    last_updated: str

class TombaClient:
    BASE_URL = "https://api.tomba.io/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("TOMBA_API_KEY")
        self.secret = secret or os.getenv("TOMBA_SECRET")

    async def domain_search(self, domain: str) -> List[TombaEmailResult]:
        """Search for emails by domain"""

    async def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str
    ) -> Optional[TombaEmailResult]:
        """Find specific person's email"""

    async def author_finder(self, url: str) -> Optional[TombaEmailResult]:
        """Find author email from article URL"""

    async def enrichment(self, email: str) -> Dict[str, Any]:
        """Enrich email with additional data"""
```

**Cascade Strategy** (with Hunter.io):
```python
# In a unified email finder service
class EmailFinderService:
    def __init__(self):
        self.hunter = HunterClient()
        self.tomba = TombaClient()

    async def find_emails(self, domain: str, limit: int = 10) -> List[Dict]:
        # Try Hunter first (usually better US coverage)
        if self.hunter.is_available():
            try:
                result = await self.hunter.domain_search(domain, limit=limit)
                if result.emails:
                    return self._normalize_hunter(result.emails)
            except RateLimitError:
                pass

        # Fallback to Tomba
        if self.tomba.is_available():
            result = await self.tomba.domain_search(domain)
            return self._normalize_tomba(result)

        return []
```

---

### 1.4 Domainsdb.info - Domain Search

**Purpose**: Research company web presence, find related domains

| Attribute | Details |
|-----------|---------|
| **Pricing** | **FREE** - No API key required |
| **Rate Limits** | Reasonable use (undocumented) |
| **Data** | 260M+ domains, 1000+ TLDs |
| **Max Results** | 100 per query |

**Implementation Plan**:

```python
# src/company_researcher/integrations/domainsdb.py

@dataclass
class DomainInfo:
    domain: str
    create_date: Optional[str]
    update_date: Optional[str]
    country: Optional[str]
    is_dead: bool
    a_record: Optional[List[str]]
    ns_record: Optional[List[str]]
    mx_record: Optional[List[str]]

class DomainsDBClient:
    """Free domain search API - no authentication required"""

    BASE_URL = "https://api.domainsdb.info/v1"

    async def search_domains(
        self,
        query: str,
        zone: str = "com",  # TLD filter
        page: int = 1,
        limit: int = 50
    ) -> List[DomainInfo]:
        """
        Search for domains containing query string.

        Args:
            query: Search term (e.g., company name)
            zone: TLD to search (com, net, org, etc.)
            page: Pagination
            limit: Results per page (max 100)

        Example:
            # Find all domains containing "techcorp"
            results = await client.search_domains("techcorp", zone="com")
        """
        url = f"{self.BASE_URL}/domains/search"
        params = {
            "domain": query,
            "zone": zone,
            "page": page,
            "limit": limit
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return [DomainInfo(**d) for d in data.get("domains", [])]

    async def find_related_domains(
        self,
        company_name: str
    ) -> Dict[str, List[DomainInfo]]:
        """Find all related domains across popular TLDs"""
        zones = ["com", "net", "org", "io", "co", "ai"]
        results = {}

        for zone in zones:
            domains = await self.search_domains(company_name, zone=zone)
            if domains:
                results[zone] = domains

        return results
```

**Use Cases**:
1. Find all domains owned by a company
2. Discover subsidiaries/brands
3. Competitive domain analysis
4. Trademark/brand protection research

---

### 1.5 ORB Intelligence (by D&B)

**Purpose**: Company lookup & enrichment with firmographic data

| Attribute | Details |
|-----------|---------|
| **Pricing** | Custom quotes only (enterprise-focused) |
| **Data** | 45M+ companies globally, corporate hierarchies |
| **Auth** | API Key |

**Recommendation**: **DEFER** - Enterprise pricing, use alternatives first
- Consider: Clearbit Enrichment, Apollo.io, or Crunchbase Pro
- The existing Crunchbase mock can be extended to use their actual API

---

## Category 2: Finance APIs

### 2.1 Alpha Vantage (Already Implemented - Enhancement)

**Current State**: Mock implementation in `tools/alpha_vantage_client.py`

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 25 requests/day, 5 requests/minute |
| **Premium** | $49.99/mo (75 req/min), $249.99/mo (150 req/min) |
| **Endpoints** | Stock quotes, fundamentals, forex, crypto |

**Enhancement Plan**:
```python
# Enhance existing client with production implementation

class AlphaVantageClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self._cache = TTLCache(maxsize=1000, ttl=21600)  # 6-hour cache
        self._rate_limiter = RateLimiter(calls=5, period=60)

    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamentals: market cap, PE ratio, etc."""

    async def get_income_statement(
        self,
        symbol: str,
        annual: bool = True
    ) -> List[Dict]:
        """Get income statement data"""

    async def get_balance_sheet(self, symbol: str) -> List[Dict]:
        """Get balance sheet data"""

    async def get_cash_flow(self, symbol: str) -> List[Dict]:
        """Get cash flow statement"""

    async def get_earnings(self, symbol: str) -> Dict:
        """Get earnings data and estimates"""
```

---

### 2.2 Financial Modeling Prep (FMP) - **HIGH PRIORITY**

**Purpose**: Comprehensive financial data - DCF, statements, ratios

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 250 requests/day |
| **Starter** | $14/mo (300 req/day) |
| **Premium** | $29/mo (750 req/day) |
| **Ultimate** | $49/mo (unlimited) |
| **Coverage** | US + International stocks |

**Implementation Plan**:

```python
# src/company_researcher/integrations/financial_modeling_prep.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import date
import aiohttp

@dataclass
class IncomeStatement:
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

@dataclass
class BalanceSheet:
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

@dataclass
class KeyMetrics:
    symbol: str
    date: str
    market_cap: float
    pe_ratio: float
    price_to_sales: float
    price_to_book: float
    enterprise_value: float
    ev_to_ebitda: float
    ev_to_revenue: float
    debt_to_equity: float
    current_ratio: float
    roe: float
    roa: float
    roic: float
    revenue_growth: float
    earnings_growth: float

@dataclass
class DCFValue:
    symbol: str
    date: str
    dcf: float
    stock_price: float

@dataclass
class CompanyProfile:
    symbol: str
    company_name: str
    exchange: str
    industry: str
    sector: str
    country: str
    description: str
    ceo: str
    employees: int
    website: str
    ipo_date: str
    market_cap: float


class FMPClient:
    """Financial Modeling Prep API Client"""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache = TTLCache(maxsize=500, ttl=3600)  # 1-hour cache

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def _request(self, endpoint: str, params: Dict = None) -> Any:
        """Make API request with caching and rate limiting"""
        cache_key = f"{endpoint}:{params}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        params = params or {}
        params["apikey"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        async with self._get_session() as session:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("FMP rate limit exceeded")
                response.raise_for_status()
                data = await response.json()
                self._cache[cache_key] = data
                return data

    # Company Profile
    async def get_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile and basic info"""
        data = await self._request(f"profile/{symbol}")
        if data and len(data) > 0:
            return CompanyProfile(**data[0])
        return None

    # Financial Statements
    async def get_income_statement(
        self,
        symbol: str,
        period: str = "annual",  # annual or quarter
        limit: int = 5
    ) -> List[IncomeStatement]:
        """Get income statement history"""
        endpoint = f"income-statement/{symbol}"
        data = await self._request(endpoint, {"period": period, "limit": limit})
        return [IncomeStatement(**item) for item in data]

    async def get_balance_sheet(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[BalanceSheet]:
        """Get balance sheet history"""
        endpoint = f"balance-sheet-statement/{symbol}"
        data = await self._request(endpoint, {"period": period, "limit": limit})
        return [BalanceSheet(**item) for item in data]

    async def get_cash_flow(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict]:
        """Get cash flow statement history"""
        return await self._request(
            f"cash-flow-statement/{symbol}",
            {"period": period, "limit": limit}
        )

    # Valuation & Metrics
    async def get_key_metrics(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5
    ) -> List[KeyMetrics]:
        """Get key financial metrics and ratios"""
        data = await self._request(
            f"key-metrics/{symbol}",
            {"period": period, "limit": limit}
        )
        return [KeyMetrics(**item) for item in data]

    async def get_dcf(self, symbol: str) -> Optional[DCFValue]:
        """Get discounted cash flow valuation"""
        data = await self._request(f"discounted-cash-flow/{symbol}")
        if data and len(data) > 0:
            return DCFValue(**data[0])
        return None

    async def get_rating(self, symbol: str) -> Dict:
        """Get company rating (buy/hold/sell)"""
        return await self._request(f"rating/{symbol}")

    async def get_financial_ratios(
        self,
        symbol: str,
        period: str = "annual"
    ) -> List[Dict]:
        """Get comprehensive financial ratios"""
        return await self._request(
            f"ratios/{symbol}",
            {"period": period}
        )

    # Search & Discovery
    async def search_company(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for companies by name"""
        return await self._request(
            "search",
            {"query": query, "limit": limit}
        )

    async def get_stock_peers(self, symbol: str) -> List[str]:
        """Get list of peer/competitor symbols"""
        data = await self._request(f"stock_peers?symbol={symbol}")
        return data[0].get("peersList", []) if data else []

    # News
    async def get_stock_news(
        self,
        symbol: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get stock-related news"""
        params = {"limit": limit}
        if symbol:
            params["tickers"] = symbol
        return await self._request("stock_news", params)
```

**Agent Integration** (Enhanced Financial Agent):

```python
# src/company_researcher/agents/financial/enhanced_financial.py

from ...integrations.financial_modeling_prep import FMPClient

class EnhancedFinancialAgent:
    def __init__(self):
        self.fmp = FMPClient()
        self.alpha_vantage = AlphaVantageClient()

    async def analyze_financials(
        self,
        company_name: str,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive financial analysis using multiple sources.
        """
        results = {
            "profile": None,
            "income_statement": [],
            "balance_sheet": [],
            "key_metrics": [],
            "dcf_valuation": None,
            "rating": None,
            "peers": [],
            "data_sources": []
        }

        # Resolve symbol if not provided
        if not symbol and self.fmp.is_available():
            search_results = await self.fmp.search_company(company_name)
            if search_results:
                symbol = search_results[0]["symbol"]

        if not symbol:
            return results

        # Gather data from FMP (primary)
        if self.fmp.is_available():
            try:
                results["profile"] = await self.fmp.get_profile(symbol)
                results["income_statement"] = await self.fmp.get_income_statement(symbol)
                results["balance_sheet"] = await self.fmp.get_balance_sheet(symbol)
                results["key_metrics"] = await self.fmp.get_key_metrics(symbol)
                results["dcf_valuation"] = await self.fmp.get_dcf(symbol)
                results["rating"] = await self.fmp.get_rating(symbol)
                results["peers"] = await self.fmp.get_stock_peers(symbol)
                results["data_sources"].append("Financial Modeling Prep")
            except Exception as e:
                logger.warning(f"FMP error: {e}")

        # Fallback to Alpha Vantage for missing data
        if self.alpha_vantage.is_available() and not results["income_statement"]:
            try:
                # Fill in gaps from Alpha Vantage
                results["data_sources"].append("Alpha Vantage")
            except Exception as e:
                logger.warning(f"Alpha Vantage error: {e}")

        return results
```

---

### 2.3 Finnhub - Stock Data + News

**Purpose**: Real-time market data with news and sentiment

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 60 API calls/minute |
| **Premium** | $49/mo (300 calls/min), $149/mo (600 calls/min) |
| **Features** | Real-time quotes, fundamentals, news, earnings, IPO calendar |

**Implementation Plan**:

```python
# src/company_researcher/integrations/finnhub.py

@dataclass
class CompanyNews:
    category: str
    datetime: int
    headline: str
    id: int
    image: str
    related: str
    source: str
    summary: str
    url: str

@dataclass
class EarningsCalendar:
    date: str
    eps_actual: Optional[float]
    eps_estimate: Optional[float]
    hour: str  # bmo (before market open), amc (after market close)
    quarter: int
    revenue_actual: Optional[float]
    revenue_estimate: Optional[float]
    symbol: str
    year: int

@dataclass
class CompanyMetrics:
    metric: Dict[str, Any]  # 50+ financial metrics
    symbol: str

class FinnhubClient:
    """Finnhub Stock API Client"""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        self._rate_limiter = RateLimiter(calls=60, period=60)

    # Quote & Price
    async def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        return await self._request("quote", {"symbol": symbol})

    # Company Info
    async def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile"""
        return await self._request("stock/profile2", {"symbol": symbol})

    # News
    async def get_company_news(
        self,
        symbol: str,
        from_date: str,  # YYYY-MM-DD
        to_date: str
    ) -> List[CompanyNews]:
        """Get company news in date range"""
        data = await self._request("company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        return [CompanyNews(**item) for item in data]

    async def get_market_news(self, category: str = "general") -> List[Dict]:
        """Get market news by category"""
        return await self._request("news", {"category": category})

    # Sentiment
    async def get_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment analysis"""
        return await self._request("news-sentiment", {"symbol": symbol})

    async def get_social_sentiment(self, symbol: str) -> Dict:
        """Get social media sentiment (Reddit, Twitter)"""
        return await self._request("stock/social-sentiment", {"symbol": symbol})

    # Fundamentals
    async def get_basic_financials(
        self,
        symbol: str,
        metric: str = "all"
    ) -> CompanyMetrics:
        """Get basic financial metrics"""
        data = await self._request("stock/metric", {
            "symbol": symbol,
            "metric": metric
        })
        return CompanyMetrics(**data)

    # Earnings
    async def get_earnings_calendar(
        self,
        from_date: str,
        to_date: str,
        symbol: Optional[str] = None
    ) -> List[EarningsCalendar]:
        """Get earnings calendar"""
        params = {"from": from_date, "to": to_date}
        if symbol:
            params["symbol"] = symbol
        data = await self._request("calendar/earnings", params)
        return [EarningsCalendar(**item) for item in data.get("earningsCalendar", [])]

    # Peers
    async def get_peers(self, symbol: str) -> List[str]:
        """Get company peers/competitors"""
        return await self._request("stock/peers", {"symbol": symbol})

    # Recommendations
    async def get_recommendations(self, symbol: str) -> List[Dict]:
        """Get analyst recommendations"""
        return await self._request("stock/recommendation", {"symbol": symbol})

    # Price Target
    async def get_price_target(self, symbol: str) -> Dict:
        """Get analyst price targets"""
        return await self._request("stock/price-target", {"symbol": symbol})
```

---

### 2.4 Polygon.io - Historical Stock Data

**Purpose**: Comprehensive historical tick data for analysis

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 5 API calls/minute, delayed data |
| **Starter** | $29/mo (unlimited delayed) |
| **Developer** | $79/mo (unlimited real-time) |
| **Features** | 20+ years of data, every trade/quote |

**Implementation Plan**:

```python
# src/company_researcher/integrations/polygon.py

@dataclass
class StockBar:
    ticker: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    num_transactions: int

@dataclass
class TickerDetails:
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

class PolygonClient:
    """Polygon.io Stock Market API"""

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")

    # Aggregates (Historical Bars)
    async def get_aggregates(
        self,
        ticker: str,
        multiplier: int = 1,
        timespan: str = "day",  # minute, hour, day, week, month, quarter, year
        from_date: str = None,
        to_date: str = None,
        limit: int = 120
    ) -> List[StockBar]:
        """Get aggregate bars for a stock"""
        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        data = await self._request(endpoint, {"limit": limit})
        return [StockBar(ticker=ticker, **bar) for bar in data.get("results", [])]

    # Ticker Details
    async def get_ticker_details(self, ticker: str) -> TickerDetails:
        """Get detailed info about a ticker"""
        data = await self._request(f"/v3/reference/tickers/{ticker}")
        return TickerDetails(**data.get("results", {}))

    # Related Companies
    async def get_related_companies(self, ticker: str) -> List[str]:
        """Get related companies/tickers"""
        data = await self._request(f"/v1/related-companies/{ticker}")
        return [item["ticker"] for item in data.get("results", [])]

    # News
    async def get_ticker_news(
        self,
        ticker: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get news for a ticker"""
        return await self._request(
            f"/v2/reference/news",
            {"ticker": ticker, "limit": limit}
        )

    # Financials
    async def get_financials(
        self,
        ticker: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get financial statements"""
        data = await self._request(
            f"/vX/reference/financials",
            {"ticker": ticker, "limit": limit}
        )
        return data.get("results", [])
```

---

### 2.5 SEC EDGAR (Already Implemented - Enhancement)

**Current State**: `integrations/sec_edgar.py` with basic filing retrieval

**Enhancement Plan**:
```python
# Add XBRL parsing for structured financial extraction

class EnhancedSECClient(SECEdgarClient):
    async def get_financial_facts(
        self,
        cik: str,
        concept: str = "us-gaap"
    ) -> Dict[str, Any]:
        """
        Get structured financial facts from XBRL data.

        Concepts include:
        - Revenues
        - NetIncomeLoss
        - Assets
        - Liabilities
        - StockholdersEquity
        - OperatingIncomeLoss
        - EarningsPerShareBasic
        """

    async def get_company_concept(
        self,
        cik: str,
        taxonomy: str,
        tag: str
    ) -> List[Dict]:
        """Get specific financial concept over time"""

    async def compare_companies(
        self,
        ciks: List[str],
        metrics: List[str]
    ) -> Dict[str, Dict]:
        """Compare financial metrics across companies"""
```

---

### 2.6 Finance API Cascade Service

**Purpose**: Unified service with intelligent fallback between all finance APIs

```python
# src/company_researcher/services/financial_data_service.py

class FinancialDataService:
    """
    Unified financial data service with multi-provider fallback.

    Priority order:
    1. Financial Modeling Prep (comprehensive, affordable)
    2. Finnhub (real-time, news integration)
    3. Polygon.io (historical depth)
    4. Alpha Vantage (fallback)
    5. Yahoo Finance (free fallback)
    6. SEC EDGAR (public filings)
    """

    def __init__(self):
        self.fmp = FMPClient()
        self.finnhub = FinnhubClient()
        self.polygon = PolygonClient()
        self.alpha_vantage = AlphaVantageClient()
        self.yahoo = YahooFinanceClient()
        self.sec = SECEdgarClient()

        self.circuit_breakers = {
            "fmp": CircuitBreaker(failure_threshold=3),
            "finnhub": CircuitBreaker(failure_threshold=3),
            "polygon": CircuitBreaker(failure_threshold=3),
            "alpha_vantage": CircuitBreaker(failure_threshold=3),
        }

    async def get_company_financials(
        self,
        identifier: str,  # ticker symbol or company name
        include_historical: bool = True,
        include_news: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial data from best available source.
        """
        result = {
            "profile": None,
            "quote": None,
            "financials": {
                "income_statement": [],
                "balance_sheet": [],
                "cash_flow": [],
            },
            "metrics": None,
            "valuation": None,
            "news": [],
            "peers": [],
            "data_sources": [],
            "errors": []
        }

        # Resolve ticker if needed
        ticker = await self._resolve_ticker(identifier)
        if not ticker:
            result["errors"].append(f"Could not resolve ticker for: {identifier}")
            return result

        # Get profile (FMP → Finnhub → Polygon)
        result["profile"] = await self._get_with_fallback(
            [
                (self.fmp, "get_profile", ticker),
                (self.finnhub, "get_company_profile", ticker),
                (self.polygon, "get_ticker_details", ticker),
            ]
        )

        # Get financials (FMP → SEC → Alpha Vantage)
        if include_historical:
            result["financials"] = await self._get_financials_with_fallback(ticker)

        # Get real-time quote (Finnhub → Polygon → Yahoo)
        result["quote"] = await self._get_with_fallback(
            [
                (self.finnhub, "get_quote", ticker),
                (self.yahoo, "get_quote", ticker),
            ]
        )

        # Get news (Finnhub → FMP)
        if include_news:
            result["news"] = await self._get_news_with_fallback(ticker)

        return result
```

---

## Category 3: News APIs

### 3.1 NewsAPI (Already Implemented - Enhancement)

**Current State**: `integrations/news_api.py`

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 requests/day (development only) |
| **Business** | $449/mo (250,000 requests) |
| **Limitation** | Free tier blocked in production |

**Enhancement**: Add caching and source prioritization

---

### 3.2 GNews - Google News Alternative

**Purpose**: Google News-quality results with simpler pricing

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 requests/day |
| **Basic** | $29/mo (1,000 req/day) |
| **Pro** | $79/mo (10,000 req/day) |
| **Features** | 60,000+ sources, real-time |

**Implementation Plan**:

```python
# src/company_researcher/integrations/gnews.py

@dataclass
class GNewsArticle:
    title: str
    description: str
    content: str
    url: str
    image: Optional[str]
    published_at: str
    source: Dict[str, str]  # name, url

class GNewsClient:
    """GNews API Client"""

    BASE_URL = "https://gnews.io/api/v4"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GNEWS_API_KEY")

    async def search(
        self,
        query: str,
        lang: str = "en",
        country: Optional[str] = None,
        max_results: int = 10,
        from_date: Optional[str] = None,  # YYYY-MM-DDThh:mm:ssZ
        to_date: Optional[str] = None,
        sort_by: str = "publishedAt"  # publishedAt, relevance
    ) -> List[GNewsArticle]:
        """
        Search for news articles.

        Query operators:
        - AND, OR, NOT
        - Exact phrase: "company name"
        - Exclude: -word
        """
        params = {
            "q": query,
            "lang": lang,
            "max": max_results,
            "sortby": sort_by,
            "apikey": self.api_key
        }

        if country:
            params["country"] = country
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = await self._request("search", params)
        return [GNewsArticle(**article) for article in data.get("articles", [])]

    async def get_top_headlines(
        self,
        category: Optional[str] = None,  # business, technology, etc.
        country: str = "us",
        lang: str = "en",
        max_results: int = 10
    ) -> List[GNewsArticle]:
        """Get top headlines by category"""
        params = {
            "country": country,
            "lang": lang,
            "max": max_results,
            "apikey": self.api_key
        }

        if category:
            params["topic"] = category  # business, tech, etc.

        data = await self._request("top-headlines", params)
        return [GNewsArticle(**article) for article in data.get("articles", [])]

    async def get_company_news(
        self,
        company_name: str,
        days_back: int = 7,
        max_results: int = 20
    ) -> List[GNewsArticle]:
        """Get recent news about a company"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")

        return await self.search(
            query=f'"{company_name}"',
            from_date=from_date,
            max_results=max_results,
            sort_by="relevance"
        )
```

---

### 3.3 Mediastack - Live News API

**Purpose**: Real-time news with historical access

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 500 requests/month, 15-min delay |
| **Basic** | $12.99/mo (10,000 requests) |
| **Standard** | $49.99/mo (50,000 requests) |
| **Features** | 7,500+ sources, 50+ countries |

**Implementation Plan**:

```python
# src/company_researcher/integrations/mediastack.py

@dataclass
class MediastackArticle:
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

class MediastackClient:
    """Mediastack News API Client"""

    BASE_URL = "http://api.mediastack.com/v1"

    async def get_live_news(
        self,
        keywords: Optional[str] = None,
        sources: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,  # business, technology, etc.
        countries: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> List[MediastackArticle]:
        """Get live news articles"""

    async def get_historical_news(
        self,
        keywords: str,
        date: str,  # YYYY-MM-DD
        limit: int = 25
    ) -> List[MediastackArticle]:
        """Get historical news (paid plans only)"""
```

---

### 3.4 News API Cascade Service

```python
# src/company_researcher/services/news_service.py

class NewsService:
    """
    Unified news service with multi-provider fallback.

    Priority:
    1. NewsAPI (existing, best coverage)
    2. GNews (Google-quality, affordable)
    3. Mediastack (backup)
    4. Finnhub (stock-specific)
    """

    def __init__(self):
        self.newsapi = NewsAPIClient()
        self.gnews = GNewsClient()
        self.mediastack = MediastackClient()
        self.finnhub = FinnhubClient()

    async def get_company_news(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        days_back: int = 7,
        max_results: int = 20
    ) -> List[Dict]:
        """Get company news from best available source"""

        articles = []
        sources_used = []

        # Try NewsAPI first
        if self.newsapi.is_available():
            try:
                result = await self.newsapi.search(company_name, days_back=days_back)
                articles.extend(self._normalize_newsapi(result))
                sources_used.append("NewsAPI")
            except Exception as e:
                logger.warning(f"NewsAPI error: {e}")

        # Supplement with GNews if needed
        if len(articles) < max_results and self.gnews.is_available():
            try:
                result = await self.gnews.get_company_news(
                    company_name,
                    days_back=days_back,
                    max_results=max_results - len(articles)
                )
                articles.extend(self._normalize_gnews(result))
                sources_used.append("GNews")
            except Exception as e:
                logger.warning(f"GNews error: {e}")

        # Add stock-specific news from Finnhub
        if ticker and self.finnhub.is_available():
            try:
                from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                to_date = datetime.now().strftime("%Y-%m-%d")
                result = await self.finnhub.get_company_news(ticker, from_date, to_date)
                articles.extend(self._normalize_finnhub(result))
                sources_used.append("Finnhub")
            except Exception as e:
                logger.warning(f"Finnhub error: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)

        return {
            "articles": unique_articles[:max_results],
            "sources_used": sources_used,
            "total_found": len(unique_articles)
        }
```

---

## Category 4: Data Enrichment & Validation APIs

### 4.1 Abstract Email Validation

**Purpose**: Verify contact emails are deliverable

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 verifications/month |
| **Paid** | $15/mo (5,000), $29/mo (15,000) |
| **Features** | SMTP verification, MX check, disposable detection |

**Implementation Plan**:

```python
# src/company_researcher/integrations/abstract_email.py

@dataclass
class EmailValidationResult:
    email: str
    deliverability: str  # DELIVERABLE, UNDELIVERABLE, UNKNOWN
    quality_score: float  # 0.0 to 1.0
    is_valid_format: bool
    is_free_email: bool
    is_disposable_email: bool
    is_role_email: bool
    is_catchall_email: bool
    is_mx_found: bool
    is_smtp_valid: bool
    autocorrect: Optional[str]  # Suggested correction

class AbstractEmailClient:
    """Abstract Email Validation API"""

    BASE_URL = "https://emailvalidation.abstractapi.com/v1"

    async def validate_email(self, email: str) -> EmailValidationResult:
        """Validate a single email address"""
        params = {
            "api_key": self.api_key,
            "email": email
        }
        data = await self._request("", params)
        return EmailValidationResult(**data)

    async def validate_batch(
        self,
        emails: List[str]
    ) -> List[EmailValidationResult]:
        """Validate multiple emails (with rate limiting)"""
        results = []
        for email in emails:
            result = await self.validate_email(email)
            results.append(result)
            await asyncio.sleep(0.2)  # Rate limit
        return results
```

---

### 4.2 NumVerify - Phone Validation

**Purpose**: Validate contact phone numbers

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 requests/month |
| **Basic** | $14.99/mo (5,000 requests) |
| **Features** | Number validation, carrier lookup, line type |

```python
# src/company_researcher/integrations/numverify.py

@dataclass
class PhoneValidationResult:
    valid: bool
    number: str
    local_format: str
    international_format: str
    country_prefix: str
    country_code: str
    country_name: str
    location: str
    carrier: str
    line_type: str  # mobile, landline, voip

class NumVerifyClient:
    BASE_URL = "http://apilayer.net/api"

    async def validate_phone(
        self,
        number: str,
        country_code: Optional[str] = None
    ) -> PhoneValidationResult:
        """Validate phone number"""
```

---

### 4.3 IPStack - IP Geolocation

**Purpose**: Company location data from IP addresses

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 requests/month |
| **Basic** | $9.99/mo (50,000 requests) |

```python
# src/company_researcher/integrations/ipstack.py

@dataclass
class IPLocation:
    ip: str
    type: str  # ipv4, ipv6
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: str
    latitude: float
    longitude: float

class IPStackClient:
    async def lookup(self, ip: str) -> IPLocation:
        """Get location data for IP address"""
```

---

## Category 5: Geocoding & Location APIs

### 5.1 OpenCage Geocoding

**Purpose**: Address lookup for LATAM market research

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 2,500 requests/day |
| **Small** | $50/mo (10,000/day) |
| **Medium** | $100/mo (25,000/day) |
| **Rate Limit** | 1 request/second (free), higher for paid |

**Implementation Plan**:

```python
# src/company_researcher/integrations/opencage.py

@dataclass
class GeocodingResult:
    formatted: str  # Full formatted address
    latitude: float
    longitude: float
    country: str
    country_code: str
    state: str
    city: str
    postcode: str
    road: str
    confidence: int  # 1-10
    bounds: Dict[str, float]  # northeast, southwest
    timezone: str
    currency: Dict[str, str]

@dataclass
class ReverseGeocodingResult:
    formatted: str
    components: Dict[str, str]
    annotations: Dict[str, Any]

class OpenCageClient:
    """OpenCage Geocoding API"""

    BASE_URL = "https://api.opencagedata.com/geocode/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENCAGE_API_KEY")
        self._rate_limiter = RateLimiter(calls=1, period=1)  # Free tier

    async def geocode(
        self,
        query: str,
        country_code: Optional[str] = None,
        language: str = "en",
        limit: int = 5
    ) -> List[GeocodingResult]:
        """
        Forward geocoding: address/place name → coordinates

        Examples:
            - "Av. Paulista 1578, São Paulo, Brazil"
            - "Microsoft headquarters"
        """
        params = {
            "q": query,
            "key": self.api_key,
            "language": language,
            "limit": limit,
            "no_annotations": 0
        }

        if country_code:
            params["countrycode"] = country_code

        await self._rate_limiter.acquire()
        data = await self._request("json", params)

        results = []
        for item in data.get("results", []):
            results.append(GeocodingResult(
                formatted=item.get("formatted"),
                latitude=item["geometry"]["lat"],
                longitude=item["geometry"]["lng"],
                country=item["components"].get("country", ""),
                country_code=item["components"].get("country_code", ""),
                state=item["components"].get("state", ""),
                city=item["components"].get("city", item["components"].get("town", "")),
                postcode=item["components"].get("postcode", ""),
                road=item["components"].get("road", ""),
                confidence=item.get("confidence", 0),
                bounds=item.get("bounds", {}),
                timezone=item.get("annotations", {}).get("timezone", {}).get("name", ""),
                currency=item.get("annotations", {}).get("currency", {})
            ))

        return results

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        language: str = "en"
    ) -> Optional[ReverseGeocodingResult]:
        """
        Reverse geocoding: coordinates → address
        """
        params = {
            "q": f"{latitude},{longitude}",
            "key": self.api_key,
            "language": language
        }

        await self._rate_limiter.acquire()
        data = await self._request("json", params)

        if data.get("results"):
            item = data["results"][0]
            return ReverseGeocodingResult(
                formatted=item.get("formatted"),
                components=item.get("components", {}),
                annotations=item.get("annotations", {})
            )
        return None

    async def get_company_location(
        self,
        company_name: str,
        country: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        """Get company headquarters location"""
        query = f"{company_name} headquarters"
        if country:
            query += f", {country}"

        results = await self.geocode(query, limit=1)
        return results[0] if results else None
```

---

### 5.2 Nominatim (OpenStreetMap) - FREE

**Purpose**: Free geocoding fallback

| Attribute | Details |
|-----------|---------|
| **Pricing** | **FREE** |
| **Rate Limit** | 1 request/second |
| **Terms** | Attribution required, no heavy usage |

```python
# src/company_researcher/integrations/nominatim.py

class NominatimClient:
    """OpenStreetMap Nominatim - Free geocoding"""

    BASE_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "CompanyResearcher/1.0"  # Required by ToS

    async def search(
        self,
        query: str,
        country_codes: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search for a location"""

    async def reverse(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict]:
        """Reverse geocode coordinates"""
```

---

### 5.3 GeoDB Cities

**Purpose**: City/region data for market sizing

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 1,000 requests/day |
| **Basic** | $10/mo (10,000/day) |
| **Features** | City data, population, distance calculations |

```python
# src/company_researcher/integrations/geodb.py

@dataclass
class City:
    id: int
    name: str
    country: str
    country_code: str
    region: str
    region_code: str
    latitude: float
    longitude: float
    population: int

class GeoDBClient:
    """GeoDB Cities API"""

    BASE_URL = "https://wft-geo-db.p.rapidapi.com/v1/geo"

    async def search_cities(
        self,
        name_prefix: str,
        country_code: Optional[str] = None,
        min_population: int = 0,
        limit: int = 10
    ) -> List[City]:
        """Search for cities by name"""

    async def get_city(self, city_id: int) -> City:
        """Get city details"""

    async def get_nearby_cities(
        self,
        city_id: int,
        radius: int = 100,  # km
        min_population: int = 0
    ) -> List[City]:
        """Get cities near a location"""

    async def get_country_cities(
        self,
        country_code: str,
        min_population: int = 100000,
        limit: int = 50
    ) -> List[City]:
        """Get major cities in a country"""
```

---

## Category 6: ML & AI Enhancement APIs

### 6.1 IBM Watson Natural Language Understanding

**Purpose**: Advanced text analysis, sentiment, entity extraction

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 30,000 NLU items/month |
| **Standard** | $0.003/item after free tier |
| **Features** | Sentiment, emotion, entities, keywords, concepts |

**Implementation Plan**:

```python
# src/company_researcher/integrations/watson_nlu.py

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EntitiesOptions, KeywordsOptions, EmotionOptions, ConceptsOptions

@dataclass
class NLUAnalysis:
    sentiment: Dict[str, Any]  # document and targeted sentiment
    emotions: Dict[str, float]  # sadness, joy, fear, disgust, anger
    entities: List[Dict]  # named entities with relevance
    keywords: List[Dict]  # key phrases with relevance
    concepts: List[Dict]  # high-level concepts

class WatsonNLUClient:
    """IBM Watson Natural Language Understanding"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("WATSON_NLU_API_KEY")
        self.url = url or os.getenv("WATSON_NLU_URL")

        if self.api_key and self.url:
            from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
            authenticator = IAMAuthenticator(self.api_key)
            self.nlu = NaturalLanguageUnderstandingV1(
                version='2022-04-07',
                authenticator=authenticator
            )
            self.nlu.set_service_url(self.url)
        else:
            self.nlu = None

    def is_available(self) -> bool:
        return self.nlu is not None

    async def analyze_text(
        self,
        text: str,
        features: List[str] = None  # sentiment, emotion, entities, keywords, concepts
    ) -> NLUAnalysis:
        """
        Analyze text with Watson NLU.

        Args:
            text: Text to analyze (up to 50KB)
            features: List of features to extract
        """
        features = features or ["sentiment", "emotion", "entities", "keywords"]

        feature_objects = Features(
            sentiment=SentimentOptions() if "sentiment" in features else None,
            emotion=EmotionOptions() if "emotion" in features else None,
            entities=EntitiesOptions(
                sentiment=True,
                limit=10
            ) if "entities" in features else None,
            keywords=KeywordsOptions(
                sentiment=True,
                emotion=True,
                limit=10
            ) if "keywords" in features else None,
            concepts=ConceptsOptions(
                limit=5
            ) if "concepts" in features else None
        )

        response = self.nlu.analyze(
            text=text,
            features=feature_objects
        ).get_result()

        return NLUAnalysis(
            sentiment=response.get("sentiment", {}),
            emotions=response.get("emotion", {}).get("document", {}).get("emotion", {}),
            entities=response.get("entities", []),
            keywords=response.get("keywords", []),
            concepts=response.get("concepts", [])
        )

    async def analyze_news_sentiment(
        self,
        articles: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple news articles.

        Returns aggregate sentiment and key themes.
        """
        all_text = " ".join([
            f"{a.get('title', '')}. {a.get('description', '')}"
            for a in articles
        ])

        analysis = await self.analyze_text(
            all_text,
            features=["sentiment", "keywords", "entities"]
        )

        return {
            "overall_sentiment": analysis.sentiment,
            "key_themes": [k["text"] for k in analysis.keywords[:5]],
            "mentioned_entities": [e["text"] for e in analysis.entities[:10]],
            "article_count": len(articles)
        }
```

---

### 6.2 Hugging Face Inference API

**Purpose**: Custom NLP models for specialized analysis

| Attribute | Details |
|-----------|---------|
| **Free Tier** | Limited requests, rate-limited |
| **Pro** | $9/mo (20x credits, priority) |
| **Features** | 200+ models, text classification, NER, summarization |

**Implementation Plan**:

```python
# src/company_researcher/integrations/huggingface.py

from huggingface_hub import InferenceClient

class HuggingFaceClient:
    """Hugging Face Inference API for ML tasks"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if self.api_key:
            self.client = InferenceClient(token=self.api_key)
        else:
            self.client = InferenceClient()  # Free tier

    async def sentiment_analysis(
        self,
        text: str,
        model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ) -> Dict[str, float]:
        """
        Analyze sentiment of text.

        Returns:
            {"POSITIVE": 0.9, "NEGATIVE": 0.1}
        """
        result = self.client.text_classification(text, model=model)
        return {item["label"]: item["score"] for item in result}

    async def named_entity_recognition(
        self,
        text: str,
        model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    ) -> List[Dict]:
        """
        Extract named entities from text.

        Returns list of:
            {"entity": "ORG", "word": "Microsoft", "score": 0.99}
        """
        return self.client.token_classification(text, model=model)

    async def summarize(
        self,
        text: str,
        model: str = "facebook/bart-large-cnn",
        max_length: int = 150
    ) -> str:
        """Summarize long text"""
        return self.client.summarization(
            text,
            model=model,
            parameters={"max_length": max_length}
        )

    async def zero_shot_classification(
        self,
        text: str,
        labels: List[str],
        model: str = "facebook/bart-large-mnli"
    ) -> Dict[str, float]:
        """
        Classify text into custom categories.

        Example:
            labels = ["positive outlook", "negative outlook", "neutral"]
        """
        result = self.client.zero_shot_classification(
            text,
            labels,
            model=model
        )
        return dict(zip(result["labels"], result["scores"]))

    async def analyze_company_sentiment(
        self,
        news_articles: List[str],
        custom_labels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive sentiment analysis for company news.
        """
        labels = custom_labels or [
            "growth potential",
            "financial risk",
            "market opportunity",
            "competitive threat",
            "regulatory concern"
        ]

        results = {label: [] for label in labels}

        for article in news_articles:
            classification = await self.zero_shot_classification(article, labels)
            for label, score in classification.items():
                results[label].append(score)

        # Calculate averages
        avg_results = {
            label: sum(scores) / len(scores) if scores else 0
            for label, scores in results.items()
        }

        return {
            "category_scores": avg_results,
            "top_category": max(avg_results, key=avg_results.get),
            "article_count": len(news_articles)
        }
```

---

## Category 7: Social & Community Data APIs

### 7.1 Reddit (PRAW) - Market Sentiment

**Purpose**: Track market sentiment, community discussions

| Attribute | Details |
|-----------|---------|
| **Free Tier** | 100 requests/minute (OAuth) |
| **Rate Limit** | 10 requests/minute (unauthenticated) |
| **Pricing** | Free under 100 QPM, $0.24/1000 calls above |

**Implementation Plan**:

```python
# src/company_researcher/integrations/reddit_client.py

import praw
from dataclasses import dataclass
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class RedditPost:
    id: str
    title: str
    selftext: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    url: str
    permalink: str

@dataclass
class RedditComment:
    id: str
    body: str
    author: str
    score: int
    created_utc: float

@dataclass
class SubredditStats:
    name: str
    subscribers: int
    active_users: int
    description: str

class RedditClient:
    """Reddit API Client using PRAW"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: str = "CompanyResearcher/1.0"
    ):
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent

        if self.client_id and self.client_secret:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
        else:
            self.reddit = None

        self._executor = ThreadPoolExecutor(max_workers=3)

    def is_available(self) -> bool:
        return self.reddit is not None

    async def search_posts(
        self,
        query: str,
        subreddits: List[str] = None,
        time_filter: str = "week",  # hour, day, week, month, year, all
        sort: str = "relevance",  # relevance, hot, top, new
        limit: int = 25
    ) -> List[RedditPost]:
        """
        Search for posts mentioning a company/topic.

        Subreddits to search:
        - stocks, investing, wallstreetbets
        - technology, business, startups
        - specific company subreddits
        """
        def _search():
            posts = []

            if subreddits:
                subreddit_str = "+".join(subreddits)
                search = self.reddit.subreddit(subreddit_str).search(
                    query,
                    time_filter=time_filter,
                    sort=sort,
                    limit=limit
                )
            else:
                search = self.reddit.subreddit("all").search(
                    query,
                    time_filter=time_filter,
                    sort=sort,
                    limit=limit
                )

            for post in search:
                posts.append(RedditPost(
                    id=post.id,
                    title=post.title,
                    selftext=post.selftext,
                    author=str(post.author) if post.author else "[deleted]",
                    subreddit=post.subreddit.display_name,
                    score=post.score,
                    upvote_ratio=post.upvote_ratio,
                    num_comments=post.num_comments,
                    created_utc=post.created_utc,
                    url=post.url,
                    permalink=f"https://reddit.com{post.permalink}"
                ))

            return posts

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, _search)

    async def get_subreddit_info(self, subreddit_name: str) -> SubredditStats:
        """Get subreddit statistics"""
        def _get_info():
            sub = self.reddit.subreddit(subreddit_name)
            return SubredditStats(
                name=sub.display_name,
                subscribers=sub.subscribers,
                active_users=sub.accounts_active,
                description=sub.public_description
            )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, _get_info)

    async def analyze_company_sentiment(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        subreddits: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze Reddit sentiment about a company.
        """
        default_subreddits = [
            "stocks", "investing", "wallstreetbets",
            "technology", "business"
        ]

        search_terms = [company_name]
        if ticker:
            search_terms.append(f"${ticker}")

        all_posts = []
        for term in search_terms:
            posts = await self.search_posts(
                query=term,
                subreddits=subreddits or default_subreddits,
                time_filter="month",
                limit=50
            )
            all_posts.extend(posts)

        # Deduplicate
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                unique_posts.append(post)

        # Calculate metrics
        if not unique_posts:
            return {"error": "No posts found", "posts": []}

        avg_score = sum(p.score for p in unique_posts) / len(unique_posts)
        avg_ratio = sum(p.upvote_ratio for p in unique_posts) / len(unique_posts)
        total_comments = sum(p.num_comments for p in unique_posts)

        # Sentiment from upvote ratios
        positive_posts = len([p for p in unique_posts if p.upvote_ratio > 0.6])
        negative_posts = len([p for p in unique_posts if p.upvote_ratio < 0.4])

        return {
            "total_posts": len(unique_posts),
            "average_score": round(avg_score, 1),
            "average_upvote_ratio": round(avg_ratio, 2),
            "total_comments": total_comments,
            "sentiment_breakdown": {
                "positive": positive_posts,
                "negative": negative_posts,
                "neutral": len(unique_posts) - positive_posts - negative_posts
            },
            "top_subreddits": self._get_top_subreddits(unique_posts),
            "top_posts": [
                {
                    "title": p.title,
                    "score": p.score,
                    "comments": p.num_comments,
                    "subreddit": p.subreddit,
                    "url": p.permalink
                }
                for p in sorted(unique_posts, key=lambda x: x.score, reverse=True)[:5]
            ]
        }

    def _get_top_subreddits(self, posts: List[RedditPost]) -> Dict[str, int]:
        """Count posts per subreddit"""
        counts = {}
        for post in posts:
            counts[post.subreddit] = counts.get(post.subreddit, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5])
```

---

### 7.2 GitHub API - Tech Company Analysis

**Purpose**: Analyze tech companies via their open source presence

| Attribute | Details |
|-----------|---------|
| **Unauthenticated** | 60 requests/hour |
| **Authenticated** | 5,000 requests/hour |
| **Features** | Repo stats, contributors, activity |

**Implementation Plan**:

```python
# src/company_researcher/integrations/github_client.py

from dataclasses import dataclass
from typing import List, Optional, Dict
import aiohttp

@dataclass
class GitHubRepo:
    name: str
    full_name: str
    description: str
    url: str
    stars: int
    forks: int
    watchers: int
    language: str
    open_issues: int
    created_at: str
    updated_at: str
    topics: List[str]

@dataclass
class GitHubOrg:
    login: str
    name: str
    description: str
    blog: str
    location: str
    email: str
    public_repos: int
    followers: int
    created_at: str

@dataclass
class GitHubActivity:
    total_commits: int
    total_contributors: int
    recent_commits: int  # Last 30 days
    top_languages: Dict[str, int]
    activity_trend: str  # increasing, stable, decreasing

class GitHubClient:
    """GitHub API Client for tech company analysis"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self._headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self._headers["Authorization"] = f"token {self.token}"

    async def get_organization(self, org_name: str) -> Optional[GitHubOrg]:
        """Get organization profile"""
        data = await self._request(f"/orgs/{org_name}")
        if data:
            return GitHubOrg(
                login=data["login"],
                name=data.get("name", ""),
                description=data.get("description", ""),
                blog=data.get("blog", ""),
                location=data.get("location", ""),
                email=data.get("email", ""),
                public_repos=data.get("public_repos", 0),
                followers=data.get("followers", 0),
                created_at=data.get("created_at", "")
            )
        return None

    async def get_org_repos(
        self,
        org_name: str,
        sort: str = "stars",  # stars, updated, pushed
        limit: int = 30
    ) -> List[GitHubRepo]:
        """Get organization's repositories"""
        repos = []
        page = 1

        while len(repos) < limit:
            data = await self._request(
                f"/orgs/{org_name}/repos",
                params={"sort": sort, "per_page": min(100, limit - len(repos)), "page": page}
            )

            if not data:
                break

            for repo in data:
                repos.append(GitHubRepo(
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description", ""),
                    url=repo["html_url"],
                    stars=repo["stargazers_count"],
                    forks=repo["forks_count"],
                    watchers=repo["watchers_count"],
                    language=repo.get("language", ""),
                    open_issues=repo["open_issues_count"],
                    created_at=repo["created_at"],
                    updated_at=repo["updated_at"],
                    topics=repo.get("topics", [])
                ))

            if len(data) < 100:
                break
            page += 1

        return repos[:limit]

    async def search_repos(
        self,
        query: str,
        sort: str = "stars",
        limit: int = 10
    ) -> List[GitHubRepo]:
        """Search for repositories"""
        data = await self._request(
            "/search/repositories",
            params={"q": query, "sort": sort, "per_page": limit}
        )

        repos = []
        for repo in data.get("items", []):
            repos.append(GitHubRepo(
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo.get("description", ""),
                url=repo["html_url"],
                stars=repo["stargazers_count"],
                forks=repo["forks_count"],
                watchers=repo["watchers_count"],
                language=repo.get("language", ""),
                open_issues=repo["open_issues_count"],
                created_at=repo["created_at"],
                updated_at=repo["updated_at"],
                topics=repo.get("topics", [])
            ))

        return repos

    async def analyze_company_github(
        self,
        org_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive GitHub analysis for a company.
        """
        org = await self.get_organization(org_name)
        if not org:
            # Try searching for repos instead
            repos = await self.search_repos(f"org:{org_name}", limit=30)
            if not repos:
                return {"error": f"Organization {org_name} not found"}
        else:
            repos = await self.get_org_repos(org_name, limit=50)

        if not repos:
            return {
                "organization": org.__dict__ if org else None,
                "repos": [],
                "metrics": {}
            }

        # Calculate metrics
        total_stars = sum(r.stars for r in repos)
        total_forks = sum(r.forks for r in repos)

        # Language distribution
        languages = {}
        for repo in repos:
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1

        # Top repos
        top_repos = sorted(repos, key=lambda x: x.stars, reverse=True)[:10]

        return {
            "organization": org.__dict__ if org else None,
            "metrics": {
                "total_repos": len(repos),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "avg_stars_per_repo": round(total_stars / len(repos), 1) if repos else 0,
                "language_distribution": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "top_repos": [
                {
                    "name": r.name,
                    "description": r.description[:100] if r.description else "",
                    "stars": r.stars,
                    "forks": r.forks,
                    "language": r.language,
                    "url": r.url
                }
                for r in top_repos
            ],
            "popular_topics": self._get_popular_topics(repos)
        }

    def _get_popular_topics(self, repos: List[GitHubRepo]) -> List[str]:
        """Get most common topics across repos"""
        topics = {}
        for repo in repos:
            for topic in repo.topics:
                topics[topic] = topics.get(topic, 0) + 1
        return [t for t, _ in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:15]]
```

---

## Architecture Patterns

### Unified Client Pattern

```python
# src/company_researcher/services/base_client.py

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import aiohttp
from cachetools import TTLCache

class BaseAPIClient(ABC):
    """Base class for all API clients"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        env_var: str = None,
        base_url: str = None,
        cache_ttl: int = 3600,
        cache_maxsize: int = 100
    ):
        self.api_key = api_key or os.getenv(env_var) if env_var else api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    def is_available(self) -> bool:
        """Check if API is configured and available"""
        return bool(self.api_key)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._get_headers()
            )
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        """Override to customize headers"""
        return {"Content-Type": "application/json"}

    async def _request(
        self,
        endpoint: str,
        params: Dict = None,
        method: str = "GET",
        use_cache: bool = True
    ) -> Any:
        """Make API request with caching"""
        cache_key = f"{method}:{endpoint}:{params}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        session = await self._get_session()
        async with session.request(method, url, params=params) as response:
            if response.status == 429:
                raise RateLimitError(f"Rate limit exceeded for {self.__class__.__name__}")
            response.raise_for_status()
            data = await response.json()

            if use_cache:
                self._cache[cache_key] = data

            return data

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
```

### Circuit Breaker Integration

```python
# src/company_researcher/services/circuit_breaker.py

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    """Circuit breaker for API fault tolerance"""

    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None

    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """Check if requests should be allowed"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        return True  # HALF_OPEN allows requests
```

---

## Configuration & Environment Setup

### Environment Variables (.env)

```env
# ===== EXISTING KEYS =====
ANTHROPIC_API_KEY=sk-ant-api03-...
TAVILY_API_KEY=tvly-...

# ===== BUSINESS & COMPANY DATA =====
HUNTER_API_KEY=your_hunter_key
TOMBA_API_KEY=your_tomba_key
TOMBA_SECRET=your_tomba_secret
# Domainsdb.info - No key required (FREE)

# ===== FINANCE APIs =====
FMP_API_KEY=your_fmp_key
FINNHUB_API_KEY=your_finnhub_key
POLYGON_API_KEY=your_polygon_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# ===== NEWS APIs =====
NEWSAPI_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key
MEDIASTACK_API_KEY=your_mediastack_key

# ===== DATA ENRICHMENT =====
ABSTRACT_API_KEY=your_abstract_key
NUMVERIFY_API_KEY=your_numverify_key
IPSTACK_API_KEY=your_ipstack_key

# ===== GEOCODING =====
OPENCAGE_API_KEY=your_opencage_key
# Nominatim - No key required (FREE)
GEODB_API_KEY=your_geodb_key

# ===== ML & AI =====
WATSON_NLU_API_KEY=your_watson_key
WATSON_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/xxx
HUGGINGFACE_API_KEY=your_hf_key

# ===== SOCIAL =====
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
GITHUB_TOKEN=your_github_token
```

### Config Updates (config.py)

```python
# Add to ResearchConfig class

class ResearchConfig(BaseSettings):
    # ... existing fields ...

    # Business & Company Data
    hunter_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("HUNTER_API_KEY"),
        description="Hunter.io API key for email finding"
    )
    tomba_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("TOMBA_API_KEY"),
        description="Tomba.io API key"
    )

    # Finance
    fmp_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FMP_API_KEY"),
        description="Financial Modeling Prep API key"
    )
    finnhub_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FINNHUB_API_KEY"),
        description="Finnhub API key"
    )
    polygon_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("POLYGON_API_KEY"),
        description="Polygon.io API key"
    )

    # News
    gnews_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GNEWS_API_KEY"),
        description="GNews API key"
    )
    mediastack_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("MEDIASTACK_API_KEY"),
        description="Mediastack API key"
    )

    # Geocoding
    opencage_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENCAGE_API_KEY"),
        description="OpenCage Geocoding API key"
    )

    # ML/AI
    watson_nlu_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("WATSON_NLU_API_KEY"),
        description="IBM Watson NLU API key"
    )
    watson_nlu_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("WATSON_NLU_URL"),
        description="IBM Watson NLU service URL"
    )
    huggingface_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("HUGGINGFACE_API_KEY"),
        description="Hugging Face API key"
    )

    # Social
    reddit_client_id: Optional[str] = Field(
        default_factory=lambda: os.getenv("REDDIT_CLIENT_ID"),
        description="Reddit API client ID"
    )
    reddit_client_secret: Optional[str] = Field(
        default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET"),
        description="Reddit API client secret"
    )
    github_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN"),
        description="GitHub personal access token"
    )
```

---

## Cost Analysis

### Monthly Cost Estimates (Moderate Usage)

| API | Free Tier | Est. Monthly Cost | Notes |
|-----|-----------|-------------------|-------|
| **Financial Modeling Prep** | 250 req/day | $0-29 | Starter sufficient for most |
| **Finnhub** | 60 req/min | $0-49 | Free tier often sufficient |
| **Polygon.io** | 5 req/min | $0-29 | Historical data needs |
| **Hunter.io** | 25/month | $0-34 | Pay per use |
| **GNews** | 100/day | $0-29 | Backup news source |
| **OpenCage** | 2,500/day | $0 | Free tier sufficient |
| **Hugging Face** | Limited | $0-9 | Pro for heavy use |
| **Reddit (PRAW)** | 100 QPM | $0 | Stay under limit |
| **GitHub** | 5,000/hr | $0 | Free with auth |
| **IBM Watson NLU** | 30,000/mo | $0-15 | Free tier generous |

### **Total Estimated Monthly Cost**: $0 - $200

**Recommended Approach**:
1. Start with free tiers for all APIs
2. Monitor usage with built-in tracking
3. Upgrade only when hitting limits
4. Use cascade fallbacks to minimize paid API calls

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Create base client patterns (`services/base_client.py`)
- [ ] Add circuit breaker to existing integrations
- [ ] Update `config.py` with all new API keys
- [ ] Create unified error handling

### Phase 2: Finance APIs (Week 2-3)
- [ ] Implement FMP client
- [ ] Implement Finnhub client
- [ ] Implement Polygon client
- [ ] Create `FinancialDataService` cascade
- [ ] Update `enhanced_financial.py` agent

### Phase 3: News & Data Enrichment (Week 3-4)
- [ ] Implement GNews client
- [ ] Implement Mediastack client
- [ ] Create `NewsService` cascade
- [ ] Implement Hunter.io client
- [ ] Implement Abstract Email validation

### Phase 4: Location & Company Data (Week 4-5)
- [ ] Implement OpenCage client
- [ ] Implement Nominatim fallback
- [ ] Implement Domainsdb client
- [ ] Add geocoding to market research agents

### Phase 5: ML & Social (Week 5-6)
- [ ] Implement Watson NLU client
- [ ] Implement Hugging Face client
- [ ] Implement Reddit/PRAW client
- [ ] Implement GitHub client
- [ ] Create sentiment analysis pipeline

### Phase 6: Integration & Testing (Week 6-7)
- [ ] Integration tests for all clients
- [ ] End-to-end workflow tests
- [ ] Performance benchmarking
- [ ] Documentation updates

---

## File Structure Summary

```
src/company_researcher/
├── integrations/
│   ├── __init__.py
│   ├── hunter_io.py          # NEW
│   ├── tomba_io.py           # NEW
│   ├── domainsdb.py          # NEW
│   ├── financial_modeling_prep.py  # NEW
│   ├── finnhub.py            # NEW
│   ├── polygon.py            # NEW
│   ├── gnews.py              # NEW
│   ├── mediastack.py         # NEW
│   ├── abstract_email.py     # NEW
│   ├── numverify.py          # NEW
│   ├── ipstack.py            # NEW
│   ├── opencage.py           # NEW
│   ├── nominatim.py          # NEW
│   ├── geodb.py              # NEW
│   ├── watson_nlu.py         # NEW
│   ├── huggingface.py        # NEW
│   ├── reddit_client.py      # NEW
│   ├── github_client.py      # NEW
│   ├── news_api.py           # EXISTING
│   ├── sec_edgar.py          # EXISTING (enhance)
│   └── crunchbase.py         # EXISTING
├── services/
│   ├── __init__.py           # NEW
│   ├── base_client.py        # NEW
│   ├── circuit_breaker.py    # NEW
│   ├── financial_data_service.py  # NEW
│   ├── news_service.py       # NEW
│   └── email_finder_service.py    # NEW
└── tools/
    └── alpha_vantage_client.py  # EXISTING (enhance)
```

---

## Quick Start Commands

```bash
# Install new dependencies
pip install praw huggingface_hub ibm-watson aiohttp cachetools

# Run tests for new integrations
pytest tests/integrations/ -v

# Test individual client
python -m src.company_researcher.integrations.financial_modeling_prep --test
```

---

## References & Documentation Links

- [Financial Modeling Prep Docs](https://site.financialmodelingprep.com/developer/docs)
- [Finnhub API Docs](https://finnhub.io/docs/api)
- [Polygon.io Docs](https://polygon.io/docs)
- [Hunter.io API Docs](https://hunter.io/api-documentation)
- [GNews API Docs](https://gnews.io/docs/)
- [OpenCage Docs](https://opencagedata.com/api)
- [IBM Watson NLU](https://cloud.ibm.com/docs/natural-language-understanding)
- [Hugging Face Inference](https://huggingface.co/docs/api-inference)
- [PRAW Docs](https://praw.readthedocs.io/)
- [GitHub REST API](https://docs.github.com/en/rest)
