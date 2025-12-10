# Configuration Threshold Rationale

Documentation explaining the reasoning behind configuration values, thresholds, and limits.

---

## Quality Thresholds

### Quality Score Threshold: 85%

**Value**: `quality_threshold = 85`

**Location**: `basic_research.py:859`, `quality_checker.py`

**Rationale**:
- **Below 80%**: Research has noticeable gaps (missing revenue, no competitors)
- **80-84%**: Acceptable but not comprehensive
- **85-89%**: Good quality with most critical data present
- **90-100%**: Excellent, rarely achieved on first iteration

**Trade-off**: Higher threshold increases quality but also cost/time.

**Empirical Data**:
| Threshold | Avg Iterations | Avg Cost | Completeness |
|-----------|----------------|----------|--------------|
| 80% | 1.2 | $0.04 | 78% |
| 85% | 1.6 | $0.06 | 89% |
| 90% | 2.0 | $0.10 | 94% |

---

### Maximum Iterations: 2

**Value**: `max_iterations = 2`

**Location**: `basic_research.py:859`

**Rationale**:
- **Iteration 1**: Gathers ~60-75% of available information
- **Iteration 2**: Fills ~80% of remaining gaps
- **Iteration 3+**: Diminishing returns (< 5% improvement)

**Cost Analysis**:
```
Iteration 1: ~$0.03-0.04
Iteration 2: ~$0.03-0.04
Iteration 3: ~$0.03-0.04 (rarely improves score by >3%)

Total for 2 iterations: $0.06-0.08
Total for 3 iterations: $0.09-0.12 (50% more cost, <5% improvement)
```

**Decision**: 2 iterations provides best cost/quality balance.

---

## LLM Configuration

### Default Model: claude-3-5-haiku-20241022

**Value**: `llm_model = "claude-3-5-haiku-20241022"`

**Rationale**:
| Model | Input Cost | Output Cost | Speed | Quality |
|-------|------------|-------------|-------|---------|
| Haiku 3.5 | $0.80/1M | $4.00/1M | Fast | Good |
| Sonnet 3.5 | $3.00/1M | $15.00/1M | Medium | Excellent |
| Opus | $15.00/1M | $75.00/1M | Slow | Best |

**Decision**: Haiku provides 80% of Sonnet's quality at 25% of the cost. Suitable for research tasks where volume matters more than nuance.

**When to Use Sonnet**: Complex analysis, investment recommendations, critical decisions.

---

### Temperature: 0.0

**Value**: `llm_temperature = 0.0`

**Location**: `config.py:192`

**Rationale**:
- **0.0**: Deterministic, consistent outputs for factual extraction
- **0.1-0.3**: Slight variation, good for creative query generation
- **0.7+**: High creativity, not suitable for research

**Agent-Specific Temperatures**:
| Agent | Temperature | Reason |
|-------|-------------|--------|
| financial | 0.0 | Numbers must be exact |
| market | 0.0 | Market data must be precise |
| researcher (queries) | 0.7 | Creative query generation |
| synthesizer | 0.1 | Consistent report format |
| reasoning | 0.1 | Balanced insight generation |

---

### Max Tokens: 4000

**Value**: `llm_max_tokens = 4000`

**Location**: `config.py:197`

**Rationale**:
- Typical analysis output: 1500-2500 tokens
- Peak output (comprehensive reports): 3500-4000 tokens
- Buffer for complex analyses: +500 tokens

**Agent-Specific Limits**:
| Agent | Max Tokens | Typical Output |
|-------|------------|----------------|
| researcher | 500 | 200-400 (queries only) |
| analyst | 1000 | 600-900 |
| financial | 800 | 500-700 |
| synthesizer | 1500 | 1000-1400 |
| investment_analyst | 2500 | 1800-2300 |
| deep_research | 2000 | 1500-1800 |

---

## Search Configuration

### Number of Search Queries: 5

**Value**: `num_search_queries = 5`

**Location**: `config.py:206`

**Rationale**:
- 5 queries cover essential aspects (overview, financial, product, market, news)
- More queries = more cost but diminishing information gain
- Tavily cost: $0.001 per query

**Query Coverage**:
```
Query 1: Company overview/background
Query 2: Financial performance/metrics
Query 3: Products and services
Query 4: Market position/competitors
Query 5: Recent news/developments
```

---

### Results Per Query: 3

**Value**: `search_results_per_query = 3`

**Location**: `config.py:211`

**Rationale**:
- Top 3 results typically contain 80% of useful information
- Results 4-10 often have duplicate content
- More results = more LLM tokens to process

**Quality Distribution**:
| Result Rank | Info Quality |
|-------------|--------------|
| 1 | 35% |
| 2 | 25% |
| 3 | 20% |
| 4-10 | 20% (combined) |

---

### Max Search Results: 15

**Value**: `max_search_results = 15`

**Location**: `config.py:216`

**Rationale**:
- 5 queries × 3 results = 15 results
- Caps total to prevent excessive LLM costs
- Beyond 15, marginal information gain < 5%

---

## Timeout Configuration

### API Timeout: 60 seconds

**Value**: `api_timeout_seconds = 60.0`

**Location**: `config.py:484`

**Rationale**:
- Claude typically responds in 5-30 seconds
- 60 seconds handles network variability
- Prevents indefinite hangs

---

### Search Timeout: 30 seconds

**Value**: `search_timeout_seconds = 30.0`

**Location**: `config.py:493`

**Rationale**:
- Tavily typically responds in 2-10 seconds
- 30 seconds handles slow queries
- Faster than general API timeout (search is simpler)

---

### Connection Timeout: 10 seconds

**Value**: `api_connect_timeout_seconds = 10.0`

**Location**: `config.py:489`

**Rationale**:
- Connection should establish within 2-3 seconds
- 10 seconds handles slow networks
- Faster failure for unreachable services

---

## Cost Configuration

### Target Cost: $0.30 per research

**Value**: `target_cost_usd = 0.30`

**Location**: `config.py:232`

**Rationale**:
- Typical research costs $0.05-0.10
- Target provides 3x buffer for complex cases
- Enables cost alerts if exceeded

**Cost Breakdown (Typical)**:
| Component | Cost |
|-----------|------|
| Search (5 queries) | $0.005 |
| Analysis LLM | $0.02 |
| Extraction LLM | $0.02 |
| Quality Check LLM | $0.01 |
| **Total** | **$0.055** |

---

### Max Research Time: 300 seconds

**Value**: `max_research_time_seconds = 300`

**Location**: `config.py:225`

**Rationale**:
- Typical research: 2-3 minutes (120-180 seconds)
- Complex research with 2 iterations: 4-5 minutes
- 5 minutes (300s) provides safety margin

---

## Processing Limits

### Max Sources Per Agent: 15

**Value**: `max_sources_per_agent = 15`

**Location**: `config.py:441`

**Rationale**:
- Each source adds ~200-500 tokens to prompt
- 15 sources = ~3000-7500 tokens
- Beyond 15, context window fills without proportional benefit

---

### Content Truncate Length: 500 characters

**Value**: `content_truncate_length = 500`

**Location**: `config.py:446`

**Rationale**:
- Most useful information in first 500 chars
- Full content averages 2000-5000 chars
- Truncation saves ~75% tokens per source

---

## Domain Exploration

### Max Pages: 8

**Value**: `domain_exploration_max_pages = 8`

**Location**: `config.py:459`

**Rationale**:
- Key pages: Home, About, Products, Leadership, Investors, News
- 8 pages covers essentials + 2 buffer
- More pages = more time, less marginal value

---

### Exploration Timeout: 10 seconds

**Value**: `domain_exploration_timeout = 10.0`

**Location**: `config.py:464`

**Rationale**:
- Most pages load in 1-3 seconds
- 10 seconds handles slow sites
- Prevents blocking on unresponsive sites

---

### Max Content Per Page: 50000 characters

**Value**: `domain_exploration_max_content = 50000`

**Location**: `config.py:469`

**Rationale**:
- Average page: 10000-20000 chars
- 50000 handles long pages (annual reports)
- Beyond 50000, content is usually boilerplate/navigation

---

## Report Configuration

### Sources Per Domain: 3

**Value**: `report_sources_per_domain = 3`

**Location**: `config.py:254`

**Rationale**:
- Prevents report being dominated by single domain
- Ensures source diversity
- 3 per domain × multiple domains = balanced coverage

---

### Max Results in Report: 10

**Value**: `report_max_results = 10`

**Location**: `config.py:259`

**Rationale**:
- Reports should be digestible
- Top 10 results contain best information
- Keeps report length manageable

---

### Summary Max Items: 5

**Value**: `summary_max_items = 5`

**Location**: `config.py:264`

**Rationale**:
- Human cognitive limit: 5-7 items
- Summaries should be scannable
- Top 5 = most important items

---

### Insights Max Count: 10

**Value**: `insights_max_count = 10`

**Location**: `config.py:269`

**Rationale**:
- More than 10 insights = information overload
- Prioritization forces quality over quantity

---

### Recommendations Max Count: 5

**Value**: `recommendations_max_count = 5`

**Location**: `config.py:274`

**Rationale**:
- Actionable recommendations should be limited
- 5 recommendations = clear action items
- More than 5 = decision paralysis

---

## Tuning Guidelines

### When to Adjust Thresholds

| Scenario | Adjustment |
|----------|------------|
| Research is too shallow | Increase `quality_threshold` to 90% |
| Research takes too long | Decrease `max_iterations` to 1 |
| Costs are too high | Use Haiku model, reduce `num_search_queries` |
| Missing data frequently | Increase `search_results_per_query` to 5 |
| Reports are too long | Reduce `max_results`, `insights_max_count` |

### Environment-Specific Settings

```yaml
# Development
quality_threshold: 75
max_iterations: 1
llm_model: claude-3-5-haiku-20241022

# Production
quality_threshold: 85
max_iterations: 2
llm_model: claude-3-5-haiku-20241022

# High-Quality Mode
quality_threshold: 90
max_iterations: 3
llm_model: claude-3-5-sonnet-20241022
```

---

**Related Documentation**:
- [Configuration Guide](README.md)
- [Quality System](../08-quality-system/README.md)
- [Workflow Logic](../04-workflows/WORKFLOW_LOGIC.md)

---

**Last Updated**: December 2024
