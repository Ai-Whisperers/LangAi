# System Architecture

This section describes the architecture of the Company Researcher system.

## Architecture Overview

The Company Researcher is a **multi-agent research system** built on LangGraph that orchestrates specialized AI agents to analyze companies. The system uses a **fan-out/fan-in pattern** for parallel execution with **quality-driven iteration**.

```
+------------------------------------------------------------------+
|                        COMPANY RESEARCHER                         |
+------------------------------------------------------------------+
|                                                                   |
|  INPUT                    PROCESSING                   OUTPUT     |
|  ======                   ==========                   ======     |
|                                                                   |
|  Company   +-----------+  +------------+  +---------+  Markdown   |
|  Name  --> | Researcher| ->| Parallel   |->| Quality |-> Report   |
|            |   Agent   |  | Specialists|  | Check   |             |
|            +-----------+  +------------+  +---------+  metrics    |
|                 |              |              |          .json    |
|                 v              v              v                   |
|            +-----------+  +-----------+  +-----------+            |
|            |  Tavily   |  | Financial |  |  Logic    |            |
|            |  Search   |  |   Agent   |  |  Critic   |            |
|            +-----------+  +-----------+  +-----------+            |
|                           |           |                           |
|                           | Market    |                           |
|                           | Agent     |                           |
|                           +-----------+                           |
|                           |           |                           |
|                           | Product   |                           |
|                           | Agent     |                           |
|                           +-----------+                           |
|                                                                   |
+------------------------------------------------------------------+
```

## Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Agents** | `src/company_researcher/agents/` | AI workers for specific tasks |
| **Workflows** | `src/company_researcher/workflows/` | LangGraph orchestration |
| **State** | `src/company_researcher/state.py` | Shared state management |
| **Config** | `src/company_researcher/config.py` | Configuration management |
| **Integrations** | `src/company_researcher/integrations/` | External API clients |
| **Quality** | `src/company_researcher/quality/` | Quality assurance |
| **LLM** | `src/company_researcher/llm/` | LLM client utilities |

## Architecture Principles

### 1. Multi-Agent Specialization

Each agent has a specific domain:

```
RESEARCHER -----> Query generation, source discovery
FINANCIAL ------> Revenue, profitability, metrics
MARKET ---------> Market position, trends, share
PRODUCT --------> Products, technology, roadmap
COMPETITOR -----> Competitive analysis
SYNTHESIZER ----> Report generation
LOGIC CRITIC ---> Fact verification
```

### 2. Parallel Execution

Specialist agents run concurrently via fan-out pattern:

```
         Researcher
             |
    +--------+--------+--------+
    |        |        |        |
Financial  Market  Product  Competitor
    |        |        |        |
    +--------+--------+--------+
             |
         Synthesizer
```

### 3. Quality-Driven Iteration

```
Research -> Quality Check -> Below 85%? -> Iterate
                 |
                 +-> Above 85%? -> Save Report
```

### 4. State-Based Communication

Agents communicate through shared state with reducers:

```python
# State updates merge automatically
{"agent_outputs": {"financial": {...}}}  # From Financial Agent
{"agent_outputs": {"market": {...}}}     # From Market Agent
# Result: {"agent_outputs": {"financial": {...}, "market": {...}}}
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [System Design](SYSTEM_DESIGN.md) | Detailed system design |
| [Data Flow](DATA_FLOW.md) | Data flow through system |
| [Agent Patterns](AGENT_PATTERNS.md) | Agent implementation patterns |
| [LangGraph Integration](LANGGRAPH.md) | LangGraph usage details |
| [State Management](STATE_MANAGEMENT.md) | State architecture |
| [diagrams/](diagrams/) | Architecture diagrams |

## Technology Decisions

### Why LangGraph?

| Feature | Benefit |
|---------|---------|
| State machines | Predictable agent orchestration |
| Parallel execution | Faster research (fan-out/fan-in) |
| Conditional edges | Quality-driven iteration |
| Built-in persistence | Checkpoint and resume |
| Visual debugging | LangGraph Studio |

### Why Claude (Anthropic)?

| Feature | Benefit |
|---------|---------|
| Long context | 200K tokens for comprehensive analysis |
| Structured output | Reliable JSON/markdown generation |
| Low hallucination | Accurate company research |
| Cost effective | $3/$15 per 1M tokens |

### Why Tavily Search?

| Feature | Benefit |
|---------|---------|
| LLM-optimized | Clean, structured results |
| No scraping | Direct content access |
| Fast | Low latency responses |
| Reliable | High uptime |

## System Layers

```
+------------------------------------------------------------------+
|                        PRESENTATION LAYER                         |
|  CLI | LangGraph Studio | Python API | REST API (future)         |
+------------------------------------------------------------------+
|                        ORCHESTRATION LAYER                        |
|  LangGraph Workflows | State Management | Quality Control         |
+------------------------------------------------------------------+
|                         AGENT LAYER                               |
|  Researcher | Financial | Market | Product | Synthesizer | Critic |
+------------------------------------------------------------------+
|                       INTEGRATION LAYER                           |
|  Tavily | DuckDuckGo | yfinance | Alpha Vantage | FMP | News     |
+------------------------------------------------------------------+
|                        FOUNDATION LAYER                           |
|  LLM Client | Configuration | Logging | Observability            |
+------------------------------------------------------------------+
```

## Key Design Patterns

### 1. Reducer Pattern (State Updates)

```python
# Custom reducer for parallel agent outputs
def merge_dicts(existing: Dict, new: Dict) -> Dict:
    result = existing.copy()
    result.update(new)
    return result

# Usage in state
agent_outputs: Annotated[Dict, merge_dicts]
```

### 2. Agent Node Pattern

```python
@agent_node(agent_name="financial", max_tokens=2000)
def financial_agent_node(state, logger, client, config):
    # Agent implementation
    return {"agent_outputs": {"financial": result}}
```

### 3. Conditional Edge Pattern

```python
def should_iterate(state):
    if state["quality_score"] >= 85:
        return "save_report"
    if state["iteration_count"] >= 2:
        return "save_report"
    return "iterate"

workflow.add_conditional_edges("quality_check", should_iterate)
```

## Security Architecture

| Layer | Protection |
|-------|------------|
| API Keys | Environment variables, never in code |
| Input | Pydantic validation |
| External | Timeout protection |
| Cost | Budget limits and tracking |
| Rate | Configurable throttling |

## Scalability Considerations

| Aspect | Current | Scalable Path |
|--------|---------|---------------|
| Concurrency | Single workflow | Multiple workers |
| State | In-memory | Redis/persistent |
| Search | Rate-limited | Distributed queue |
| Reports | Local files | Cloud storage |

## Next Steps

- [System Design](SYSTEM_DESIGN.md) - Deep dive into design
- [Data Flow](DATA_FLOW.md) - Understand data movement
- [Agent Patterns](AGENT_PATTERNS.md) - Implementation patterns

---

**Last Updated**: December 2024
