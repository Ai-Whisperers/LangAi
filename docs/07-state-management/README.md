# State Management

This section documents how state flows through the Company Researcher system.

## Overview

The system uses **LangGraph state** to manage data flow between agents. State is:

- **Typed**: Using TypedDict for type safety
- **Annotated**: Using reducers for parallel updates
- **Immutable**: Each node returns partial updates
- **Tracked**: Cost and token counting

```
State Flow:
INPUT --> [Agent 1] --> State Update --> [Agent 2] --> State Update --> OUTPUT
              |                              |
              +------ Parallel Updates ------+
```

## State Schema

**Location**: `src/company_researcher/state.py`

### OverallState Definition

```python
from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add

class OverallState(TypedDict, total=False):
    # ============ INPUT ============
    company_name: str

    # ============ RESEARCH DATA ============
    search_queries: List[str]
    search_results: Annotated[List[Dict], add]  # Parallel safe

    # ============ COMPANY INFORMATION ============
    company_overview: Optional[str]
    key_metrics: Optional[Dict]
    products_services: Optional[List]
    competitors: Optional[List]
    recent_news: Optional[List]

    # ============ AGENT OUTPUTS ============
    agent_outputs: Annotated[Dict[str, Any], merge_dicts]

    # ============ QUALITY METRICS ============
    quality_score: Optional[float]
    gaps_detected: Optional[List[str]]
    contradictions: Optional[List[Dict]]

    # ============ CONTROL FLOW ============
    iteration_count: int
    current_phase: Optional[str]

    # ============ COST TRACKING ============
    total_cost: Annotated[float, add]
    total_tokens: Annotated[Dict, add_tokens]

    # ============ OUTPUT ============
    sources: Annotated[List[str], add]
    comprehensive_report: Optional[str]
    report_path: Optional[str]
```

## State Categories

### Input State

Initial state provided by the user:

```python
initial_state = {
    "company_name": "Microsoft"
}
```

### Research State

Data collected during research:

```python
{
    "search_queries": [
        "Microsoft company overview",
        "Microsoft financials 2024",
        "Microsoft products services"
    ],
    "search_results": [
        {"title": "...", "url": "...", "content": "..."},
        # ... more results
    ]
}
```

### Agent Output State

Results from each agent:

```python
{
    "agent_outputs": {
        "researcher": {
            "queries_generated": 3,
            "results_found": 25
        },
        "financial": {
            "revenue": "$198B",
            "growth": "7%",
            "analysis": "..."
        },
        "market": {
            "market_share": "35%",
            "position": "Leader",
            "analysis": "..."
        },
        "product": {
            "products": ["Azure", "Office 365"],
            "analysis": "..."
        }
    }
}
```

### Quality State

Quality metrics:

```python
{
    "quality_score": 88.5,
    "gaps_detected": [],
    "contradictions": []
}
```

### Control State

Workflow control:

```python
{
    "iteration_count": 1,
    "current_phase": "synthesizer"
}
```

### Cost State

Token and cost tracking:

```python
{
    "total_cost": 0.0386,
    "total_tokens": {
        "input": 8500,
        "output": 3200
    }
}
```

### Output State

Final output:

```python
{
    "comprehensive_report": "# Microsoft Research Report\n\n...",
    "report_path": "outputs/research/microsoft/00_full_report.md",
    "sources": ["https://...", "https://..."]
}
```

## State Reducers

Reducers handle concurrent state updates from parallel agents.

### Built-in: `add`

For lists and numbers:

```python
from operator import add

# Lists get concatenated
search_results: Annotated[List[Dict], add]
# [a, b] + [c, d] = [a, b, c, d]

# Numbers get summed
total_cost: Annotated[float, add]
# 0.02 + 0.03 = 0.05
```

### Custom: `merge_dicts`

For agent outputs:

```python
def merge_dicts(existing: Dict, new: Dict) -> Dict:
    """Merge dictionaries, new values override existing."""
    result = existing.copy()
    result.update(new)
    return result

agent_outputs: Annotated[Dict[str, Any], merge_dicts]
# {"a": 1} + {"b": 2} = {"a": 1, "b": 2}
```

### Custom: `add_tokens`

For token counting:

```python
def add_tokens(existing: Dict, new: Dict) -> Dict:
    """Add token counts."""
    return {
        "input": existing.get("input", 0) + new.get("input", 0),
        "output": existing.get("output", 0) + new.get("output", 0)
    }

total_tokens: Annotated[Dict, add_tokens]
# {"input": 100, "output": 50} + {"input": 200, "output": 100}
# = {"input": 300, "output": 150}
```

## State Updates

### Agent Return Pattern

Each agent returns a partial state update:

```python
def financial_agent_node(state: OverallState) -> Dict:
    # Do analysis
    result = analyze_financials(state["company_name"])

    # Return partial update
    return {
        "agent_outputs": {
            "financial": result
        },
        "total_cost": result.cost,
        "total_tokens": {
            "input": result.input_tokens,
            "output": result.output_tokens
        }
    }
```

### Parallel Updates

When agents run in parallel, updates are merged using reducers:

```python
# Agent 1 returns:
{"agent_outputs": {"financial": {...}}, "total_cost": 0.02}

# Agent 2 returns:
{"agent_outputs": {"market": {...}}, "total_cost": 0.03}

# Merged state:
{
    "agent_outputs": {
        "financial": {...},  # From Agent 1
        "market": {...}      # From Agent 2
    },
    "total_cost": 0.05  # Sum of both
}
```

## State Access Patterns

### Reading State

```python
def my_agent_node(state: OverallState) -> Dict:
    # Access input
    company = state["company_name"]

    # Access with default
    results = state.get("search_results", [])

    # Access nested
    financial = state.get("agent_outputs", {}).get("financial", {})

    # Check existence
    if "quality_score" in state:
        score = state["quality_score"]
```

### Writing State

```python
def my_agent_node(state: OverallState) -> Dict:
    # Always return a dict with updates
    return {
        "my_field": "value",
        "agent_outputs": {
            "my_agent": {"analysis": "..."}
        }
    }
```

### Conditional Logic

```python
def should_iterate(state: OverallState) -> str:
    """Conditional edge based on state."""
    quality = state.get("quality_score", 0)
    iterations = state.get("iteration_count", 0)

    if quality >= 85:
        return "finish"
    if iterations >= 2:
        return "finish"
    return "iterate"
```

## State Lifecycle

```
1. INITIALIZATION
   state = {"company_name": "Microsoft"}

2. RESEARCHER NODE
   state += {
       "search_queries": [...],
       "search_results": [...],
       "sources": [...],
       "iteration_count": 1
   }

3. PARALLEL SPECIALISTS
   state += {
       "agent_outputs": {
           "financial": {...},
           "market": {...},
           "product": {...}
       },
       "total_cost": 0.08
   }

4. SYNTHESIZER
   state += {
       "comprehensive_report": "...",
       "quality_score": 88
   }

5. QUALITY CHECK
   state += {
       "gaps_detected": [],
       "contradictions": []
   }

6. SAVE REPORT
   state += {
       "report_path": "outputs/..."
   }

7. FINAL STATE
   {
       "company_name": "Microsoft",
       "search_queries": [...],
       "search_results": [...],
       "agent_outputs": {...},
       "comprehensive_report": "...",
       "quality_score": 88,
       "total_cost": 0.08,
       "report_path": "outputs/..."
   }
```

## State Persistence

### Checkpointing

```python
from langgraph.checkpoint import MemorySaver

# Enable checkpointing
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Run with thread ID
config = {"configurable": {"thread_id": "research-123"}}
result = app.invoke(initial_state, config)

# Resume from checkpoint
result = app.invoke(None, config)  # Continues from last state
```

### State Snapshots

```python
# Get state at any point
snapshot = app.get_state(config)
print(f"Current node: {snapshot.next}")
print(f"State: {snapshot.values}")

# Update state manually
app.update_state(config, {"quality_score": 90})
```

## Debugging State

### Logging State Changes

```python
import structlog
logger = structlog.get_logger()

def debug_state(state: OverallState, node_name: str):
    logger.info(
        "state_update",
        node=node_name,
        company=state.get("company_name"),
        iteration=state.get("iteration_count"),
        quality=state.get("quality_score"),
        cost=state.get("total_cost")
    )
```

### State Visualization

In LangGraph Studio:
1. Run workflow
2. Click on any node
3. Inspect "State In" and "State Out"

---

**Related Documentation**:
- [Workflow Documentation](../04-workflows/)
- [Agent Documentation](../03-agents/)
- [Architecture](../02-architecture/)

---

**Last Updated**: December 2024
