# Implementation Guide

Deep dive into the Company Researcher codebase - how the code works and how to navigate it.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Table of Contents

- [Project Structure](#project-structure)
- [Code Organization](#code-organization)
- [How Workflows Execute](#how-workflows-execute)
- [How Agents Work](#how-agents-work)
- [State Updates and Reducers](#state-updates-and-reducers)
- [Quality Check Logic](#quality-check-logic)
- [Report Generation](#report-generation)
- [Cost Tracking](#cost-tracking)
- [Configuration System](#configuration-system)
- [Error Handling](#error-handling)

---

## Project Structure

```
src/company_researcher/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── state.py                 # State definitions and reducers
├── prompts.py               # LLM prompt templates
│
├── agents/                  # Agent implementations
│   ├── __init__.py
│   ├── base.py             # Base agent utilities
│   ├── researcher.py        # Researcher agent (query + search)
│   ├── financial.py         # Financial specialist
│   ├── market.py            # Market specialist
│   ├── product.py           # Product specialist
│   ├── synthesizer.py       # Synthesis agent
│   └── analyst.py           # Legacy analyst (Phase 1-3)
│
├── quality/                 # Quality checking system
│   ├── __init__.py
│   └── checker.py           # Quality scoring logic
│
├── tools/                   # Tool integrations
│   ├── __init__.py
│   ├── tavily_search.py     # Tavily API wrapper
│   └── claude_client.py     # Claude API wrapper
│
└── workflows/               # LangGraph workflows
    ├── __init__.py
    ├── basic_research.py          # Phase 1: Simple workflow
    ├── multi_agent_research.py    # Phase 3: Sequential specialists
    └── parallel_agent_research.py # Phase 4: Parallel specialists

root/
├── hello_research.py        # Main entry point CLI
├── requirements.txt         # Python dependencies
├── env.example              # Environment template
├── .env                     # Local environment (not committed)
└── outputs/                 # Generated reports
    ├── {company}/
    │   └── report_{timestamp}.md
    └── logs/
        └── PHASE4_VALIDATION_SUMMARY.md
```

---

## Code Organization

### Core Modules

#### config.py
**Purpose**: Centralized configuration management

```python
class ResearchConfig(BaseSettings):
    """Pydantic-based configuration"""

    # API Keys
    anthropic_api_key: str
    tavily_api_key: str

    # Model Settings
    llm_model: str = "claude-3-5-haiku-20241022"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 4000

    # Search Settings
    num_search_queries: int = 5
    search_results_per_query: int = 3

    # Methods
    def validate_api_keys(self) -> None
    def get_model_pricing(self) -> dict
    def calculate_llm_cost(self, input_tokens, output_tokens) -> float
```

**Key Features**:
- Loads from `.env` file via `python-dotenv`
- Validates API keys on instantiation
- Calculates LLM costs based on token usage
- Singleton pattern via `get_config()`

**Usage**:
```python
from company_researcher.config import get_config

config = get_config()
client = Anthropic(api_key=config.anthropic_api_key)
cost = config.calculate_llm_cost(1000, 500)
```

#### state.py
**Purpose**: State management and type definitions

**Key Components**:
1. **InputState**: Workflow input (company_name only)
2. **OverallState**: Complete state with annotations
3. **OutputState**: Final output format
4. **Custom Reducers**: `merge_dicts`, `add_tokens`

**Example State Update**:
```python
# Agent returns state updates:
return {
    "agent_outputs": {"financial": {...}},  # Uses merge_dicts
    "total_cost": 0.01,                     # Uses add
    "total_tokens": {"input": 100, "output": 50}  # Uses add_tokens
}

# LangGraph automatically merges these with existing state
```

#### prompts.py
**Purpose**: Centralized LLM prompt templates

**Prompts Defined**:
- `GENERATE_QUERIES_PROMPT`: Generate search queries
- `ANALYZE_RESULTS_PROMPT`: Analyze search results
- `EXTRACT_DATA_PROMPT`: Extract structured data
- `QUALITY_CHECK_PROMPT`: Score research quality
- `FINANCIAL_ANALYSIS_PROMPT`: Financial extraction

**Pattern**:
```python
GENERATE_QUERIES_PROMPT = """You are a research assistant...

Company: {company_name}

Generate {num_queries} specific search queries...

Output format:
["query 1", "query 2", ...]
"""

# Usage:
prompt = GENERATE_QUERIES_PROMPT.format(
    company_name="Tesla",
    num_queries=5
)
```

---

## How Workflows Execute

### Workflow Creation

**File**: `workflows/parallel_agent_research.py`

```python
def create_parallel_agent_workflow() -> StateGraph:
    """Build the workflow graph"""

    # 1. Create graph with state types
    workflow = StateGraph(
        OverallState,           # Internal state
        input=InputState,       # Input type
        output=OutputState      # Output type
    )

    # 2. Add all nodes
    workflow.add_node("researcher", researcher_agent_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("product", product_agent_node)
    workflow.add_node("synthesizer", synthesizer_agent_node)
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("save_report", save_report_node)

    # 3. Define edges (execution flow)
    workflow.set_entry_point("researcher")

    # Parallel fan-out
    workflow.add_edge("researcher", "financial")
    workflow.add_edge("researcher", "market")
    workflow.add_edge("researcher", "product")

    # Fan-in to synthesizer
    workflow.add_edge("financial", "synthesizer")
    workflow.add_edge("market", "synthesizer")
    workflow.add_edge("product", "synthesizer")

    # Continue to quality check
    workflow.add_edge("synthesizer", "check_quality")

    # Conditional routing
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {
            "iterate": "researcher",
            "finish": "save_report"
        }
    )

    workflow.add_edge("save_report", END)

    # 4. Compile to executable graph
    return workflow.compile()
```

### Workflow Invocation

```python
def research_company(company_name: str) -> OutputState:
    # Create workflow
    workflow = create_parallel_agent_workflow()

    # Create initial state
    initial_state = create_initial_state(company_name)

    # Execute workflow
    final_state = workflow.invoke(initial_state)

    # Convert to output
    return create_output_state(final_state)
```

**Execution Flow**:
1. `workflow.invoke(initial_state)` starts execution
2. LangGraph calls entry point node (`researcher`)
3. Researcher returns state updates
4. LangGraph merges updates into state
5. LangGraph identifies next nodes (financial, market, product)
6. Executes them in parallel (asyncio internally)
7. Waits for all parallel nodes to complete
8. Continues to synthesizer
9. Continues to check_quality
10. Calls decision function `should_continue_research(state)`
11. Routes to "iterate" or "finish" based on return value
12. If "iterate", loops back to researcher
13. If "finish", saves report and ends

### Parallel Execution Details

**LangGraph's Automatic Parallelization**:

```python
# These three edges from researcher
workflow.add_edge("researcher", "financial")
workflow.add_edge("researcher", "market")
workflow.add_edge("researcher", "product")

# Cause LangGraph to execute financial, market, product concurrently
# Because they:
# 1. All depend on researcher (same parent)
# 2. Don't depend on each other
# 3. All lead to synthesizer (same child)
```

**Internal Behavior**:
- LangGraph uses `asyncio.gather()` to run nodes concurrently
- Each node gets a **copy** of the current state (immutable read)
- Each node returns **partial state updates**
- Reducers merge concurrent updates safely
- Execution continues when **all** parallel nodes complete

---

## How Agents Work

### Agent Node Pattern

Every agent follows this standard pattern:

```python
def agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Standard agent node function.

    Args:
        state: Current workflow state (read-only perspective)

    Returns:
        Partial state updates to merge into OverallState
    """
    # 1. Initialize
    print(f"[AGENT: {name}] Starting...")
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    # 2. Extract inputs from state
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    # 3. Prepare prompt
    prompt = AGENT_PROMPT.format(
        company_name=company_name,
        data=format_data(search_results)
    )

    # 4. Call LLM
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    # 5. Extract result
    result = response.content[0].text

    # 6. Calculate cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    # 7. Track agent metrics
    agent_output = {
        "analysis": result,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    # 8. Return partial state updates
    return {
        "agent_outputs": {agent_name: agent_output},  # merge_dicts
        "total_cost": cost,                            # add
        "total_tokens": {                              # add_tokens
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
```

### Example: Researcher Agent

**File**: `agents/researcher.py`

```python
def researcher_agent_node(state: OverallState) -> Dict[str, Any]:
    """Combined query generation + search execution"""

    # Check if iterating with missing info
    missing_info = state.get("missing_info", [])
    if missing_info:
        # Generate focused queries for gaps
        num_queries = 3
        query_context = f"Focus on: {missing_info}"
    else:
        # Initial broad research
        num_queries = 5
        query_context = ""

    # Generate queries via LLM
    response = client.messages.create(
        model=config.llm_model,
        messages=[{"role": "user", "content": GENERATE_QUERIES_PROMPT}]
    )

    queries = parse_queries(response.content[0].text)

    # Execute searches via Tavily
    all_results = []
    for query in queries:
        search_response = tavily_client.search(query, max_results=3)
        all_results.extend(search_response["results"])

    # Return state updates
    return {
        "search_results": all_results,           # Replaces (no reducer)
        "sources": extract_sources(all_results), # Uses 'add' (appends)
        "agent_outputs": {"researcher": {...}},  # Uses merge_dicts
        "total_cost": cost,                      # Uses 'add'
        "total_tokens": {...}                    # Uses add_tokens
    }
```

**Key Points**:
- Agents are **pure functions**: `state → updates`
- Agents **read** from state, **return** updates
- LangGraph **merges** updates using reducers
- Agents **don't modify** state directly

### Example: Financial Agent

**File**: `agents/financial.py`

```python
def financial_agent_node(state: OverallState) -> Dict[str, Any]:
    """Extract financial metrics from search results"""

    search_results = state.get("search_results", [])

    # Format results for analysis
    formatted = "\n\n".join([
        f"Source {i}: {r['title']}\n{r['content'][:500]}"
        for i, r in enumerate(search_results[:15])
    ])

    # Financial analysis prompt
    prompt = FINANCIAL_ANALYSIS_PROMPT.format(
        company_name=state["company_name"],
        search_results=formatted
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    financial_analysis = response.content[0].text

    # Return only this agent's contribution
    return {
        "agent_outputs": {"financial": {
            "analysis": financial_analysis,
            "cost": cost
        }},
        "total_cost": cost,
        "total_tokens": {...}
    }
```

---

## State Updates and Reducers

### State Flow Diagram

```mermaid
graph TD
    START[Initial State] --> RESEARCHER[Researcher Node<br/>Returns state updates]

    RESEARCHER --> SPLIT{LangGraph<br/>Parallel Dispatcher}

    SPLIT --> |Copy of state| FIN[Financial Agent<br/>Returns: agent_outputs.financial]
    SPLIT --> |Copy of state| MKT[Market Agent<br/>Returns: agent_outputs.market]
    SPLIT --> |Copy of state| PRD[Product Agent<br/>Returns: agent_outputs.product]

    FIN --> MERGE[merge_dicts Reducer<br/>Combines concurrent updates]
    MKT --> MERGE
    PRD --> MERGE

    MERGE --> STATE[Updated State<br/>agent_outputs = {financial, market, product}]
    STATE --> SYNTH[Synthesizer Node]

    SYNTH --> QUALITY[Quality Check<br/>Returns: quality_score]
    QUALITY --> DECISION{should_continue?}

    DECISION -->|iterate| RESEARCHER
    DECISION -->|finish| END[Final State]

    style START fill:#e1f5fe
    style SPLIT fill:#fff9c4
    style FIN fill:#c8e6c9
    style MKT fill:#c8e6c9
    style PRD fill:#c8e6c9
    style MERGE fill:#ffe0b2
    style STATE fill:#f8bbd0
    style DECISION fill:#d1c4e9
```

### How State Merging Works

**Without Reducers** (default):
```python
# Agent A returns:
{"company_overview": "New value A"}

# State becomes:
{"company_overview": "New value A"}  # Replaces old value

# Agent B returns (later):
{"company_overview": "New value B"}

# State becomes:
{"company_overview": "New value B"}  # Replaces again
```

**With 'add' Reducer** (appending):
```python
# Definition:
search_results: Annotated[List[Dict], add]

# Agent A returns:
{"search_results": [result1, result2]}

# State becomes:
{"search_results": [result1, result2]}

# Agent B returns:
{"search_results": [result3, result4]}

# State becomes (appended):
{"search_results": [result1, result2, result3, result4]}
```

**With merge_dicts Reducer** (Phase 4 parallel execution):
```python
# Definition:
agent_outputs: Annotated[Optional[Dict], merge_dicts]

# Financial agent returns (parallel):
{"agent_outputs": {"financial": {...}}}

# Market agent returns (concurrent):
{"agent_outputs": {"market": {...}}}

# Product agent returns (concurrent):
{"agent_outputs": {"product": {...}}}

# merge_dicts combines:
{
    "agent_outputs": {
        "financial": {...},
        "market": {...},
        "product": {...}
    }
}
```

**With add_tokens Reducer** (custom accumulation):
```python
# Definition:
total_tokens: Annotated[Dict[str, int], add_tokens]

def add_tokens(left, right):
    return {
        "input": left.get("input", 0) + right.get("input", 0),
        "output": left.get("output", 0) + right.get("output", 0)
    }

# Agent A returns:
{"total_tokens": {"input": 100, "output": 50}}

# Agent B returns (parallel):
{"total_tokens": {"input": 200, "output": 75}}

# add_tokens combines:
{"total_tokens": {"input": 300, "output": 125}}
```

### Reducer Implementation

**File**: `state.py`

```python
def merge_dicts(left: Optional[Dict], right: Optional[Dict]) -> Dict:
    """
    Merge two dictionaries.

    Used for agent_outputs to allow parallel agents to each
    contribute their results without conflicts.
    """
    if left is None:
        left = {}
    if right is None:
        right = {}
    # Shallow merge - right keys overwrite left keys
    return {**left, **right}


def add_tokens(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """
    Add token counts from two dictionaries.

    Used for total_tokens to accumulate across parallel agents.
    """
    return {
        "input": left.get("input", 0) + right.get("input", 0),
        "output": left.get("output", 0) + right.get("output", 0)
    }
```

**Annotation Usage**:
```python
from typing import Annotated
from operator import add

class OverallState(TypedDict):
    # Default (replace):
    company_name: str

    # Append to list:
    search_results: Annotated[List[Dict], add]

    # Add numbers:
    total_cost: Annotated[float, add]

    # Custom merge:
    agent_outputs: Annotated[Optional[Dict], merge_dicts]
    total_tokens: Annotated[Dict[str, int], add_tokens]
```

---

## Quality Check Logic

### Quality Scoring Function

**File**: `quality/checker.py`

```python
def check_research_quality(
    company_name: str,
    extracted_data: str,
    sources: List[Dict]
) -> Dict[str, Any]:
    """
    Score research quality 0-100.

    Returns:
        {
            "quality_score": float,
            "missing_information": List[str],
            "strengths": List[str],
            "cost": float,
            "tokens": Dict[str, int]
        }
    """

    # Build quality check prompt
    prompt = QUALITY_CHECK_PROMPT.format(
        company_name=company_name,
        extracted_data=extracted_data,
        sources=format_sources(sources)
    )

    # Call Claude for quality assessment
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response
    result = json.loads(response.content[0].text)

    # Calculate cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    return {
        "quality_score": result["quality_score"],
        "missing_information": result["missing_information"],
        "strengths": result.get("strengths", []),
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
```

### Quality Criteria

**Prompt Structure** (`prompts.py`):

```python
QUALITY_CHECK_PROMPT = """...

1. **Completeness** (0-40 points):
   - Company overview? (10 points)
   - Financial metrics? (10 points)
   - Products/services? (10 points)
   - Competitive analysis? (10 points)

2. **Accuracy** (0-30 points):
   - Facts supported by sources? (15 points)
   - Numbers/dates specific? (15 points)

3. **Depth** (0-30 points):
   - Insightful analysis? (15 points)
   - Beyond surface level? (15 points)

Be strict: Only score 85+ for truly comprehensive research.
"""
```

### Decision Function

**File**: `workflows/parallel_agent_research.py`

```python
def should_continue_research(state: OverallState) -> str:
    """
    Decision: iterate or finish?

    Returns:
        "iterate" - Loop back to researcher
        "finish" - Save report and end
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 2

    if quality_score >= 85:
        # Quality threshold met
        return "finish"

    elif iteration_count >= max_iterations:
        # Max iterations reached
        return "finish"

    else:
        # Try again
        return "iterate"
```

**Routing**:
```python
workflow.add_conditional_edges(
    "check_quality",
    should_continue_research,
    {
        "iterate": "researcher",  # Function returns "iterate"
        "finish": "save_report"   # Function returns "finish"
    }
)
```

---

## Report Generation

### Save Report Node

**File**: `workflows/parallel_agent_research.py`

```python
def save_report_node(state: OverallState) -> Dict[str, Any]:
    """Generate and save markdown report"""

    # Extract data from state
    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})
    sources = state.get("sources", [])

    # Build report content
    report_content = f"""# {company_name} - Research Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

{state.get("company_overview", "Not available")}

---

## Sources

{format_sources_for_report(sources)}

---

*Quality Score: {state.get('quality_score', 0):.1f}/100*
*Cost: ${state.get('total_cost', 0.0):.4f}*
"""

    # Save to file
    output_dir = f"outputs/{company_name}"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{output_dir}/report_{timestamp}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return {"report_path": report_path}
```

### Output State Conversion

```python
def create_output_state(state: OverallState) -> OutputState:
    """Convert OverallState to OutputState"""

    duration = (datetime.now() - state.get("start_time")).total_seconds()

    return {
        "company_name": state.get("company_name", ""),
        "report_path": state.get("report_path", ""),
        "metrics": {
            "duration_seconds": duration,
            "cost_usd": state.get("total_cost", 0.0),
            "tokens": state.get("total_tokens", {}),
            "sources_count": len(state.get("sources", [])),
            "quality_score": state.get("quality_score", 0.0),
            "iterations": state.get("iteration_count", 0)
        },
        "success": state.get("report_path") is not None
    }
```

---

## Cost Tracking

### Cost Calculation

**File**: `config.py`

```python
def get_model_pricing(self) -> dict:
    """Get pricing per 1M tokens"""
    pricing = {
        "claude-3-5-haiku-20241022": {
            "input": 0.80,   # $0.80 per 1M input tokens
            "output": 4.00   # $4.00 per 1M output tokens
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00
        }
    }
    return pricing.get(self.llm_model, {"input": 3.00, "output": 15.00})


def calculate_llm_cost(self, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for LLM usage"""
    pricing = self.get_model_pricing()
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
```

### Per-Agent Cost Tracking

Each agent tracks its own cost:

```python
def agent_node(state: OverallState) -> Dict[str, Any]:
    # ... LLM call ...

    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    return {
        "agent_outputs": {
            "agent_name": {
                "cost": cost,  # Individual agent cost
                # ...
            }
        },
        "total_cost": cost  # Uses 'add' reducer to accumulate
    }
```

### Search API Cost

```python
# Tavily approximate cost
search_cost = num_queries * 0.001  # $0.001 per search

total_cost = llm_cost + search_cost
```

---

## Configuration System

### Environment Loading

**File**: `config.py`

```python
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()

class ResearchConfig(BaseSettings):
    # Pydantic automatically loads from environment

    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### Singleton Pattern

```python
_config: Optional[ResearchConfig] = None

def get_config() -> ResearchConfig:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = ResearchConfig()
        _config.validate_api_keys()
    return _config
```

**Usage Throughout Codebase**:
```python
from company_researcher.config import get_config

config = get_config()
client = Anthropic(api_key=config.anthropic_api_key)
```

---

## Error Handling

### API Key Validation

```python
def validate_api_keys(self) -> None:
    """Validate required API keys"""
    if not self.anthropic_api_key:
        raise ValueError(
            "Missing ANTHROPIC_API_KEY. "
            "Get your key at: https://console.anthropic.com/"
        )

    if not self.tavily_api_key:
        raise ValueError(
            "Missing TAVILY_API_KEY. "
            "Get your key at: https://tavily.com/"
        )
```

### JSON Parsing Fallback

```python
try:
    # Try to parse JSON response
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    queries = json.loads(content.strip())
except json.JSONDecodeError:
    # Fallback to default queries
    queries = [
        f"{company_name} company overview",
        f"{company_name} revenue financial performance",
        # ...
    ]
```

### Graceful Degradation

```python
def financial_agent_node(state: OverallState) -> Dict[str, Any]:
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Financial] WARNING: No search results!")
        return {
            "agent_outputs": {
                "financial": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    # ... normal processing ...
```

---

## Next Steps

**For Developers**:
- Read [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) to create new agents
- Review [API_REFERENCE.md](API_REFERENCE.md) for function signatures
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design

**For Extending the System**:
- Phase 4-6: Add observability (AgentOps, LangSmith)
- Phase 7-10: Implement new specialist agents
- Phase 11-12: Add memory and caching

See [MASTER_20_PHASE_PLAN.md](../planning/MASTER_20_PHASE_PLAN.md) for roadmap.

---

**Last Updated**: December 5, 2025
**Version**: 0.4.0 (Phase 4 Complete)
