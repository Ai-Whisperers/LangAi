# Workflow Documentation

This section documents the LangGraph workflows that orchestrate the research system.

## Overview

The Company Researcher uses **LangGraph** for workflow orchestration. LangGraph provides:

- **State machines**: Predictable execution flow
- **Parallel execution**: Fan-out/fan-in patterns
- **Conditional edges**: Dynamic routing
- **Checkpointing**: Resume from interruptions
- **Visual debugging**: LangGraph Studio

## Main Workflow: Parallel Multi-Agent Research

**Location**: `src/company_researcher/workflows/parallel_agent_research.py`

### Workflow Diagram

```
                    +---------------+
                    |    START      |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    |  RESEARCHER   |
                    |    AGENT      |
                    +-------+-------+
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
    +------------+   +------------+   +------------+
    |  FINANCIAL |   |   MARKET   |   |  PRODUCT   |
    |   AGENT    |   |   AGENT    |   |   AGENT    |
    +------+-----+   +------+-----+   +------+-----+
            |               |               |
            +---------------+---------------+
                            |
                            v
                    +---------------+
                    | SYNTHESIZER   |
                    |    AGENT      |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    | LOGIC CRITIC  |
                    |    AGENT      |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    | QUALITY CHECK |
                    +-------+-------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
    +---------------+            +---------------+
    | score >= 85%  |            | score < 85%   |
    | OR iter >= 2  |            | AND iter < 2  |
    +-------+-------+            +-------+-------+
            |                           |
            v                           v
    +---------------+            +---------------+
    | SAVE REPORT   |            |   ITERATE     |
    +-------+-------+            +-------+-------+
            |                           |
            v                           |
    +---------------+                   |
    |     END       |<------------------+
    +---------------+
```

### Workflow Definition

```python
from langgraph.graph import StateGraph, END
from company_researcher.state import OverallState

# Create workflow
workflow = StateGraph(OverallState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("financial", financial_agent_node)
workflow.add_node("market", market_agent_node)
workflow.add_node("product", product_agent_node)
workflow.add_node("competitor", competitor_scout_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("logic_critic", logic_critic_node)
workflow.add_node("quality_check", quality_check_node)
workflow.add_node("save_report", save_report_node)

# Set entry point
workflow.set_entry_point("researcher")

# Parallel edges (fan-out)
workflow.add_edge("researcher", "financial")
workflow.add_edge("researcher", "market")
workflow.add_edge("researcher", "product")
workflow.add_edge("researcher", "competitor")

# Converge edges (fan-in)
workflow.add_edge("financial", "synthesizer")
workflow.add_edge("market", "synthesizer")
workflow.add_edge("product", "synthesizer")
workflow.add_edge("competitor", "synthesizer")

# Sequential edges
workflow.add_edge("synthesizer", "logic_critic")
workflow.add_edge("logic_critic", "quality_check")

# Conditional edge (iteration decision)
workflow.add_conditional_edges(
    "quality_check",
    should_iterate,
    {
        "iterate": "researcher",
        "finish": "save_report"
    }
)

# End point
workflow.add_edge("save_report", END)

# Compile
app = workflow.compile()
```

## Node Definitions

### Researcher Node

```python
def researcher_node(state: OverallState) -> Dict:
    """Generate queries and execute searches."""
    company = state["company_name"]
    iteration = state.get("iteration_count", 0)

    # Generate search queries
    queries = generate_search_queries(company, iteration)

    # Execute searches
    results = execute_searches(queries)

    # Extract sources
    sources = extract_sources(results)

    return {
        "search_queries": queries,
        "search_results": results,
        "sources": sources,
        "iteration_count": iteration + 1
    }
```

### Specialist Node Pattern

```python
@agent_node(agent_name="financial", max_tokens=2000)
def financial_agent_node(
    state: OverallState,
    logger: Logger,
    client: Anthropic,
    config: ResearchConfig
) -> Dict:
    """Analyze company financials."""
    company = state["company_name"]
    results = state["search_results"]

    # Run analysis
    analysis = analyze_financials(company, results, client, config)

    return {
        "agent_outputs": {"financial": analysis},
        "total_cost": analysis.cost
    }
```

### Quality Check Node

```python
def quality_check_node(state: OverallState) -> Dict:
    """Check quality and decide on iteration."""
    # Calculate quality score
    score = calculate_quality_score(state)

    # Detect gaps
    gaps = detect_gaps(state)

    return {
        "quality_score": score,
        "gaps_detected": gaps
    }
```

### Conditional Router

```python
def should_iterate(state: OverallState) -> str:
    """Determine if iteration is needed."""
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)

    # Pass threshold
    if quality_score >= 85:
        return "finish"

    # Max iterations
    if iteration_count >= 2:
        return "finish"

    # Iterate
    return "iterate"
```

## State Management

### State Schema

```python
class OverallState(TypedDict, total=False):
    # Input
    company_name: str

    # Research data
    search_queries: List[str]
    search_results: Annotated[List[Dict], add]  # Parallel safe

    # Company info
    company_overview: Optional[str]
    key_metrics: Optional[Dict]
    products_services: Optional[List]
    competitors: Optional[List]

    # Agent outputs
    agent_outputs: Annotated[Dict[str, Any], merge_dicts]

    # Quality metrics
    quality_score: Optional[float]
    gaps_detected: Optional[List[str]]

    # Control
    iteration_count: int

    # Cost tracking
    total_cost: Annotated[float, add]
    total_tokens: Annotated[Dict, add_tokens]

    # Output
    sources: Annotated[List[str], add]
    report_path: Optional[str]
```

### State Reducers

```python
def add(existing: List, new: List) -> List:
    """Append new items to list."""
    return existing + new

def merge_dicts(existing: Dict, new: Dict) -> Dict:
    """Merge dictionaries."""
    result = existing.copy()
    result.update(new)
    return result

def add_tokens(existing: Dict, new: Dict) -> Dict:
    """Add token counts."""
    return {
        "input": existing.get("input", 0) + new.get("input", 0),
        "output": existing.get("output", 0) + new.get("output", 0)
    }
```

## Running Workflows

### Basic Execution

```python
from company_researcher.workflows import app

# Run research
result = app.invoke({
    "company_name": "Microsoft"
})

print(f"Quality: {result['quality_score']}")
print(f"Report: {result['report_path']}")
```

### With Checkpointing

```python
from langgraph.checkpoint import MemorySaver

# Create checkpointer
checkpointer = MemorySaver()

# Compile with checkpointing
app = workflow.compile(checkpointer=checkpointer)

# Run with thread ID
config = {"configurable": {"thread_id": "research-1"}}
result = app.invoke({"company_name": "Microsoft"}, config)

# Resume if interrupted
result = app.invoke(None, config)  # Continues from checkpoint
```

### Async Execution

```python
import asyncio

async def run_research(company: str):
    result = await app.ainvoke({"company_name": company})
    return result

# Run
result = asyncio.run(run_research("Microsoft"))
```

### Streaming

```python
# Stream events
for event in app.stream({"company_name": "Microsoft"}):
    print(f"Node: {event.get('node')}")
    print(f"Output: {event.get('output')}")
```

## LangGraph Studio

### Configuration

**File**: `langgraph.json`

```json
{
  "dependencies": [
    "."
  ],
  "graphs": {
    "company_research": "./src/graphs/research_graph.py:graph",
    "simple_test": "./src/graphs/simple_graph.py:graph"
  },
  "env": ".env"
}
```

### Starting Studio

```bash
# Install LangGraph Studio
pip install langgraph-studio

# Start server
langgraph studio

# Open browser to http://localhost:8000
```

### Using Studio

1. Select `company_research` graph
2. Enter input: `{"company_name": "Microsoft"}`
3. Click "Run"
4. Watch agents execute in real-time
5. Inspect state at each node

## Available Workflows

| Workflow | Location | Description |
|----------|----------|-------------|
| `parallel_agent_research` | `workflows/parallel_agent_research.py` | Main research workflow |
| `basic_research` | `workflows/basic_research.py` | Simple sequential workflow |
| `comprehensive_research` | `workflows/comprehensive_research.py` | Full-feature research workflow |
| `cache_aware_workflow` | `workflows/cache_aware_workflow.py` | Cache-aware workflow helpers |
| `multi_agent_research` | `workflows/multi_agent_research.py` | Multi-agent workflow variant |

See also: [Workflow Deep Dive](WORKFLOW_DEEP_DIVE.md)

---

**Related Documentation**:
- [Agent Documentation](../03-agents/)
- [State Management](../07-state-management/)
- [LangGraph Studio Guide](LANGGRAPH_STUDIO_GUIDE.md)

---

**Last Updated**: December 2024
