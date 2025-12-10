# Data Flow Analysis & Optimization Recommendations

## Current State: How Data Flows Now

### Basic Workflow (basic_research.py)

```
START
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Query Generation                                   │
│   generate_queries_node()                                   │
│   - Multilingual query generation                           │
│   - Parent company detection                                │
│   - 10-13 search queries generated                         │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Search (ONLY TAVILY)                               │
│   search_node()                                             │
│   - Sequential Tavily searches                              │
│   - No financial API calls                                  │
│   - No web scraping                                         │
│   - No SEC filings                                          │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: LLM Analysis                                       │
│   analyze_node() → news_sentiment_node() → extract_data_node()
│   - Claude analyzes search results                          │
│   - Sentiment extracted from search (not dedicated news)    │
│   - Structured data extraction                              │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Quality Check                                      │
│   check_quality_node()                                      │
│   - Score calculation                                       │
│   - Missing info detection                                  │
│   - If < 85: loop back to generate_queries (expensive!)     │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Advanced Analysis                                  │
│   competitive_analysis → risk_assessment → investment_thesis│
│   - All depend on LLM-extracted data                        │
│   - No fresh data fetching for analysis                     │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Report                                             │
│   save_report_node()                                        │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
END
```

### Comprehensive Workflow (comprehensive_research.py)

```
START
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Data Collection (Sequential, Not Parallel!)        │
│   generate_queries → search → fetch_financial → fetch_news  │
│   - Each step waits for previous to complete                │
│   - Could run in parallel but doesn't                       │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Parallel Analysis (Also Sequential!)               │
│   core → financial → market → esg → brand → sentiment       │
│   - Despite "parallel" in docs, runs sequentially           │
│   - Code comment: "Parallel would be ideal but keeping      │
│     sequential for simplicity"                              │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
(Same as basic from here)
```

---

## Problems with Current Flow

### 1. Data Sources - Only Using ~25%

| Source | Status | Impact |
|--------|--------|--------|
| Tavily Search | ✓ USED | Primary data source |
| Financial APIs (FMP/Finnhub/Polygon) | PARTIAL | Only via provider fallback |
| SEC EDGAR | ✗ UNUSED | **FREE** - 10-K, 10-Q, 8-K available |
| Company Websites | ✗ UNUSED | Firecrawl/ScrapeGraph ready |
| News APIs | PARTIAL | NewsAPI used but not GNews/Mediastack |
| Reddit | ✗ UNUSED | Customer sentiment missing |
| GitHub | ✗ UNUSED | Tech company analysis missing |
| Hunter.io | ✗ UNUSED | Contact discovery missing |

### 2. Sequential Where Parallel Would Help

**Current:** Data collection runs sequentially
```
search ─→ financial ─→ news  (15-20 seconds total)
```

**Better:** Run data collection in parallel
```
search     ┐
financial  ├─→ (5-8 seconds total)
news       ┘
```

### 3. Wasteful Iteration Strategy

**Current:** When quality < 85, restart from scratch
```
Quality check fails → generate_queries → search → analyze → ...
```

**Problem:** Re-runs ALL searches even if only one area is weak (e.g., financials).

**Better:** Targeted gap-filling
```
Quality check fails → identify_gaps → fetch_missing_only → reanalyze
```

### 4. No Primary Source Integration

Currently relies 100% on web search results parsed by LLM.

**Missing Primary Sources:**
- SEC filings (10-K, 10-Q for US public companies)
- Company investor relations pages
- Official press releases
- Earnings call transcripts

### 5. Analysis Without Real Data

The current flow:
```
LLM extracts "financials" from search snippets → LLM creates investment thesis
```

The data path is: **Web snippet → LLM interpretation → LLM analysis**

Better:
```
Real financial data from API → Direct analysis with actual numbers
```

---

## Recommended Data Flow v2.0

### Proposed Architecture

```
START
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Entity Resolution & Classification (NEW)           │
│                                                              │
│   identify_company()                                         │
│   - Detect if public/private company                         │
│   - Find ticker symbol (if public)                           │
│   - Detect region (US, EU, LATAM, APAC)                     │
│   - Detect industry sector                                   │
│   - Check if tech company (for GitHub analysis)              │
│                                                              │
│   Output: company_profile                                    │
│   {                                                          │
│     ticker: "AAPL",                                         │
│     is_public: true,                                        │
│     region: "US",                                           │
│     industry: "Technology",                                 │
│     data_strategies: ["sec_filings", "financial_apis", ...] │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Parallel Data Collection (CONCURRENT!)             │
│                                                              │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │ Web Search  │ │ Financial   │ │ News        │           │
│   │ (Tavily)    │ │ APIs        │ │ (NewsAPI)   │           │
│   │             │ │ (FMP/yf)    │ │             │           │
│   └─────────────┘ └─────────────┘ └─────────────┘           │
│         │               │               │                    │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │ SEC EDGAR   │ │ Company     │ │ Social      │           │
│   │ (if US)     │ │ Website     │ │ (Reddit)    │           │
│   │             │ │ (Firecrawl) │ │             │           │
│   └─────────────┘ └─────────────┘ └─────────────┘           │
│         │               │               │                    │
│         └───────────────┼───────────────┘                    │
│                         ▼                                    │
│              Combined Raw Data Store                         │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Data Validation & Deduplication (NEW)              │
│                                                              │
│   validate_and_dedupe()                                      │
│   - Cross-reference facts across sources                     │
│   - Flag contradictions early                                │
│   - Score source reliability                                 │
│   - Track data freshness                                     │
│                                                              │
│   Output: validated_data_store with confidence scores        │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: Parallel Analysis (TRUE PARALLEL with asyncio)     │
│                                                              │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │ Financial   │ │ Market &    │ │ ESG         │           │
│   │ Analysis    │ │ Competitive │ │ Analysis    │           │
│   │ (uses real  │ │ Analysis    │ │             │           │
│   │ API data!)  │ │             │ │             │           │
│   └─────────────┘ └─────────────┘ └─────────────┘           │
│         │               │               │                    │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │ Risk        │ │ Sentiment   │ │ Brand       │           │
│   │ Assessment  │ │ Analysis    │ │ Analysis    │           │
│   │             │ │ (news +     │ │             │           │
│   │             │ │ social)     │ │             │           │
│   └─────────────┘ └─────────────┘ └─────────────┘           │
│         │               │               │                    │
│         └───────────────┼───────────────┘                    │
│                         ▼                                    │
│              Combined Analysis Results                       │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: Gap Detection & Targeted Fill (NEW)                │
│                                                              │
│   detect_gaps()                                              │
│   - Check coverage for each section                          │
│   - Identify specific missing data points                    │
│                                                              │
│   If gaps found:                                             │
│   targeted_fill()                                            │
│   - Only fetch what's missing                                │
│   - Use appropriate source for gap type                      │
│   - e.g., Missing financials → Financial API retry           │
│   - e.g., Missing ESG → ESG-specific search                  │
│                                                              │
│   Loop limit: 2 targeted iterations (not full restarts!)     │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: Synthesis & Investment Thesis                      │
│                                                              │
│   synthesize()                                               │
│   - Combine all validated analyses                           │
│   - Weight by confidence scores                              │
│   - Generate investment thesis with actual data              │
│   - Create comprehensive report                              │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
END
```

---

## Implementation Priority

### Immediate Wins (1-2 days)

1. **Add SEC EDGAR to Phase 2** (FREE!)
   ```python
   # In comprehensive_research.py
   async def fetch_sec_filings_node(state):
       if state["is_us_public"]:
           client = SECEdgarClient()
           filings = await client.get_filings(state["ticker"])
           return {"sec_filings": filings}
   ```

2. **Parallelize Data Collection**
   ```python
   # Use asyncio.gather for parallel fetches
   async def parallel_data_collection(state):
       results = await asyncio.gather(
           search_task(state),
           financial_task(state),
           news_task(state),
           sec_task(state) if state["is_us_public"] else asyncio.sleep(0),
           return_exceptions=True
       )
       return merge_results(results)
   ```

3. **Add Entity Resolution Node**
   ```python
   def identify_company_node(state):
       company_name = state["company_name"]

       # Try to find ticker
       ticker = guess_ticker(company_name)

       # Detect if public
       is_public = ticker is not None

       # Detect region
       region = detect_region(company_name)

       # Detect industry
       industry = detect_industry(company_name)

       return {
           "ticker": ticker,
           "is_public": is_public,
           "region": region,
           "industry": industry,
       }
   ```

### Short Term (1 week)

4. **Add Company Website Scraping**
   ```python
   async def scrape_company_website_node(state):
       client = FirecrawlClient()
       # Find company website from search results
       website = extract_company_website(state["search_results"])
       if website:
           about_page = await client.scrape(f"{website}/about")
           team_page = await client.scrape(f"{website}/team")
           return {"website_data": {"about": about_page, "team": team_page}}
   ```

5. **Implement Targeted Gap Filling**
   ```python
   def detect_and_fill_gaps(state):
       gaps = identify_gaps(state)

       for gap in gaps:
           if gap.type == "financial":
               # Try different financial source
               data = retry_financial_fetch(state)
           elif gap.type == "leadership":
               # Search specifically for leadership
               data = search_leadership(state["company_name"])
           # ...

       return merge_gap_data(state, data)
   ```

### Medium Term (2-3 weeks)

6. **Add Reddit/Social Sentiment**
7. **Add GitHub Analysis for Tech Companies**
8. **Add True Async Parallel Analysis Nodes**

---

## Data Source Priority by Company Type

### US Public Company (e.g., Apple, Microsoft)

| Priority | Source | Data Type |
|----------|--------|-----------|
| 1 | SEC EDGAR | 10-K, 10-Q, 8-K, DEF 14A |
| 2 | Financial APIs | Real-time quotes, fundamentals |
| 3 | News APIs | Recent news, press releases |
| 4 | Tavily Search | Web content, analysis |
| 5 | Company Website | IR page, leadership |

### International Public Company (e.g., Embraer, Samsung)

| Priority | Source | Data Type |
|----------|--------|-----------|
| 1 | Financial APIs | Fundamentals (limited) |
| 2 | Tavily Search | Multilingual search |
| 3 | News APIs | International news |
| 4 | Company Website | IR page (may need translation) |

### Private Company (e.g., Startup)

| Priority | Source | Data Type |
|----------|--------|-----------|
| 1 | Tavily Search | Press, funding news |
| 2 | Company Website | About, team, products |
| 3 | Crunchbase | Funding, investors |
| 4 | News APIs | Recent coverage |
| 5 | GitHub (if tech) | Open source activity |
| 6 | Reddit | Product sentiment |

---

## Expected Impact

### Current Performance

| Metric | Current |
|--------|---------|
| Data sources used | 2-3 |
| Primary source data | 0% |
| Parallel operations | 0% |
| Time for research | ~45-60s |
| Iteration efficiency | 0% (full restart) |

### After Optimization

| Metric | Expected |
|--------|----------|
| Data sources used | 6-8 |
| Primary source data | 40-60% (SEC filings!) |
| Parallel operations | 80% |
| Time for research | ~20-30s |
| Iteration efficiency | 70% (targeted fill) |

### Quality Improvements

- **Financial Accuracy**: 40% → 85% (real API data vs. LLM extraction)
- **Data Freshness**: Variable → Tracked (FreshnessTracker)
- **Source Reliability**: Unknown → Scored (SourceQualityAssessor)
- **Coverage**: 60% → 90% (more data sources)

---

## Summary: The Core Changes

1. **Start with entity resolution** - Know what kind of company before searching
2. **Parallelize all data fetching** - Don't wait sequentially
3. **Use primary sources first** - SEC, financial APIs, company website
4. **Validate before analyzing** - Cross-reference, detect contradictions early
5. **Fill gaps surgically** - Don't restart entire workflow
6. **Use real numbers** - Financial APIs, not LLM extraction from snippets

**The key insight:** We're currently using LLMs to extract data that APIs provide directly. SEC EDGAR is FREE and gives exact financial data, but we're ignoring it and asking Claude to guess from web snippets.
