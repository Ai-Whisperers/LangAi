# Data Enrichment Implementation Plan

*Practical guide for filling research data gaps*

---

## Executive Summary

This document provides a prioritized implementation plan with specific tools, APIs, and services to integrate into the Company Researcher system to achieve 85%+ quality scores.

**Current State:** 50-70% quality scores
**Target State:** 85%+ quality scores
**Estimated Effort:** 4-6 weeks for Phase 1

---

## Phase 1: Quick Wins (FREE) - Week 1-2

### 1.1 LinkedIn Data Extraction

**What we get:** Employee count, executive names, company description, headquarters

**Implementation Options:**

| Option | Cost | Difficulty | Data Quality |
|--------|------|------------|--------------|
| **Proxycurl API** | $0.01/profile | Easy | High |
| **RapidAPI LinkedIn** | Freemium | Easy | Medium |
| **Selenium scraping** | Free | Hard | Medium |
| **SerpAPI Google (LinkedIn)** | $50/mo | Easy | High |

**Recommended:** Proxycurl API (pay-per-use, no monthly commitment)

```python
# Example integration
# src/company_researcher/integrations/linkedin.py

import httpx

class LinkedInProvider:
    BASE_URL = "https://nubela.co/proxycurl/api/linkedin/company"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_company_data(self, company_url: str) -> dict:
        """Fetch company data from LinkedIn via Proxycurl."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"url": company_url, "resolve_numeric_id": "true"}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, headers=headers, params=params)
            return response.json()

    def extract_key_metrics(self, data: dict) -> dict:
        return {
            "employee_count": data.get("company_size_on_linkedin"),
            "headquarters": data.get("hq", {}).get("city"),
            "industry": data.get("industry"),
            "description": data.get("description"),
            "specialties": data.get("specialities"),
            "founded_year": data.get("founded_year"),
            "website": data.get("website"),
        }
```

**Environment Variables:**
```env
PROXYCURL_API_KEY=your_key_here
```

---

### 1.2 Wikipedia Structured Data

**What we get:** Company overview, founding date, key people, headquarters, products

**Implementation:** Use Wikipedia API + Wikidata for structured data

```python
# src/company_researcher/integrations/wikipedia.py

import httpx

class WikipediaProvider:
    WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"
    WIKIDATA_API = "https://www.wikidata.org/wiki/Special:EntityData"

    async def get_company_summary(self, company_name: str) -> dict:
        """Get Wikipedia summary for a company."""
        url = f"{self.WIKI_API}/{company_name.replace(' ', '_')}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
        return {}

    async def get_wikidata(self, wikidata_id: str) -> dict:
        """Get structured data from Wikidata."""
        url = f"{self.WIKIDATA_API}/{wikidata_id}.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

**Cost:** FREE

---

### 1.3 OpenCorporates (Company Registry)

**What we get:** Legal name, registration number, status, directors, filings

**API:** https://api.opencorporates.com

```python
# src/company_researcher/integrations/opencorporates.py

class OpenCorporatesProvider:
    BASE_URL = "https://api.opencorporates.com/v0.4"

    async def search_company(self, name: str, country: str = None) -> list:
        """Search for companies by name."""
        params = {"q": name}
        if country:
            params["country_code"] = country

        url = f"{self.BASE_URL}/companies/search"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            return data.get("results", {}).get("companies", [])

    async def get_company(self, jurisdiction: str, company_number: str) -> dict:
        """Get detailed company information."""
        url = f"{self.BASE_URL}/companies/{jurisdiction}/{company_number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

**Cost:** FREE (basic) / $99/mo (premium)

---

### 1.4 Ookla Speedtest Intelligence (Network Quality)

**What we get:** Network speeds, coverage quality, latency

**Options:**

| Source | Cost | Data Type |
|--------|------|-----------|
| **Speedtest Global Index** | FREE | Country-level rankings |
| **OpenSignal Public Reports** | FREE | PDF reports by country |
| **nPerf** | FREE | Speed test results |

**Implementation:** Scrape public reports or use their embeddable data

```python
# src/company_researcher/integrations/network_quality.py

class NetworkQualityProvider:
    SPEEDTEST_URL = "https://www.speedtest.net/global-index"

    async def get_country_ranking(self, country: str) -> dict:
        """Get mobile/fixed speeds from Speedtest Global Index."""
        # Parse the global index page for country data
        # Returns: {"mobile_speed_mbps": 45.2, "fixed_speed_mbps": 89.1, "rank": 52}
        pass
```

---

## Phase 2: Financial Data APIs - Week 2-3

### 2.1 SEC EDGAR (US-Listed Parent Companies)

**What we get:** 10-K, 20-F, 8-K filings with segment data

**Implementation:** Use SEC EDGAR API (FREE)

```python
# src/company_researcher/integrations/sec_edgar.py

class SECEdgarProvider:
    BASE_URL = "https://data.sec.gov"

    async def get_company_filings(self, cik: str, form_type: str = "10-K") -> list:
        """Get SEC filings for a company."""
        url = f"{self.BASE_URL}/submissions/CIK{cik.zfill(10)}.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"User-Agent": "CompanyResearcher/1.0"})
            data = response.json()

            # Filter by form type
            filings = data.get("filings", {}).get("recent", {})
            return [
                f for f in zip(filings.get("form", []), filings.get("accessionNumber", []))
                if f[0] == form_type
            ]

    async def get_filing_content(self, accession_number: str) -> str:
        """Download filing content."""
        # Implementation to fetch and parse filing
        pass
```

**Cost:** FREE

---

### 2.2 Yahoo Finance / yfinance

**What we get:** Stock prices, market cap, P/E ratio, financial statements

```python
# src/company_researcher/integrations/yahoo_finance.py

import yfinance as yf

class YahooFinanceProvider:
    def get_company_data(self, ticker: str) -> dict:
        """Get financial data from Yahoo Finance."""
        stock = yf.Ticker(ticker)

        return {
            "market_cap": stock.info.get("marketCap"),
            "pe_ratio": stock.info.get("trailingPE"),
            "revenue": stock.info.get("totalRevenue"),
            "profit_margin": stock.info.get("profitMargins"),
            "employees": stock.info.get("fullTimeEmployees"),
            "sector": stock.info.get("sector"),
            "industry": stock.info.get("industry"),
            "description": stock.info.get("longBusinessSummary"),
            "website": stock.info.get("website"),
            "headquarters": f"{stock.info.get('city')}, {stock.info.get('country')}",
        }

    def get_financials(self, ticker: str) -> dict:
        """Get financial statements."""
        stock = yf.Ticker(ticker)
        return {
            "income_statement": stock.income_stmt.to_dict(),
            "balance_sheet": stock.balance_sheet.to_dict(),
            "cash_flow": stock.cashflow.to_dict(),
        }
```

**Cost:** FREE (rate limited)
**Requirements:** `pip install yfinance`

---

### 2.3 Financial Modeling Prep API

**What we get:** Financial statements, ratios, SEC filings, stock prices

```python
# src/company_researcher/integrations/fmp.py

class FinancialModelingPrepProvider:
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_company_profile(self, ticker: str) -> dict:
        url = f"{self.BASE_URL}/profile/{ticker}?apikey={self.api_key}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()[0] if response.json() else {}

    async def get_income_statement(self, ticker: str, years: int = 5) -> list:
        url = f"{self.BASE_URL}/income-statement/{ticker}?limit={years}&apikey={self.api_key}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

**Cost:** FREE (250 calls/day) / $19/mo (unlimited)

---

## Phase 3: Industry-Specific Data - Week 3-4

### 3.1 GSMA Intelligence (Telecom)

**What we get:** Subscriber data, ARPU, market share, spectrum, network coverage

**Access:** Subscription required (~$5,000-10,000/year)

**Alternative FREE sources:**
- GSMA public reports: https://www.gsma.com/mobileeconomy/
- ITU statistics: https://www.itu.int/en/ITU-D/Statistics/
- World Bank telecom data: https://data.worldbank.org/indicator/IT.CEL.SETS

```python
# src/company_researcher/integrations/telecom_data.py

class TelecomDataProvider:
    ITU_API = "https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx"
    WORLD_BANK_API = "https://api.worldbank.org/v2"

    async def get_country_telecom_stats(self, country_code: str) -> dict:
        """Get telecom statistics for a country from World Bank."""
        indicators = [
            "IT.CEL.SETS",  # Mobile subscriptions
            "IT.CEL.SETS.P2",  # Mobile subscriptions per 100 people
            "IT.NET.USER.ZS",  # Internet users (% of population)
        ]

        results = {}
        for indicator in indicators:
            url = f"{self.WORLD_BANK_API}/country/{country_code}/indicator/{indicator}?format=json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                if len(data) > 1:
                    results[indicator] = data[1][0]["value"] if data[1] else None

        return results
```

---

### 3.2 Crunchbase (Startups & Tech)

**What we get:** Funding rounds, investors, founders, company description

```python
# src/company_researcher/integrations/crunchbase.py

class CrunchbaseProvider:
    BASE_URL = "https://api.crunchbase.com/api/v4"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_organization(self, name: str) -> dict:
        url = f"{self.BASE_URL}/searches/organizations"
        headers = {"X-cb-user-key": self.api_key}
        payload = {
            "field_ids": ["name", "short_description", "founded_on", "num_employees_enum"],
            "query": [{"type": "predicate", "field_id": "name", "operator_id": "contains", "values": [name]}]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.json()
```

**Cost:** FREE (basic) / $99/mo (pro)

---

## Phase 4: Regional Data Sources - Week 4-5

### 4.1 LATAM Telecom Regulators

| Country | Regulator | API/Data | URL |
|---------|-----------|----------|-----|
| Paraguay | CONATEL | Monthly reports | conatel.gov.py |
| Brazil | ANATEL | Open data portal | dados.anatel.gov.br |
| Mexico | IFT | Statistics | ift.org.mx |
| Colombia | CRC | Reports | crcom.gov.co |
| Chile | SUBTEL | Statistics | subtel.gob.cl |
| Peru | OSIPTEL | Open data | osiptel.gob.pe |
| Argentina | ENACOM | Statistics | enacom.gob.ar |

```python
# src/company_researcher/integrations/latam_regulators.py

class LatamRegulatorProvider:
    REGULATORS = {
        "BR": {"name": "ANATEL", "api": "https://www.anatel.gov.br/dados/"},
        "MX": {"name": "IFT", "api": None},
        "CO": {"name": "CRC", "api": None},
        "CL": {"name": "SUBTEL", "api": None},
        "PE": {"name": "OSIPTEL", "api": "https://www.osiptel.gob.pe/"},
        "AR": {"name": "ENACOM", "api": None},
        "PY": {"name": "CONATEL", "api": None},
    }

    async def get_telecom_stats(self, country_code: str) -> dict:
        """Fetch telecom statistics from country regulator."""
        # Implementation varies by country - some have APIs, others need scraping
        pass
```

---

### 4.2 Brazilian Data Sources (ANATEL)

ANATEL has excellent open data:

```python
# src/company_researcher/integrations/anatel.py

class ANATELProvider:
    BASE_URL = "https://www.anatel.gov.br/dadosabertos/paineis_de_dados"

    async def get_mobile_subscribers(self) -> dict:
        """Get mobile subscriber data by operator."""
        # ANATEL provides CSV/Excel downloads
        # Key datasets:
        # - Acessos de Telefonia Móvel (mobile subscribers)
        # - Acessos de Banda Larga Fixa (fixed broadband)
        # - Qualidade de Serviços (quality metrics)
        pass
```

---

## Phase 5: News & Sentiment Enhancement - Week 5-6

### 5.1 Google News RSS (Already Implemented)

Enhance existing implementation with better parsing:

```python
# Improvements to existing news provider
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}"

# Add language/country support for LATAM
LATAM_NEWS_CONFIG = {
    "BR": {"hl": "pt-BR", "gl": "BR"},
    "MX": {"hl": "es-MX", "gl": "MX"},
    "AR": {"hl": "es-AR", "gl": "AR"},
    "CO": {"hl": "es-CO", "gl": "CO"},
    "CL": {"hl": "es-CL", "gl": "CL"},
}
```

---

### 5.2 NewsAPI.org

**What we get:** Headlines, content, sentiment-ready articles

```python
# src/company_researcher/integrations/newsapi.py

class NewsAPIProvider:
    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_company_news(self, company_name: str, days: int = 30) -> list:
        from datetime import datetime, timedelta

        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "apiKey": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            return response.json().get("articles", [])
```

**Cost:** FREE (100 requests/day) / $449/mo (business)

---

## Recommended Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Enrichment Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   LinkedIn   │  │   Wikipedia  │  │ OpenCorporates│          │
│  │  (Proxycurl) │  │   (FREE)     │  │   (FREE)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────▼─────────────────▼─────────────────▼───────┐          │
│  │              DataEnrichmentRouter                 │          │
│  │    - Routes queries to appropriate providers      │          │
│  │    - Caches responses (disk-based)               │          │
│  │    - Handles fallbacks                           │          │
│  └──────────────────────┬───────────────────────────┘          │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────┐          │
│  │              EnrichedCompanyProfile               │          │
│  │    - employee_count (LinkedIn)                    │          │
│  │    - headquarters (Wikipedia/LinkedIn)            │          │
│  │    - legal_name (OpenCorporates)                 │          │
│  │    - executives (LinkedIn)                        │          │
│  │    - financials (Yahoo Finance/SEC)              │          │
│  │    - network_quality (Ookla/OpenSignal)          │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority Matrix

| Integration | Impact | Effort | Cost | Priority |
|-------------|--------|--------|------|----------|
| LinkedIn (Proxycurl) | HIGH | LOW | $0.01/call | P0 |
| Wikipedia/Wikidata | MEDIUM | LOW | FREE | P0 |
| Yahoo Finance | HIGH | LOW | FREE | P0 |
| SEC EDGAR | HIGH | MEDIUM | FREE | P1 |
| OpenCorporates | MEDIUM | LOW | FREE | P1 |
| Google News (enhanced) | MEDIUM | LOW | FREE | P1 |
| ANATEL (Brazil) | HIGH (Brazil) | MEDIUM | FREE | P1 |
| Financial Modeling Prep | MEDIUM | LOW | FREE/Paid | P2 |
| Crunchbase | MEDIUM | LOW | FREE/Paid | P2 |
| Ookla/OpenSignal | MEDIUM | MEDIUM | FREE | P2 |
| GSMA Intelligence | HIGH | LOW | $$$$ | P3 |

---

## Environment Variables to Add

```env
# Data Enrichment APIs
PROXYCURL_API_KEY=your_key
FMP_API_KEY=your_key
CRUNCHBASE_API_KEY=your_key
NEWSAPI_KEY=your_key

# Optional Premium
GSMA_API_KEY=your_key
LINKEDIN_SALES_NAV_KEY=your_key
```

---

## New File Structure

```
src/company_researcher/integrations/
├── __init__.py
├── search_router.py          # Existing
├── financial_data.py         # Existing
├── news_providers.py         # Existing
├── enrichment/               # NEW
│   ├── __init__.py
│   ├── linkedin.py           # Proxycurl integration
│   ├── wikipedia.py          # Wikipedia/Wikidata
│   ├── opencorporates.py     # Company registry
│   ├── yahoo_finance.py      # Financial data
│   ├── sec_edgar.py          # SEC filings
│   ├── network_quality.py    # Ookla/OpenSignal
│   ├── telecom_regulators.py # LATAM regulators
│   └── router.py             # EnrichmentRouter
```

---

## Quick Start Implementation

### Step 1: Install Dependencies

```bash
pip install yfinance httpx feedparser
```

### Step 2: Create Base Enrichment Router

```python
# src/company_researcher/integrations/enrichment/router.py

from typing import Dict, Any, Optional
from .linkedin import LinkedInProvider
from .wikipedia import WikipediaProvider
from .yahoo_finance import YahooFinanceProvider

class DataEnrichmentRouter:
    """Routes data enrichment requests to appropriate providers."""

    def __init__(self):
        self.linkedin = LinkedInProvider(os.getenv("PROXYCURL_API_KEY"))
        self.wikipedia = WikipediaProvider()
        self.yahoo = YahooFinanceProvider()
        self._cache = {}

    async def enrich_company(self, company_name: str, ticker: str = None) -> Dict[str, Any]:
        """Enrich company data from all available sources."""

        enriched = {
            "company_name": company_name,
            "sources_used": [],
        }

        # Wikipedia (FREE, always try)
        try:
            wiki_data = await self.wikipedia.get_company_summary(company_name)
            if wiki_data:
                enriched.update({
                    "description": wiki_data.get("extract"),
                    "wikipedia_url": wiki_data.get("content_urls", {}).get("desktop", {}).get("page"),
                })
                enriched["sources_used"].append("wikipedia")
        except Exception as e:
            pass

        # Yahoo Finance (if ticker provided)
        if ticker:
            try:
                yahoo_data = self.yahoo.get_company_data(ticker)
                enriched.update({
                    "employee_count": yahoo_data.get("employees"),
                    "market_cap": yahoo_data.get("market_cap"),
                    "revenue": yahoo_data.get("revenue"),
                    "headquarters": yahoo_data.get("headquarters"),
                    "industry": yahoo_data.get("industry"),
                })
                enriched["sources_used"].append("yahoo_finance")
            except Exception as e:
                pass

        # LinkedIn (if API key configured)
        if os.getenv("PROXYCURL_API_KEY"):
            try:
                # Search for company LinkedIn URL first
                linkedin_data = await self.linkedin.get_company_data(f"https://linkedin.com/company/{company_name.lower().replace(' ', '-')}")
                if linkedin_data:
                    enriched.update({
                        "employee_count": linkedin_data.get("company_size_on_linkedin") or enriched.get("employee_count"),
                        "specialties": linkedin_data.get("specialities"),
                    })
                    enriched["sources_used"].append("linkedin")
            except Exception as e:
                pass

        return enriched
```

### Step 3: Integrate into Workflow

Add enrichment step after initial data collection:

```python
# In comprehensive_research.py, add new node:

def data_enrichment_node(state: OverallState) -> Dict[str, Any]:
    """Enrich company data from additional sources."""
    from ..integrations.enrichment.router import DataEnrichmentRouter

    router = DataEnrichmentRouter()
    enriched = await router.enrich_company(
        company_name=state["company_name"],
        ticker=state.get("stock_ticker")
    )

    # Merge enriched data into state
    return {
        "employee_count": enriched.get("employee_count"),
        "headquarters": enriched.get("headquarters"),
        "market_cap": enriched.get("market_cap"),
        "enrichment_sources": enriched.get("sources_used"),
    }
```

---

## Estimated Costs (Monthly)

| Tier | Tools | Monthly Cost | Quality Improvement |
|------|-------|--------------|---------------------|
| **FREE** | Wikipedia, Yahoo Finance, SEC EDGAR, Google News RSS | $0 | +15 points |
| **Basic** | + Proxycurl (100 calls), NewsAPI | ~$20 | +25 points |
| **Pro** | + FMP, Crunchbase Pro | ~$150 | +35 points |
| **Enterprise** | + GSMA, LinkedIn Sales Nav | ~$1,000+ | +45 points |

---

## Next Steps

1. **Immediate:** Implement Wikipedia + Yahoo Finance (FREE, high impact)
2. **Week 1:** Add Proxycurl LinkedIn integration
3. **Week 2:** Integrate SEC EDGAR for US-listed parents
4. **Week 3:** Add LATAM regulator scrapers (ANATEL first)
5. **Week 4:** Test and refine quality improvements

---

*Document created: December 2025*
