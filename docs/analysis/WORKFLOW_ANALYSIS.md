# Company Researcher Workflow Analysis

## Executive Summary

This document provides a comprehensive analysis of the Company Researcher workflow, covering:
1. **Query Generation Strategy** - How search queries are created
2. **Search Execution** - How searches are performed across multiple providers
3. **Data Extraction** - How information is extracted from raw content
4. **Quality Assessment** - How extracted data is validated
5. **Iteration Logic** - How re-search is triggered based on quality gaps

---

## 1. Query Generation Strategy

### Current Approach

The system uses a **multi-layered query generation strategy** with support for:
- Base queries (general company research)
- Multilingual queries (regional and language-specific)
- Specialized queries (executive/leadership, financial, competitive)
- Parent company and alternative name queries
- Regional source queries (country-specific sources)

### Key Files Involved

| File | Purpose |
|------|---------|
| `src/company_researcher/ai/query/generator.py` | AIQueryGenerator class - main query generation engine |
| `src/company_researcher/agents/research/multilingual_search.py` | MultilingualSearchGenerator - regional and multilingual queries |
| `src/company_researcher/workflows/nodes/search_nodes.py` | generate_queries_node - orchestrates query generation |
| `src/company_researcher/prompts/` | Prompt templates for query generation |
| `src/company_researcher/shared/search.py` | QueryDiversifier - semantic query diversification |

### Process Flow

```
Input: company_name, region (detected), language
  ↓
1. Multilingual Generator Detection
   - Detects region (LATAM, North America, Europe, etc.)
   - Detects primary language
   ↓
2. Multi-Source Query Generation
   ├─ AIQueryGenerator.generate_queries()
   │  └─ Uses LLM-based prompt to create diverse queries
   ├─ MultilingualSearchGenerator
   │  ├─ Regional source queries (site:conatel.gov.py)
   │  ├─ Parent company queries
   │  └─ Alternative name queries
   ├─ Specialized queries
   │  └─ Leadership, financial, competitive queries
   └─ QueryDiversifier (semantic diversification)
      └─ Ensures queries cover different information categories
   ↓
3. Query Refinement
   - AIQueryGenerator.refine_queries()
   - Analyzes coverage gaps
   - Generates additional queries for missing areas
   ↓
Output: List of 10-20+ optimized queries
```

### Key Methods in AIQueryGenerator

| Method | Purpose | Returns |
|--------|---------|---------|
| `generate_queries()` | Creates initial query set based on company context | `QueryGenerationResult` |
| `refine_queries()` | Analyzes coverage gaps and refines queries | Refined query list |
| `generate_multilingual_queries()` | Creates queries in multiple languages for regions | Multilingual queries |
| `_parse_generation_result()` | Parses LLM output into structured queries | `List[MultilingualQuery]` |

### Query Categories (from `shared/search.py`)

The system diversifies queries across **8 information categories**:

```python
QUERY_CATEGORIES = {
    "official_filings": {          # SEC filings, regulatory documents
        "priority": 1,
        "min_results": 3,
        "domains": ["sec.gov"]
    },
    "investor_relations": {         # Earnings calls, investor materials
        "priority": 1,
        "min_results": 5
    },
    "financial_news": {             # News on financials
        "priority": 2,
        "min_results": 8
    },
    "company_overview": {           # General company info
        "priority": 2,
        "min_results": 5
    },
    "competitive_analysis": {       # Competitor and market position
        "priority": 2,
        "min_results": 5
    },
    "product_info": {               # Products and services
        "priority": 3,
        "min_results": 5
    },
    "recent_news": {                # Recent developments
        "priority": 3,
        "min_results": 5
    },
    "leadership": {                 # CEO, executives
        "priority": 3,
        "min_results": 3
    }
}
```

### Limitations in Current Logic

| Limitation | Impact | Potential Fix |
|-----------|--------|--------------|
| **Limited LLM control over query diversity** | Queries may be similar or overlapping | Implement constraint-based generation with diversity scoring |
| **No automatic language detection** | May miss regional sources | Integrate auto-language detection (langdetect library) |
| **Static priority weights** | May not adapt to company type | Implement dynamic weighting based on company classification |
| **No query effectiveness feedback** | Queries aren't optimized based on result quality | Add feedback loop: track results/query correlation |
| **Limited handling of private companies** | May waste queries on unavailable data sources | Classify company type first, adjust query strategy |
| **No temporal query adjustment** | All queries treat data equally regardless of date | Add time-aware query generation (recent results emphasis) |

---

## 2. Search Execution

### Current Approach

The system uses a **cost-optimized, multi-provider search strategy** with:
- FREE-first approach (DuckDuckGo before paid)
- Automatic fallback chain on failure
- Provider health tracking
- Persistent disk caching
- Result deduplication (URL + semantic)
- Calibrated scoring

### Key Files Involved

| File | Purpose |
|------|---------|
| `src/company_researcher/integrations/search_router.py` | SearchRouter - main search orchestration |
| `src/company_researcher/shared/search.py` | RobustSearchClient - diversified search with health tracking |
| `src/company_researcher/integrations/` | Provider implementations (serper, brave, tavily, duckduckgo) |
| `src/company_researcher/workflows/nodes/search_nodes.py` | search_node - executes searches in workflow |

### Search Provider Chain

```
TIER SYSTEM (Cost-optimized)
├─ FREE tier (unlimited)
│  └─ DuckDuckGo
├─ STANDARD tier (DuckDuckGo → Serper fallback)
│  ├─ DuckDuckGo (free)
│  └─ Serper ($0.01/search)
└─ PREMIUM tier (escalating fallback)
   ├─ DuckDuckGo (free)
   ├─ Brave ($0.10/1000 queries)
   ├─ Serper ($0.01/search)
   └─ Tavily ($0.02/search)

FALLBACK LOGIC:
If DuckDuckGo fails or returns < min_results:
  → Try Brave (3 results = ~$0.0003)
  → If still insufficient, try Serper
  → Last resort: Tavily

EXECUTIVE QUERIES:
- Special handling for CEO/leadership queries
- min_results=5 forces escalation to Serper for better data
```

### Process Flow

```
Input: search_queries, quality_tier (free/standard/premium)
  ↓
1. Initialize SearchRouter with cache
   - Load persistent disk cache
   - Initialize provider health tracking
   ↓
2. For Each Query:
   ├─ Check cache (avoid API call)
   │  └─ If found: return cached result (0 cost)
   ├─ Filter to HEALTHY providers
   │  └─ Skip if consecutive_failures >= 3 (exponential backoff)
   ├─ Execute fallback chain
   │  ├─ Try DuckDuckGo first (free)
   │  ├─ If < min_results or error: Try next provider
   │  └─ Track response time for health metrics
   ├─ Deduplicate results
   │  ├─ URL-level deduplication
   │  └─ Semantic deduplication (85%+ similarity threshold)
   ├─ Score results (calibrated scoring)
   │  ├─ Authority score (domain-based)
   │  ├─ Relevance score (query match in title/snippet)
   │  └─ Rank decay (first results scored higher)
   └─ Cache successful result
      ↓
Output: SearchResponse (results, cost, provider, cached status)
```

### Result Scoring Algorithm (from `shared/search.py`)

```python
def calculate_combined_score(query: str):
    """Weighted combination for result ranking"""
    authority_score = _calculate_authority()  # Domain-based (0-1)
    relevance_score = _calculate_relevance(query)  # Query match (0-1)
    rank_factor = 1.0 / (1.0 + 0.1 * raw_rank)  # Position decay

    combined_score = (
        authority_score * 0.4 +    # 40% domain authority
        relevance_score * 0.4 +    # 40% query relevance
        rank_factor * 0.2          # 20% position in results
    )
```

### Authority Tiers (Domain-Based)

| Tier | Score | Examples |
|------|-------|----------|
| Official/Regulatory | 1.0 | sec.gov, investor.*, ir.* |
| Major Financial News | 0.85 | bloomberg.com, reuters.com, wsj.com, ft.com |
| Reputable Tech/Business | 0.70 | techcrunch.com, forbes.com, cnbc.com |
| General Domains | 0.55 | .com, .org, .net (all others) |
| Low Authority | 0.40 | Other domains |

### Provider Health Tracking

```python
@dataclass
class ProviderHealth:
    name: str
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    avg_response_time_ms: float = 0.0
    total_requests: int = 0
    total_successes: int = 0

    @property
    def is_healthy(self) -> bool:
        if consecutive_failures >= 3:
            # Exponential backoff: 60s, 120s, 240s, 480s, 960s (max 32s)
            cooldown = 60 * (2 ** min(consecutive_failures - 3, 5))
            return (now - last_failure) >= cooldown
        return True

    @property
    def success_rate(self) -> float:
        return successes / total_requests
```

### Caching Strategy

```python
PersistentCache (30-day TTL)
├─ Cache key: SHA256(query + max_results)
├─ Storage: .cache/search/ directory
├─ Format: JSON files
├─ Deduplication:
│  ├─ URL-based (exact URL match)
│  └─ Semantic-based (85%+ embedding similarity)
└─ Saves 100% of cost for repeated queries
```

### Limitations in Current Logic

| Limitation | Impact | Potential Fix |
|-----------|--------|--------------|
| **Authority scoring is domain-based only** | Doesn't account for page-specific authority | Add page-level factors (domain authority, backlinks) |
| **Relevance scoring uses simple keyword matching** | Misses semantic relevance | Integrate semantic similarity (embeddings) |
| **Cache TTL is fixed (30 days)** | Old cached data for volatile info (news, stock prices) | Implement adaptive TTL based on data type |
| **No query-specific provider selection** | Uses same providers for all query types | Route news queries to news-focused providers (NewsAPI) |
| **Deduplication threshold is static (85%)** | May be too strict or too loose for different content | Make threshold adaptive based on content type |
| **No coverage tracking across queries** | Doesn't know if all categories are adequately covered | Implement coverage map to identify gaps |
| **Limited to 8 result categories** | May miss important information categories | Expand categories based on company classification |

---

## 3. Data Extraction

### Current Approach

The system extracts structured data from raw search results using:
- **LLM-based extraction** (semantic understanding)
- **Fact-level modeling** (ExtractionResult, ExtractedFact)
- **Contradiction resolution** (rule-based + LLM)
- **Cost-optimized routing** (cheap models for classification)
- **Field-level completeness checking**

### Key Files Involved

| File | Purpose |
|------|---------|
| `src/company_researcher/ai/extraction/extractor.py` | AIDataExtractor - semantic data extraction |
| `src/company_researcher/ai/extraction/models.py` | Data models (ExtractedFact, CompanyClassification, etc.) |
| `src/company_researcher/quality/quality_checker.py` | Field completeness checking |
| `src/company_researcher/workflows/nodes/analysis_nodes.py` | extract_data_node - extraction orchestration |

### Output Schema: REQUIRED_FIELDS (Completeness Checking)

```python
REQUIRED_FIELDS = {
    # Core company info
    "company_name": ["company name", "legal name", "trading as"],
    "headquarters": ["headquarters", "headquarter", "based in", "located in"],
    "founded": ["founded", "established", "incorporated"],
    "industry": ["industry", "sector", "business segment"],
    "employees": ["employees", "workforce", "staff count", "headcount"],

    # Leadership
    "ceo": ["ceo", "chief executive", "managing director", "general manager"],
    "leadership_team": ["leadership", "management team", "board", "executives"],

    # Financial metrics
    "revenue": ["revenue", "sales", "turnover", "annual revenue"],
    "profit_margin": ["profit margin", "net margin", "operating margin"],
    "market_cap": ["market cap", "market capitalization", "valuation"],

    # Market position
    "market_share": ["market share", "share of market", "% of market"],
    "subscribers": ["subscribers", "customers", "users", "client base"],
    "competitors": ["competitor", "rival", "competing", "market player"],

    # Operational
    "products_services": ["product", "service", "offering", "solution"],
    "geographic_presence": ["geographic", "countries", "regions", "operations in"],
}
```

### Extraction Process

```
Input: search_results (raw text from web)
  ↓
1. Company Classification (Phase 1)
   ├─ Classify company type (public, private, NGO, etc.)
   ├─ Determine available data sources
   ├─ Detect region and language
   └─ Identify special data sources (SEC, patent databases, etc.)
   ↓
2. Fact Extraction (Phase 2)
   ├─ Extract facts with confidence scores
   ├─ Categorize facts (financial, operational, leadership)
   ├─ Attribute to sources
   └─ Track extraction confidence
   ↓
3. Contradiction Detection (Phase 3)
   ├─ Rule-based detection (format, temporal)
   ├─ LLM-based semantic detection
   ├─ Severity scoring (critical, major, minor)
   └─ Resolution recommendation
   ↓
4. Field Completeness Checking (Phase 4)
   ├─ Check presence of all required fields
   ├─ Categorize missing fields by priority
   │  ├─ Critical: company_name, revenue, ceo, market_share
   │  ├─ Important: headquarters, employees, competitors
   │  └─ Other: all remaining fields
   └─ Generate targeted queries for gaps
   ↓
Output: ExtractionResult (structured data, confidence, completeness)
```

### Data Models

```python
@dataclass
class ExtractedFact:
    """Single fact extracted from text"""
    type: FactType  # "string", "number", "date", "url"
    category: FactCategory  # "financial", "operational", etc.
    field: str  # "revenue", "ceo", etc.
    value: str
    source_url: str
    extracted_text: str  # Original context
    confidence: float  # 0-1 confidence score
    timestamp: datetime
    contradictions: List['ContradictionAnalysis'] = []

@dataclass
class ExtractionResult:
    """Complete extraction result"""
    company_name: str
    classification: CompanyClassification
    facts: List[ExtractedFact]
    contradictions: List[ContradictionAnalysis]
    field_completeness: Dict[str, FieldCompletenessInfo]
    overall_completeness: float  # 0-100%
    extraction_quality_score: float  # 0-100%
    sources: List[SourceAttribution]
```

### Completeness Scoring

```python
def check_field_completeness(extracted_data: str) -> Dict:
    """Check which required fields are present/missing"""
    field_score = (present_count / total_fields) * 100

    # Calculate composite quality score
    critical_penalty = len(critical_missing) * 5  # -5 per critical field
    important_penalty = len(important_missing) * 2  # -2 per important field

    return {
        "field_score": field_score,                    # 0-100
        "present_fields": [...],
        "missing_fields": [...],
        "critical_missing": [...],                     # Highest priority
        "important_missing": [...],                    # Medium priority
        "other_missing": [...]                         # Low priority
    }
```

### Limitations in Current Logic

| Limitation | Impact | Potential Fix |
|-----------|--------|--------------|
| **Field detection uses keyword matching** | May miss context-aware field values | Switch to semantic field extraction using embeddings |
| **Confidence scoring is not transparent** | Hard to understand why extraction failed | Add explainability scores per fact |
| **Contradiction detection is rule-based** | Misses semantic contradictions | Enhance with semantic similarity checking |
| **No source reliability weighting** | All sources treated equally | Weight facts by source authority score |
| **Pattern-based value extraction** | Regex patterns miss edge cases (currencies, units) | Use Named Entity Recognition (NER) for structured extraction |
| **No temporal coherence checking** | May accept contradictory data from different time periods | Track fact timestamps and temporal consistency |
| **Limited field category coverage** | Only 15 core fields defined | Expand to domain-specific fields (e.g., telecom: subscribers) |

---

## 4. Quality Assessment

### Current Approach

The system uses a **multi-level quality assessment**:
1. **Field-level completeness** (fast, no LLM)
2. **LLM-based assessment** (semantic quality, using cheap models)
3. **Composite scoring** (60% LLM + 40% field completeness)
4. **Critical field penalties** (-5 points per critical missing field)
5. **Recommended queries for gaps** (targeted follow-up searches)

### Key Files Involved

| File | Purpose |
|------|---------|
| `src/company_researcher/quality/quality_checker.py` | check_research_quality() - main quality assessment |
| `src/company_researcher/research/data_threshold.py` | DataThresholdChecker - pre/post research validation |
| `src/company_researcher/research/quality_enforcer.py` | ReportQualityEnforcer - report-level quality standards |
| `src/company_researcher/research/metrics_validator.py` | Numerical data validation |
| `src/company_researcher/quality/contradiction_detector.py` | Contradiction detection |

### Quality Assessment Process

```
Input: company_name, extracted_data, sources
  ↓
1. Fast Field Completeness Check (no LLM)
   ├─ Scan extracted_data for field keywords
   ├─ Identify present fields
   ├─ Identify missing fields (critical, important, other)
   └─ Calculate field_score (0-100%)
   ↓
2. LLM Quality Assessment (cost-optimized)
   ├─ Use smart_completion() for cheap routing
   │  └─ DeepSeek V3 ($0.14/1M) preferred
   ├─ Ask LLM to assess:
   │  ├─ Overall quality (0-100)
   │  ├─ Missing information items
   │  ├─ Strengths of research
   │  └─ Recommended search queries
   └─ Parse JSON response
   ↓
3. Composite Scoring
   ├─ composite_score = (llm_score * 0.6) + (field_score * 0.4)
   ├─ Apply critical field penalty: -5 per critical field
   └─ Clamp to 0-100 range
   ↓
4. Gap Analysis
   ├─ Generate field-based queries for missing fields
   ├─ Merge with LLM-recommended queries
   ├─ Deduplicate final query list
   └─ Limit to top 10 queries
   ↓
Output: QualityResult
├─ quality_score: 0-100
├─ field_score: 0-100
├─ llm_quality_score: 0-100 (or None if LLM failed)
├─ missing_fields: [...]
├─ critical_missing: [...] (trigger re-search)
├─ important_missing: [...]
├─ recommended_queries: [...] (for next iteration)
├─ cost: actual API cost
└─ tokens: {input, output}
```

### Quality Thresholds

```
Quality Score → Decision
└─ 85+ : PROCEED to report generation
└─ 60-85: TRIGGER RE-SEARCH (if iterations < max)
└─ < 60 : FORCE RE-SEARCH (multiple strategies)
         └─ Multilingual queries
         └─ Parent company search
         └─ Alternative sources
         └─ Relaxed query terms
         └─ Regional sources
         └─ Archived data
         └─ Press releases
```

### Data Sufficiency Assessment (DataThresholdChecker)

```python
SECTION_REQUIREMENTS = {
    "financial": {
        "weight": 30,
        "min_coverage": 40,
        "expected_fields": ["revenue", "net_income", "profit_margin", ...],
        "critical_fields": ["revenue"],
        "value_patterns": [r'\$[\d,]+', r'[\d,]+%']
    },
    "market": {
        "weight": 20,
        "min_coverage": 30,
        "expected_fields": ["market_cap", "market_share", "pe_ratio", ...]
    },
    "company_info": {
        "weight": 15,
        "min_coverage": 50,
        "expected_fields": ["headquarters", "employees", "founded", ...]
    },
    "competitive": {
        "weight": 15,
        "min_coverage": 25,
        "expected_fields": ["competitors", "competitive_advantages", ...]
    },
    "products": {
        "weight": 10,
        "min_coverage": 25,
        "expected_fields": ["main_products", "services", ...]
    },
    "strategy": {
        "weight": 10,
        "min_coverage": 20,
        "expected_fields": ["growth_strategy", "future_outlook", ...]
    }
}
```

### Report Quality Enforcer

```
Quality Levels:
├─ EXCELLENT (90-100): Ready to publish
├─ GOOD (75-89): Minor issues, acceptable
├─ ACCEPTABLE (60-74): Gaps present, needs improvement
├─ POOR (40-59): Significant gaps, publishable with caveats
└─ UNACCEPTABLE (<40): Don't publish

Required Sections:
├─ Executive Summary (min 100 words, 3+ data points)
├─ Company Overview (min 150 words, 5+ data points, required fields)
├─ Financial Analysis (min 200 words, 8+ data points, required fields)
├─ Market Position (min 100 words, 3+ data points)
├─ Competitive Analysis (min 100 words, 2+ data points)
├─ Strategy & Outlook (min 100 words, 2+ data points)
├─ Risk Assessment (min 80 words)
├─ Investment Thesis (min 150 words)
└─ Sources (with citations)
```

### Limitations in Current Logic

| Limitation | Impact | Potential Fix |
|-----------|--------|--------------|
| **Quality threshold is fixed (85)** | May be too high or low for different company types | Implement adaptive thresholds based on company classification |
| **Field completeness uses keyword matching** | Misses extracted facts that use synonyms | Integrate semantic field matching |
| **No weighting by field importance** | All fields treated equally in scoring | Implement field-specific weights (revenue > color) |
| **LLM assessment uses text scanning** | Doesn't understand context deeply | Enhance with structured extraction and semantic analysis |
| **Composite scoring is fixed 60/40** | May not be optimal for different company types | Learn optimal weights from historical data |
| **No temporal completeness checking** | Recent news missing triggers low scores | Implement recency-aware quality assessment |
| **Gap analysis is query-based only** | Doesn't check if follow-up searches will help | Predict query effectiveness before triggering re-search |
| **No multi-source validation** | Doesn't check fact agreement across sources | Implement fact cross-validation across sources |

---

## 5. Iteration Logic

### Current Approach

The system uses **bounded iteration** with:
- Maximum 2 iterations per research session
- Quality score threshold (85+) for completion
- Targeted re-search based on quality gaps
- Multiple retry strategies for different failure modes

### Key Files Involved

| File | Purpose |
|------|---------|
| `src/company_researcher/workflows/comprehensive_research.py` | should_continue_research() - iteration decision |
| `src/company_researcher/workflows/nodes/analysis_nodes.py` | check_quality_node - triggers iteration |
| `src/company_researcher/research/data_threshold.py` | RetryStrategy enum - different re-search approaches |

### Iteration Flow

```
ITERATION 0 (Initial Search)
  ↓
1. Generate initial queries (10-20)
2. Execute searches (cost-optimized fallback)
3. Extract data from results
4. Check quality
  └─ quality_score = 0-100
  ↓
QUALITY DECISION POINT:
  ├─ quality_score >= 85 ? → FINISH (good enough)
  ├─ iteration_count >= max (2) ? → FINISH (max iterations)
  └─ 60 <= quality_score < 85 ? → ITERATE (try to improve)
  ↓
ITERATION N (1..max)
  ↓
1. Analyze gaps
   ├─ Identify critical missing fields
   ├─ Identify important missing fields
   └─ Get recommended queries from quality assessment
  ↓
2. Generate targeted re-search queries
   ├─ Field-based queries for missing fields
   ├─ Merge with LLM-recommended queries
   └─ Deduplicate and limit to top 10
  ↓
3. Execute targeted search (same process as iteration 0)
  ↓
4. Extract new data
   ├─ Append to existing data
   ├─ Merge duplicate facts
   └─ Update contradictions
  ↓
5. Check quality again (re-evaluate)
   └─ quality_score = new assessment
  ↓
DECISION:
  ├─ quality_score >= 85 ? → FINISH
  ├─ iteration_count >= max ? → FINISH
  └─ ELSE → ITERATE (next iteration)
  ↓
OUTPUT: Final comprehensive research with metrics
```

### Decision Logic (`should_continue_research()`)

```python
def should_continue_research(state: OverallState) -> str:
    """
    Conditional router: should we continue researching or move to report?
    """
    iteration_count = state.get("iteration_count", 0)
    quality_score = state.get("quality_score", 0)
    max_iterations = 2

    # Decision thresholds
    if quality_score >= 85:
        # Quality is good - proceed to report
        return "finish"

    elif iteration_count >= max_iterations:
        # Maximum iterations reached - proceed to report
        return "finish"

    else:
        # Quality low and iterations remaining - re-search
        return "continue_research"
```

### Retry Strategies (from `data_threshold.py`)

When quality is low and iterations remain, the system can apply:

```python
class RetryStrategy(Enum):
    MULTILINGUAL = "multilingual"          # Different languages
    PARENT_COMPANY = "parent_company"      # Search parent company
    ALTERNATIVE_SOURCES = "alternative_sources"  # Different providers
    RELAXED_QUERIES = "relaxed_queries"    # Broader search terms
    REGIONAL_SOURCES = "regional_sources"  # Country-specific sources
    ARCHIVED_DATA = "archived_data"        # Web archive (Wayback)
    PRESS_RELEASES = "press_releases"      # Official announcements
    NONE = "none"                          # No retry possible
```

### Iteration State Tracking

```python
OverallState updates per iteration:
├─ iteration_count: int (incremented after quality check)
├─ quality_score: float (new assessment after re-search)
├─ missing_info: List[str] (updated gap list)
├─ search_results: Annotated[List, add] (appended, not replaced)
├─ notes: List[str] (appended for cumulative analysis)
├─ total_cost: Annotated[float, add] (accumulated cost)
├─ total_tokens: Annotated[Dict, add_tokens] (accumulated tokens)
└─ sources: Annotated[List, add] (appended)
```

### Cost Tracking Across Iterations

```
Iteration 0:
  - generate_queries: LLM call (input/output tokens)
  - search: DuckDuckGo (free) + potential fallbacks
  - analyze: LLM call for analysis
  - extract_data: LLM call for extraction
  - check_quality: LLM call (cheap model via smart_completion)
  Total Cost Iteration 0: ~$0.05-0.30 (mostly LLM, some search)

Iteration 1 (if triggered):
  - quality check recommends 10 gap-filling queries
  - search: Same fallback chain (likely hits cache)
  - extract_data: New extraction (LLM call)
  - check_quality: Another LLM assessment
  Total Cost Iteration 1: ~$0.05-0.20 (less due to cache hits)

Total Research Cost: Cumulative across iterations
```

### Limitations in Current Logic

| Limitation | Impact | Potential Fix |
|-----------|--------|--------------|
| **Max iterations is hardcoded (2)** | May give up too early or loop unnecessarily | Make adaptive based on quality improvement rate |
| **Quality threshold is fixed (85)** | One-size-fits-all doesn't account for company complexity | Use dynamic thresholds based on company type |
| **Re-search uses same query generation** | May regenerate similar queries | Track attempted queries, avoid repeats |
| **No convergence detection** | Doesn't detect if quality won't improve | Monitor quality delta: if delta < threshold, stop |
| **No cost-benefit analysis** | May spend $1 to gain 1 point of quality | Implement cost-aware iteration (stop if cost/benefit bad) |
| **Missing field list not prioritized** | May fill unimportant gaps first | Prioritize by field importance weight |
| **No multi-threaded re-search** | Sequential iteration is slow | Parallelize gap-filling queries in iteration 1+ |
| **No learning from iterations** | Doesn't improve strategy based on what worked | Track effective strategies per company type |
| **No early exit for unanimous low quality** | Continues to iteration 2 even if quality won't improve | Implement predictive stopping based on data patterns |

---

## 6. Complete Workflow State Machine

```
START
  ↓
PHASE 1: Company Classification
  ├─ Detect region, language, company type
  ├─ Identify available data sources
  └─ Determine special handling (SEC, etc.)
  ↓
PHASE 2: Query Generation
  ├─ Generate base queries
  ├─ Add multilingual/regional queries
  ├─ Add specialized queries
  └─ Refine based on coverage gaps
  ↓
PHASE 3: Search Execution (ITERATION LOOP)
  │
  ├─ [ITERATION 0]
  │  ├─ Search with cost-optimized provider fallback
  │  ├─ Cache results
  │  ├─ Deduplicate and score results
  │  └─ Analyze search results
  │
  ├─ PHASE 4: Data Extraction
  │  ├─ Extract facts with confidence
  │  ├─ Detect contradictions
  │  ├─ Check field completeness
  │  └─ Assess data sufficiency
  │
  ├─ PHASE 5: Quality Assessment
  │  ├─ Field-level completeness check (fast)
  │  ├─ LLM quality assessment (cheap model)
  │  ├─ Composite scoring (60% LLM + 40% field)
  │  ├─ Generate recommended queries
  │  └─ Calculate quality_score
  │
  ├─ DECISION: Continue Research?
  │  ├─ If quality >= 85 → PROCEED
  │  ├─ If iterations >= 2 → PROCEED
  │  └─ If 60 <= quality < 85 → [RE-SEARCH]
  │
  └─ [ITERATION 1] (if triggered)
     ├─ Generate targeted gap-filling queries
     ├─ Execute targeted search
     ├─ Extract new data
     ├─ Re-assess quality
     └─ DECISION (same logic)
  ↓
PHASE 6: Report Generation
  ├─ Synthesize all extracted data
  ├─ Validate report quality
  ├─ Generate markdown report
  └─ Include source citations
  ↓
PHASE 7: Output & Metrics
  ├─ Iterations: number of cycles
  ├─ Total Cost: accumulated API costs
  ├─ Total Tokens: cumulative token usage
  ├─ Quality Score: final assessment
  ├─ Duration: elapsed time
  └─ Sources: all attributed sources
  ↓
END
```

---

## 7. Key Output Schema Fields

### ResearchRequest (Input)
```python
{
    "company_name": str,                    # Required
    "depth": "quick"|"standard"|"comprehensive",  # Optional
    "include_financial": bool,              # Optional
    "include_market": bool,
    "include_competitive": bool,
    "include_news": bool,
    "include_brand": bool,
    "include_social": bool,
    "include_sales": bool,
    "include_investment": bool,
    "webhook_url": Optional[str],           # For async notification
    "metadata": Dict[str, Any]              # Custom metadata
}
```

### ResearchResult (Output)
```python
{
    "task_id": str,                         # Unique identifier
    "company_name": str,
    "status": "pending"|"running"|"completed"|"failed"|"cancelled",
    "created_at": datetime,
    "completed_at": Optional[datetime],
    "duration_seconds": float,
    "total_cost": float,                    # Total API cost
    "agent_outputs": {
        # For multi-agent workflow:
        # "researcher": {...},
        # "financial_agent": {...},
        # "market_agent": {...},
        # "logic_critic": {...}
    },
    "synthesis": {
        # Aggregated insights across agents
    },
    "quality_score": Optional[float],       # 0-100
    "error": Optional[str]
}
```

### OverallState (Internal)
```python
{
    # Input
    "company_name": str,

    # Query Generation
    "search_queries": List[str],
    "detected_region": str,
    "detected_language": str,

    # Search Results
    "search_results": List[Dict],           # Accumulated
    "sources": List[Dict],                  # Accumulated

    # Analysis
    "notes": List[str],                     # Accumulated LLM notes
    "company_overview": Optional[str],      # Extracted narrative

    # Structured Data
    "key_metrics": Optional[Dict],
    "products_services": Optional[List[str]],
    "competitors": Optional[List[str]],
    "key_insights": Optional[List[str]],

    # Classification
    "company_classification": Optional[Dict],
    "is_public_company": Optional[bool],
    "stock_ticker": Optional[str],

    # Quality & Iteration
    "quality_score": Optional[float],       # 0-100
    "iteration_count": int,                 # Number of re-search cycles
    "missing_info": Optional[List[str]],

    # Metrics
    "start_time": datetime,
    "total_cost": float,                    # Accumulated cost
    "total_tokens": {"input": int, "output": int},
    "report_path": Optional[str]
}
```

---

## 8. Cost Optimization Highlights

### Search Cost Strategy
```
Provider Costs:
├─ DuckDuckGo: FREE
├─ Brave Search: ~$0.0003 per result (3 results)
├─ Serper: $0.01 per search
├─ Tavily: $0.02 per search

COST-FIRST Strategy:
1. Always try DuckDuckGo first (saves 100%)
2. Only escalate to Brave if needed (1/3 price of Serper)
3. Cache results persistently (saves 100% on repeat)
4. Track provider health to avoid bad providers

Result: Typical search costs:
├─ Best case: $0 (DuckDuckGo hit + cache hit)
├─ Good case: $0.0003-0.01 (DDG hit, no cache)
└─ Bad case: $0.01-0.02 per query (Serper/Tavily)
```

### LLM Cost Strategy
```
Model Selection via smart_completion():
├─ DeepSeek V3: $0.14/1M input, $0.42/1M output (cheap!)
├─ GPT-4o-mini: $0.15/1M input, $0.60/1M output (fallback)
├─ Claude 3.5 Sonnet: $3/1M input, $15/1M output (expensive)

Cost Optimization:
├─ Quality check: Use DeepSeek (classification task)
├─ Data extraction: Use Claude (complex reasoning)
└─ Analysis: Use available model (flexibility)

Result: ~$0.02-0.10 per research iteration (mostly LLM)
```

---

## 9. Performance Optimization Opportunities

### High-Impact Improvements

| Opportunity | Effort | Impact | Recommendation |
|-------------|--------|--------|-----------------|
| Query effectiveness ranking | Medium | High - avoid wasted searches | Implement query→result correlation tracking |
| Adaptive quality thresholds | Medium | High - avoid over/under-iterations | Learn thresholds from historical data |
| Semantic field detection | High | High - better completeness scores | Integrate embeddings for field matching |
| Early exit detection | Low | Medium - stop wasted iterations | Monitor quality delta and convergence |
| Parallel re-search queries | Medium | Medium - faster iterations | Parallelize gap-filling searches |
| Multi-source fact validation | High | High - catch contradictions early | Cross-validate facts across sources |

### Quick Wins (Low Effort, Good Impact)

1. **Add query effectiveness tracking** (1 day)
   - Log each query + result count
   - Identify ineffective queries
   - Remove from future iterations

2. **Implement early convergence detection** (0.5 days)
   - Monitor quality delta: quality(n) - quality(n-1)
   - Stop if delta < 5 points consecutive 2 iterations
   - Prevents wasted iteration 2

3. **Add cost-aware iteration control** (1 day)
   - Calculate cost per quality point: delta_cost / delta_quality
   - Stop if cost/benefit ratio exceeds threshold
   - Prevents expensive low-value iterations

4. **Improve field detection with synonyms** (0.5 days)
   - Expand REQUIRED_FIELDS with more keywords
   - Add fuzzy matching for keyword detection
   - Reduce false negatives

5. **Add query prioritization by rarity** (1 day)
   - Identify queries with unique results
   - Execute high-uniqueness queries first
   - Reduces query redundancy

---

## 10. Recommended Next Steps

### Phase 1: Monitoring & Visibility (1 week)
1. Add comprehensive logging for workflow metrics
2. Track query effectiveness (results/query ratio)
3. Monitor quality improvement per iteration
4. Build dashboard for cost breakdown

### Phase 2: Quality Improvements (2-3 weeks)
1. Implement adaptive quality thresholds
2. Add multi-source fact validation
3. Enhance semantic field detection
4. Build query effectiveness model

### Phase 3: Cost Optimization (1-2 weeks)
1. Add cost-aware iteration control
2. Implement query recommendation engine
3. Optimize provider selection per query type
4. Add predictive early exit

### Phase 4: Scalability (2-4 weeks)
1. Implement parallel query execution
2. Add concurrent agent processing
3. Build distributed caching
4. Optimize database queries

---

## Summary

The Company Researcher workflow is a sophisticated, **iterative research system** with:
- **Multi-layered query generation** covering diverse information categories
- **Cost-optimized search** with FREE-first strategy and persistent caching
- **Semantic data extraction** with contradiction detection
- **Multi-level quality assessment** combining field completeness + LLM evaluation
- **Bounded iteration** (max 2 cycles) with quality-based decision logic

Key strengths:
✓ Cost-conscious (DuckDuckGo first, smart provider fallback)
✓ Comprehensive (8 information categories, field completeness tracking)
✓ Flexible (supports multilingual, regional, specialized queries)
✓ Transparent (detailed quality scoring with gap identification)

Key opportunities for improvement:
- Adaptive quality thresholds based on company type
- Better query effectiveness ranking
- Multi-source fact validation
- Early convergence detection
- Cost-aware iteration control
