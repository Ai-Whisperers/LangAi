# Quality System

This section documents the quality assurance system that ensures research accuracy.

## Overview

The quality system ensures research meets quality standards through:

1. **Quality Scoring**: Evaluate completeness and accuracy
2. **Contradiction Detection**: Find conflicting information
3. **Gap Detection**: Identify missing critical data
4. **Iterative Improvement**: Automatically improve until threshold met

```
QUALITY SYSTEM
     |
     +-- Quality Checker (Scoring)
     |
     +-- Contradiction Detector (Verification)
     |
     +-- Gap Detector (Completeness)
     |
     +-- Iteration Engine (Improvement)
```

## Quality Score

The system calculates a quality score (0-100) based on multiple factors:

### Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | 30% | All required sections present |
| **Financial Data** | 25% | Revenue, growth, profitability |
| **Market Data** | 20% | Position, trends, share |
| **Source Quality** | 15% | Diverse, authoritative sources |
| **Coherence** | 10% | No internal contradictions |

### Calculation

```python
def calculate_quality_score(state: OverallState) -> float:
    scores = {
        "completeness": check_completeness(state),
        "financial_data": check_financial_data(state),
        "market_data": check_market_data(state),
        "source_quality": check_sources(state),
        "coherence": check_coherence(state)
    }

    weights = {
        "completeness": 0.30,
        "financial_data": 0.25,
        "market_data": 0.20,
        "source_quality": 0.15,
        "coherence": 0.10
    }

    return sum(scores[k] * weights[k] for k in scores)
```

### Threshold

Default quality threshold: **85%**

Research passes when `quality_score >= 85`. Below this, the system iterates.

## Completeness Check

Verifies all required sections are present:

### Required Sections

| Section | Weight | Required Fields |
|---------|--------|-----------------|
| Executive Summary | 15% | Key findings, recommendation |
| Company Overview | 15% | Background, business model |
| Financial Analysis | 20% | Revenue, profitability, growth |
| Market Position | 15% | Market size, share, position |
| Products/Services | 15% | Product list, descriptions |
| Competitive Analysis | 10% | Competitors, differentiation |
| Strategic Outlook | 10% | Opportunities, risks |

### Implementation

```python
def check_completeness(state: OverallState) -> float:
    """Score 0-100 for section completeness."""
    sections = {
        "company_overview": state.get("company_overview"),
        "financials": state.get("agent_outputs", {}).get("financial"),
        "market": state.get("agent_outputs", {}).get("market"),
        "products": state.get("products_services"),
        "competitors": state.get("competitors"),
    }

    present = sum(1 for v in sections.values() if v)
    return (present / len(sections)) * 100
```

## Financial Data Check

Validates financial metrics are present:

### Required Metrics

| Metric | Priority | Example |
|--------|----------|---------|
| Revenue | Critical | $198B |
| Revenue Growth | High | 7% YoY |
| Gross Margin | High | 69% |
| Operating Margin | Medium | 41% |
| Net Margin | Medium | 35% |
| Market Cap | Medium | $2.8T |

### Scoring

```python
def check_financial_data(state: OverallState) -> float:
    """Score 0-100 for financial data quality."""
    financial = state.get("agent_outputs", {}).get("financial", {})

    metrics = {
        "revenue": 25,          # 25 points
        "revenue_growth": 20,   # 20 points
        "gross_margin": 15,     # 15 points
        "operating_margin": 15, # 15 points
        "net_margin": 15,       # 15 points
        "market_cap": 10,       # 10 points
    }

    score = 0
    for metric, points in metrics.items():
        if financial.get(metric):
            score += points

    return score
```

## Contradiction Detection

Identifies conflicting information across agents.

### Contradiction Types

| Type | Example | Severity |
|------|---------|----------|
| **Numeric** | "Revenue $198B" vs "$190B" | High |
| **Temporal** | "Founded 1975" vs "1976" | Medium |
| **Categorical** | "Leader" vs "Challenger" | Medium |
| **Directional** | "Growing" vs "Declining" | High |

### Detection Process

```python
class ContradictionDetector:
    def detect(self, agent_outputs: Dict) -> List[Contradiction]:
        contradictions = []

        # Extract all claims
        claims = self._extract_claims(agent_outputs)

        # Compare pairwise
        for i, claim_a in enumerate(claims):
            for claim_b in claims[i+1:]:
                if self._are_contradictory(claim_a, claim_b):
                    contradictions.append(Contradiction(
                        claim_a=claim_a,
                        claim_b=claim_b,
                        severity=self._assess_severity(claim_a, claim_b)
                    ))

        return contradictions

    def _are_contradictory(self, a: Claim, b: Claim) -> bool:
        # Same topic but different values
        if a.topic == b.topic and a.value != b.value:
            return True
        return False
```

### Resolution Strategies

| Strategy | When Used |
|----------|-----------|
| `prefer_recent` | Use most recent source |
| `prefer_authoritative` | Use most authoritative source |
| `average` | Average numeric values |
| `flag` | Highlight for manual review |

## Gap Detection

Identifies missing critical information.

### Gap Categories

| Category | Examples |
|----------|----------|
| **Financial** | Missing revenue, missing growth rate |
| **Market** | Missing market share, missing position |
| **Product** | Missing product list, missing tech stack |
| **Competitive** | Missing competitors, missing SWOT |

### Detection Logic

```python
def detect_gaps(state: OverallState) -> List[str]:
    gaps = []

    # Financial gaps
    financial = state.get("agent_outputs", {}).get("financial", {})
    if not financial.get("revenue"):
        gaps.append("Missing revenue data")
    if not financial.get("growth_rate"):
        gaps.append("Missing growth rate")
    if not financial.get("profitability"):
        gaps.append("Missing profitability metrics")

    # Market gaps
    market = state.get("agent_outputs", {}).get("market", {})
    if not market.get("market_size"):
        gaps.append("Missing market size")
    if not market.get("market_share"):
        gaps.append("Missing market share")

    # Product gaps
    if not state.get("products_services"):
        gaps.append("Missing products/services list")

    # Competitor gaps
    if not state.get("competitors"):
        gaps.append("Missing competitor analysis")

    return gaps
```

## Iterative Improvement

When quality score is below threshold, the system iterates:

### Iteration Flow

```
1. Calculate quality score
2. IF score < 85% AND iterations < 2:
   a. Detect gaps
   b. Generate targeted queries for gaps
   c. Execute additional searches
   d. Re-run analysis
   e. Recalculate quality
3. ELSE:
   Save report
```

### Gap-Targeted Queries

```python
def generate_gap_queries(company: str, gaps: List[str]) -> List[str]:
    """Generate search queries to fill gaps."""
    queries = []

    for gap in gaps:
        if "revenue" in gap.lower():
            queries.append(f"{company} revenue financial results 2024")
        elif "market share" in gap.lower():
            queries.append(f"{company} market share industry position")
        elif "competitors" in gap.lower():
            queries.append(f"{company} competitors competitive landscape")
        # ... more gap-specific queries

    return queries
```

### Iteration Limits

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 2 | Maximum improvement attempts |
| `quality_threshold` | 85 | Minimum acceptable score |
| `min_improvement` | 5 | Minimum score increase per iteration |

## Quality Metrics Output

The system outputs detailed quality metrics:

```json
{
    "quality_score": 88,
    "quality_breakdown": {
        "completeness": 95,
        "financial_data": 90,
        "market_data": 85,
        "source_quality": 80,
        "coherence": 90
    },
    "iterations": 1,
    "gaps_detected": [],
    "gaps_filled": ["revenue data", "market share"],
    "contradictions_found": 1,
    "contradictions_resolved": 1,
    "sources_count": 24,
    "source_diversity": {
        "news": 8,
        "official": 5,
        "financial": 6,
        "analysis": 5
    }
}
```

## Configuration

```yaml
# research_config.yaml

quality:
  threshold: 85.0
  min_sections: 6
  require_financials: true

gap_filling:
  enabled: true
  max_iterations: 2
  min_improvement: 5

contradiction:
  detection_enabled: true
  auto_resolve: true
  resolution_strategy: prefer_recent
```

---

**Related Documentation**:
- [Quality Agents](../03-agents/quality/)
- [Workflows](../04-workflows/)
- [Configuration](../06-configuration/)

---

**Last Updated**: December 2024
