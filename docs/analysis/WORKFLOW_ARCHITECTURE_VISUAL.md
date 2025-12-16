# Company Researcher Workflow - Visual Architecture Guide

## 1. High-Level Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INPUT: Company Name                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PHASE 1:       │
                    │ Classification  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    Region:          Language:              Company Type:
    LATAM/EU/NA      Spanish/English        Public/Private/NGO
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PHASE 2:       │
                    │ Query Generation│
                    │ (10-20 queries) │
                    └────────┬────────┘
                             │
        ┌────────┬───────────┼──────────┬────────┐
        │        │           │          │        │
        ▼        ▼           ▼          ▼        ▼
    Base      Multi-      Specialized Regional  Parent
    Queries   lingual     Queries     Queries   Company
             Queries
        │        │           │          │        │
        └────────┴───────────┼──────────┴────────┘
                             │
         ┌───────────────────▼───────────────────┐
         │                                       │
         │   ╔═════════════════════════════════╗ │
         │   ║   ITERATION LOOP (max 2)       ║ │
         │   ╚═════════════════════════════════╝ │
         │                                       │
         │   ┌─────────────────────────────────┐ │
         │   │ PHASE 3: Search Execution       │ │
         │   │                                 │ │
         │   │ [Provider Fallback Chain]       │ │
         │   │  1. DuckDuckGo (FREE)           │ │
         │   │  2. Brave ($0.0003)             │ │
         │   │  3. Serper ($0.01)              │ │
         │   │  4. Tavily ($0.02)              │ │
         │   │                                 │ │
         │   │ ├─ Cache Check (saves $)        │ │
         │   │ ├─ Provider Health Tracking     │ │
         │   │ ├─ Result Deduplication (URL+) │ │
         │   │ └─ Calibrated Scoring          │ │
         │   └─────────────────────────────────┘ │
         │                  │                    │
         │                  ▼                    │
         │   ┌─────────────────────────────────┐ │
         │   │ PHASE 4: Data Extraction        │ │
         │   │                                 │ │
         │   │ ├─ Company Classification       │ │
         │   │ ├─ Fact Extraction (confidence) │ │
         │   │ ├─ Contradiction Detection      │ │
         │   │ └─ Field Completeness Check     │ │
         │   └─────────────────────────────────┘ │
         │                  │                    │
         │                  ▼                    │
         │   ┌─────────────────────────────────┐ │
         │   │ PHASE 5: Quality Assessment     │ │
         │   │                                 │ │
         │   │ ├─ Field Completeness (fast)    │ │
         │   │ ├─ LLM Assessment (cheap model) │ │
         │   │ ├─ Composite Score (0-100)      │ │
         │   │ └─ Gap Analysis                 │ │
         │   │   └─ Recommended Queries        │ │
         │   └─────────────────────────────────┘ │
         │                  │                    │
         │          ┌───────▼────────┐           │
         │          │   DECISION:    │           │
         │          │ Continue?      │           │
         │          └──────┬─────────┘           │
         │                 │                    │
         │     ┌───────────┼───────────┐        │
         │     │           │           │        │
         │ quality<85?   iter<2?   YES│        │
         │     │YES        YES        │        │
         │     └───────────┬───────────┘        │
         │                 │                    │
         │    [Generate Gap-Filling Queries]    │
         │                 │                    │
         │    (Loop back to PHASE 3)            │
         │                                       │
         └───────────────────┬───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PHASE 6:       │
                    │ Report Generation│
                    │                 │
                    │ ├─ Synthesize   │
                    │ ├─ Validate     │
                    │ ├─ Format       │
                    │ └─ Export       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  OUTPUT:        │
                    │ Report + Metrics│
                    └─────────────────┘
```

---

## 2. Query Generation Pipeline

```
INPUT: company_name, region, language
│
├─ AIQueryGenerator.generate_queries()
│  │
│  ├─ LLM Prompt: "Generate 5 search queries for {company}"
│  ├─ Parse response into structured queries
│  └─ Return: List[MultilingualQuery]
│
├─ MultilingualSearchGenerator
│  │
│  ├─ generate_queries(region, language)
│  │  └─ Leverage regional knowledge
│  │
│  ├─ get_parent_company_queries()
│  │  └─ Search holding company if private
│  │
│  ├─ get_alternative_name_queries()
│  │  └─ Search alternate names (trading as, DBA, etc.)
│  │
│  └─ get_regional_source_queries()
│     └─ Country-specific sources (site:conatel.gov.py)
│
├─ Specialized Query Templates
│  │
│  ├─ CEO/Leadership Queries (5+)
│  │  └─ "who is CEO", "gerente general", "appointed"
│  │
│  ├─ Financial Queries (3+)
│  │  └─ "revenue", "earnings", "net income"
│  │
│  ├─ Competitive Queries (3+)
│  │  └─ "competitors", "market share", "vs"
│  │
│  ├─ Product Queries (3+)
│  │  └─ "products", "services", "offerings"
│  │
│  ├─ Market Position Queries (3+)
│  │  └─ "market cap", "stock price", "trading"
│  │
│  └─ News & Recent Queries (3+)
│     └─ "news", "announcement", "2024"
│
├─ QueryDiversifier
│  │
│  ├─ Category-based generation (8 categories)
│  │  ├─ Official Filings (SEC 10-K)
│  │  ├─ Investor Relations (earnings calls)
│  │  ├─ Financial News
│  │  ├─ Company Overview
│  │  ├─ Competitive Analysis
│  │  ├─ Product Info
│  │  ├─ Recent News
│  │  └─ Leadership
│  │
│  └─ Semantic deduplication
│     └─ Remove 85%+ similar queries
│
└─ AIQueryGenerator.refine_queries()
   │
   ├─ Analyze coverage gaps from initial queries
   ├─ Identify missing categories
   ├─ Generate additional queries to fill gaps
   └─ Return: Refined query list

OUTPUT: 10-20+ optimized, diverse queries
```

---

## 3. Search Execution Flow (Provider Fallback)

```
FOR EACH QUERY:
│
├─ Check Persistent Cache (.cache/search/)
│  │
│  ├─ Cache Key = SHA256(query + max_results)
│  │
│  ├─ Found & Fresh? (TTL < 30 days)
│  │  ├─ YES → Return cached result (COST: $0)
│  │  └─ No semantic deduplication needed
│  │
│  └─ NOT Found → Continue to live search
│
├─ Provider Selection (COST-OPTIMIZED)
│  │
│  ├─ Filter to HEALTHY providers
│  │  │
│  │  └─ ProviderHealth.is_healthy = No 3+ consecutive failures
│  │
│  ├─ Try Providers in Order:
│  │
│  │  1. DuckDuckGo (FREE)
│  │     ├─ Success? → Cache + Return (✓)
│  │     └─ Fail? → Try next provider
│  │
│  │  2. Brave ($0.0003 per 3 results)
│  │     ├─ Success? → Cache + Return (✓)
│  │     └─ Fail? → Try next provider
│  │
│  │  3. Serper ($0.01 per search)
│  │     ├─ Success? → Cache + Return (✓)
│  │     └─ Fail? → Try next provider
│  │
│  │  4. Tavily ($0.02 per search)
│  │     ├─ Success? → Cache + Return (✓)
│  │     └─ Fail? → Return empty results
│  │
│  ├─ Special Handling for EXECUTIVE queries
│  │  └─ min_results=5 forces escalation to Serper
│  │
│  └─ Health Tracking
│     ├─ Success: consecutive_failures = 0
│     ├─ Failure: consecutive_failures++
│     ├─ 3+ failures: Exponential backoff (60s, 120s, 240s...)
│     └─ All providers down: Reset health, try again
│
├─ Result Processing
│  │
│  ├─ Normalize results (url, title, snippet)
│  │
│  ├─ Deduplication:
│  │  │
│  │  ├─ URL-based (exact match)
│  │  │  └─ Remove duplicate URLs
│  │  │
│  │  └─ Semantic (85%+ similarity)
│  │     ├─ Encode snippet with SentenceTransformer
│  │     ├─ Compare embeddings
│  │     └─ Remove 85%+ similar content
│  │
│  ├─ Scoring (Calibrated):
│  │  │
│  │  ├─ Authority (domain-based)
│  │  │  ├─ sec.gov: 1.0
│  │  │  ├─ bloomberg.com, reuters.com: 0.85
│  │  │  ├─ techcrunch.com, forbes.com: 0.70
│  │  │  ├─ .com/.org/.net: 0.55
│  │  │  └─ other: 0.40
│  │  │
│  │  ├─ Relevance (query match in title/snippet)
│  │  │  ├─ Title match: 60% weight
│  │  │  └─ Snippet match: 40% weight
│  │  │
│  │  ├─ Rank Decay (position in results)
│  │  │  └─ factor = 1.0 / (1.0 + 0.1 * position)
│  │  │
│  │  └─ Combined Score:
│  │     = authority * 0.4
│  │     + relevance * 0.4
│  │     + rank_decay * 0.2
│  │
│  └─ Add to Results
│
├─ Cache Result
│  │
│  ├─ Store in .cache/search/{query_hash}.json
│  ├─ TTL: 30 days
│  └─ Format: SearchResponse (serializable)
│
└─ Return SearchResponse
   ├─ results: List[SearchResult]
   ├─ provider: Which provider succeeded
   ├─ cost: API cost (or $0 for cache hit)
   ├─ cached: bool
   └─ success: bool

PROVIDER COSTS:
├─ Cache Hit: $0.00 (saves 100%)
├─ DuckDuckGo: $0.00 (unlimited free)
├─ Brave: ~$0.0003 per result (3 results = $0.0009)
├─ Serper: $0.01 per search
└─ Tavily: $0.02 per search

TYPICAL COST PER QUERY:
├─ Best case: $0.00 (cache hit)
├─ Good case: $0.00 (DuckDuckGo)
├─ OK case: $0.001 (Brave 3 results)
└─ Bad case: $0.01-0.02 (Serper/Tavily)
```

---

## 4. Data Extraction Pipeline

```
INPUT: search_results (raw text), extracted_data (if iteration 2+)
│
├─ PHASE 4A: Company Classification
│  │
│  ├─ Classify company type
│  │  ├─ Public (traded on stock exchange)
│  │  ├─ Private (not traded)
│  │  ├─ NGO/Non-profit
│  │  ├─ Government
│  │  └─ Academic/Research
│  │
│  ├─ Detect region
│  │  ├─ LATAM, North America, Europe, Asia Pacific, etc.
│  │
│  ├─ Identify available data sources
│  │  ├─ SEC EDGAR (US public companies)
│  │  ├─ Investor relations website
│  │  ├─ Stock exchange filings
│  │  ├─ Press releases
│  │  └─ News outlets
│  │
│  └─ Determine special handling
│     ├─ Parent company data available?
│     └─ Regional regulatory requirements?
│
├─ PHASE 4B: Fact Extraction
│  │
│  ├─ For each search result:
│  │  │
│  │  ├─ Extract facts with confidence
│  │  │  ├─ Field: revenue, ceo, employees, etc.
│  │  │  ├─ Value: the extracted value
│  │  │  ├─ Confidence: 0-1 score
│  │  │  ├─ Source: URL and context
│  │  │  └─ Type: string, number, date, url
│  │  │
│  │  ├─ Categorize fact
│  │  │  ├─ Financial (revenue, profit, margins)
│  │  │  ├─ Operational (employees, locations)
│  │  │  ├─ Leadership (CEO, board)
│  │  │  ├─ Market (market cap, share price)
│  │  │  └─ Products (offerings, services)
│  │  │
│  │  └─ Store fact with source attribution
│  │
│  └─ Result: List[ExtractedFact]
│
├─ PHASE 4C: Contradiction Detection
│  │
│  ├─ Rule-based detection
│  │  ├─ Format conflicts (e.g., "10,000" vs "10K")
│  │  ├─ Temporal conflicts (date range, obsolescence)
│  │  └─ Magnitude outliers (e.g., revenue in billions vs thousands)
│  │
│  ├─ LLM-based semantic detection
│  │  ├─ Analyze conflicting facts semantically
│  │  └─ Determine if truly contradictory
│  │
│  ├─ Severity scoring
│  │  ├─ CRITICAL: Blocks publication (e.g., wrong CEO)
│  │  ├─ MAJOR: Should be fixed (e.g., 10% revenue discrepancy)
│  │  ├─ MINOR: Nice to fix (e.g., extra spaces)
│  │  └─ INFO: Informational only
│  │
│  └─ Result: List[Contradiction]
│
├─ PHASE 4D: Field Completeness Check
│  │
│  ├─ Scan extracted_data for field keywords
│  │
│  ├─ REQUIRED FIELDS (15 core fields):
│  │  ├─ Core (5): company_name, headquarters, founded, industry, employees
│  │  ├─ Leadership (2): ceo, leadership_team
│  │  ├─ Financial (3): revenue, profit_margin, market_cap
│  │  ├─ Market (3): market_share, subscribers, competitors
│  │  └─ Operational (2): products_services, geographic_presence
│  │
│  ├─ Categorize missing fields by priority
│  │  ├─ CRITICAL (4): company_name, revenue, ceo, market_share
│  │  ├─ IMPORTANT (4): headquarters, employees, competitors, subscribers
│  │  └─ OTHER (7): all remaining fields
│  │
│  ├─ Calculate completeness score
│  │  └─ field_score = (present / total) * 100
│  │
│  └─ Result: Dict[field_score, present_fields, missing_fields]
│
└─ PHASE 4E: Generate Gap Queries
   │
   ├─ For each missing field:
   │  └─ Create targeted query template
   │
   ├─ Example:
   │  ├─ Missing "ceo" → Query: "Apple CEO name"
   │  ├─ Missing "revenue" → Query: "Apple annual revenue 2024"
   │  ├─ Missing "market_share" → Query: "Apple market share smartphone"
   │  └─ Missing "competitors" → Query: "Apple competitors in smartphone market"
   │
   └─ Result: List[gap_filling_queries]

OUTPUT: ExtractionResult
├─ classification: CompanyClassification
├─ facts: List[ExtractedFact] (with confidence)
├─ contradictions: List[Contradiction]
├─ field_completeness: Dict[field → score]
└─ overall_completeness: 0-100%
```

---

## 5. Quality Assessment Flow

```
INPUT: company_name, extracted_data, sources
│
├─ STEP 1: Fast Field Completeness Check (NO LLM)
│  │
│  ├─ Scan extracted_data for field keywords
│  ├─ Count present fields (0-15)
│  ├─ Calculate field_score = (present / 15) * 100
│  │
│  └─ Result: field_score (0-100%)
│
├─ STEP 2: LLM Quality Assessment (CHEAP MODEL)
│  │
│  ├─ Use smart_completion() for cost routing
│  │  └─ DeepSeek V3: $0.14/1M (preferred for classification)
│  │
│  ├─ Prompt LLM:
│  │  ├─ "Rate overall quality 0-100"
│  │  ├─ "List missing information items"
│  │  ├─ "List research strengths"
│  │  ├─ "Recommend follow-up queries"
│  │  └─ "Response format: JSON"
│  │
│  ├─ Parse JSON response
│  │
│  └─ Result: llm_quality_score (0-100%)
│
├─ STEP 3: Critical Field Penalty
│  │
│  ├─ Check for missing CRITICAL fields (4 max)
│  │  └─ company_name, revenue, ceo, market_share
│  │
│  ├─ Apply penalty: -5 points per critical field
│  │  └─ Max penalty: -20 points
│  │
│  └─ Example:
│     ├─ llm_score: 75, field_score: 70
│     ├─ critical_missing: [ceo, revenue] → -10 penalty
│     └─ Adjusted field_score: 70 - 10 = 60
│
├─ STEP 4: Composite Scoring
│  │
│  ├─ composite = (llm_score * 0.6) + (field_score * 0.4)
│  │
│  ├─ Example calculation:
│  │  ├─ LLM score: 75
│  │  ├─ Field score: 60 (after penalty)
│  │  ├─ composite = (75 * 0.6) + (60 * 0.4)
│  │  ├─ composite = 45 + 24 = 69
│  │  └─ Final quality_score: 69/100
│  │
│  └─ Clamp to 0-100 range
│
├─ STEP 5: Gap Analysis & Query Generation
│  │
│  ├─ Combine sources of recommendations:
│  │  │
│  │  ├─ Field-based gaps:
│  │  │  └─ For each missing field, generate targeted query
│  │  │
│  │  └─ LLM recommendations:
│  │     └─ Parse recommended queries from LLM response
│  │
│  ├─ Merge and deduplicate
│  ├─ Limit to top 10 queries
│  │
│  └─ Result: List[gap_filling_queries]
│
└─ STEP 6: Return Quality Result
   ├─ quality_score: 0-100 (composite)
   ├─ field_score: 0-100 (fast check)
   ├─ llm_quality_score: 0-100 (or None if failed)
   ├─ missing_fields: [...]
   ├─ critical_missing: [...] (high priority)
   ├─ important_missing: [...]
   ├─ strengths: [...] (from LLM)
   ├─ recommended_queries: [...] (for re-search)
   ├─ cost: API cost
   └─ tokens: {input: X, output: Y}

QUALITY THRESHOLDS:
├─ 85+: PROCEED to report (good enough)
├─ 60-84: RE-SEARCH if iterations < 2
└─ <60: FORCE RE-SEARCH
```

---

## 6. Iteration Decision Logic

```
QUALITY SCORE from Phase 5
│
├─ 85+? ────────────────────────────────────────┐
│  YES                                           │
├─ Iterations >= 2? ────────────────────────────┐
│  YES                                           │
├─ Score >= 60? ───────────────────────────┐    │
│  NO                                       │    │
│   └─ FORCE RE-SEARCH (multiple strategies)   │
│      ├─ Multilingual queries                  │
│      ├─ Parent company search                 │
│      ├─ Alternative sources                   │
│      ├─ Relaxed query terms                   │
│      └─ Regional sources                      │
│      └─ BUT: Since iter >= 2, SKIP TO END     │
│                                               │
│   PROCEED TO REPORT ◄──────────────────────────┘

DETAILED DECISION TREE:

┌─────────────────────────────────────────────┐
│ QUALITY ASSESSMENT COMPLETE                 │
│ quality_score = X, iteration_count = N      │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ quality_score >= 85?    │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │ YES                NO   │
        ▼                         ▼
    FINISH              ┌────────────────────┐
  (Report)             │ iteration_count >= 2?
                       └────────────┬────────┘
                                    │
                       ┌────────────┴────────────┐
                       │ YES                  NO  │
                       ▼                          ▼
                    FINISH              ┌──────────────────┐
                  (Report)              │ 60 <= score < 85?
                                        └────────────┬─────┘
                                                     │
                                        ┌────────────┴────────────┐
                                        │ YES                   NO
                                        ▼                        ▼
                                  RE-SEARCH                    FINISH
                                    (Iter+1)                (Report)
                                        │
                                        └──→ Back to Phase 3
```

---

## 7. Complete State Machine

```
                    ┌──────────────────────┐
                    │   START RESEARCH     │
                    │  company_name = X    │
                    └──────────┬───────────┘
                               │
                        ┌──────▼──────┐
                        │  PHASE 1:   │
                        │Classification
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │  PHASE 2:   │
                        │   Queries   │
                        └──────┬──────┘
                               │
        ┏━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━┓
        ┃       ITERATION LOOP (max 2 iterations)      ┃
        ┃     ┌────────────────────────────────┐     ┃
        ┃     │ ITERATION N:                   │     ┃
        ┃     │ ├─ PHASE 3: Search            │     ┃
        ┃     │ ├─ PHASE 4: Extract Data      │     ┃
        ┃     │ └─ PHASE 5: Quality Assessment│     ┃
        ┃     └────────────────┬───────────────┘     ┃
        ┃                      │                      ┃
        ┃          ┌───────────▼────────────┐        ┃
        ┃          │  DECISION:             │        ┃
        ┃          │  Continue Research?    │        ┃
        ┃          └───────────┬────────────┘        ┃
        ┃                      │                      ┃
        ┃          ┌───────────┴───────────┐         ┃
        ┃          │ YES (Re-search)       │         ┃
        ┃          ├─ Quality < 85?        │         ┃
        ┃          ├─ Iteration < 2?       │         ┃
        ┃          └─ Generate Gap Queries │         ┃
        ┃                      │                      ┃
        ┃          ┌───────────▼───────────┐         ┃
        ┃          │ [Loop back to top]    │         ┃
        ┃          └───────────┬───────────┘         ┃
        ┃                      │                      ┃
        ┃          ┌───────────┴───────────┐         ┃
        ┃          │ NO (Proceed)          │         ┃
        ┃          ├─ Quality >= 85?       │         ┃
        ┃          ├─ Iteration >= 2?      │         ┃
        ┃          └─ Done iterating       │         ┃
        ┃                      │                      ┃
        ┗━━━━━━━━━━━━━━━━━━━━━┃━━━━━━━━━━━━━━━━━━━━━┛
                               │
                        ┌──────▼──────┐
                        │  PHASE 6:   │
                        │Report Synth │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │  PHASE 7:   │
                        │Output &     │
                        │Export Report│
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   FINISHED  │
                        │  Metrics +  │
                        │  Report URL │
                        └─────────────┘
```

---

## 8. Cost Flow Per Iteration

```
┌─────────────────────────────────────────────────────────────────┐
│                   ITERATION 0 (Initial Search)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Generate Queries                                              │
│  ├─ AIQueryGenerator.generate_queries() [LLM]                 │
│  │  ├─ Model: Claude 3.5 Sonnet                              │
│  │  ├─ Tokens: ~500 input, 300 output                        │
│  │  └─ Cost: $0.018                                          │
│  │                                                             │
│  └─ Total: 15-20 queries generated                            │
│                                                                 │
│  Search (10-20 queries)                                        │
│  ├─ Provider Success Rate:                                    │
│  │  ├─ 80% cache hits (previous searches): $0.00             │
│  │  ├─ 15% DuckDuckGo hits: $0.00                           │
│  │  ├─ 4% Brave escalation: $0.001 each                      │
│  │  └─ 1% Serper escalation: $0.01 each                      │
│  │                                                             │
│  └─ Avg cost per query: $0.001-0.003                         │
│     └─ 15 queries × $0.002 = $0.03                           │
│                                                                 │
│  Analysis & Extraction                                         │
│  ├─ Analyze search results [LLM]                             │
│  │  ├─ Model: Claude 3.5 Sonnet                              │
│  │  ├─ Tokens: ~2000 input, 1000 output                      │
│  │  └─ Cost: $0.090                                          │
│  │                                                             │
│  └─ Extract structured data [LLM]                            │
│     ├─ Model: Claude 3.5 Sonnet                              │
│     ├─ Tokens: ~3000 input, 2000 output                      │
│     └─ Cost: $0.150                                          │
│                                                                 │
│  Quality Assessment                                            │
│  ├─ Field completeness check: $0.00 (no LLM)               │
│  │                                                             │
│  └─ LLM quality assessment [CHEAP MODEL]                     │
│     ├─ Model: DeepSeek V3 (via smart_completion)           │
│     ├─ Tokens: ~1000 input, 500 output                       │
│     └─ Cost: $0.00007 ✓ Very cheap!                         │
│                                                                 │
│  ┌─────────────────────────────────────────────┐             │
│  │ ITERATION 0 TOTAL COST: ~$0.25-0.30        │             │
│  │ ├─ Searches: $0.03                          │             │
│  │ ├─ Analysis: $0.09                          │             │
│  │ ├─ Extraction: $0.15                        │             │
│  │ └─ Quality: $0.00007                        │             │
│  └─────────────────────────────────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           ITERATION 1 (IF TRIGGERED - Gap Filling)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Generate Gap-Filling Queries (5-10)                          │
│  ├─ From recommended_queries (LLM-generated)                  │
│  ├─ No new LLM call needed!                                  │
│  └─ Cost: $0.00                                              │
│                                                                 │
│  Search (5-10 queries)                                        │
│  ├─ Higher hit rate:                                         │
│  │  ├─ 40% cache hits (some unique queries): $0.00          │
│  │  ├─ 50% DuckDuckGo: $0.00                                │
│  │  └─ 10% Brave/Serper: $0.005                             │
│  │                                                             │
│  └─ Avg cost per query: $0.0005                              │
│     └─ 8 queries × $0.0005 = $0.004                          │
│                                                                 │
│  Analysis & Extraction                                         │
│  ├─ Analyze new results [LLM]                               │
│  │  ├─ Model: Claude 3.5 Sonnet                              │
│  │  ├─ Tokens: ~1000 input, 500 output                       │
│  │  └─ Cost: $0.045                                          │
│  │                                                             │
│  └─ Extract new facts [LLM]                                  │
│     ├─ Model: Claude 3.5 Sonnet                              │
│     ├─ Tokens: ~2000 input, 1000 output                      │
│     └─ Cost: $0.090                                          │
│                                                                 │
│  Quality Assessment                                            │
│  └─ Same as iteration 0: $0.00007                            │
│                                                                 │
│  ┌─────────────────────────────────────────────┐             │
│  │ ITERATION 1 TOTAL COST: ~$0.14-0.16        │             │
│  │ ├─ Searches: $0.004                         │             │
│  │ ├─ Analysis: $0.045                         │             │
│  │ ├─ Extraction: $0.090                       │             │
│  │ └─ Quality: $0.00007                        │             │
│  └─────────────────────────────────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              TYPICAL TOTAL RESEARCH COST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Iteration 0:          $0.25-0.30                             │
│  Iteration 1 (opt):    $0.14-0.16 (if triggered)             │
│                                                                 │
│  Total (1 iteration):  $0.25-0.30                             │
│  Total (2 iterations): $0.39-0.46                             │
│                                                                 │
│  ✓ Cost optimization at each layer:                          │
│    - FREE DuckDuckGo first                                    │
│    - Persistent caching (eliminates repeat costs)             │
│    - Cheap LLM models for quality (DeepSeek)                 │
│    - Bounded iterations (max 2)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Key Architecture Patterns

### Pattern 1: Provider Fallback Chain (Cost Optimization)

```
TRY_NEXT_PROVIDER on:
├─ Network error
├─ Rate limit (429)
├─ API error (5xx)
├─ Insufficient results (< min_results)
└─ Timeout (> 30s)

PROVIDER ORDER (Cost-optimized):
├─ Free tier: DuckDuckGo ($0)
├─ Cheap tier: Brave ($0.0003 per 3 results)
├─ Standard tier: Serper ($0.01)
└─ Last resort: Tavily ($0.02)
```

### Pattern 2: Health Tracking (Exponential Backoff)

```
consecutive_failures = 0
  │
  ├─ SUCCESS → reset to 0, update metrics
  │
  └─ FAILURE → increment
     │
     ├─ failures = 1-2 → try next immediately
     ├─ failures = 3 → wait 60s
     ├─ failures = 4 → wait 120s
     ├─ failures = 5 → wait 240s
     └─ failures = 6+ → wait 480s (max)
```

### Pattern 3: Persistent Caching (Money Saver)

```
Cache Hit Rate by Scenario:
├─ First research (cold): 0% (no cache)
├─ Re-research same company: 60-80% (cached base queries)
├─ Research similar companies: 30-40% (shared queries)
└─ Batch research (100 companies): 70%+ (massive savings)

Example Cost Impact:
├─ Without cache: 100 companies × $0.35 = $35
├─ With cache (30% hit): 100 companies × $0.25 = $25 (29% savings)
├─ With cache (70% hit): 100 companies × $0.15 = $15 (57% savings)
└─ Batch operations: Savings compound!
```

### Pattern 4: Smart Model Routing (LLM Cost)

```
Task Type → Best Model (via smart_completion)
├─ Classification (quality check): DeepSeek V3 ($0.14/1M)
├─ Extraction (complex reasoning): Claude ($3/1M)
├─ Analysis (general purpose): DeepSeek or Claude
└─ Fallback strategy: If primary unavailable, use next

Cost Savings:
├─ DeepSeek for classification: 95% cheaper than Claude
├─ Quality assessment (most frequent): ~$0.00007 per iteration
└─ Extraction/analysis: Use best model for quality
```

---

## Summary

The architecture balances three concerns:

1. **COST EFFICIENCY**
   - FREE-first provider selection (DuckDuckGo)
   - Persistent caching (eliminates repeat costs)
   - Cheap model routing (DeepSeek for classification)
   - Bounded iterations (max 2)
   - Result: $0.25-0.46 per research

2. **COMPREHENSIVENESS**
   - Multi-layered query generation (8 categories)
   - Semantic diversification (85%+ deduplication)
   - Field completeness tracking (15 core fields)
   - Contradiction detection
   - Result: Deep, valid research

3. **FLEXIBILITY**
   - Fallback chains (handles failures gracefully)
   - Health tracking (learns provider reliability)
   - Cost-aware iteration (stops when not worth it)
   - Region/language awareness
   - Result: Works globally, adapts dynamically
