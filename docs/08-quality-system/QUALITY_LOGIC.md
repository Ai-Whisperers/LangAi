# Quality System Logic

Detailed documentation of quality scoring algorithms, contradiction detection, and gap analysis.

---

## Quality Module Architecture

```
quality/
├── models.py                    # Core data models
├── quality_checker.py           # Main quality scoring
├── contradiction_detector.py    # Contradiction detection
├── enhanced_contradiction_detector.py  # LLM-enhanced detection
├── cross_source_validator.py    # Multi-source validation
├── gap_detector.py              # Gap identification
├── source_tracker.py            # Source management
├── source_assessor.py           # Source quality scoring
├── confidence_scorer.py         # Fact confidence scoring
├── freshness_tracker.py         # Data freshness assessment
├── fact_extractor.py            # Structured fact extraction
├── source_attribution.py        # Source-to-fact mapping
└── audit_trail.py               # Research provenance
```

---

## Quality Scoring Algorithm

### check_research_quality()

**Location**: `quality/quality_checker.py`

```python
def check_research_quality(
    company_name: str,
    extracted_data: str,
    sources: List[Dict]
) -> Dict:
    """
    Main quality assessment function.

    Returns:
        {
            "quality_score": float,       # 0-100
            "missing_information": List[str],
            "strengths": List[str],
            "recommended_queries": List[str],
            "cost": float,
            "tokens": {"input": int, "output": int}
        }
    """
```

### Scoring Components

| Component | Weight | Points | Criteria |
|-----------|--------|--------|----------|
| **Completeness** | 40% | 0-40 | All sections present |
| **Accuracy** | 30% | 0-30 | Facts supported by sources |
| **Depth** | 30% | 0-30 | Beyond surface-level info |

### Completeness Scoring (0-40 points)

```python
def check_completeness(extracted_data: str) -> int:
    score = 0

    # Company overview present (10 points)
    if has_company_overview(extracted_data):
        score += 10

    # Financial metrics present (10 points)
    if has_financial_metrics(extracted_data):
        score += 10

    # Products/services present (10 points)
    if has_products_services(extracted_data):
        score += 10

    # Competitive analysis present (10 points)
    if has_competitive_info(extracted_data):
        score += 10

    return score
```

### Accuracy Scoring (0-30 points)

```python
def check_accuracy(extracted_data: str, sources: List) -> int:
    score = 0

    # Facts supported by sources (15 points)
    supported_ratio = count_supported_facts(extracted_data, sources)
    score += int(supported_ratio * 15)

    # Numbers/dates specific and verifiable (15 points)
    specificity = measure_specificity(extracted_data)
    score += int(specificity * 15)

    return score
```

### Depth Scoring (0-30 points)

```python
def check_depth(extracted_data: str) -> int:
    score = 0

    # Insightful analysis (15 points)
    insight_quality = assess_insight_quality(extracted_data)
    score += int(insight_quality * 15)

    # Beyond surface-level (15 points)
    depth_level = measure_analysis_depth(extracted_data)
    score += int(depth_level * 15)

    return score
```

---

## Contradiction Detection

### ContradictionDetector

**Location**: `quality/contradiction_detector.py`

```python
class ContradictionDetector:
    """
    Detects conflicting information across agent outputs.
    """

    def detect(self, agent_outputs: Dict) -> List[Contradiction]:
        """
        Main detection method.

        Steps:
        1. Extract claims from all agents
        2. Categorize claims by topic
        3. Compare claims within same topic
        4. Identify contradictions
        5. Assess severity
        """
```

### Contradiction Types

| Type | Example | Detection Method |
|------|---------|------------------|
| **Numeric** | Revenue $198B vs $190B | Value difference > 10% |
| **Temporal** | Founded 1975 vs 1976 | Year mismatch |
| **Categorical** | "Market Leader" vs "Challenger" | Semantic opposition |
| **Directional** | "Growing" vs "Declining" | Trend opposition |
| **Factual** | "Public company" vs "Private" | Boolean contradiction |

### Severity Levels

```python
class ContradictionSeverity(Enum):
    CRITICAL = "critical"  # Core business facts conflict
    HIGH = "high"          # Financial data conflicts
    MEDIUM = "medium"      # Market position conflicts
    LOW = "low"            # Minor detail conflicts
```

### Severity Assignment Logic

```python
def assess_severity(contradiction: Contradiction) -> ContradictionSeverity:
    claim_a, claim_b = contradiction.claims

    # Revenue/valuation conflicts are CRITICAL
    if "revenue" in claim_a.topic or "valuation" in claim_a.topic:
        if value_difference > 0.20:  # >20% difference
            return ContradictionSeverity.CRITICAL
        return ContradictionSeverity.HIGH

    # Market share conflicts are HIGH
    if "market share" in claim_a.topic:
        return ContradictionSeverity.HIGH

    # Employee count, founding date are MEDIUM
    if claim_a.topic in ["employees", "founded", "headquarters"]:
        return ContradictionSeverity.MEDIUM

    # Everything else is LOW
    return ContradictionSeverity.LOW
```

### Resolution Strategies

| Strategy | When Used | Logic |
|----------|-----------|-------|
| `prefer_recent` | Dated sources | Use most recent source |
| `prefer_authoritative` | Mixed sources | Official > News > Blog |
| `prefer_primary` | Multiple layers | Original > Quoted |
| `average` | Numeric data | Average close values |
| `flag` | Can't resolve | Mark for manual review |

```python
class ResolutionStrategy(Enum):
    PREFER_RECENT = "prefer_recent"
    PREFER_AUTHORITATIVE = "prefer_authoritative"
    PREFER_PRIMARY = "prefer_primary"
    AVERAGE = "average"
    FLAG = "flag"
```

---

## Gap Detection

### detect_gaps()

**Location**: Implicit in quality_checker.py

```python
def detect_gaps(state: Dict) -> List[str]:
    """
    Identify missing critical information.

    Returns list of gap descriptions.
    """
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

### Gap Categories

| Category | Required Fields | Priority |
|----------|----------------|----------|
| **Financial** | revenue, growth, margins | Critical |
| **Market** | market_size, market_share, position | High |
| **Product** | products_list, key_features | High |
| **Competitive** | competitors, advantages | Medium |
| **Strategic** | opportunities, risks | Medium |
| **Operational** | employees, locations | Low |

### Gap-to-Query Mapping

```python
def generate_gap_queries(company: str, gaps: List[str]) -> List[str]:
    """
    Generate search queries to fill detected gaps.
    """
    queries = []

    gap_templates = {
        "revenue": "{company} revenue financial results 2024",
        "growth_rate": "{company} revenue growth year over year",
        "market_share": "{company} market share industry position",
        "market_size": "{company} total addressable market TAM",
        "competitors": "{company} competitors competitive landscape",
        "products": "{company} products services offerings",
        "employees": "{company} employee count headcount",
    }

    for gap in gaps:
        for key, template in gap_templates.items():
            if key in gap.lower():
                queries.append(template.format(company=company))
                break

    return queries
```

---

## Source Quality Assessment

### SourceQualityAssessor

**Location**: `quality/source_assessor.py`

```python
class SourceQualityAssessor:
    """
    Assess source reliability and authority.
    """

    def assess(self, source: Dict) -> SourceQuality:
        """
        Returns:
            SourceQuality with tier and score
        """
```

### Source Tiers

| Tier | Examples | Trust Score |
|------|----------|-------------|
| **Tier 1** | Official filings (SEC, company IR) | 95-100 |
| **Tier 2** | Major news (Reuters, Bloomberg, WSJ) | 80-90 |
| **Tier 3** | Industry publications (TechCrunch, Forbes) | 70-80 |
| **Tier 4** | General news (local newspapers) | 50-70 |
| **Tier 5** | Blogs, social media | 20-50 |

### Domain Classification

```python
SOURCE_CLASSIFICATIONS = {
    # Tier 1: Official/Primary
    "sec.gov": {"tier": 1, "type": "regulatory"},
    "investor.": {"tier": 1, "type": "official"},
    "ir.": {"tier": 1, "type": "official"},

    # Tier 2: Major Financial News
    "reuters.com": {"tier": 2, "type": "news"},
    "bloomberg.com": {"tier": 2, "type": "news"},
    "wsj.com": {"tier": 2, "type": "news"},
    "ft.com": {"tier": 2, "type": "news"},

    # Tier 3: Tech/Business Publications
    "techcrunch.com": {"tier": 3, "type": "publication"},
    "forbes.com": {"tier": 3, "type": "publication"},
    "businessinsider.com": {"tier": 3, "type": "publication"},

    # Tier 4: General News
    "default": {"tier": 4, "type": "news"},

    # Tier 5: Low Authority
    "medium.com": {"tier": 5, "type": "blog"},
    "substack.com": {"tier": 5, "type": "blog"},
}
```

---

## Confidence Scoring

### ConfidenceScorer

**Location**: `quality/confidence_scorer.py`

```python
class ConfidenceScorer:
    """
    Score confidence level for extracted facts.
    """

    def score(self, fact: Dict, sources: List) -> ScoredFact:
        """
        Multi-factor confidence scoring.

        Factors:
        1. Source count (multiple sources = higher)
        2. Source quality (tier 1/2 = higher)
        3. Recency (newer = higher for financial)
        4. Specificity (exact numbers = higher)
        5. Corroboration (cross-source match = higher)
        """
```

### Confidence Factors

```python
@dataclass
class ConfidenceFactors:
    source_count: float      # 0-1 (normalized by expected count)
    source_quality: float    # 0-1 (average tier score)
    recency: float           # 0-1 (days since publication)
    specificity: float       # 0-1 (vague vs precise)
    corroboration: float     # 0-1 (agreement across sources)

    def calculate_confidence(self) -> float:
        """
        Weighted average of factors.
        """
        weights = {
            "source_count": 0.15,
            "source_quality": 0.25,
            "recency": 0.20,
            "specificity": 0.15,
            "corroboration": 0.25,
        }

        score = (
            self.source_count * weights["source_count"] +
            self.source_quality * weights["source_quality"] +
            self.recency * weights["recency"] +
            self.specificity * weights["specificity"] +
            self.corroboration * weights["corroboration"]
        )

        return min(1.0, max(0.0, score))
```

### Confidence Levels

```python
class ConfidenceLevel(Enum):
    VERY_HIGH = "very_high"   # >= 0.90
    HIGH = "high"             # >= 0.75
    MEDIUM = "medium"         # >= 0.50
    LOW = "low"               # >= 0.25
    VERY_LOW = "very_low"     # < 0.25
```

---

## Freshness Tracking

### FreshnessTracker

**Location**: `quality/freshness_tracker.py`

```python
class FreshnessTracker:
    """
    Assess data freshness by type.
    """

    def assess(self, data: Dict, data_type: DataType) -> FreshnessAssessment:
        """
        Freshness varies by data type.
        """
```

### Freshness Thresholds

| Data Type | Fresh | Acceptable | Stale |
|-----------|-------|------------|-------|
| **Stock Price** | < 1 day | < 7 days | > 7 days |
| **Quarterly Financials** | < 3 months | < 6 months | > 6 months |
| **Annual Revenue** | < 12 months | < 18 months | > 18 months |
| **Employee Count** | < 6 months | < 12 months | > 12 months |
| **Market Share** | < 6 months | < 12 months | > 12 months |
| **Company Overview** | < 12 months | < 24 months | > 24 months |
| **Leadership** | < 3 months | < 6 months | > 6 months |

```python
FRESHNESS_THRESHOLDS = {
    DataType.STOCK_PRICE: FreshnessThreshold(
        fresh_days=1,
        acceptable_days=7,
        stale_days=30
    ),
    DataType.QUARTERLY_FINANCIALS: FreshnessThreshold(
        fresh_days=90,
        acceptable_days=180,
        stale_days=365
    ),
    DataType.ANNUAL_REVENUE: FreshnessThreshold(
        fresh_days=365,
        acceptable_days=540,
        stale_days=730
    ),
    # ... etc
}
```

---

## Cross-Source Validation

### CrossSourceValidator

**Location**: `quality/cross_source_validator.py`

```python
class CrossSourceValidator:
    """
    Validate facts across multiple sources.
    """

    def validate(self, facts: List[Fact], sources: List[Source]) -> ValidationResult:
        """
        Cross-reference facts against sources.

        Returns:
            ValidationResult with:
            - validated_facts: Facts confirmed by 2+ sources
            - unvalidated_facts: Facts from single source
            - conflicts: Facts with contradicting sources
        """
```

### Validation Logic

```python
def validate_fact(fact: Fact, sources: List[Source]) -> ValidationStatus:
    """
    Determine validation status for a fact.
    """
    supporting_sources = find_supporting_sources(fact, sources)
    contradicting_sources = find_contradicting_sources(fact, sources)

    if len(supporting_sources) >= 2 and len(contradicting_sources) == 0:
        return ValidationStatus.VALIDATED

    if len(supporting_sources) >= 1 and len(contradicting_sources) == 0:
        return ValidationStatus.SINGLE_SOURCE

    if len(contradicting_sources) > 0:
        if len(supporting_sources) > len(contradicting_sources):
            return ValidationStatus.LIKELY_VALID
        else:
            return ValidationStatus.CONFLICTED

    return ValidationStatus.UNVALIDATED
```

---

## Quality Integration with Workflow

### Workflow Integration Points

```
Workflow Node          Quality Module Used
─────────────────────────────────────────────
analyze_node       →   source_assessor
extract_data_node  →   fact_extractor, confidence_scorer
check_quality_node →   quality_checker, gap_detector, contradiction_detector
synthesizer_node   →   cross_source_validator
save_report_node   →   audit_trail
```

### Quality State Fields

```python
# Fields populated by quality modules
state = {
    "quality_score": float,           # From quality_checker
    "missing_info": List[str],        # From gap_detector
    "contradictions": List[Dict],     # From contradiction_detector
    "source_quality_scores": Dict,    # From source_assessor
    "fact_confidence": Dict,          # From confidence_scorer
    "validation_results": Dict,       # From cross_source_validator
}
```

---

## Configuration Options

### Quality Config Parameters

```yaml
# research_config.yaml
quality:
  threshold: 85.0              # Minimum passing score
  min_sections: 6              # Required report sections
  require_financials: true     # Financials mandatory?

gap_filling:
  enabled: true
  max_iterations: 2
  min_improvement: 5           # Min score increase per iteration

contradiction:
  detection_enabled: true
  auto_resolve: true
  resolution_strategy: prefer_recent

source_assessment:
  min_sources: 5               # Minimum sources for research
  tier_weights:
    tier_1: 1.0
    tier_2: 0.8
    tier_3: 0.6
    tier_4: 0.4
    tier_5: 0.2

freshness:
  strict_mode: false           # Reject stale data?
  warning_threshold_days: 365
```

---

**Related Documentation**:
- [Workflow Logic](../04-workflows/WORKFLOW_LOGIC.md)
- [Agent Contracts](../03-agents/AGENT_CONTRACTS.md)
- [Configuration](../06-configuration/README.md)

---

**Last Updated**: December 2024
