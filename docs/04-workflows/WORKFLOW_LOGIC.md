# Workflow Logic Documentation

Comprehensive documentation of the LangGraph workflow decision logic, state transitions, and control flow.

---

## Workflow Architecture

### Node Sequence

```
START
  │
  ▼
┌─────────────────────┐
│  generate_queries   │  ← Entry point
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│      search         │  ← Tavily API calls
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     analyze         │  ← Claude analysis
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  news_sentiment     │  ← Sentiment scoring
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   extract_data      │  ← Structured extraction
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  check_quality      │  ← Quality gate (DECISION)
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
[score < 85]  [score >= 85]
[iter < 2]    [OR iter >= 2]
    │           │
    │           ▼
    │    ┌─────────────────────┐
    │    │competitive_analysis │
    │    └─────────┬───────────┘
    │              │
    │              ▼
    │    ┌─────────────────────┐
    │    │  risk_assessment    │
    │    └─────────┬───────────┘
    │              │
    │              ▼
    │    ┌─────────────────────┐
    │    │ investment_thesis   │
    │    └─────────┬───────────┘
    │              │
    │              ▼
    │    ┌─────────────────────┐
    │    │    save_report      │
    │    └─────────┬───────────┘
    │              │
    │              ▼
    │            END
    │
    └──────────────► generate_queries (LOOP BACK)
```

---

## State Transitions

### State Schema

```python
class OverallState(TypedDict):
    # Input (immutable)
    company_name: str

    # Query Generation Phase
    search_queries: List[str]
    detected_region: Optional[str]
    detected_language: Optional[str]

    # Search Phase
    search_results: Annotated[List[Dict], add]  # Accumulates
    sources: Annotated[List[Dict], add]          # Accumulates

    # Analysis Phase
    notes: List[str]
    news_sentiment: Optional[Dict]

    # Extraction Phase
    company_overview: Optional[str]
    key_metrics: Optional[Dict]
    products_services: Optional[List[str]]
    competitors: Optional[List[str]]
    key_insights: Optional[List[str]]

    # Quality Phase
    quality_score: Optional[float]       # 0-100
    iteration_count: int                 # Starts at 0
    missing_info: Optional[List[str]]

    # Enhanced Analysis Phase
    competitive_matrix: Optional[Dict]
    risk_profile: Optional[Dict]
    investment_thesis: Optional[Dict]

    # Agent Coordination
    agent_outputs: Annotated[Optional[Dict], merge_dicts]

    # Metrics (accumulate across iterations)
    start_time: datetime
    total_cost: Annotated[float, add]
    total_tokens: Annotated[Dict[str, int], add_tokens]

    # Output
    report_path: Optional[str]
```

### Reducer Functions

| Field | Reducer | Behavior |
|-------|---------|----------|
| `search_results` | `add` | Appends new results to existing list |
| `sources` | `add` | Appends new sources to existing list |
| `total_cost` | `add` | Sums costs across all nodes |
| `total_tokens` | `add_tokens` | Sums input/output tokens separately |
| `agent_outputs` | `merge_dicts` | Merges parallel agent outputs |

```python
def merge_dicts(left: Dict, right: Dict) -> Dict:
    """Merge for parallel agent outputs."""
    return {**(left or {}), **(right or {})}

def add_tokens(left: Dict, right: Dict) -> Dict:
    """Add token counts from parallel agents."""
    return {
        "input": left.get("input", 0) + right.get("input", 0),
        "output": left.get("output", 0) + right.get("output", 0)
    }
```

---

## Decision Logic

### Quality Gate Decision

**Location**: `basic_research.py:847`

```python
def should_continue_research(state: OverallState) -> str:
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 2  # HARDCODED THRESHOLD

    # Decision tree
    if quality_score >= 85:
        return "finish"
    elif iteration_count >= max_iterations:
        return "finish"
    else:
        return "iterate"
```

### Decision Matrix

| Condition | Quality Score | Iteration Count | Action |
|-----------|--------------|-----------------|--------|
| Quality Met | >= 85 | Any | `finish` → proceed to analysis |
| Max Iterations | < 85 | >= 2 | `finish` → proceed (accept lower quality) |
| Continue | < 85 | < 2 | `iterate` → loop back to generate_queries |

### Threshold Rationale

| Threshold | Value | Rationale |
|-----------|-------|-----------|
| Quality Score | 85% | Balances completeness vs. cost. Below 80% has noticeable gaps. Above 90% has diminishing returns. |
| Max Iterations | 2 | Each iteration costs ~$0.03. Two iterations usually fill 80% of gaps. Three rarely improves quality significantly. |

---

## Node Specifications

### 1. generate_queries_node

**Purpose**: Generate search queries with multilingual support

**Input State**:
```python
{
    "company_name": str,  # Required
    "iteration_count": int  # For iteration-aware query generation
}
```

**Output State**:
```python
{
    "search_queries": List[str],  # 5-8 queries
    "detected_region": str,        # e.g., "BRAZIL", "MEXICO"
    "detected_language": str       # e.g., "PT", "ES"
}
```

**Logic**:
1. Detect company region from name patterns
2. Generate multilingual queries (English + local language)
3. Add parent company queries if applicable
4. Limit total to `config.num_search_queries + 3`

---

### 2. search_node

**Purpose**: Execute Tavily searches

**Input State**:
```python
{
    "search_queries": List[str],
    "total_cost": float
}
```

**Output State**:
```python
{
    "search_results": List[Dict],  # Appended via reducer
    "sources": List[Dict],          # Appended via reducer
    "total_cost": float             # Added via reducer
}
```

**Cost Calculation**:
```python
tavily_cost = len(search_queries) * 0.001  # $0.001 per query
```

---

### 3. analyze_node

**Purpose**: LLM analysis of search results

**Input State**:
```python
{
    "company_name": str,
    "search_results": List[Dict],
    "total_cost": float,
    "total_tokens": Dict
}
```

**Output State**:
```python
{
    "notes": List[str],  # Analysis text
    "total_cost": float,
    "total_tokens": Dict
}
```

**LLM Call**:
- Model: `config.llm_model` (default: claude-3-5-haiku-20241022)
- Max tokens: `config.llm_max_tokens` (default: 4000)
- Temperature: `config.llm_temperature` (default: 0.0)

---

### 4. news_sentiment_node

**Purpose**: Analyze sentiment from search results

**Input State**:
```python
{
    "company_name": str,
    "search_results": List[Dict]
}
```

**Output State**:
```python
{
    "news_sentiment": {
        "company_name": str,
        "total_articles": int,
        "sentiment_score": float,      # -1.0 to 1.0
        "sentiment_level": str,        # "very_negative" to "very_positive"
        "sentiment_trend": str,        # "improving", "stable", "declining"
        "key_topics": List[str],
        "positive_highlights": List[str],
        "negative_highlights": List[str],
        "confidence": float,
        "category_breakdown": Dict[str, int]
    }
}
```

---

### 5. extract_data_node

**Purpose**: Extract structured data from notes

**Input State**:
```python
{
    "company_name": str,
    "notes": List[str],
    "sources": List[Dict],
    "total_cost": float,
    "total_tokens": Dict
}
```

**Output State**:
```python
{
    "company_overview": str,  # Markdown formatted
    "total_cost": float,
    "total_tokens": Dict
}
```

---

### 6. check_quality_node

**Purpose**: Evaluate research quality and trigger iteration

**Input State**:
```python
{
    "company_name": str,
    "company_overview": str,
    "sources": List[Dict],
    "iteration_count": int,
    "total_cost": float,
    "total_tokens": Dict
}
```

**Output State**:
```python
{
    "quality_score": float,         # 0-100
    "missing_info": List[str],      # Gaps identified
    "iteration_count": int,         # Incremented
    "total_cost": float,
    "total_tokens": Dict
}
```

**Quality Scoring Logic** (from `quality_checker.py`):

```python
# Scoring components
completeness_score = check_completeness(state)    # 0-40 points
accuracy_score = check_accuracy(state)            # 0-30 points
depth_score = check_depth(state)                  # 0-30 points

quality_score = completeness_score + accuracy_score + depth_score
```

---

### 7. competitive_analysis_node

**Purpose**: Generate competitive matrix

**Input State**:
```python
{
    "company_name": str,
    "key_metrics": Optional[Dict],
    "competitors": Optional[List[str]]
}
```

**Output State**:
```python
{
    "competitive_matrix": {
        "company": {
            "name": str,
            "scores": Dict[str, float],
            "position": str
        },
        "competitors": List[Dict],
        "dimensions": List[str],
        "strategic_groups": Dict,
        "insights": List[str],
        "recommendations": List[str]
    }
}
```

---

### 8. risk_assessment_node

**Purpose**: Quantify company risks

**Input State**:
```python
{
    "company_name": str,
    "company_overview": str,
    "notes": List[str],
    "key_metrics": Optional[Dict],
    "competitors": Optional[List[str]],
    "key_insights": Optional[List[str]],
    "detected_region": Optional[str]
}
```

**Output State**:
```python
{
    "risk_profile": {
        "company_name": str,
        "overall_score": float,      # 0-100
        "grade": str,                # A-F
        "risks": List[Dict],         # Individual risks
        "category_scores": Dict[str, float],
        "risk_adjusted_metrics": Dict
    }
}
```

---

### 9. investment_thesis_node

**Purpose**: Generate investment recommendation

**Input State**:
```python
{
    "company_name": str,
    "company_overview": str,
    "key_metrics": Optional[Dict],
    "products_services": Optional[List[str]],
    "competitors": Optional[List[str]],
    "key_insights": Optional[List[str]],
    "competitive_matrix": Optional[Dict],
    "risk_profile": Optional[Dict]
}
```

**Output State**:
```python
{
    "investment_thesis": {
        "company_name": str,
        "recommendation": str,       # "strong_buy" to "strong_sell"
        "confidence": float,         # 0-1
        "target_horizon": str,
        "summary": str,
        "bull_case": Dict,
        "bear_case": Dict,
        "valuation": Optional[Dict],
        "key_metrics_to_watch": List[str],
        "suitable_for": List[str]
    }
}
```

---

### 10. save_report_node

**Purpose**: Generate and save markdown report

**Input State**: (Full state)

**Output State**:
```python
{
    "report_path": str  # e.g., "outputs/research/Microsoft/report_20241208_143022.md"
}
```

**Report Structure**:
```
outputs/research/{company_name}/
├── report_{timestamp}.md  # Full report with all sections
```

---

## Iteration Behavior

### First Iteration (iteration_count=0)

1. `generate_queries` → General queries covering overview, financials, products, market
2. `search` → Execute all queries
3. `analyze` → Initial analysis
4. `news_sentiment` → Sentiment baseline
5. `extract_data` → Initial extraction
6. `check_quality` → Score typically 60-75% for well-known companies
7. **Decision**: Usually `iterate` (score < 85)

### Second Iteration (iteration_count=1)

1. `generate_queries` → Gap-filling queries based on `missing_info`
2. `search` → Additional targeted searches
3. `analyze` → Supplemental analysis
4. `news_sentiment` → Updated sentiment
5. `extract_data` → Merged extraction
6. `check_quality` → Score typically 80-90%
7. **Decision**: Usually `finish` (score >= 85 OR max iterations)

### State Accumulation

During iterations, these fields accumulate:
- `search_results`: All results from all iterations
- `sources`: All sources from all iterations
- `total_cost`: Sum of all costs
- `total_tokens`: Sum of all tokens

---

## Error Handling

### API Failures

| Error Type | Handling |
|------------|----------|
| Tavily API failure | Workflow continues with empty results |
| Anthropic API failure | Raises exception, workflow stops |
| Timeout | Uses `config.api_timeout_seconds` (60s default) |

### Quality Fallback

If after `max_iterations` quality is still below threshold:
- Workflow proceeds to analysis phase anyway
- Report includes warning about data quality
- `quality_score` reflects actual achieved score

---

## Cost Model

### Per-Node Costs

| Node | Cost Source | Typical Cost |
|------|-------------|--------------|
| generate_queries | None (rule-based) | $0.00 |
| search | Tavily: $0.001/query | $0.005-0.008 |
| analyze | Claude LLM | $0.01-0.02 |
| news_sentiment | Rule-based | $0.00 |
| extract_data | Claude LLM | $0.01-0.02 |
| check_quality | Claude LLM | $0.005-0.01 |
| competitive_analysis | Rule-based | $0.00 |
| risk_assessment | Rule-based | $0.00 |
| investment_thesis | Rule-based | $0.00 |
| save_report | None (file I/O) | $0.00 |

### Total Cost Breakdown

| Iterations | Typical Total Cost |
|------------|-------------------|
| 1 | $0.03-0.05 |
| 2 | $0.06-0.10 |

---

## Configuration Impact

### Key Config Parameters

| Parameter | Default | Impact |
|-----------|---------|--------|
| `num_search_queries` | 5 | More queries = more results but higher cost |
| `search_results_per_query` | 3 | Results per query |
| `max_search_results` | 15 | Cap on total results processed |
| `llm_model` | claude-3-5-haiku-20241022 | Model determines quality/cost tradeoff |
| `llm_max_tokens` | 4000 | Output limit per LLM call |
| `llm_temperature` | 0.0 | Deterministic outputs |

---

**Related Documentation**:
- [State Management](../07-state-management/README.md)
- [Quality System](../08-quality-system/README.md)
- [Configuration](../06-configuration/README.md)

---

**Last Updated**: December 2024
