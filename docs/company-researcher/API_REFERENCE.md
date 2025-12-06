# API Reference

Complete API documentation for the Company Researcher system.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Table of Contents

- [Main Entry Points](#main-entry-points)
- [State Types](#state-types)
- [Agent Nodes](#agent-nodes)
- [Workflow Functions](#workflow-functions)
- [Configuration](#configuration)
- [Quality System](#quality-system)
- [Utilities](#utilities)
- [Type Definitions](#type-definitions)

---

## Main Entry Points

### research_company()

Main function to research a company using the parallel multi-agent workflow.

```python
def research_company(company_name: str) -> OutputState
```

**Parameters**:
- `company_name` (str): Name of the company to research

**Returns**:
- `OutputState`: Dictionary containing:
  - `company_name` (str): Name of researched company
  - `report_path` (str): Path to generated markdown report
  - `metrics` (Dict[str, Any]): Performance metrics
    - `duration_seconds` (float): Total execution time
    - `cost_usd` (float): Total cost in USD
    - `tokens` (Dict[str, int]): Token usage (`input`, `output`)
    - `sources_count` (int): Number of sources used
    - `quality_score` (float): Quality score 0-100
    - `iterations` (int): Number of research iterations
  - `success` (bool): Whether research completed successfully

**Example**:
```python
from company_researcher.workflows.parallel_agent_research import research_company

result = research_company("Tesla")

print(f"Report: {result['report_path']}")
print(f"Quality: {result['metrics']['quality_score']:.1f}/100")
print(f"Cost: ${result['metrics']['cost_usd']:.4f}")
```

**Raises**:
- `ValueError`: If API keys are not configured
- `Exception`: If LLM or search API calls fail

---

## State Types

### InputState

Minimal input to start the workflow.

```python
class InputState(TypedDict):
    company_name: str
```

**Fields**:
- `company_name` (str): Name of company to research

### OverallState

Complete state maintained throughout the workflow.

```python
class OverallState(TypedDict):
    # Input
    company_name: str

    # Query Generation
    search_queries: List[str]

    # Search Results
    search_results: Annotated[List[Dict[str, Any]], add]

    # Analysis
    notes: List[str]

    # Extracted Data
    company_overview: Optional[str]
    key_metrics: Optional[Dict[str, Any]]
    products_services: Optional[List[str]]
    competitors: Optional[List[str]]
    key_insights: Optional[List[str]]

    # Metadata
    sources: Annotated[List[Dict[str, str]], add]

    # Quality
    quality_score: Optional[float]
    iteration_count: int
    missing_info: Optional[List[str]]

    # Agent Coordination (Phase 4)
    agent_outputs: Annotated[Optional[Dict[str, Any]], merge_dicts]

    # Metrics
    start_time: datetime
    total_cost: Annotated[float, add]
    total_tokens: Annotated[Dict[str, int], add_tokens]

    # Report
    report_path: Optional[str]
```

**Field Details**:

| Field | Type | Reducer | Description |
|-------|------|---------|-------------|
| `company_name` | str | None | Company being researched |
| `search_queries` | List[str] | None | Generated search queries |
| `search_results` | List[Dict] | `add` | Search results from Tavily |
| `notes` | List[str] | None | LLM summaries |
| `company_overview` | Optional[str] | None | Synthesized company description |
| `key_metrics` | Optional[Dict] | None | Extracted metrics |
| `products_services` | Optional[List[str]] | None | Products/services list |
| `competitors` | Optional[List[str]] | None | Competitor names |
| `key_insights` | Optional[List[str]] | None | Notable findings |
| `sources` | List[Dict] | `add` | Source metadata |
| `quality_score` | Optional[float] | None | Quality score 0-100 |
| `iteration_count` | int | None | Current iteration number |
| `missing_info` | Optional[List[str]] | None | Identified gaps |
| `agent_outputs` | Optional[Dict] | `merge_dicts` | Agent-specific outputs |
| `start_time` | datetime | None | Workflow start time |
| `total_cost` | float | `add` | Cumulative cost |
| `total_tokens` | Dict[str, int] | `add_tokens` | Cumulative tokens |
| `report_path` | Optional[str] | None | Path to saved report |

### OutputState

Final output from the workflow.

```python
class OutputState(TypedDict):
    company_name: str
    report_path: str
    metrics: Dict[str, Any]
    success: bool
```

**Fields**:
- `company_name` (str): Name of researched company
- `report_path` (str): Path to generated report file
- `metrics` (Dict[str, Any]): Performance metrics (see [research_company()](#research_company))
- `success` (bool): `True` if report was generated successfully

---

## Agent Nodes

All agent nodes follow the same signature pattern.

### Agent Node Signature

```python
def agent_node(state: OverallState) -> Dict[str, Any]
```

**Parameters**:
- `state` (OverallState): Current workflow state (read-only)

**Returns**:
- `Dict[str, Any]`: Partial state updates to merge

**Standard Return Format**:
```python
{
    "agent_outputs": {
        "agent_name": {
            "analysis": str,          # Agent's output
            "cost": float,            # LLM cost
            "tokens": {               # Token usage
                "input": int,
                "output": int
            },
            "data_extracted": bool    # Success indicator
        }
    },
    "total_cost": float,              # For 'add' reducer
    "total_tokens": {                 # For 'add_tokens' reducer
        "input": int,
        "output": int
    }
}
```

### researcher_agent_node()

Generates search queries and executes web searches.

```python
def researcher_agent_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `missing_info` (Optional[List[str]]): Used for focused iteration queries

**Returns**:
```python
{
    "search_results": List[Dict],     # Search results from Tavily
    "sources": List[Dict],            # Source metadata
    "agent_outputs": {
        "researcher": {
            "queries_generated": int,
            "queries": List[str],
            "sources_found": int,
            "cost": float,
            "tokens": Dict[str, int]
        }
    },
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

### financial_agent_node()

Extracts financial metrics and data.

```python
def financial_agent_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `search_results` (List[Dict]): Required

**Returns**:
```python
{
    "agent_outputs": {
        "financial": {
            "analysis": str,          # Financial data extraction
            "data_extracted": bool,
            "cost": float,
            "tokens": Dict[str, int]
        }
    },
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

### market_agent_node()

Analyzes market position and competition.

```python
def market_agent_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `search_results` (List[Dict]): Required

**Returns**:
```python
{
    "agent_outputs": {
        "market": {
            "analysis": str,          # Market analysis
            "data_extracted": bool,
            "cost": float,
            "tokens": Dict[str, int]
        }
    },
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

### product_agent_node()

Catalogs products, services, and technology.

```python
def product_agent_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `search_results` (List[Dict]): Required

**Returns**:
```python
{
    "agent_outputs": {
        "product": {
            "analysis": str,          # Product analysis
            "data_extracted": bool,
            "cost": float,
            "tokens": Dict[str, int]
        }
    },
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

### synthesizer_agent_node()

Combines all specialist insights into comprehensive overview.

```python
def synthesizer_agent_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `search_results` (List[Dict]): Required
- `agent_outputs` (Dict): Specialist agent outputs

**Returns**:
```python
{
    "company_overview": str,          # Synthesized overview
    "agent_outputs": {
        "synthesizer": {
            "specialists_combined": int,
            "cost": float,
            "tokens": Dict[str, int]
        }
    },
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

---

## Workflow Functions

### create_parallel_agent_workflow()

Creates the compiled LangGraph workflow.

```python
def create_parallel_agent_workflow() -> StateGraph
```

**Returns**:
- `StateGraph`: Compiled LangGraph workflow ready for execution

**Example**:
```python
from company_researcher.workflows.parallel_agent_research import create_parallel_agent_workflow

workflow = create_parallel_agent_workflow()
result = workflow.invoke({"company_name": "Tesla"})
```

### check_quality_node()

Evaluates research quality and determines iteration.

```python
def check_quality_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `company_overview` (str): Required
- `sources` (List[Dict]): Required
- `iteration_count` (int): Required

**Returns**:
```python
{
    "quality_score": float,           # Score 0-100
    "missing_info": List[str],        # Identified gaps
    "iteration_count": int,           # Incremented
    "total_cost": float,
    "total_tokens": Dict[str, int]
}
```

### save_report_node()

Generates and saves the markdown report.

```python
def save_report_node(state: OverallState) -> Dict[str, Any]
```

**Input Requirements** (from state):
- `company_name` (str): Required
- `company_overview` (str): Required
- `sources` (List[Dict]): Required
- `agent_outputs` (Dict): For metrics
- `quality_score` (float): For report metadata
- `total_cost` (float): For report metadata

**Returns**:
```python
{
    "report_path": str  # Path to saved markdown file
}
```

**Side Effects**:
- Creates directory `outputs/{company_name}/` if it doesn't exist
- Writes markdown report to `outputs/{company_name}/report_{timestamp}.md`

### should_continue_research()

Decision function for conditional routing.

```python
def should_continue_research(state: OverallState) -> str
```

**Input Requirements** (from state):
- `quality_score` (float): Required
- `iteration_count` (int): Required

**Returns**:
- `"iterate"`: Loop back to researcher for another iteration
- `"finish"`: Proceed to save report

**Logic**:
- Returns `"finish"` if `quality_score >= 85`
- Returns `"finish"` if `iteration_count >= 2`
- Otherwise returns `"iterate"`

---

## Configuration

### ResearchConfig

Configuration class using Pydantic settings.

```python
class ResearchConfig(BaseSettings):
    # API Keys
    anthropic_api_key: str
    tavily_api_key: str

    # Model Configuration
    llm_model: str = "claude-3-5-haiku-20241022"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 4000

    # Search Configuration
    num_search_queries: int = 5
    search_results_per_query: int = 3
    max_search_results: int = 15

    # Research Parameters
    max_research_time_seconds: int = 300
    target_cost_usd: float = 0.30

    # Output Configuration
    output_dir: str = "outputs"
    report_format: str = "markdown"
```

**Methods**:

#### validate_api_keys()

```python
def validate_api_keys(self) -> None
```

Validates that required API keys are present.

**Raises**:
- `ValueError`: If `ANTHROPIC_API_KEY` or `TAVILY_API_KEY` is missing

#### get_model_pricing()

```python
def get_model_pricing(self) -> dict
```

Returns pricing for the configured model.

**Returns**:
```python
{
    "input": float,   # Cost per 1M input tokens
    "output": float   # Cost per 1M output tokens
}
```

#### calculate_llm_cost()

```python
def calculate_llm_cost(self, input_tokens: int, output_tokens: int) -> float
```

Calculates cost for LLM usage.

**Parameters**:
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens

**Returns**:
- `float`: Total cost in USD

**Example**:
```python
config = get_config()
cost = config.calculate_llm_cost(1000, 500)
# cost = (1000/1_000_000 * 0.80) + (500/1_000_000 * 4.00)
# cost = 0.0008 + 0.002 = 0.0028
```

### get_config()

Returns the global configuration instance (singleton).

```python
def get_config() -> ResearchConfig
```

**Returns**:
- `ResearchConfig`: Global configuration instance

**Example**:
```python
from company_researcher.config import get_config

config = get_config()
client = Anthropic(api_key=config.anthropic_api_key)
```

---

## Quality System

### check_research_quality()

Scores research quality and identifies gaps.

```python
def check_research_quality(
    company_name: str,
    extracted_data: str,
    sources: List[Dict[str, str]]
) -> Dict[str, Any]
```

**Parameters**:
- `company_name` (str): Name of company being researched
- `extracted_data` (str): Extracted company information
- `sources` (List[Dict]): List of source metadata

**Returns**:
```python
{
    "quality_score": float,           # Score 0-100
    "missing_information": List[str], # Identified gaps
    "strengths": List[str],          # What's good
    "recommended_queries": List[str], # Suggested searches
    "cost": float,                    # LLM cost
    "tokens": {                       # Token usage
        "input": int,
        "output": int
    }
}
```

**Quality Scoring Criteria**:
- **Completeness** (0-40 points): Coverage of key topics
- **Accuracy** (0-30 points): Source quality and specificity
- **Depth** (0-30 points): Analysis quality

**Example**:
```python
from company_researcher.quality import check_research_quality

result = check_research_quality(
    company_name="Tesla",
    extracted_data="Tesla is an electric vehicle manufacturer...",
    sources=[
        {"title": "Tesla Q4 Earnings", "url": "https://...", "score": 0.95}
    ]
)

print(f"Quality: {result['quality_score']:.1f}/100")
if result['quality_score'] < 85:
    print("Missing:")
    for item in result['missing_information']:
        print(f"  - {item}")
```

---

## Utilities

### State Creation

#### create_initial_state()

```python
def create_initial_state(company_name: str) -> OverallState
```

Creates initial state for a new research workflow.

**Parameters**:
- `company_name` (str): Name of company to research

**Returns**:
- `OverallState`: Initialized state with default values

**Example**:
```python
from company_researcher.state import create_initial_state

state = create_initial_state("Tesla")
# state["company_name"] == "Tesla"
# state["iteration_count"] == 0
# state["total_cost"] == 0.0
```

#### create_output_state()

```python
def create_output_state(state: OverallState) -> OutputState
```

Converts OverallState to OutputState.

**Parameters**:
- `state` (OverallState): Complete workflow state

**Returns**:
- `OutputState`: Final output format

### State Reducers

#### merge_dicts()

```python
def merge_dicts(left: Optional[Dict], right: Optional[Dict]) -> Dict
```

Merge two dictionaries (shallow merge).

**Parameters**:
- `left` (Optional[Dict]): Existing dictionary
- `right` (Optional[Dict]): New dictionary to merge

**Returns**:
- `Dict`: Merged dictionary (`{**left, **right}`)

**Usage**:
```python
agent_outputs: Annotated[Optional[Dict[str, Any]], merge_dicts]
```

#### add_tokens()

```python
def add_tokens(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]
```

Add token counts from two dictionaries.

**Parameters**:
- `left` (Dict[str, int]): Existing token counts
- `right` (Dict[str, int]): New token counts to add

**Returns**:
```python
{
    "input": int,   # Sum of input tokens
    "output": int   # Sum of output tokens
}
```

**Usage**:
```python
total_tokens: Annotated[Dict[str, int], add_tokens]
```

### Prompt Utilities

#### format_search_results_for_analysis()

```python
def format_search_results_for_analysis(results: List[Dict]) -> str
```

Formats search results for LLM analysis prompts.

**Parameters**:
- `results` (List[Dict]): Search results from Tavily

**Returns**:
- `str`: Formatted string with result titles, URLs, content, scores

#### format_sources_for_report()

```python
def format_sources_for_report(sources: List[Dict[str, str]]) -> str
```

Formats sources for the final markdown report.

**Parameters**:
- `sources` (List[Dict]): Source metadata dictionaries

**Returns**:
- `str`: Markdown-formatted numbered list of sources

**Example Output**:
```
1. [Tesla Q4 2024 Earnings](https://example.com/q4-earnings)
2. [Tesla Cybertruck Launch](https://example.com/cybertruck)
```

---

## Type Definitions

### Search Result

```python
{
    "title": str,          # Result title
    "url": str,            # Result URL
    "content": str,        # Result content/snippet
    "score": float         # Relevance score 0-1
}
```

### Source Metadata

```python
{
    "title": str,          # Source title
    "url": str,            # Source URL
    "score": float         # Relevance score 0-1
}
```

### Agent Output

```python
{
    "analysis": str,       # Agent's analysis/extraction
    "data_extracted": bool,  # Success indicator
    "cost": float,         # LLM cost for this agent
    "tokens": {            # Token usage
        "input": int,
        "output": int
    }
}
```

### Metrics

```python
{
    "duration_seconds": float,   # Total execution time
    "cost_usd": float,           # Total cost in USD
    "tokens": {                  # Total token usage
        "input": int,
        "output": int
    },
    "sources_count": int,        # Number of sources
    "quality_score": float,      # Quality score 0-100
    "iterations": int            # Number of iterations
}
```

---

## Error Handling

### ValueError

Raised when required configuration is missing:

```python
try:
    config = get_config()
except ValueError as e:
    # "Missing ANTHROPIC_API_KEY. Get your key at: ..."
    print(f"Configuration error: {e}")
```

### JSON Parsing Errors

Agents handle JSON parsing errors gracefully with fallback values:

```python
try:
    queries = json.loads(response_text)
except json.JSONDecodeError:
    # Use default queries
    queries = [f"{company_name} company overview", ...]
```

### Missing Data

Agents handle missing input data gracefully:

```python
if not search_results:
    return {
        "agent_outputs": {
            "agent_name": {
                "analysis": "No search results available",
                "data_extracted": False,
                "cost": 0.0
            }
        }
    }
```

---

## Version History

### 0.4.0 (Current)
- Parallel multi-agent execution
- Custom state reducers (`merge_dicts`, `add_tokens`)
- 5 agents: Researcher, Financial, Market, Product, Synthesizer
- Fan-out/fan-in pattern

### 0.3.0
- Sequential multi-agent execution
- 4 specialist agents
- Quality iteration loop

### 0.2.0
- Quality scoring system
- Iteration based on quality threshold
- Missing information detection

### 0.1.0
- Basic LangGraph workflow
- Single researcher agent
- Simple report generation

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and architecture
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - How the code works
- [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) - Creating new agents
- [USER_GUIDE.md](USER_GUIDE.md) - How to use the system

---

**Last Updated**: December 5, 2025
**Version**: 0.4.0 (Phase 4 Complete)
