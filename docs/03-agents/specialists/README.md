# Specialist Agents

Specialist agents analyze specific business domains in parallel, providing deep expertise in their area.

## Overview

```
SPECIALIST AGENTS (Parallel Execution)
    |
    +-- Financial Agent: Revenue, profitability, balance sheet
    |
    +-- Market Agent: Market size, position, trends
    |
    +-- Product Agent: Products, technology, roadmap
    |
    +-- Competitor Scout: Competitors, positioning
    |
    +-- Brand Auditor: Brand perception, reputation
    |
    +-- Social Media Agent: Social presence, engagement
```

## Financial Agent

**Purpose**: Deep financial analysis of the company

**Location**: `src/company_researcher/agents/financial/`

### Analysis Areas

| Area | Metrics | Sources |
|------|---------|---------|
| **Revenue** | Total revenue, growth rate, segments | SEC filings, earnings |
| **Profitability** | Gross margin, operating margin, net margin | Financial reports |
| **Balance Sheet** | Assets, liabilities, cash position | 10-K, 10-Q |
| **Valuation** | P/E ratio, market cap, EV/EBITDA | Stock data |
| **Cash Flow** | Operating CF, free CF, capital allocation | Financial statements |

### Output Structure

```python
{
    "financial": {
        "revenue": {
            "total": "$198.3B",
            "growth_yoy": "7.0%",
            "segments": {
                "Intelligent Cloud": "$87.9B",
                "Productivity": "$69.3B",
                "Personal Computing": "$41.1B"
            }
        },
        "profitability": {
            "gross_margin": "69.4%",
            "operating_margin": "41.2%",
            "net_margin": "35.1%"
        },
        "balance_sheet": {
            "total_assets": "$411B",
            "cash_and_equivalents": "$111B",
            "debt": "$47B"
        },
        "valuation": {
            "market_cap": "$2.8T",
            "pe_ratio": 35.2,
            "ev_ebitda": 24.5
        },
        "analysis": "Microsoft demonstrates strong financial health...",
        "confidence": 0.92
    }
}
```

### External Integrations

| Source | Data Provided | API Required |
|--------|--------------|--------------|
| yfinance | Stock prices, basic financials | No (free) |
| Alpha Vantage | Fundamentals, income statements | Yes |
| Financial Modeling Prep | Comprehensive financials | Yes |
| SEC EDGAR | Official filings (10-K, 10-Q) | No (public) |

---

## Market Agent

**Purpose**: Analyze market position, size, and competitive dynamics

**Location**: `src/company_researcher/agents/market/market.py`

### Analysis Areas

| Area | Metrics | Focus |
|------|---------|-------|
| **Market Size** | TAM, SAM, SOM | Industry sizing |
| **Market Position** | Share, rank, leadership | Competitive standing |
| **Trends** | Growth drivers, disruptions | Market dynamics |
| **Geography** | Regional breakdown | Geographic presence |

### Output Structure

```python
{
    "market": {
        "market_size": {
            "tam": "$500B",
            "growth_rate": "12% CAGR"
        },
        "market_position": {
            "share": "35%",
            "rank": 1,
            "category": "Cloud Computing"
        },
        "trends": [
            "AI/ML integration driving growth",
            "Multi-cloud adoption increasing",
            "Edge computing emerging"
        ],
        "competitive_dynamics": {
            "intensity": "High",
            "key_battlegrounds": ["Enterprise AI", "Cloud Infrastructure"]
        },
        "analysis": "Microsoft holds strong position in cloud...",
        "confidence": 0.88
    }
}
```

---

## Product Agent

**Purpose**: Catalog products, technology stack, and roadmap

**Location**: `src/company_researcher/agents/specialized/`

### Analysis Areas

| Area | Focus | Data Points |
|------|-------|-------------|
| **Products** | Core offerings | Name, category, pricing |
| **Technology** | Tech stack, architecture | Languages, frameworks, cloud |
| **Innovation** | Recent launches, patents | New products, R&D |
| **Roadmap** | Future direction | Announcements, plans |

### Output Structure

```python
{
    "product": {
        "products": [
            {
                "name": "Azure",
                "category": "Cloud Platform",
                "description": "Enterprise cloud services",
                "key_features": ["IaaS", "PaaS", "AI Services"]
            },
            {
                "name": "Microsoft 365",
                "category": "Productivity Suite",
                "description": "Office applications bundle"
            }
        ],
        "technology_stack": {
            "languages": ["C#", "TypeScript", "Python"],
            "cloud": "Azure (primary)",
            "ai_ml": ["Azure AI", "OpenAI partnership"]
        },
        "recent_launches": [
            "Copilot (AI assistant) - 2023",
            "Azure AI Studio - 2024"
        ],
        "analysis": "Microsoft maintains diverse product portfolio...",
        "confidence": 0.90
    }
}
```

---

## Competitor Scout Agent

**Purpose**: Identify and analyze competitors

**Location**: `src/company_researcher/agents/research/`

### Analysis Areas

| Area | Focus | Output |
|------|-------|--------|
| **Competitors** | Who competes | Company list |
| **Comparison** | How they compare | Strengths/weaknesses |
| **Intensity** | Competitive pressure | High/Medium/Low |
| **Positioning** | Market differentiation | Strategy comparison |

### Output Structure

```python
{
    "competitor": {
        "competitors": [
            {
                "name": "Amazon (AWS)",
                "overlap": "Cloud computing",
                "threat_level": "High",
                "strengths": ["Market leader", "Ecosystem"],
                "weaknesses": ["Enterprise focus"]
            },
            {
                "name": "Google (GCP)",
                "overlap": "Cloud, AI/ML",
                "threat_level": "Medium",
                "strengths": ["AI leadership", "Data capabilities"],
                "weaknesses": ["Enterprise relationships"]
            }
        ],
        "competitive_intensity": "High",
        "differentiators": [
            "Enterprise integration",
            "Hybrid cloud strength",
            "Developer ecosystem"
        ],
        "analysis": "Microsoft faces strong competition from...",
        "confidence": 0.85
    }
}
```

---

## Brand Auditor Agent

**Purpose**: Assess brand perception and reputation

**Location**: `src/company_researcher/agents/specialized/brand_auditor.py`

### Analysis Areas

| Area | Focus | Sources |
|------|-------|---------|
| **Brand Strength** | Recognition, loyalty | Surveys, rankings |
| **Reputation** | Public perception | News, reviews |
| **Sentiment** | Customer sentiment | Social, forums |
| **Issues** | PR challenges | News analysis |

### Output Structure

```python
{
    "brand": {
        "brand_strength": "Strong",
        "brand_value_rank": 3,
        "reputation_score": 78,
        "sentiment": {
            "positive": 0.65,
            "neutral": 0.25,
            "negative": 0.10
        },
        "key_associations": [
            "Innovation", "Enterprise", "Reliability"
        ],
        "recent_issues": [],
        "analysis": "Microsoft brand has transformed significantly..."
    }
}
```

---

## Social Media Agent

**Purpose**: Analyze social media presence and engagement

**Location**: `src/company_researcher/agents/specialized/social_media.py`

### Analysis Areas

| Platform | Metrics | Focus |
|----------|---------|-------|
| **LinkedIn** | Followers, engagement | B2B presence |
| **Twitter/X** | Followers, mentions | Public discourse |
| **YouTube** | Subscribers, views | Content engagement |
| **Reddit** | Sentiment, discussions | Community perception |

### Output Structure

```python
{
    "social_media": {
        "platforms": {
            "linkedin": {
                "followers": "18M+",
                "engagement_rate": "High"
            },
            "twitter": {
                "followers": "14M+",
                "sentiment": "Positive"
            }
        },
        "content_strategy": "Educational, product-focused",
        "engagement_level": "High",
        "community_sentiment": "Generally positive",
        "analysis": "Strong social presence across platforms..."
    }
}
```

---

## Parallel Execution

All specialist agents run in parallel after the Researcher completes:

```
Time
  |
  v
  [Researcher] ─────┬─────> [Financial] ─────┐
                    ├─────> [Market] ────────┼─────> [Synthesizer]
                    ├─────> [Product] ───────┤
                    └─────> [Competitor] ────┘
                                 │
                                 └─ (Parallel execution)
```

### State Handling

```python
# Parallel agents update state concurrently
# Reducers merge updates safely

agent_outputs: Annotated[Dict, merge_dicts]
# Result: {"financial": {...}, "market": {...}, "product": {...}}

total_cost: Annotated[float, add]
# Result: Sum of all agent costs
```

---

**Related Documentation**:
- [Core Agents](../core/)
- [Quality Agents](../quality/)
- [Agent Patterns](../../02-architecture/AGENT_PATTERNS.md)

---

**Last Updated**: December 2024
