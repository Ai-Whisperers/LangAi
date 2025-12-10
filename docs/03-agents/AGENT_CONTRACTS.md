# Agent Input/Output Contracts

Formal specification of input requirements, output formats, and side effects for all agents.

---

## Contract Format

Each agent contract follows this structure:

```
AGENT: agent_name
PURPOSE: What the agent does
INPUT: Required state fields
OUTPUT: State fields returned
SIDE_EFFECTS: External calls made
COST: Token/API costs incurred
```

---

## Core Agents

### ResearcherAgent

```yaml
AGENT: researcher
PURPOSE: Generate targeted search queries based on company name and gaps

INPUT:
  company_name: str          # Required
  missing_info: List[str]    # Optional - gaps from previous iteration
  iteration_count: int       # Current iteration number

OUTPUT:
  search_queries: List[str]  # 5-8 targeted queries
  detected_region: str       # "US", "BRAZIL", "MEXICO", etc.
  detected_language: str     # "EN", "PT", "ES"

SIDE_EFFECTS: None (rule-based)

COST: $0.00 (no LLM calls)

CONFIG:
  researcher_max_tokens: 500
  researcher_temperature: 0.7
```

**Query Generation Logic**:
```python
# Iteration 0: General queries
queries = [
    f"{company_name} company overview",
    f"{company_name} revenue financial results",
    f"{company_name} products services",
    f"{company_name} competitors market share",
    f"{company_name} recent news"
]

# Iteration 1+: Gap-filling queries based on missing_info
if "revenue" in missing_info:
    queries.append(f"{company_name} annual revenue 2024")
if "market share" in missing_info:
    queries.append(f"{company_name} market position ranking")
```

---

### AnalystAgent

```yaml
AGENT: analyst
PURPOSE: Analyze search results and extract key information

INPUT:
  company_name: str
  search_results: List[Dict]  # Raw search results

OUTPUT:
  notes: List[str]            # Analysis notes (markdown)
  total_cost: float           # LLM cost incurred
  total_tokens: Dict          # {input: int, output: int}

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01-0.02 per call

CONFIG:
  analyst_max_tokens: 1000
  analyst_temperature: 0.1
```

---

### SynthesizerAgent

```yaml
AGENT: synthesizer
PURPOSE: Combine outputs from specialist agents into coherent report

INPUT:
  company_name: str
  agent_outputs: Dict         # Outputs from all agents
    financial: Dict
    market: Dict
    product: Dict

OUTPUT:
  company_overview: str       # Synthesized markdown
  key_metrics: Dict           # Extracted metrics
  products_services: List[str]
  competitors: List[str]
  key_insights: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01-0.02 per call

CONFIG:
  synthesizer_max_tokens: 1500
  synthesizer_temperature: 0.1
```

---

## Specialist Agents

### FinancialAgent

```yaml
AGENT: financial
PURPOSE: Extract and analyze financial metrics

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.financial:
    revenue: str              # e.g., "$198B (2024)"
    revenue_growth: str       # e.g., "7% YoY"
    gross_margin: str         # e.g., "69%"
    operating_margin: str     # e.g., "41%"
    net_margin: str           # e.g., "35%"
    market_cap: str           # e.g., "$2.8T"
    funding: str              # For private companies
    financial_health: str     # "STRONG/MODERATE/WEAK"
    analysis: str             # Detailed analysis text

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01 per call

CONFIG:
  financial_max_tokens: 800
  financial_temperature: 0.0  # Deterministic for numbers
```

---

### EnhancedFinancialAgent

```yaml
AGENT: enhanced_financial
PURPOSE: Deep financial analysis with multiple data sources

INPUT:
  company_name: str
  search_results: List[Dict]
  financial_data: Dict        # From yfinance/Alpha Vantage

OUTPUT:
  agent_outputs.enhanced_financial:
    revenue_analysis: str
    profitability_analysis: str
    balance_sheet_strength: str
    cash_flow_analysis: str
    valuation_assessment: str
    risk_assessment: str
    financial_summary: str

SIDE_EFFECTS:
  - Anthropic API call (1 message)
  - yfinance API call (optional)
  - Alpha Vantage API call (optional)

COST: ~$0.015 per call

CONFIG:
  enhanced_financial_max_tokens: 1200
```

---

### InvestmentAnalystAgent

```yaml
AGENT: investment_analyst
PURPOSE: Generate investment thesis and recommendation

INPUT:
  company_name: str
  research_data: Dict         # All available research

OUTPUT:
  agent_outputs.investment_analyst:
    investment_thesis: str
    business_quality: Dict
      moat_strength: str      # "WIDE/NARROW/NONE"
      management_quality: str
      business_model: str
    growth_assessment: Dict
      historical_growth: str
      future_drivers: List[str]
      growth_stage: str       # "EARLY/GROWTH/MATURE/DECLINING"
    risk_analysis: Dict
      business_risks: List[str]
      financial_risks: List[str]
      risk_level: str         # "LOW/MODERATE/HIGH/CRITICAL"
    valuation: Dict
      current_multiples: Dict
      peer_comparison: str
      verdict: str            # "UNDERVALUED/FAIR/OVERVALUED"
    recommendation: Dict
      rating: str             # "STRONG BUY" to "STRONG SELL"
      key_factors: List[str]
      catalysts: List[str]
      monitoring_checklist: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.02-0.03 per call

CONFIG:
  investment_analyst_max_tokens: 2500
  investment_analyst_temperature: 0.1
```

---

### MarketAgent

```yaml
AGENT: market
PURPOSE: Analyze market position and competitive landscape

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.market:
    market_share: str         # e.g., "35% domestic, 12% global"
    market_position: str      # e.g., "#1 in cloud, #2 in OS"
    market_size: str          # TAM estimate
    competitors: List[str]    # Competitor names
    competitive_advantages: List[str]
    market_trends: List[str]
    analysis: str

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01 per call

CONFIG:
  market_max_tokens: 800
  market_temperature: 0.0
```

---

### EnhancedMarketAgent

```yaml
AGENT: enhanced_market
PURPOSE: Comprehensive market sizing and industry analysis

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.enhanced_market:
    market_sizing:
      tam: str                # Total Addressable Market
      sam: str                # Serviceable Available Market
      som: str                # Serviceable Obtainable Market
      penetration: str
    industry_trends:
      growing: List[str]
      declining: List[str]
      emerging: List[str]
    regulatory_landscape: Dict
    competitive_dynamics: Dict
    customer_intelligence: Dict
    market_summary: str

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.015 per call

CONFIG:
  enhanced_market_max_tokens: 1200
```

---

### CompetitorScoutAgent

```yaml
AGENT: competitor_scout
PURPOSE: Deep competitive intelligence analysis

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.competitor_scout:
    landscape_overview: Dict
      industry: str
      competitor_count: int
      intensity: str          # "LOW/MODERATE/HIGH/INTENSE"
    direct_competitors: List[Dict]
      name: str
      market_position: str
      strengths: List[str]
      weaknesses: List[str]
      threat_level: str       # "CRITICAL/HIGH/MEDIUM/LOW"
    indirect_competitors: List[str]
    emerging_threats: List[str]
    positioning_map: str
    competitive_advantages: Dict
    strategic_recommendations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.015 per call

CONFIG:
  competitor_scout_max_tokens: 1500
```

---

### ProductAgent

```yaml
AGENT: product
PURPOSE: Analyze products, services, and technology

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.product:
    products: List[str]       # Product names
    services: List[str]       # Service offerings
    key_features: List[str]
    technology_stack: List[str]
    recent_launches: List[str]
    product_strategy: str
    analysis: str

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01 per call

CONFIG:
  product_max_tokens: 1000
```

---

## Quality Agents

### LogicCriticAgent

```yaml
AGENT: logic_critic
PURPOSE: Evaluate research quality and identify contradictions

INPUT:
  company_name: str
  research_summary: str       # Synthesized research
  fact_count: int
  contradiction_count: int
  gap_count: int
  quality_score: float

OUTPUT:
  agent_outputs.logic_critic:
    verification_status: str
    contradiction_analysis: str
    gap_assessment: str
    confidence_assessment: str
    recommendations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01 per call

CONFIG:
  logic_critic_max_tokens: 800
  logic_critic_temperature: 0.0  # Strict evaluation
```

---

### QualityCheckerAgent

```yaml
AGENT: quality_checker
PURPOSE: Score research quality and identify gaps

INPUT:
  company_name: str
  extracted_data: str
  sources: List[Dict]

OUTPUT:
  quality_score: float        # 0-100
  missing_information: List[str]
  strengths: List[str]
  recommended_queries: List[str]
  cost: float
  tokens: Dict

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.01 per call

SCORING COMPONENTS:
  completeness: 0-40 points
    - company_overview: 10 points
    - financial_metrics: 10 points
    - products_services: 10 points
    - competitive_analysis: 10 points
  accuracy: 0-30 points
    - source_support: 15 points
    - specificity: 15 points
  depth: 0-30 points
    - insight_quality: 15 points
    - beyond_surface: 15 points
```

---

## Specialized Agents

### BrandAuditorAgent

```yaml
AGENT: brand_auditor
PURPOSE: Comprehensive brand health analysis

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.brand_auditor:
    brand_identity: Dict
    brand_perception: Dict
      sentiment: str          # "POSITIVE/NEUTRAL/NEGATIVE/MIXED"
    brand_positioning: Dict
    brand_equity: Dict
    brand_strength: Dict
      score: int              # 0-100
      rating: str             # "DOMINANT/STRONG/MODERATE/WEAK/EMERGING"
      trend: str              # "IMPROVING/STABLE/DECLINING"
    recommendations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.02 per call

CONFIG:
  brand_auditor_max_tokens: 2000
```

---

### SocialMediaAgent

```yaml
AGENT: social_media
PURPOSE: Analyze social media presence and engagement

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.social_media:
    platform_presence: Dict   # Per platform metrics
    content_strategy: Dict
    engagement_analysis: Dict
    competitive_comparison: Dict
    social_score: int         # 0-100
    recommendations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.015 per call

CONFIG:
  social_media_max_tokens: 1500
```

---

### SalesIntelligenceAgent

```yaml
AGENT: sales_intelligence
PURPOSE: Generate B2B sales insights and lead qualification

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.sales_intelligence:
    company_snapshot: Dict
    lead_qualification: Dict
      lead_score: str         # "HOT/WARM/COOL/COLD"
      buying_stage: str
    decision_makers: Dict
    pain_points: List[str]
    buying_triggers: List[str]
    engagement_strategy: Dict
    account_score: int        # 0-100

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.02 per call

CONFIG:
  sales_intelligence_max_tokens: 1800
```

---

## Research Agents

### DeepResearchAgent

```yaml
AGENT: deep_research
PURPOSE: Multi-iteration comprehensive research

INPUT:
  company_name: str
  depth: str                  # "QUICK/STANDARD/COMPREHENSIVE"
  iteration: int
  max_iterations: int
  search_results: List[Dict]
  existing_facts: List[Dict]
  gaps: List[str]

OUTPUT:
  agent_outputs.deep_research:
    key_facts: List[Dict]
      fact: str
      category: str
      confidence: str
      source: str
    cross_validation: Dict
    research_gaps: List[str]
    follow_up_queries: List[str]
    confidence_assessment: Dict
    key_findings: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1-2 messages)

COST: ~$0.02-0.04 per iteration

CONFIG:
  deep_research_max_tokens: 2000
  deep_research_temperature: 0.0
```

---

### ReasoningAgent

```yaml
AGENT: reasoning
PURPOSE: Apply structured reasoning frameworks

INPUT:
  company_name: str
  reasoning_type: str         # "ANALYTICAL/STRATEGIC/COMPARATIVE"
  research_data: Dict

OUTPUT:
  agent_outputs.reasoning:
    key_observations: List[str]
    pattern_analysis: str
    reasoning_analysis: str
    inferences: List[Dict]
      inference: str
      confidence: str
    conclusions: List[str]
    limitations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1-3 messages)

COST: ~$0.02-0.05 per call

CONFIG:
  reasoning_max_tokens: 2000
  reasoning_temperature: 0.1
```

---

## ESG Agent

### ESGAgent

```yaml
AGENT: esg
PURPOSE: Environmental, Social, Governance analysis

INPUT:
  company_name: str
  search_results: List[Dict]

OUTPUT:
  agent_outputs.esg:
    environmental: Dict
      score: int
      initiatives: List[str]
      risks: List[str]
    social: Dict
      score: int
      initiatives: List[str]
      risks: List[str]
    governance: Dict
      score: int
      board_composition: str
      risks: List[str]
    overall_esg_score: int    # 0-100
    rating: str               # "A" to "F"
    controversies: List[str]
    recommendations: List[str]

SIDE_EFFECTS:
  - Anthropic API call (1 message)

COST: ~$0.015 per call

CONFIG:
  esg_max_tokens: 1500
```

---

## Output Reducer Behavior

### Parallel Agent Execution

When agents run in parallel (Phase 4+), outputs are merged using reducers:

```python
# Multiple agents return simultaneously
agent_a_output = {"agent_outputs": {"financial": {...}}}
agent_b_output = {"agent_outputs": {"market": {...}}}
agent_c_output = {"agent_outputs": {"product": {...}}}

# merge_dicts reducer combines them
final_state["agent_outputs"] = {
    "financial": {...},
    "market": {...},
    "product": {...}
}
```

### Cost Accumulation

```python
# Each agent adds to total cost
agent_a_output = {"total_cost": 0.01}
agent_b_output = {"total_cost": 0.012}
agent_c_output = {"total_cost": 0.008}

# add reducer sums them
final_state["total_cost"] = 0.030
```

---

**Related Documentation**:
- [Workflow Logic](../04-workflows/WORKFLOW_LOGIC.md)
- [State Management](../07-state-management/README.md)
- [Configuration](../06-configuration/README.md)

---

**Last Updated**: December 2024
