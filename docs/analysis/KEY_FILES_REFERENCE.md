# Company Researcher - Key Files Reference

## Quick Navigation Guide

### Query Generation

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/ai/query/generator.py` | `AIQueryGenerator.generate_queries()` | LLM-based query generation |
| | `AIQueryGenerator.refine_queries()` | Coverage-based query refinement |
| | `AIQueryGenerator.generate_multilingual_queries()` | Regional/multilingual queries |
| `src/company_researcher/agents/research/multilingual_search.py` | `create_multilingual_generator()` | Region/language detection |
| | `MultilingualSearchGenerator.generate_queries()` | Region-specific queries |
| | `get_parent_company_queries()` | Parent company search |
| | `get_regional_source_queries()` | Country-specific sources |
| `src/company_researcher/shared/search.py` | `QueryDiversifier.generate_diverse_queries()` | Category-based diversification |
| | `QUERY_CATEGORIES` constant | 8 information categories |
| `src/company_researcher/prompts/` | Prompt templates | Query generation prompts |

---

### Search Execution

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/integrations/search_router.py` | `SearchRouter.search()` | Main search orchestration |
| | `get_search_router()` | Singleton factory |
| | `SearchRouter._search_with_fallback()` | Provider fallback chain |
| | `PersistentCache` | Disk-based caching (30-day TTL) |
| `src/company_researcher/shared/search.py` | `RobustSearchClient.search_company()` | Diversified search client |
| | `RobustSearchClient._search_with_fallback()` | Fallback execution |
| | `SearchResult.calculate_combined_score()` | Result scoring |
| | `ProviderHealth` dataclass | Health tracking |
| | `QueryDiversifier.is_duplicate()` | Deduplication (URL + semantic) |
| `src/company_researcher/workflows/nodes/search_nodes.py` | `search_node()` | Workflow search node |
| | `_is_executive_query()` | Executive query detection |
| `src/company_researcher/integrations/` | Provider clients | Individual provider APIs |
| | `serper_client.py` | Serper search |
| | `brave_client.py` | Brave search |
| | `tavily_client.py` | Tavily search |

---

### Data Extraction

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/ai/extraction/extractor.py` | `AIDataExtractor.extract_all()` | Main extraction orchestration |
| | `AIDataExtractor.classify_company()` | Company type classification |
| | `AIDataExtractor.extract_facts()` | Fact extraction with confidence |
| | `get_data_extractor()` | Singleton factory |
| `src/company_researcher/ai/extraction/models.py` | `ExtractedFact` | Single fact dataclass |
| | `ExtractionResult` | Complete extraction output |
| | `CompanyClassification` | Classification result |
| | `FactType`, `FactCategory` | Enums for fact properties |
| `src/company_researcher/workflows/nodes/analysis_nodes.py` | `extract_data_node()` | Extraction workflow node |
| | `analyze_node()` | Search result analysis |
| `src/company_researcher/ai/quality/contradition_detector.py` | Contradiction detection | Rule-based + LLM detection |

---

### Quality Assessment

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/quality/quality_checker.py` | `check_research_quality()` | Main quality assessment |
| | `check_field_completeness()` | Fast field-level check |
| | `REQUIRED_FIELDS` constant | 15 core fields definition |
| | `_generate_queries_for_missing_fields()` | Gap-based query generation |
| `src/company_researcher/research/data_threshold.py` | `DataThresholdChecker.check()` | Pre/post research validation |
| | `DataThresholdChecker.SECTION_REQUIREMENTS` | Section requirements |
| | `RetryStrategy` enum | Re-search strategies |
| | `DataSufficiency` enum | Sufficiency levels |
| `src/company_researcher/research/quality_enforcer.py` | `ReportQualityEnforcer` | Report-level quality |
| | `QualityLevel` enum | Quality tiers |
| | `SectionAnalysis` | Per-section assessment |
| | `QualityReport` | Complete quality report |
| `src/company_researcher/quality/contradiction_detector.py` | Contradiction detection | Rule-based + LLM detection |
| `src/company_researcher/research/metrics_validator.py` | Numerical validation | Value format validation |

---

### Iteration & Workflow Control

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/workflows/comprehensive_research.py` | `create_comprehensive_workflow()` | Main workflow graph |
| | `should_continue_research()` | Iteration decision logic |
| | `generate_queries_node()` | Query generation node |
| | `search_node()` | Search execution node |
| | `quality_check_node()` | Quality assessment node |
| `src/company_researcher/workflows/nodes/analysis_nodes.py` | `check_quality_node()` | Quality check in analysis |
| | `should_continue_research()` | Iteration decision (fallback) |
| `src/company_researcher/workflows/parallel_agent_research.py` | Multi-agent workflow | Phase 9+ parallel agents |
| | `check_quality_node()` | Quality with Logic Critic |
| `src/company_researcher/workflows/multi_agent_research.py` | `check_quality_node()` | Quality assessment |
| | `should_continue_research()` | Iteration router |

---

### State Management

| File | Key Classes/Functions | Purpose |
|------|----------------------|---------|
| `src/company_researcher/state.py` | `OverallState` | Complete workflow state |
| | `InputState` | Initial input |
| | `OutputState` | Final output |
| | `merge_dicts()` | Concurrent update merger |
| | `add_tokens()` | Token accumulation |
| `src/company_researcher/state/typed_models.py` | Typed state models | Type-safe state |
| `src/company_researcher/state/persistence.py` | State persistence | Checkpoint/recovery |

---

### API Models

| File | Key Classes | Purpose |
|------|------------|---------|
| `src/company_researcher/api/models.py` | `ResearchRequest` | API input validation |
| | `ResearchResponse` | Initial API response |
| | `ResearchResult` | Final result output |
| | `BatchRequest` | Batch research input |
| | `WebhookConfig` | Webhook configuration |
| | `ResearchDepthEnum` | Depth levels (quick/standard/comprehensive) |

---

### Cost & Monitoring

| File | Key Functions | Purpose |
|------|---------------|---------|
| `src/company_researcher/config.py` | `get_config()` | Configuration management |
| | `calculate_llm_cost()` | LLM cost calculation |
| `src/company_researcher/llm/smart_client.py` | `smart_completion()` | Cost-optimized model routing |
| | Model selection logic | Route to cheapest appropriate model |
| `src/company_researcher/monitoring/cost_tracker.py` | Cost tracking | Per-component costs |
| `src/company_researcher/monitoring/metrics.py` | Performance metrics | Latency, throughput tracking |

---

## Important Constants & Configurations

### Query Categories (8)
```python
# Location: src/company_researcher/shared/search.py
QUERY_CATEGORIES = {
    "official_filings": {priority: 1, min_results: 3},
    "investor_relations": {priority: 1, min_results: 5},
    "financial_news": {priority: 2, min_results: 8},
    "company_overview": {priority: 2, min_results: 5},
    "competitive_analysis": {priority: 2, min_results: 5},
    "product_info": {priority: 3, min_results: 5},
    "recent_news": {priority: 3, min_results: 5},
    "leadership": {priority: 3, min_results: 3}
}
```

### Required Fields (15)
```python
# Location: src/company_researcher/quality/quality_checker.py
REQUIRED_FIELDS = {
    "company_name": ["company name", "legal name", "trading as"],
    "headquarters": ["headquarters", "headquarter", "based in", "located in"],
    "founded": ["founded", "established", "incorporated"],
    "industry": ["industry", "sector", "business segment"],
    "employees": ["employees", "workforce", "staff count", "headcount"],
    "ceo": ["ceo", "chief executive", "managing director", "general manager"],
    "leadership_team": ["leadership", "management team", "board", "executives"],
    "revenue": ["revenue", "sales", "turnover", "annual revenue"],
    "profit_margin": ["profit margin", "net margin", "operating margin"],
    "market_cap": ["market cap", "market capitalization", "valuation"],
    "market_share": ["market share", "share of market", "% of market"],
    "subscribers": ["subscribers", "customers", "users", "client base"],
    "competitors": ["competitor", "rival", "competing", "market player"],
    "products_services": ["product", "service", "offering", "solution"],
    "geographic_presence": ["geographic", "countries", "regions", "operations in"]
}
```

### Quality Thresholds
```python
# Location: Various workflow files
QUALITY_SCORE_THRESHOLD = 85              # Minimum to proceed
FIELD_COMPLETENESS_WEIGHT = 0.4           # 40% of composite score
LLM_QUALITY_WEIGHT = 0.6                  # 60% of composite score
CRITICAL_FIELD_PENALTY = 5                # -5 points per critical field
MAX_ITERATIONS = 2                        # Maximum re-search cycles
```

### Provider Fallback Chain
```python
# Location: src/company_researcher/integrations/search_router.py
FALLBACK_CHAIN = [
    ("duckduckgo", "FREE"),
    ("brave", "$0.0003 per 3 results"),
    ("serper", "$0.01 per search"),
    ("tavily", "$0.02 per search")
]
```

### Authority Scoring (Domain-Based)
```python
# Location: src/company_researcher/shared/search.py
AUTHORITY_SCORES = {
    "sec.gov": 1.0,                        # Official/regulatory
    "investor.*": 1.0,
    "ir.*": 1.0,
    "bloomberg.com": 0.85,                 # Major financial news
    "reuters.com": 0.85,
    "wsj.com": 0.85,
    "ft.com": 0.85,
    "techcrunch.com": 0.70,                # Reputable tech/business
    "forbes.com": 0.70,
    "cnbc.com": 0.70,
    ".com/.org/.net": 0.55,                # General domains
    "other": 0.40                          # Low authority
}
```

---

## Data Flow Examples

### Query Generation Example

```
Input: "Tesla"
  │
  ├─ AIQueryGenerator.generate_queries()
  │  └─ LLM: "Generate 5 diverse search queries for Tesla"
  │     Return: [
  │       {"query": "Tesla company overview", "purpose": "general"},
  │       {"query": "Tesla revenue financial results", "purpose": "financial"},
  │       {"query": "Elon Musk CEO Tesla", "purpose": "leadership"},
  │       {"query": "Tesla electric vehicles products", "purpose": "products"},
  │       {"query": "Tesla vs competitors market share", "purpose": "competitive"}
  │     ]
  │
  ├─ MultilingualSearchGenerator.generate_queries()
  │  └─ Region-aware: Spanish "Tesla ingresos", Portuguese "Tesla CEO"
  │
  ├─ Specialized Queries: CEO, financial, competitive
  │
  └─ Result: 15-20 optimized, diverse queries
```

### Search Execution Example

```
Query: "Tesla revenue 2024"
  │
  ├─ Check cache (.cache/search/{hash})
  │  └─ Cache hit? Yes → Return cached result ($0.00)
  │
  └─ NOT found in cache → Execute search
     │
     ├─ Try DuckDuckGo (FREE)
     │  └─ Timeout? Yes → Try next provider
     │
     ├─ Try Brave ($0.0003)
     │  └─ Success! 3 results → Cost: $0.0003
     │
     ├─ Deduplicate & Score
     │  ├─ URL deduplication
     │  ├─ Semantic dedup (embeddings, 85% threshold)
     │  └─ Score: authority * 0.4 + relevance * 0.4 + rank * 0.2
     │
     ├─ Cache result
     │  └─ Store in .cache/search/{hash}.json (TTL: 30 days)
     │
     └─ Return SearchResponse
        ├─ results: [...] (scored)
        ├─ provider: "brave"
        ├─ cost: 0.0003
        ├─ cached: false
        └─ success: true
```

### Quality Assessment Example

```
Input: extracted_data = "Tesla Inc... headquartered in Austin...
        CEO: Elon Musk... revenue $81.4B... 250,000+ employees..."
       sources = [{url: "...", title: "..."}]
  │
  ├─ STEP 1: Field Completeness Check (fast)
  │  ├─ Scan for keywords:
  │  │  ├─ "company_name"? YES (Tesla)
  │  │  ├─ "headquarters"? YES (Austin)
  │  │  ├─ "ceo"? YES (Elon Musk)
  │  │  ├─ "revenue"? YES ($81.4B)
  │  │  ├─ "employees"? YES (250,000)
  │  │  └─ [more fields...]
  │  │
  │  └─ field_score = 12/15 * 100 = 80%
  │
  ├─ STEP 2: LLM Quality Assessment (cheap model)
  │  ├─ Model: DeepSeek V3 (via smart_completion)
  │  ├─ Prompt: "Rate quality 0-100, list gaps"
  │  ├─ Response: {
  │  │    "quality_score": 78,
  │  │    "missing_information": ["Profitability metrics", "Board composition"],
  │  │    "strengths": ["Strong financial data", "Clear leadership info"],
  │  │    "recommended_queries": ["Tesla profit margin", "Tesla board directors"]
  │  │  }
  │  │
  │  └─ llm_quality_score = 78
  │
  ├─ STEP 3: Critical Field Penalty
  │  ├─ Critical fields: company_name, revenue, ceo, market_share
  │  ├─ Missing critical fields: [market_share] (not mentioned)
  │  ├─ Penalty: -5 points
  │  └─ field_score_adjusted = 80 - 5 = 75
  │
  ├─ STEP 4: Composite Scoring
  │  ├─ composite = (78 * 0.6) + (75 * 0.4)
  │  ├─ composite = 46.8 + 30 = 76.8
  │  └─ quality_score = 77 (final)
  │
  ├─ STEP 5: Decision
  │  ├─ quality_score (77) < threshold (85)?
  │  ├─ iteration_count (0) < max (2)?
  │  └─ Decision: RE-SEARCH
  │
  └─ Output: QualityResult
     ├─ quality_score: 77
     ├─ field_score: 75
     ├─ llm_quality_score: 78
     ├─ missing_fields: [market_share, board_composition, ...]
     ├─ critical_missing: [market_share]
     ├─ recommended_queries: [
     │    "Tesla market share electric vehicle industry",
     │    "Tesla profit margin earnings",
     │    "Tesla board of directors"
     │  ]
     └─ [Ready for iteration 1]
```

---

## Testing & Debugging Quick Reference

### Check Query Generation
```python
from company_researcher.ai.query import get_query_generator

generator = get_query_generator()
result = generator.generate_queries(
    company_name="Tesla",
    context="US electric vehicle manufacturer"
)
print(f"Generated {len(result.queries)} queries")
for q in result.queries:
    print(f"  - {q.query} (purpose: {q.purpose})")
```

### Check Search Router
```python
from company_researcher.integrations import get_search_router

router = get_search_router()
response = router.search(
    query="Tesla revenue",
    quality="premium",  # Try all providers
    max_results=5
)
print(f"Provider: {response.provider}")
print(f"Cached: {response.cached}")
print(f"Cost: ${response.cost:.4f}")
print(f"Results: {len(response.results)}")
```

### Check Quality Assessment
```python
from company_researcher.quality import check_research_quality

quality_result = check_research_quality(
    company_name="Tesla",
    extracted_data="Tesla Inc... CEO Elon Musk... Revenue $81.4B...",
    sources=[{"url": "...", "title": "..."}]
)
print(f"Quality Score: {quality_result['quality_score']:.1f}/100")
print(f"Field Score: {quality_result['field_score']:.1f}")
print(f"Missing Fields: {quality_result['missing_fields']}")
print(f"Recommended Queries: {quality_result['recommended_queries']}")
```

### Check Iteration Decision
```python
from company_researcher.workflows.comprehensive_research import should_continue_research
from company_researcher.state import OverallState

# Mock state
state = {
    "quality_score": 78.5,
    "iteration_count": 0
}

decision = should_continue_research(state)
print(f"Decision: {decision}")  # "continue_research" or "finish"
```

---

## Performance Tuning

### To Improve Speed
1. Parallelize query execution (10 queries in parallel)
2. Use Groq (1,300+ tokens/sec) instead of Anthropic
3. Enable persistent caching (significant speedup for batch)
4. Reduce max_results per query (fewer results = faster)

### To Improve Quality
1. Increase max_iterations (currently 2)
2. Lower quality_score_threshold (currently 85)
3. Add more specialized queries per category
4. Implement multi-source fact validation

### To Reduce Cost
1. Increase cache TTL (30 days → 60 days)
2. Use DuckDuckGo more aggressively (only escalate on true failure)
3. Batch research (100 companies) to maximize cache hits
4. Use DeepSeek for more tasks (95% cheaper than Claude)

---

## Common Issues & Solutions

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| Low quality scores | Missing required fields | Check REQUIRED_FIELDS spelling, adjust keywords |
| High costs | API overuse, poor caching | Check cache dir exists, verify TTL setting |
| Slow searches | Bad provider health | Check provider API status, reset health tracking |
| Empty results | All providers failing | Check API keys configured, network connectivity |
| Contradictions | Conflicting data sources | Review contradiction_detector rules, adjust thresholds |
