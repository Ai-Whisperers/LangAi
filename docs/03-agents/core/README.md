# Core Agents

Core agents handle the fundamental research workflow: gathering data, analyzing it, and synthesizing reports.

## Overview

```
CORE AGENTS
    |
    +-- Researcher Agent: Query generation + search execution
    |
    +-- Analyst Agent: Data extraction + summarization
    |
    +-- Synthesizer Agent: Report generation + quality scoring
```

## Researcher Agent

**Purpose**: Generate search queries, execute searches, discover sources

**Location**: `src/company_researcher/agents/core/researcher.py`

### Responsibilities

1. Generate intelligent search queries from company name
2. Execute searches via Tavily and/or DuckDuckGo
3. Explore company domains for additional content
4. Collect and deduplicate sources
5. Return structured search results

### Input

```python
{
    "company_name": "Microsoft"
}
```

### Output

```python
{
    "search_queries": [
        "Microsoft company overview financials",
        "Microsoft products services 2024",
        "Microsoft market position competitors"
    ],
    "search_results": [
        {"title": "...", "url": "...", "content": "..."},
        # ... more results
    ],
    "sources": ["https://microsoft.com", ...],
    "total_cost": 0.02
}
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `researcher_max_tokens` | 1000 | Max tokens for query generation |
| `num_search_queries` | 3 | Number of queries to generate |
| `max_search_results` | 10 | Results per query |

### Implementation

```python
def researcher_node(state: OverallState) -> Dict:
    company = state["company_name"]

    # Generate queries
    queries = generate_queries(company)

    # Execute searches
    results = []
    for query in queries:
        results.extend(tavily_search(query))

    # Explore domain
    domain_content = explore_domain(company)
    results.extend(domain_content)

    return {
        "search_queries": queries,
        "search_results": results,
        "sources": extract_sources(results)
    }
```

---

## Analyst Agent

**Purpose**: Extract key information and summarize search results

**Location**: `src/company_researcher/agents/core/analyst.py`

### Responsibilities

1. Process raw search results
2. Extract company overview and key facts
3. Identify financial metrics mentioned
4. Summarize products/services
5. Note competitors mentioned

### Input

```python
{
    "company_name": "Microsoft",
    "search_results": [...]
}
```

### Output

```python
{
    "company_overview": "Microsoft Corporation is...",
    "key_metrics": {
        "revenue": "$198B",
        "employees": "220,000+"
    },
    "products_services": ["Azure", "Office 365", ...],
    "competitors": ["Amazon", "Google", "Salesforce"],
    "agent_outputs": {"analyst": {...}},
    "total_cost": 0.03
}
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `analyst_max_tokens` | 2000 | Max tokens for analysis |
| `analyst_temperature` | 0.0 | LLM temperature |

### Prompt Template

```
You are a business analyst. Analyze search results for {company}.

Extract:
1. Company Overview (2-3 sentences)
2. Key Financial Metrics (revenue, growth, profitability)
3. Products and Services
4. Competitors Mentioned
5. Notable Recent News

Search Results:
{formatted_results}
```

---

## Synthesizer Agent

**Purpose**: Combine all agent outputs into a comprehensive report

**Location**: `src/company_researcher/agents/core/synthesizer.py`

### Responsibilities

1. Wait for all specialist agents to complete
2. Combine outputs into coherent report
3. Resolve any contradictions between agents
4. Calculate overall quality score
5. Format final markdown report

### Input

```python
{
    "company_name": "Microsoft",
    "agent_outputs": {
        "analyst": {...},
        "financial": {...},
        "market": {...},
        "product": {...}
    }
}
```

### Output

```python
{
    "comprehensive_report": "# Microsoft Research Report\n\n...",
    "quality_score": 88.5,
    "report_sections": {
        "executive_summary": "...",
        "company_overview": "...",
        "financials": "...",
        "market_position": "...",
        "products": "...",
        "competitors": "...",
        "strategy": "..."
    },
    "total_cost": 0.04
}
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `synthesizer_max_tokens` | 4000 | Max tokens for synthesis |
| `synthesizer_temperature` | 0.0 | LLM temperature |

### Report Structure

```markdown
# {Company} Research Report

## Executive Summary
- Key findings
- Investment thesis
- Risk factors

## Company Overview
- Background and history
- Business model
- Leadership

## Financial Analysis
- Revenue and growth
- Profitability
- Balance sheet

## Market Position
- Market size and share
- Competitive landscape
- Industry trends

## Products & Services
- Product portfolio
- Technology stack
- Recent launches

## Competitive Analysis
- Key competitors
- Competitive advantages
- Weaknesses

## Strategic Outlook
- Growth opportunities
- Risks and challenges
- Future direction

## Sources
- List of citations
```

### Quality Scoring

The Synthesizer calculates quality based on:

| Component | Weight | Criteria |
|-----------|--------|----------|
| Completeness | 30% | All sections present |
| Financial Data | 25% | Revenue, growth, profitability |
| Market Data | 20% | Position, trends, share |
| Source Quality | 15% | Diverse, recent, authoritative |
| Coherence | 10% | No contradictions |

---

## Agent Interaction

### Execution Order

```
Researcher ──────┬──────> Financial ─────────┐
                 ├──────> Market ────────────├──> Synthesizer
                 ├──────> Product ───────────┤
                 └──────> Competitor ────────┘
```

### State Flow

```python
# Step 1: Researcher populates initial state
state = {"search_results": [...], "sources": [...]}

# Step 2: Specialists add their outputs (parallel)
state["agent_outputs"]["financial"] = {...}
state["agent_outputs"]["market"] = {...}

# Step 3: Synthesizer combines everything
state["comprehensive_report"] = "..."
state["quality_score"] = 88.5
```

---

**Related Documentation**:
- [Specialist Agents](../specialists/)
- [Quality Agents](../quality/)
- [Workflow Documentation](../../04-workflows/)

---

**Last Updated**: December 2024
