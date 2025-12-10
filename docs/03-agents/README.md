# Agent Documentation

This section documents all AI agents in the Company Researcher system.

## Agent Overview

The system uses specialized AI agents, each focused on a specific research domain. Agents run in parallel where possible to maximize efficiency.

```
                         AGENTS
                           |
        +------------------+------------------+
        |                  |                  |
     CORE              SPECIALIST         QUALITY
        |                  |                  |
   Researcher         Financial          Logic Critic
   Analyst            Market
   Synthesizer        Product
                      Competitor Scout
                      Brand Auditor
                      Social Media
```

## Agent Categories

### Core Agents

Core agents handle the main research workflow:

| Agent | Purpose | Location |
|-------|---------|----------|
| **Researcher** | Query generation, search execution | `agents/core/researcher.py` |
| **Analyst** | Data summarization and extraction | `agents/core/analyst.py` |
| **Synthesizer** | Report generation and combination | `agents/core/synthesizer.py` |

[Detailed Core Agent Documentation](core/)

### Specialist Agents

Specialist agents analyze specific business domains:

| Agent | Purpose | Location |
|-------|---------|----------|
| **Financial** | Revenue, profitability, metrics | `agents/financial/` |
| **Market** | Market position, trends, share | `agents/market/` |
| **Product** | Products, technology, roadmap | `agents/specialized/` |
| **Competitor Scout** | Competitive intelligence | `agents/research/` |
| **Brand Auditor** | Brand perception, reputation | `agents/specialized/` |
| **Social Media** | Social presence analysis | `agents/specialized/` |

[Detailed Specialist Agent Documentation](specialists/)

### Quality Agents

Quality agents ensure research accuracy:

| Agent | Purpose | Location |
|-------|---------|----------|
| **Logic Critic** | Fact verification, contradiction detection | `agents/quality/` |
| **Quality Checker** | Completeness scoring | `quality/` |

[Detailed Quality Agent Documentation](quality/)

## Agent Execution Flow

```
1. RESEARCHER AGENT
   Input: company_name
   Output: search_queries, search_results, sources

2. PARALLEL SPECIALISTS (Fan-Out)
   ├── FINANCIAL AGENT
   │   Input: search_results
   │   Output: revenue, profitability, financial_health
   │
   ├── MARKET AGENT
   │   Input: search_results
   │   Output: market_size, trends, position
   │
   ├── PRODUCT AGENT
   │   Input: search_results
   │   Output: products, technology, roadmap
   │
   └── COMPETITOR AGENT
       Input: search_results
       Output: competitors, competitive_intensity

3. SYNTHESIZER AGENT (Fan-In)
   Input: all agent_outputs
   Output: comprehensive_report, quality_score

4. LOGIC CRITIC AGENT
   Input: comprehensive_report
   Output: verified_facts, contradictions, gaps
```

## Agent Communication

Agents communicate through shared state:

```python
# Each agent returns partial state updates
return {
    "agent_outputs": {
        "financial": {
            "revenue": "$198B",
            "analysis": "Strong growth..."
        }
    },
    "total_cost": 0.05
}
```

State updates are merged using reducers:

```python
# Parallel agent outputs merge automatically
agent_outputs: Annotated[Dict, merge_dicts]
```

## Agent Implementation Patterns

### Pattern 1: BaseSpecialistAgent

For agents with complex parsing:

```python
class FinancialAgent(BaseSpecialistAgent[FinancialResult]):
    def _get_prompt(self, company: str, results: List) -> str:
        return f"Analyze financials for {company}..."

    def _parse_analysis(self, response: str) -> FinancialResult:
        return parse_financial_data(response)
```

### Pattern 2: @agent_node Decorator

For simpler agents:

```python
@agent_node(agent_name="market", max_tokens=1500)
def market_agent_node(state, logger, client, config):
    # Agent logic
    return {"agent_outputs": {"market": result}}
```

### Pattern 3: Custom Class

For agents with external integrations:

```python
class EnhancedFinancialAgent:
    def __init__(self, config):
        self.llm = get_anthropic_client(config)
        self.alpha_vantage = AlphaVantageClient(config)
        self.yfinance = YFinanceClient()

    def analyze(self, company: str) -> FinancialResult:
        # Combine LLM + external data
        pass
```

## Agent Configuration

Each agent has configurable parameters:

```python
# config.py
researcher_max_tokens: int = 1000
researcher_temperature: float = 0.0

financial_max_tokens: int = 2000
financial_temperature: float = 0.0

market_max_tokens: int = 1500
market_temperature: float = 0.0
```

## Creating a New Agent

### Step 1: Define Result Type

```python
@dataclass
class MyAgentResult:
    analysis: str
    metrics: Dict[str, Any]
    confidence: float
```

### Step 2: Implement Agent

```python
@agent_node(agent_name="my_agent", max_tokens=1500)
def my_agent_node(
    state: OverallState,
    logger: Logger,
    client: Anthropic,
    config: ResearchConfig
) -> Dict[str, Any]:
    # Get data from state
    company = state["company_name"]
    results = state["search_results"]

    # Build prompt
    prompt = f"""
    Analyze {company} for [specific aspect].

    Search Results:
    {format_results(results)}

    Provide:
    1. Analysis
    2. Key metrics
    3. Confidence score
    """

    # Call LLM
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    result = parse_response(response)

    # Return state update
    return {
        "agent_outputs": {"my_agent": result},
        "total_cost": calculate_cost(response.usage)
    }
```

### Step 3: Register in Workflow

```python
# workflows/parallel_agent_research.py
workflow.add_node("my_agent", my_agent_node)
workflow.add_edge("researcher", "my_agent")
workflow.add_edge("my_agent", "synthesizer")
```

### Step 4: Add Configuration

```python
# config.py
my_agent_max_tokens: int = 1500
my_agent_temperature: float = 0.0
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [Core Agents](core/) | Researcher, Analyst, Synthesizer |
| [Specialist Agents](specialists/) | Financial, Market, Product, etc. |
| [Quality Agents](quality/) | Logic Critic, Quality Checker |
| [Agent Patterns](../02-architecture/AGENT_PATTERNS.md) | Implementation patterns |

---

**Last Updated**: December 2024
