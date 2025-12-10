# System Design

Detailed design documentation for the Company Researcher system.

## Design Goals

1. **Accuracy**: Produce factually correct company research
2. **Speed**: Complete research in 2-5 minutes
3. **Cost Efficiency**: Target ~$0.08 per research
4. **Quality**: Achieve 85%+ quality scores consistently
5. **Extensibility**: Easy to add new agents and integrations

## System Components

### 1. Core Research Engine

```
src/company_researcher/
├── agents/           # AI agents
│   ├── core/         # Researcher, Analyst, Synthesizer
│   ├── financial/    # Financial analysis
│   ├── market/       # Market analysis
│   ├── specialized/  # Domain-specific
│   ├── research/     # Deep research
│   └── quality/      # Quality assurance
├── workflows/        # LangGraph workflows
├── state.py          # State definitions
├── config.py         # Configuration
├── types.py          # Type definitions
└── prompts.py        # Prompt templates
```

### 2. External Integrations

```
src/company_researcher/integrations/
├── tavily_client.py        # Web search
├── alpha_vantage.py        # Stock data
├── financial_modeling_prep.py  # Financial data
├── finnhub.py              # Real-time quotes
├── gnews.py                # News
├── reddit_client.py        # Social sentiment
├── github_client.py        # Tech analysis
└── sec_edgar.py            # SEC filings
```

### 3. Quality System

```
src/company_researcher/quality/
├── quality_checker.py           # Score calculation
├── contradiction_detector.py    # Fact verification
├── gap_detector.py              # Missing info detection
└── enhanced_contradiction_detector.py  # Advanced QA
```

## Agent Design

### Agent Hierarchy

```
BaseAgent (Abstract)
    |
    +-- BaseSpecialistAgent[T] (Generic)
    |       |
    |       +-- FinancialAgent
    |       +-- MarketAgent
    |       +-- ProductAgent
    |       +-- BrandAuditorAgent
    |       +-- SocialMediaAgent
    |
    +-- CoreAgent
            |
            +-- ResearcherAgent
            +-- AnalystAgent
            +-- SynthesizerAgent
            +-- LogicCriticAgent
```

### Agent Interface

```python
class BaseSpecialistAgent(Generic[T], ABC):
    """Base class for specialist analysis agents."""

    def __init__(self, config: ResearchConfig):
        self.config = config
        self.client = get_anthropic_client(config)

    @abstractmethod
    def _get_prompt(self, company: str, results: List[Dict]) -> str:
        """Return the analysis prompt."""
        pass

    @abstractmethod
    def _parse_analysis(self, response: str) -> T:
        """Parse LLM response into structured result."""
        pass

    def analyze(self, company: str, results: List[Dict]) -> T:
        """Run analysis and return structured result."""
        prompt = self._get_prompt(company, results)
        response = self.client.messages.create(...)
        return self._parse_analysis(response)
```

### Agent Node Decorator

```python
@agent_node(
    agent_name="financial",
    max_tokens=2000,
    temperature=0.0
)
def financial_agent_node(
    state: OverallState,
    logger: Logger,
    client: Anthropic,
    config: ResearchConfig
) -> Dict[str, Any]:
    """Financial analysis agent node."""
    # Implementation
    return {"agent_outputs": {"financial": result}}
```

## Workflow Design

### Main Workflow Graph

```python
# workflows/parallel_agent_research.py

workflow = StateGraph(OverallState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("financial", financial_agent_node)
workflow.add_node("market", market_agent_node)
workflow.add_node("product", product_agent_node)
workflow.add_node("competitor", competitor_scout_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("quality_check", quality_check_node)
workflow.add_node("save_report", save_report_node)

# Entry point
workflow.set_entry_point("researcher")

# Parallel fan-out from researcher
workflow.add_edge("researcher", "financial")
workflow.add_edge("researcher", "market")
workflow.add_edge("researcher", "product")
workflow.add_edge("researcher", "competitor")

# Fan-in to synthesizer
workflow.add_edge("financial", "synthesizer")
workflow.add_edge("market", "synthesizer")
workflow.add_edge("product", "synthesizer")
workflow.add_edge("competitor", "synthesizer")

# Quality check with conditional iteration
workflow.add_edge("synthesizer", "quality_check")
workflow.add_conditional_edges(
    "quality_check",
    should_iterate,
    {
        "iterate": "researcher",
        "finish": "save_report"
    }
)

# End point
workflow.set_finish_point("save_report")

# Compile
app = workflow.compile()
```

### State Schema

```python
class OverallState(TypedDict, total=False):
    # Input
    company_name: str

    # Research data
    search_queries: List[str]
    search_results: Annotated[List[Dict], add]

    # Company information
    company_overview: Optional[str]
    key_metrics: Optional[Dict]
    products_services: Optional[List]
    competitors: Optional[List]

    # Agent outputs (parallel safe)
    agent_outputs: Annotated[Dict[str, Any], merge_dicts]

    # Quality metrics
    quality_score: Optional[float]
    gaps_detected: Optional[List[str]]
    contradictions: Optional[List[Dict]]

    # Control flow
    iteration_count: int

    # Cost tracking
    total_cost: Annotated[float, add]
    total_tokens: Annotated[Dict, add_tokens]

    # Output
    sources: Annotated[List[str], add]
    report_path: Optional[str]
```

## Data Flow

### Research Pipeline

```
1. INPUT
   └── company_name: "Microsoft"

2. RESEARCHER NODE
   ├── Generate 3-5 search queries
   ├── Execute Tavily searches
   ├── Explore company domains
   └── Output: search_results[], sources[]

3. PARALLEL SPECIALISTS (Fan-Out)
   ├── FINANCIAL: revenue, profitability, metrics
   ├── MARKET: position, trends, share
   ├── PRODUCT: offerings, tech stack
   └── COMPETITOR: competitors, intensity

4. SYNTHESIZER (Fan-In)
   ├── Wait for all specialists
   ├── Combine agent_outputs
   ├── Generate comprehensive report
   └── Calculate quality_score

5. QUALITY CHECK
   ├── Evaluate completeness
   ├── Detect contradictions
   ├── Identify gaps
   └── Decision: iterate or finish

6. CONDITIONAL BRANCH
   ├── IF quality >= 85%: save_report
   └── ELSE IF iterations < 2: researcher (iterate)

7. SAVE REPORT
   ├── Generate markdown files
   ├── Save metrics.json
   └── Return report_path
```

## Configuration Design

### Hierarchical Configuration

```python
@dataclass
class ResearchConfig:
    # API Keys (from environment)
    anthropic_api_key: str
    tavily_api_key: Optional[str]

    # Model settings
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 4096

    # Search settings
    num_search_queries: int = 3
    max_search_results: int = 10
    search_strategy: str = "free_first"

    # Quality settings
    quality_threshold: float = 85.0
    max_iterations: int = 2

    # Agent-specific settings (50+)
    researcher_max_tokens: int = 1000
    financial_max_tokens: int = 2000
    market_max_tokens: int = 1500
    # ... more settings

    # Output settings
    output_dir: str = "outputs/research"
    report_formats: List[str] = ["md"]
```

### Configuration Loading

```python
# Priority: CLI args > Environment > YAML > Defaults
config = ResearchConfig.from_env()
config = config.merge_yaml("research_config.yaml")
config = config.merge_cli(args)
```

## Error Handling

### Retry Strategy

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10),
    retry=retry_if_exception_type(RateLimitError)
)
async def call_llm(prompt: str) -> str:
    """Call LLM with retry on rate limits."""
    pass
```

### Fallback Chain

```python
async def search(query: str) -> List[Dict]:
    """Search with fallback chain."""
    try:
        return await tavily_search(query)
    except TavilyError:
        return await duckduckgo_search(query)
    except Exception:
        return []  # Empty results, don't fail
```

### Graceful Degradation

```python
def analyze_company(company: str) -> Report:
    """Analyze with graceful degradation."""
    report = Report()

    # Each section can fail independently
    report.financials = safe_call(analyze_financials, company)
    report.market = safe_call(analyze_market, company)
    report.products = safe_call(analyze_products, company)

    return report
```

## Cost Optimization

### Token Budgeting

```python
# Per-agent token limits
AGENT_TOKEN_BUDGETS = {
    "researcher": 1000,
    "financial": 2000,
    "market": 1500,
    "product": 1500,
    "synthesizer": 3000,
}

# Total budget per research
MAX_TOTAL_TOKENS = 15000  # ~$0.10 at current prices
```

### Cost Calculation

```python
def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-3-5-sonnet-20241022"
) -> float:
    """Calculate LLM cost in USD."""
    PRICES = {
        "claude-3-5-sonnet-20241022": (0.003, 0.015),  # per 1K tokens
        "claude-3-haiku-20240307": (0.00025, 0.00125),
    }
    input_price, output_price = PRICES[model]
    return (input_tokens * input_price + output_tokens * output_price) / 1000
```

## Observability Design

### Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "agent_completed",
    agent="financial",
    company="Microsoft",
    cost=0.05,
    duration_ms=2340
)
```

### Tracing

```python
# LangSmith integration
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "company-researcher"

# AgentOps integration
import agentops
agentops.init()
```

### Metrics

```python
# metrics.json output
{
    "company": "Microsoft",
    "quality_score": 88,
    "iterations": 1,
    "total_cost": 0.0386,
    "total_tokens": {
        "input": 8500,
        "output": 3200
    },
    "duration_seconds": 154,
    "agents_executed": ["researcher", "financial", "market", "synthesizer"],
    "sources_count": 24
}
```

## Extension Points

### Adding a New Agent

1. Create agent class in `agents/`
2. Define result dataclass
3. Implement `_get_prompt()` and `_parse_analysis()`
4. Register in workflow graph
5. Add configuration parameters

### Adding a New Data Source

1. Create client in `integrations/`
2. Add API key to configuration
3. Create enhanced agent using the source
4. Add fallback handling

### Adding a New Output Format

1. Extend `output/pipeline.py`
2. Add format handlers
3. Update configuration options
4. Add to default formats

---

**Last Updated**: December 2024
