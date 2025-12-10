# Financial Data Integrations

Documentation for financial data API integrations.

## Overview

The system uses multiple financial data providers:

```
Financial Data Request
         |
    +----+----+
    |         |
    v         v
+--------+ +-------+
|yfinance| | APIs  |
+--------+ +-------+
    |         |
    v         v
+-------------------+
| Combined Results  |
+-------------------+
```

## yfinance (Primary - Free)

**Library**: https://github.com/ranaroussi/yfinance

Free access to Yahoo Finance data.

### Features

- Stock prices and history
- Basic financials
- Company info
- No API key required
- Unlimited requests

### Data Available

| Data Type | Method | Example |
|-----------|--------|---------|
| Stock Price | `ticker.info` | Current price, market cap |
| History | `ticker.history()` | Historical prices |
| Financials | `ticker.financials` | Income statement |
| Balance Sheet | `ticker.balance_sheet` | Assets, liabilities |
| Cash Flow | `ticker.cashflow` | Cash flow statement |

### Usage

```python
import yfinance as yf

# Get company data
ticker = yf.Ticker("MSFT")

# Basic info
info = ticker.info
revenue = info.get("totalRevenue")
market_cap = info.get("marketCap")

# Financial statements
financials = ticker.financials
balance = ticker.balance_sheet
cash_flow = ticker.cashflow

# Historical data
history = ticker.history(period="1y")
```

### Implementation

```python
# integrations/yfinance_client.py

class YFinanceClient:
    def get_company_data(self, ticker_symbol: str) -> Dict:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        return {
            "symbol": ticker_symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "revenue": info.get("totalRevenue"),
            "net_income": info.get("netIncomeToCommon"),
            "employees": info.get("fullTimeEmployees"),
            "price": info.get("currentPrice"),
            "pe_ratio": info.get("trailingPE"),
        }
```

---

## Alpha Vantage

**Website**: https://www.alphavantage.co

Comprehensive financial data API.

### Configuration

```env
ALPHA_VANTAGE_API_KEY=your-api-key
```

### Free Tier Limits

- 25 API calls per day
- 5 calls per minute

### Data Available

| Endpoint | Data | Rate Limit |
|----------|------|------------|
| `OVERVIEW` | Company fundamentals | 5/min |
| `INCOME_STATEMENT` | Income statements | 5/min |
| `BALANCE_SHEET` | Balance sheet | 5/min |
| `CASH_FLOW` | Cash flow | 5/min |
| `EARNINGS` | Quarterly earnings | 5/min |

### Usage

```python
from company_researcher.integrations import AlphaVantageClient

client = AlphaVantageClient(config)
overview = await client.get_overview("MSFT")
income = await client.get_income_statement("MSFT")
```

### Response Example

```python
{
    "Symbol": "MSFT",
    "Name": "Microsoft Corporation",
    "Sector": "Technology",
    "MarketCapitalization": "2800000000000",
    "RevenueTTM": "198000000000",
    "GrossProfitTTM": "137000000000",
    "PERatio": "35.5",
    "EPS": "9.5"
}
```

---

## Financial Modeling Prep (FMP)

**Website**: https://financialmodelingprep.com

Comprehensive financial API with broader coverage.

### Configuration

```env
FMP_API_KEY=your-api-key
```

### Free Tier Limits

- 250 API calls per day

### Data Available

| Endpoint | Data | Format |
|----------|------|--------|
| `/profile` | Company profile | JSON |
| `/income-statement` | Income statements | JSON |
| `/balance-sheet-statement` | Balance sheets | JSON |
| `/cash-flow-statement` | Cash flows | JSON |
| `/key-metrics` | Financial ratios | JSON |
| `/financial-growth` | Growth metrics | JSON |

### Usage

```python
from company_researcher.integrations import FMPClient

client = FMPClient(config)
profile = await client.get_profile("MSFT")
metrics = await client.get_key_metrics("MSFT")
```

---

## Finnhub

**Website**: https://finnhub.io

Real-time stock data and news.

### Configuration

```env
FINNHUB_API_KEY=your-api-key
```

### Free Tier Limits

- 60 API calls per minute

### Data Available

| Endpoint | Data |
|----------|------|
| `/quote` | Real-time quote |
| `/company-profile2` | Company profile |
| `/company-news` | Company news |
| `/recommendation` | Analyst recommendations |
| `/metric` | Financial metrics |

### Usage

```python
from company_researcher.integrations import FinnhubClient

client = FinnhubClient(config)
quote = await client.get_quote("MSFT")
news = await client.get_company_news("MSFT", days=7)
```

---

## SEC EDGAR

**Website**: https://www.sec.gov/edgar

Official SEC filings for US public companies.

### Features

- 10-K (Annual reports)
- 10-Q (Quarterly reports)
- 8-K (Current reports)
- Proxy statements
- No API key required

### Implementation

```python
from company_researcher.integrations import SECEdgarClient

client = SECEdgarClient()

# Get recent filings
filings = await client.get_filings(
    ticker="MSFT",
    filing_type="10-K",
    limit=5
)

# Parse filing content
content = await client.get_filing_content(filing_url)
```

### Data Extracted

```python
{
    "filing_type": "10-K",
    "filing_date": "2024-07-30",
    "period_end": "2024-06-30",
    "url": "https://www.sec.gov/Archives/...",
    "revenue": "$198,270,000,000",
    "net_income": "$69,583,000,000",
    "total_assets": "$411,976,000,000"
}
```

---

## Financial Data Flow

```python
async def get_comprehensive_financials(company: str) -> Dict:
    """Get financials from multiple sources."""
    ticker = find_ticker_symbol(company)

    # Parallel data collection
    yf_data, av_data, fmp_data = await asyncio.gather(
        yfinance_client.get_data(ticker),
        alpha_vantage_client.get_data(ticker),
        fmp_client.get_data(ticker),
        return_exceptions=True
    )

    # Merge and prioritize
    return merge_financial_data(
        yf_data,   # Free, always available
        av_data,   # More detailed if available
        fmp_data   # Most comprehensive if available
    )
```

---

## Configuration

```python
# config.py

# yfinance (no key needed)
yfinance_timeout: int = 30

# Alpha Vantage
alpha_vantage_api_key: Optional[str] = Field(env="ALPHA_VANTAGE_API_KEY")
alpha_vantage_rate_limit: int = 5  # per minute

# FMP
fmp_api_key: Optional[str] = Field(env="FMP_API_KEY")
fmp_rate_limit: int = 250  # per day

# Finnhub
finnhub_api_key: Optional[str] = Field(env="FINNHUB_API_KEY")
finnhub_rate_limit: int = 60  # per minute
```

---

**Related Documentation**:
- [Search Providers](../search/)
- [News Sources](../news/)
- [Financial Agent](../../03-agents/specialists/)

---

**Last Updated**: December 2024
