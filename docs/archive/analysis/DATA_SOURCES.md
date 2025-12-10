# Data Sources & Integration Reference

Complete reference for all external data sources integrated into Company Researcher.

---

## Quick Reference

| Category | Source | Free Tier | Best For |
|----------|--------|-----------|----------|
| **Search** | Tavily | 1,000/mo | Web search, research queries |
| **AI** | Anthropic Claude | Pay-per-use | Analysis, synthesis, reasoning |
| **Financial** | FMP | 250/day | Fundamentals, ratios, DCF |
| **Financial** | Finnhub | 60/min | Real-time quotes, news |
| **Financial** | Polygon | 5/min | Historical data, tickers |
| **Financial** | yfinance | Unlimited | Quick stock data (no API key) |
| **News** | NewsAPI | 100/day | Breaking news, headlines |
| **News** | GNews | 100/day | Global news coverage |
| **News** | Mediastack | 500/mo | Multi-country news |
| **Contact** | Hunter.io | 25/mo | Email discovery |
| **Scraping** | Firecrawl | 500 credits | LLM-ready web scraping |
| **Scraping** | ScrapeGraph | Varies | AI-powered extraction |
| **Social** | Reddit | 100/min | Community sentiment |
| **Social** | GitHub | 5,000/hr | Tech company research |
| **Geo** | OpenCage | 2,500/day | Company locations |
| **Regulatory** | SEC EDGAR | Unlimited | US public company filings |

---

## 1. Search & Research

### Tavily Search
**Purpose:** Primary web search engine for research queries

**Environment Variable:** `TAVILY_API_KEY`

**Capabilities:**
- Web search with AI-optimized results
- Research-focused query processing
- Content extraction and summarization
- Source credibility scoring

**What You Can Do:**
```python
from tavily import TavilyClient

client = TavilyClient(api_key="...")

# Basic search
results = client.search("Microsoft Azure market share 2024")

# Deep research
results = client.search(
    query="Tesla competitive advantages",
    search_depth="advanced",
    max_results=20
)

# Get answer with sources
answer = client.qna_search("What is Apple's revenue?")
```

**Rate Limits:**
- Free: 1,000 searches/month
- Pro: 10,000 searches/month

**Dashboard:** https://app.tavily.com

---

## 2. AI Analysis

### Anthropic Claude
**Purpose:** Core AI for analysis, synthesis, and reasoning

**Environment Variable:** `ANTHROPIC_API_KEY`

**Capabilities:**
- Company analysis and synthesis
- Financial statement interpretation
- Competitive analysis
- Report generation
- Multi-step reasoning

**What You Can Do:**
```python
from anthropic import Anthropic

client = Anthropic()

# Analysis request
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Analyze Tesla's competitive position..."
    }]
)
```

**Rate Limits:**
- Varies by tier (check console)
- Token-based pricing

**Dashboard:** https://console.anthropic.com

---

## 3. Financial Data

### Financial Modeling Prep (FMP)
**Purpose:** Comprehensive financial fundamentals

**Environment Variable:** `FMP_API_KEY`

**Capabilities:**
- Company profiles
- Income statements (annual/quarterly)
- Balance sheets
- Cash flow statements
- Key financial ratios
- DCF valuations
- Historical prices
- SEC filings

**What You Can Do:**
```python
from src.company_researcher.integrations import FMPClient

client = FMPClient(api_key="...")

# Company profile
profile = await client.get_company_profile("AAPL")
# Returns: name, description, CEO, employees, market cap, sector, industry

# Financial statements
income = await client.get_income_statement("AAPL", period="annual", limit=5)
# Returns: revenue, gross profit, operating income, net income, EPS

balance = await client.get_balance_sheet("AAPL")
# Returns: total assets, liabilities, equity, cash, debt

# Valuation
dcf = await client.get_dcf("AAPL")
# Returns: DCF value, stock price, date

# Key metrics
metrics = await client.get_key_metrics("AAPL")
# Returns: P/E, P/B, ROE, ROA, debt ratios, margins
```

**Rate Limits:**
- Free: 250 requests/day
- Starter: 750 requests/day ($14/mo)

**Dashboard:** https://site.financialmodelingprep.com/developer/dashboard

---

### Finnhub
**Purpose:** Real-time market data and news

**Environment Variable:** `FINNHUB_API_KEY`

**Capabilities:**
- Real-time stock quotes
- Company profiles
- Company news
- Earnings calendars
- SEC filings
- Insider transactions
- Recommendations
- Price targets
- ESG scores
- Sentiment analysis

**What You Can Do:**
```python
from src.company_researcher.integrations import FinnhubClient

client = FinnhubClient(api_key="...")

# Real-time quote
quote = await client.get_quote("AAPL")
# Returns: current price, change, high, low, open, previous close

# Company profile
profile = await client.get_company_profile("AAPL")
# Returns: country, exchange, IPO date, market cap, shares outstanding

# Company news
news = await client.get_company_news("AAPL", from_date, to_date)
# Returns: headlines, summaries, sources, sentiment

# Insider transactions
insiders = await client.get_insider_transactions("AAPL")
# Returns: transaction type, shares, value, insider name

# Recommendations
recs = await client.get_recommendations("AAPL")
# Returns: buy, hold, sell counts by period

# ESG scores
esg = await client.get_esg_scores("AAPL")
# Returns: environmental, social, governance scores
```

**Rate Limits:**
- Free: 60 API calls/minute
- Premium: Higher limits

**Dashboard:** https://finnhub.io/dashboard

---

### Polygon.io
**Purpose:** Historical market data

**Environment Variable:** `POLYGON_API_KEY`

**Capabilities:**
- Historical OHLCV data
- Ticker details
- Market news
- Stock splits/dividends
- Financial data
- Related companies

**What You Can Do:**
```python
from src.company_researcher.integrations import PolygonClient

client = PolygonClient(api_key="...")

# Ticker details
details = await client.get_ticker_details("AAPL")
# Returns: name, description, employees, SIC code, homepage

# Historical bars
bars = await client.get_stock_bars("AAPL", "2024-01-01", "2024-12-01")
# Returns: OHLCV data with timestamps

# News
news = await client.get_news("AAPL", limit=10)
# Returns: articles with title, author, published date
```

**Rate Limits:**
- Free: 5 API calls/minute (delayed data)
- Starter: Unlimited (real-time)

**Dashboard:** https://polygon.io/dashboard

---

### yfinance (Yahoo Finance)
**Purpose:** Quick financial data without API key

**Environment Variable:** None required

**Capabilities:**
- Stock prices and history
- Company info
- Financial statements
- Analyst recommendations
- Institutional holders

**What You Can Do:**
```python
import yfinance as yf

# Get ticker
ticker = yf.Ticker("AAPL")

# Company info
info = ticker.info
# Returns: sector, industry, employees, market cap, description

# Historical prices
hist = ticker.history(period="1y")
# Returns: DataFrame with OHLCV

# Financial statements
income = ticker.financials
balance = ticker.balance_sheet
cashflow = ticker.cashflow

# Recommendations
recs = ticker.recommendations
```

**Rate Limits:**
- No official API, may be rate limited
- Use responsibly

---

## 4. News Data

### NewsAPI
**Purpose:** Global news aggregation

**Environment Variable:** `NEWSAPI_KEY`

**Capabilities:**
- Top headlines by country/category
- Everything search (full archive)
- Source filtering
- Date range queries
- Language filtering

**What You Can Do:**
```python
from src.company_researcher.integrations import NewsAPIClient

client = NewsAPIClient(api_key="...")

# Search everything
articles = await client.search_everything(
    query="Tesla earnings",
    from_date=datetime.now() - timedelta(days=7),
    language="en",
    sort_by="relevancy"
)
# Returns: title, description, content, source, author, published date

# Top headlines
headlines = await client.get_top_headlines(
    country="us",
    category="business"
)

# Filter by source
tech_news = await client.search_everything(
    query="AI",
    sources="techcrunch,wired,ars-technica"
)
```

**Rate Limits:**
- Developer (free): 100 requests/day, 1 month history
- Business: 250,000 requests/month, full history

**Dashboard:** https://newsapi.org/account

---

### GNews
**Purpose:** Global news from 60,000+ sources

**Environment Variable:** `GNEWS_API_KEY`

**Capabilities:**
- News search
- Top headlines by topic
- Country filtering
- Language support (40+)
- Date filtering

**What You Can Do:**
```python
from src.company_researcher.integrations import GNewsClient

client = GNewsClient(api_key="...")

# Search news
articles = await client.search(
    query="Microsoft Azure",
    max_results=10,
    language="en"
)
# Returns: title, description, content, url, image, published date

# Top headlines by topic
headlines = await client.get_top_headlines(
    topic="business",
    country="us"
)
# Topics: world, nation, business, technology, entertainment, sports, science, health
```

**Rate Limits:**
- Free: 100 requests/day
- Basic: 1,000 requests/day ($29/mo)

**Dashboard:** https://gnews.io/dashboard

---

### Mediastack
**Purpose:** Live news from 7,500+ sources

**Environment Variable:** `MEDIASTACK_API_KEY`

**Capabilities:**
- Live news feed
- Historical news (paid)
- Category filtering
- Country/language filtering
- Keyword search

**What You Can Do:**
```python
from src.company_researcher.integrations import MediastackClient

client = MediastackClient(api_key="...")

# Search news
articles = await client.search(
    keywords="Apple iPhone",
    countries="us,gb",
    languages="en",
    categories="business,technology",
    limit=25
)
# Returns: author, title, description, url, source, image, category, published date

# Live news
live = await client.get_live_news(limit=50)
```

**Rate Limits:**
- Free: 500 requests/month, HTTP only, 15-min delay
- Basic: 10,000 requests/month, HTTPS ($12.99/mo)

**Dashboard:** https://mediastack.com/dashboard

---

## 5. Contact & Company Data

### Hunter.io
**Purpose:** Email discovery and verification

**Environment Variable:** `HUNTER_API_KEY`

**Capabilities:**
- Domain search (find all emails at a domain)
- Email finder (find specific person's email)
- Email verification
- Company information
- Email patterns

**What You Can Do:**
```python
from src.company_researcher.integrations import HunterIOClient

client = HunterIOClient(api_key="...")

# Find emails at a domain
result = await client.domain_search("microsoft.com")
# Returns: list of emails with names, positions, confidence scores

# Find specific person's email
email = await client.email_finder(
    domain="microsoft.com",
    first_name="Satya",
    last_name="Nadella"
)
# Returns: email, confidence score, sources

# Verify email
verification = await client.verify_email("test@microsoft.com")
# Returns: result (deliverable/undeliverable), score, checks

# Get account usage
account = await client.get_account()
# Returns: searches used/available, verifications used/available
```

**Rate Limits:**
- Free: 25 searches/month, 50 verifications/month
- Starter: 500 searches/month ($49/mo)

**Dashboard:** https://hunter.io/dashboard

---

### Crunchbase
**Purpose:** Startup and company data

**Environment Variable:** `CRUNCHBASE_API_KEY`

**Capabilities:**
- Company profiles
- Funding history
- Investors
- Acquisitions
- Key people
- News mentions

**What You Can Do:**
```python
from src.company_researcher.integrations import CrunchbaseClient

client = CrunchbaseClient(api_key="...")

# Company profile
company = await client.get_company("openai")
# Returns: description, founded date, funding total, employee count

# Funding rounds
funding = await client.get_funding_rounds("openai")
# Returns: round type, amount, date, investors

# Key people
people = await client.get_key_people("openai")
# Returns: name, title, LinkedIn
```

**Note:** Crunchbase API has limited free access. Consider their data licensing for production use.

---

## 6. Web Scraping

### Firecrawl
**Purpose:** LLM-ready web scraping

**Environment Variable:** `FIRECRAWL_API_KEY`

**Capabilities:**
- Single page scraping to markdown
- Full website crawling
- URL mapping/discovery
- Structured data extraction
- Screenshot capture

**What You Can Do:**
```python
from src.company_researcher.integrations import FirecrawlClient

client = FirecrawlClient(api_key="...")

# Scrape single page
page = await client.scrape_url("https://company.com/about")
# Returns: markdown content, metadata, links

# Crawl entire website
result = await client.crawl_website(
    url="https://company.com",
    max_pages=50,
    include_paths=["/blog/*", "/news/*"]
)
# Returns: list of pages with markdown content

# Map website URLs
urls = await client.map_url("https://company.com")
# Returns: list of all discovered URLs

# Extract structured data
data = await client.extract(
    url="https://company.com/team",
    schema={"employees": [{"name": "string", "role": "string"}]}
)
# Returns: structured JSON matching schema
```

**Rate Limits:**
- Free: 500 credits (1 credit = 1 page)
- Hobby: 3,000 credits/month ($19/mo)

**Dashboard:** https://firecrawl.dev/dashboard

---

### ScrapeGraph
**Purpose:** AI-powered web extraction

**Environment Variable:** `SCRAPEGRAPH_API_KEY`

**Capabilities:**
- Natural language extraction prompts
- Structured output with schemas
- Multi-page crawling with extraction
- Search and scrape

**What You Can Do:**
```python
from src.company_researcher.integrations import ScrapeGraphClient

client = ScrapeGraphClient(api_key="...")

# Smart scrape with prompt
result = await client.smart_scrape(
    url="https://company.com/about",
    prompt="Extract the company's mission statement and founding year"
)
# Returns: extracted data based on prompt

# Scrape with schema
result = await client.scrape_with_schema(
    url="https://company.com/team",
    schema={
        "team_members": [{
            "name": "string",
            "role": "string",
            "bio": "string"
        }]
    }
)
# Returns: structured data matching schema

# Search and scrape
result = await client.search_and_scrape(
    query="Tesla factory locations",
    num_results=5
)
# Returns: scraped content from search results
```

---

## 7. Social Media

### Reddit
**Purpose:** Community discussions and sentiment

**Environment Variables:**
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

**Capabilities:**
- Subreddit posts
- Comments
- User posts
- Search across Reddit
- Sentiment analysis (via content)

**What You Can Do:**
```python
from src.company_researcher.integrations import RedditClient

client = RedditClient(
    client_id="...",
    client_secret="...",
    user_agent="CompanyResearcher/1.0"
)

# Search subreddit
posts = await client.search_subreddit(
    subreddit="stocks",
    query="AAPL",
    sort="relevance",
    limit=25
)
# Returns: title, content, author, score, comments count, url

# Get hot posts
hot = await client.get_hot_posts("wallstreetbets", limit=10)

# Get comments on post
comments = await client.get_comments(post_id)
# Returns: comment tree with scores

# Search all of Reddit
results = await client.search("Tesla stock", limit=50)
```

**Rate Limits:**
- OAuth: 100 requests/minute
- Unauthenticated: 10 requests/minute

**Dashboard:** https://www.reddit.com/prefs/apps

---

### GitHub
**Purpose:** Tech company/project research

**Environment Variable:** `GITHUB_TOKEN`

**Capabilities:**
- Repository search
- Organization info
- Code search
- Contributor analysis
- Release tracking
- Issue/PR activity

**What You Can Do:**
```python
from src.company_researcher.integrations import GitHubClient

client = GitHubClient(token="...")

# Search repositories
repos = await client.search_repos("openai language:python")
# Returns: name, description, stars, forks, language, topics

# Get organization
org = await client.get_organization("microsoft")
# Returns: name, description, public repos count, followers

# Get repository details
repo = await client.get_repository("microsoft/vscode")
# Returns: full details including contributors, releases

# Search code
code = await client.search_code("api key in:file language:python")
# Returns: file paths and snippets

# Get rate limit status
limits = await client.get_rate_limit()
# Returns: limit, remaining, reset time
```

**Rate Limits:**
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour

**Dashboard:** https://github.com/settings/tokens

---

## 8. Geolocation

### OpenCage
**Purpose:** Geocoding company locations

**Environment Variable:** `OPENCAGE_API_KEY`

**Capabilities:**
- Forward geocoding (address to coordinates)
- Reverse geocoding (coordinates to address)
- Timezone information
- Currency information
- Boundary data

**What You Can Do:**
```python
from src.company_researcher.integrations import OpenCageClient

client = OpenCageClient(api_key="...")

# Forward geocode
result = await client.geocode("1 Apple Park Way, Cupertino, CA")
# Returns: lat, lng, formatted address, country, timezone, bounds

# Reverse geocode
result = await client.reverse_geocode(37.3349, -122.0090)
# Returns: address components, timezone, what3words

# Batch geocode
results = await client.batch_geocode([
    "Microsoft Way, Redmond, WA",
    "1600 Amphitheatre Parkway, Mountain View, CA"
])
```

**Rate Limits:**
- Free: 2,500 requests/day
- Small: 10,000 requests/day ($50/mo)

**Dashboard:** https://opencagedata.com/dashboard

---

### Nominatim (OpenStreetMap)
**Purpose:** Free geocoding (no API key)

**Environment Variable:** None required

**Capabilities:**
- Forward geocoding
- Reverse geocoding
- Address search
- POI search

**What You Can Do:**
```python
from src.company_researcher.integrations import NominatimClient

client = NominatimClient(user_agent="CompanyResearcher/1.0")

# Geocode address
result = await client.geocode("Apple Park, Cupertino")
# Returns: lat, lng, display name, address components

# Search
results = await client.search("tech companies near San Francisco")
```

**Rate Limits:**
- 1 request/second (be respectful)
- No heavy usage

---

## 9. Regulatory Data

### SEC EDGAR
**Purpose:** US public company filings

**Environment Variable:** None (but set user agent)

**Capabilities:**
- 10-K (annual reports)
- 10-Q (quarterly reports)
- 8-K (current reports)
- Proxy statements
- Insider transactions
- Company facts API

**What You Can Do:**
```python
from src.company_researcher.integrations import SECEdgarClient

client = SECEdgarClient(user_agent="your-email@company.com")

# Get company filings
filings = await client.get_filings(
    cik="0000320193",  # Apple's CIK
    form_types=["10-K", "10-Q"],
    limit=10
)
# Returns: filing date, form type, document URLs

# Get company facts (structured data)
facts = await client.get_company_facts("0000320193")
# Returns: all reported facts (revenue, assets, etc.) in structured format

# Search filings
results = await client.search_filings(
    query="artificial intelligence",
    form_types=["10-K"],
    date_from="2024-01-01"
)

# Get specific filing content
content = await client.get_filing_document(filing_url)
```

**Rate Limits:**
- 10 requests/second
- Must include valid User-Agent with contact email

**Documentation:** https://www.sec.gov/developer

---

## 10. ML/AI Services

### HuggingFace
**Purpose:** ML model inference

**Environment Variable:** `HUGGINGFACE_API_KEY`

**Capabilities:**
- Text classification
- Named entity recognition
- Sentiment analysis
- Text generation
- Embeddings
- Zero-shot classification

**What You Can Do:**
```python
from src.company_researcher.integrations import HuggingFaceClient

client = HuggingFaceClient(api_key="...")

# Sentiment analysis
sentiment = await client.analyze_sentiment(
    "Apple reported record quarterly revenue"
)
# Returns: label (positive/negative), score

# Named entity recognition
entities = await client.extract_entities(
    "Tim Cook announced new products at Apple Park"
)
# Returns: entities with types (PERSON, ORG, LOC)

# Zero-shot classification
result = await client.classify(
    text="Tesla opens new factory in Berlin",
    labels=["expansion", "layoffs", "earnings", "product launch"]
)
# Returns: best matching label with confidence

# Text embeddings
embeddings = await client.get_embeddings(["text1", "text2"])
# Returns: vector embeddings for similarity search
```

**Rate Limits:**
- Free: Rate limited (varies by model)
- Pro: Higher limits ($9/mo)

**Dashboard:** https://huggingface.co/settings/tokens

---

## Unified Providers

### FinancialDataProvider
**Purpose:** Unified interface with automatic fallback

**Fallback Chain:** yfinance → FMP → Finnhub → Polygon

```python
from src.company_researcher.integrations import create_financial_provider

provider = create_financial_provider(config)

# Automatically tries providers in order
data = provider.get_financial_data("AAPL")
# Returns: FinancialData with price, market cap, PE, revenue, etc.
```

### NewsProvider
**Purpose:** Unified news with automatic fallback

**Fallback Chain:** NewsAPI → GNews → Mediastack → Tavily

```python
from src.company_researcher.integrations import create_news_provider

provider = create_news_provider(config)

# Automatically aggregates from available providers
news = provider.search_news("Tesla", max_results=20)
# Returns: deduplicated articles from all sources
```

---

## Checking Your Quotas

Run the quota checker to see status of all APIs:

```bash
python src/company_researcher/integrations/api_quota_checker.py
```

Output shows:
- Which APIs are configured
- Current usage vs limits
- Reset times
- Error status

---

## Environment Setup

Create a `.env` file with your API keys:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# Financial (at least one recommended)
FMP_API_KEY=...
FINNHUB_API_KEY=...
POLYGON_API_KEY=...

# News (at least one recommended)
NEWSAPI_KEY=...
GNEWS_API_KEY=...
MEDIASTACK_API_KEY=...

# Optional but useful
HUNTER_API_KEY=...
FIRECRAWL_API_KEY=...
GITHUB_TOKEN=ghp_...
OPENCAGE_API_KEY=...
HUGGINGFACE_API_KEY=hf_...

# Reddit (optional)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

---

## Cost Optimization Tips

1. **Use free tiers wisely** - yfinance and SEC EDGAR have no limits
2. **Cache aggressively** - Most data doesn't change hourly
3. **Use unified providers** - They handle fallbacks automatically
4. **Batch requests** - When APIs support it
5. **Monitor usage** - Run quota checker regularly
6. **Prioritize sources** - Configure provider order based on your needs
