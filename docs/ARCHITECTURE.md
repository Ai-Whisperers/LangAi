# Company Researcher Architecture

## System Overview

The Company Researcher is a multi-agent research system that analyzes companies using LLM-powered agents orchestrated via LangGraph workflows.

```
                    +------------------+
                    |   User Request   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Research Graph  |
                    |   (LangGraph)    |
                    +--------+---------+
                             |
           +-----------------+-----------------+
           |                 |                 |
           v                 v                 v
    +------------+    +------------+    +------------+
    |  Researcher|    |   Analyst  |    | Synthesizer|
    |   Agent    |    |   Agent    |    |   Agent    |
    +------------+    +------------+    +------------+
           |                 |                 |
           v                 v                 v
    +--------------------------------------------------+
    |              Specialist Agents (Parallel)        |
    +--------------------------------------------------+
    |  Financial  |  Market  |  Brand  |  Social  | ...|
    +--------------------------------------------------+
                             |
                             v
                    +------------------+
                    |  Quality Check   |
                    |  (Contradiction  |
                    |   Detection)     |
                    +------------------+
                             |
                             v
                    +------------------+
                    |  Output Pipeline |
                    |  (Report Gen)    |
                    +------------------+
```

---

## Module Structure

```
src/company_researcher/
├── agents/                 # All agent implementations
│   ├── base/              # Base classes and utilities
│   │   ├── specialist.py  # BaseSpecialistAgent, ParsingMixin
│   │   ├── node.py        # @agent_node decorator
│   │   └── search_formatting.py
│   ├── core/              # Core workflow agents
│   │   ├── researcher.py  # Query generation
│   │   ├── analyst.py     # Data summarization
│   │   └── synthesizer.py # Report synthesis
│   ├── financial/         # Financial analysis agents
│   ├── market/            # Market analysis agents
│   ├── specialized/       # Domain-specific agents
│   ├── research/          # Deep research agents
│   └── quality/           # Quality assurance agents
├── graphs/                # LangGraph workflow definitions
│   └── research_graph.py  # Main research workflow
├── llm/                   # LLM client management
│   ├── client_factory.py  # Anthropic client creation
│   ├── langchain_client.py
│   └── vision.py          # Vision capabilities
├── tools/                 # External tool integrations
│   ├── tavily_search.py   # Web search
│   ├── alpha_vantage_client.py
│   └── sec_edgar_parser.py
├── quality/               # Quality validation
│   ├── contradiction_detector.py
│   └── quality_checker.py
├── output/                # Report generation
│   └── pipeline.py
├── config.py              # Centralized configuration
├── state.py               # Workflow state management
└── types.py               # Centralized type definitions
```

---

## Data Flow

### 1. Research Initiation

```
User Input (company_name)
        |
        v
+------------------+
| ResearchConfig   |  <-- Environment variables, API keys
+------------------+
        |
        v
+------------------+
| OverallState     |  <-- Workflow state container
| - company_name   |
| - search_results |
| - agent_outputs  |
+------------------+
```

### 2. Agent Execution Flow

```
OverallState
     |
     +---> Researcher Agent ---> Generate search queries
     |            |
     |            v
     |     Tavily Search API ---> search_results
     |
     +---> Analyst Agent ---> Summarize results
     |
     +---> Parallel Specialist Agents:
     |       |
     |       +---> Financial Agent
     |       +---> Market Agent
     |       +---> Brand Agent
     |       +---> Social Media Agent
     |       +---> ... (10+ specialists)
     |
     +---> Quality Check ---> Detect contradictions
     |
     +---> Synthesizer Agent ---> Generate final report
     |
     v
Final Report (Markdown/JSON)
```

---

## Agent Architecture Patterns

### Pattern 1: BaseSpecialistAgent

For standard analysis agents that process search results.

```
+--------------------------------+
|     BaseSpecialistAgent[T]     |
+--------------------------------+
| - config: ResearchConfig       |
| - client: Anthropic            |
+--------------------------------+
| + analyze(company, results)    |
| # _get_prompt() [abstract]     |
| # _parse_analysis() [abstract] |
| # _format_search_results()     |
+--------------------------------+
            ^
            |
+--------------------------------+
|     BrandAuditorAgent          |
|     SalesIntelligenceAgent     |
|     SocialMediaAgent           |
+--------------------------------+
```

### Pattern 2: @agent_node Decorator

For simple agents with maximum boilerplate reduction.

```python
@agent_node(
    agent_name="product",
    max_tokens=1000,
    temperature=0.0
)
def product_agent_node(state, logger, client, config, ...):
    # Agent logic here
    ...
```

### Pattern 3: Custom Class

For agents with external API integrations.

```
+--------------------------------+
|    EnhancedFinancialAgent      |
+--------------------------------+
| - search_tool: Callable        |
| - llm_client: Anthropic        |
| - alpha_vantage: AVClient      |
| - sec_edgar: SECParser         |
+--------------------------------+
| + analyze(company, results)    |
+--------------------------------+
```

---

## State Management

### OverallState (TypedDict)

```python
class OverallState(TypedDict, total=False):
    company_name: str           # Target company
    search_results: List[Dict]  # Raw search results
    agent_outputs: Dict[str, Any]  # Per-agent outputs
    total_cost: float           # Accumulated LLM cost
    errors: List[str]           # Error collection
    metadata: Dict[str, Any]    # Workflow metadata
```

### State Updates

Each agent returns a partial state update:

```python
return {
    "agent_outputs": {
        "financial": {
            "revenue": "...",
            "analysis": "...",
            "cost": 0.05
        }
    },
    "total_cost": 0.05
}
```

---

## Configuration Architecture

```python
ResearchConfig (Pydantic BaseSettings)
├── API Keys
│   ├── anthropic_api_key
│   ├── tavily_api_key
│   ├── alpha_vantage_api_key
│   └── langsmith_api_key
├── Model Configuration
│   ├── llm_model
│   ├── llm_temperature
│   └── llm_max_tokens
├── Search Configuration
│   ├── num_search_queries
│   └── max_search_results
├── Agent-Specific Settings (50+)
│   ├── researcher_max_tokens
│   ├── analyst_max_tokens
│   ├── financial_max_tokens
│   └── ...
└── Output Configuration
    ├── output_dir
    └── report_format
```

---

## LLM Client Architecture

```
+------------------+
| client_factory   |
+------------------+
        |
        v
+------------------+
| get_anthropic_   |    Returns configured Anthropic client
| client()         |
+------------------+
        |
        v
+------------------+
| calculate_cost() |    Calculates LLM usage cost
+------------------+
        |
        v
+------------------+
| safe_extract_    |    Safely extracts text from response
| text()           |
+------------------+
```

---

## Quality Assurance Pipeline

```
Agent Outputs
     |
     v
+------------------------+
| ContradictionDetector  |
+------------------------+
| - compare_claims()     |
| - detect_conflicts()   |
| - suggest_resolution() |
+------------------------+
     |
     v
+------------------------+
| QualityChecker         |
+------------------------+
| - check_completeness() |
| - validate_sources()   |
| - score_quality()      |
+------------------------+
     |
     v
Quality Report
```

---

## External Service Integrations

| Service | Module | Purpose |
|---------|--------|---------|
| Anthropic Claude | `llm/client_factory.py` | LLM inference |
| Tavily | `tools/tavily_search.py` | Web search |
| Alpha Vantage | `tools/alpha_vantage_client.py` | Stock data |
| SEC EDGAR | `tools/sec_edgar_parser.py` | Financial filings |
| LangSmith | `config.py` | Observability |
| AgentOps | `config.py` | Agent monitoring |

---

## Workflow Orchestration (LangGraph)

```python
# graphs/research_graph.py

workflow = StateGraph(OverallState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("financial", financial_agent_node)
workflow.add_node("market", market_agent_node)
workflow.add_node("synthesizer", synthesizer_node)

# Define edges
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "parallel_agents")  # Fan-out
workflow.add_edge("parallel_agents", "synthesizer")  # Fan-in
workflow.set_finish_point("synthesizer")

# Compile
app = workflow.compile()
```

---

## Type System (types.py)

All enums and shared types are centralized:

```python
# Domain Enums
BrandStrength, BrandHealth, SentimentCategory
LeadScore, BuyingStage, CompanySize
SocialPlatform, EngagementLevel, ContentStrategy
InvestmentRating, RiskLevel, MoatStrength
ContradictionSeverity, ResolutionStrategy

# Shared Types
SearchResult = TypedDict(...)
AgentOutput = TypedDict(...)
```

---

## Security Considerations

1. **API Key Management**: All keys loaded from environment variables
2. **Input Validation**: Pydantic models validate all configuration
3. **Timeout Protection**: All external calls have configurable timeouts
4. **Cost Tracking**: LLM usage tracked to prevent runaway costs
5. **Rate Limiting**: Search queries throttled per configuration

---

## Extension Points

### Adding a New Agent

1. Choose pattern (BaseSpecialistAgent, decorator, or custom)
2. Define result dataclass
3. Implement agent class/function
4. Register in workflow graph
5. Add configuration parameters

### Adding a New Data Source

1. Create client in `tools/`
2. Add configuration for API keys
3. Create enhanced agent that uses the source
4. Register in workflow

### Adding New Output Formats

1. Extend `output/pipeline.py`
2. Add format handlers
3. Update configuration options
