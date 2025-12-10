# Quality Agents

Quality agents ensure research accuracy through fact verification, contradiction detection, and completeness scoring.

## Overview

```
QUALITY SYSTEM
    |
    +-- Logic Critic Agent: Fact verification, contradiction detection
    |
    +-- Quality Checker: Completeness scoring, gap detection
    |
    +-- Enhanced Contradiction Detector: Advanced conflict resolution
```

## Logic Critic Agent

**Purpose**: Verify facts and detect contradictions in research

**Location**: `src/company_researcher/agents/quality/`

### Responsibilities

1. **Fact Extraction**: Identify factual claims from all agents
2. **Contradiction Detection**: Find conflicting information
3. **Gap Analysis**: Identify missing critical information
4. **Confidence Scoring**: Rate reliability of claims
5. **Resolution Suggestions**: Recommend how to resolve conflicts

### Input

```python
{
    "company_name": "Microsoft",
    "agent_outputs": {
        "financial": {"revenue": "$198B", ...},
        "market": {"market_share": "35%", ...}
    },
    "comprehensive_report": "..."
}
```

### Output

```python
{
    "logic_critic": {
        "facts_extracted": [
            {
                "claim": "Revenue is $198B",
                "source_agent": "financial",
                "confidence": 0.95,
                "verification_status": "verified"
            },
            {
                "claim": "Market share is 35%",
                "source_agent": "market",
                "confidence": 0.80,
                "verification_status": "plausible"
            }
        ],
        "contradictions": [
            {
                "type": "numeric_conflict",
                "claim_1": {"agent": "financial", "value": "220,000 employees"},
                "claim_2": {"agent": "analyst", "value": "200,000 employees"},
                "severity": "medium",
                "resolution": "Use most recent source (financial)"
            }
        ],
        "gaps": [
            "Missing R&D spending data",
            "No customer acquisition cost mentioned"
        ],
        "overall_quality": 88,
        "recommendations": [
            "Verify employee count from official source",
            "Add R&D investment figures"
        ]
    }
}
```

### Contradiction Types

| Type | Description | Severity |
|------|-------------|----------|
| `numeric_conflict` | Different numbers for same metric | Medium-High |
| `temporal_conflict` | Inconsistent dates or timeframes | Medium |
| `categorical_conflict` | Different classifications | Low-Medium |
| `directional_conflict` | Opposite conclusions | High |
| `source_conflict` | Sources disagree | Medium |

### Quality Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Factual Accuracy | 30% | Claims are verifiable |
| Internal Consistency | 25% | No contradictions |
| Completeness | 25% | All key areas covered |
| Source Quality | 20% | Authoritative, recent sources |

---

## Quality Checker

**Purpose**: Score overall research quality and identify gaps

**Location**: `src/company_researcher/quality/quality_checker.py`

### Scoring System

The quality score (0-100) is calculated from:

```python
def calculate_quality_score(state: OverallState) -> float:
    scores = {
        "completeness": check_completeness(state),      # 30%
        "financial_data": check_financial_data(state),  # 25%
        "market_data": check_market_data(state),        # 20%
        "source_quality": check_sources(state),         # 15%
        "coherence": check_coherence(state),            # 10%
    }

    weights = {
        "completeness": 0.30,
        "financial_data": 0.25,
        "market_data": 0.20,
        "source_quality": 0.15,
        "coherence": 0.10,
    }

    return sum(scores[k] * weights[k] for k in scores)
```

### Completeness Check

Required sections for passing score:

| Section | Required | Weight |
|---------|----------|--------|
| Executive Summary | Yes | 15% |
| Company Overview | Yes | 15% |
| Financial Analysis | Yes | 20% |
| Market Position | Yes | 15% |
| Product/Services | Yes | 15% |
| Competitive Analysis | Yes | 10% |
| Strategic Outlook | Yes | 10% |

### Gap Detection

```python
def detect_gaps(state: OverallState) -> List[str]:
    gaps = []

    # Financial gaps
    if not state.get("key_metrics", {}).get("revenue"):
        gaps.append("Missing revenue data")
    if not state.get("key_metrics", {}).get("growth_rate"):
        gaps.append("Missing growth rate")

    # Market gaps
    if not state.get("agent_outputs", {}).get("market", {}).get("market_share"):
        gaps.append("Missing market share data")

    # Product gaps
    if not state.get("products_services"):
        gaps.append("Missing products/services list")

    return gaps
```

---

## Enhanced Contradiction Detector

**Purpose**: Advanced contradiction detection with resolution

**Location**: `src/company_researcher/quality/enhanced_contradiction_detector.py`

### Detection Methods

1. **Semantic Comparison**: Compare meaning, not just text
2. **Numeric Range Analysis**: Check if numbers are within expected variance
3. **Temporal Alignment**: Verify dates and timeframes match
4. **Cross-Reference Validation**: Check claims against multiple sources

### Resolution Strategies

| Strategy | When Used | Action |
|----------|-----------|--------|
| `prefer_recent` | Temporal conflict | Use most recent data |
| `prefer_authoritative` | Source conflict | Use most authoritative source |
| `average_values` | Minor numeric conflict | Average the values |
| `flag_for_review` | Major conflict | Highlight for manual review |
| `remove_claim` | Unverifiable | Remove from report |

### Implementation

```python
class EnhancedContradictionDetector:
    def detect(self, report: str, agent_outputs: Dict) -> List[Contradiction]:
        contradictions = []

        # Extract all claims
        claims = self._extract_claims(report, agent_outputs)

        # Compare claims pairwise
        for claim_a, claim_b in combinations(claims, 2):
            if self._are_about_same_topic(claim_a, claim_b):
                if self._are_contradictory(claim_a, claim_b):
                    contradiction = Contradiction(
                        claim_a=claim_a,
                        claim_b=claim_b,
                        severity=self._assess_severity(claim_a, claim_b),
                        resolution=self._suggest_resolution(claim_a, claim_b)
                    )
                    contradictions.append(contradiction)

        return contradictions

    def resolve(self, contradiction: Contradiction) -> Resolution:
        strategy = contradiction.resolution
        if strategy == "prefer_recent":
            return self._resolve_by_recency(contradiction)
        elif strategy == "prefer_authoritative":
            return self._resolve_by_authority(contradiction)
        # ... more strategies
```

---

## Quality-Driven Iteration

The quality system drives the iteration loop:

```
Research
    |
    v
Quality Check
    |
    +---> Score >= 85%? ---> YES ---> Save Report
    |
    +---> Score < 85%? ---> NO ---> Iterations < 2?
                                        |
                                        +---> YES ---> Iterate
                                        |
                                        +---> NO ---> Save Report
```

### Iteration Process

1. **Detect Gaps**: Identify missing information
2. **Generate Targeted Queries**: Create search queries for gaps
3. **Execute Additional Searches**: Fill in missing data
4. **Re-analyze**: Run agents on new data
5. **Re-score**: Calculate new quality score

```python
def should_iterate(state: OverallState) -> str:
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)

    if quality_score >= 85:
        return "finish"

    if iteration_count >= 2:
        logger.warning(f"Max iterations reached, quality={quality_score}")
        return "finish"

    return "iterate"
```

---

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
    "contradictions_found": 1,
    "contradictions_resolved": 1,
    "fact_confidence": {
        "high": 15,
        "medium": 8,
        "low": 2
    }
}
```

---

**Related Documentation**:
- [Core Agents](../core/)
- [Specialist Agents](../specialists/)
- [Quality System](../../08-quality-system/)

---

**Last Updated**: December 2024
