# Code Examples

Practical examples demonstrating how to use the Company Researcher system.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Research](#basic-research)
- [Batch Research](#batch-research)
- [Custom Agents](#custom-agents)
- [Cost Analysis](#cost-analysis)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

All examples are in the [examples/](../../examples/) directory and can be run directly:

```bash
# Basic research
python examples/basic_research.py

# Batch research
python examples/batch_research.py

# Custom agent
python examples/custom_agent.py

# Cost analysis
python examples/cost_analysis.py
```

---

## Basic Research

**File**: [examples/basic_research.py](../../examples/basic_research.py)

The simplest way to research a company using the Phase 4 parallel multi-agent system.

### Code

```python
from src.company_researcher.workflows.parallel_agent_research import research_company

# Research a company
result = research_company("Tesla")

# Access results
print(f"Quality Score: {result['quality_score']}/100")
print(f"Total Cost: ${result['total_cost']}")
print(f"Report saved: {result['report_path']}")
```

### Output Structure

```python
{
    "company_name": "Tesla",
    "quality_score": 88.0,
    "total_cost": 0.0234,
    "total_tokens": {
        "input": 12543,
        "output": 3421
    },
    "report": "# Tesla - Company Research Report\n...",
    "report_path": "outputs/Tesla/report_20251205_143022.md"
}
```

### When to Use

- Quick one-off research
- Testing the system
- Learning the basics

---

## Batch Research

**File**: [examples/batch_research.py](../../examples/batch_research.py)

Research multiple companies and compare results.

### Code

```python
from examples.batch_research import batch_research, compare_results

# Research multiple companies
companies = ["Microsoft", "Tesla", "Stripe", "OpenAI", "Anthropic"]
results = batch_research(companies)

# Compare results
compare_results(results)
```

### Output

```
=== Batch Research Summary ===

Total Companies: 5
Successful: 4
Failed: 1

Quality Scores:
  ✅ Microsoft: 88.0/100
  ✅ Stripe: 88.0/100
  ⚠️ Tesla: 78.0/100
  ✅ OpenAI: 85.5/100

Cost Analysis:
  Total Cost: $0.0892
  Average Cost per Company: $0.0223

Token Usage:
  Total Input Tokens: 48,234
  Total Output Tokens: 13,567
  Total Tokens: 61,801

Failed Companies:
  ❌ Anthropic: Rate limit exceeded
```

### Features

- Parallel company research
- Quality score comparison
- Cost aggregation
- Error handling per company
- Summary statistics

### When to Use

- Competitive analysis (compare multiple companies)
- Portfolio research
- Market landscape analysis
- Cost estimation for large batches

---

## Custom Agents

**File**: [examples/custom_agent.py](../../examples/custom_agent.py)

Create a custom agent and integrate it into the workflow.

This example creates a **News Agent** that specializes in finding recent news, press releases, and announcements.

### Creating a Custom Agent

```python
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from src.company_researcher.state import OverallState
from src.company_researcher.config import config

def news_agent_node(state: OverallState) -> Dict[str, Any]:
    """Custom News Agent that analyzes recent news."""

    # 1. Extract inputs from state
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    # 2. Create specialized prompt
    prompt = f"""Analyze recent news for {company_name}.

    Focus on:
    - Major announcements (last 6 months)
    - Product launches
    - Funding/acquisition news
    - Leadership changes

    Sources: {format_search_results(search_results)}
    """

    # 3. Call LLM
    llm = ChatAnthropic(
        model=config.llm_model,
        temperature=0.0,
        api_key=config.anthropic_api_key
    )
    response = llm.invoke(prompt)

    # 4. Track costs
    cost = config.calculate_llm_cost(
        response.usage_metadata["input_tokens"],
        response.usage_metadata["output_tokens"]
    )

    # 5. Return state updates
    return {
        "agent_outputs": {"news": response.content},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage_metadata["input_tokens"],
            "output": response.usage_metadata["output_tokens"]
        }
    }
```

### Integrating into Workflow

```python
from langgraph.graph import StateGraph, END

def create_custom_workflow():
    """Create workflow with custom News Agent."""
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add standard agents
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("product", product_agent_node)

    # Add custom agent
    workflow.add_node("news", news_agent_node)

    # Add synthesis and quality nodes
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("check_quality", check_quality_node)

    # Set entry point
    workflow.set_entry_point("researcher")

    # Fan-out to parallel agents (includes custom news agent)
    workflow.add_edge("researcher", "financial")
    workflow.add_edge("researcher", "market")
    workflow.add_edge("researcher", "product")
    workflow.add_edge("researcher", "news")  # Custom agent

    # Fan-in to synthesizer
    workflow.add_edge("financial", "synthesizer")
    workflow.add_edge("market", "synthesizer")
    workflow.add_edge("product", "synthesizer")
    workflow.add_edge("news", "synthesizer")  # Custom agent

    # Continue workflow
    workflow.add_edge("synthesizer", "check_quality")
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {"iterate": "researcher", "finish": "save_report"}
    )
    workflow.add_edge("save_report", END)

    return workflow.compile()
```

### Custom Agent Ideas

**Sentiment Agent**:
- Analyze public sentiment from social media
- Reddit discussions, Twitter mentions
- Glassdoor reviews

**Tech Stack Agent**:
- Identify technologies used (GitHub, job postings)
- Engineering blog analysis
- Stack Overflow activity

**ESG Agent**:
- Environmental initiatives
- Social impact programs
- Governance practices

**Patent Agent**:
- Recent patent filings
- Innovation areas
- R&D focus

### When to Use

- Specialized research needs
- Domain-specific analysis
- Extending system capabilities
- Experimentation with new agent types

---

## Cost Analysis

**File**: [examples/cost_analysis.py](../../examples/cost_analysis.py)

Track and analyze research costs in detail.

### Single Company Analysis

```python
from examples.cost_analysis import analyze_research_costs

# Analyze costs for one company
analysis = analyze_research_costs("Stripe")
```

**Output**:

```
======================================================================
Company: Stripe
Quality Score: 88.0/100
======================================================================

Total Cost: $0.0234

Token Usage:
  Input Tokens:     12,543 (78.6%)
  Output Tokens:     3,421 (21.4%)
  Total Tokens:     15,964

Cost Metrics:
  Cost per Token:         $0.000001
  Tokens per Dollar:      682,137
  Cost per Quality Point: $0.00027

Estimated Cost Breakdown:
  Researcher:    $0.0047 (20%)
  Specialists:   $0.0117 (50%)
    - Financial: $0.0040
    - Market:    $0.0040
    - Product:   $0.0037
  Synthesizer:   $0.0047 (20%)
  Quality Check: $0.0023 (10%)
```

### Batch Cost Analysis

```python
from examples.cost_analysis import batch_cost_analysis

# Analyze costs across multiple companies
batch_analysis = batch_cost_analysis([
    "Microsoft",
    "Tesla",
    "OpenAI"
])
```

**Output**:

```
======================================================================
AGGREGATE STATISTICS
======================================================================

Companies Analyzed: 3

Cost Summary:
  Total Cost:     $0.0678
  Average Cost:   $0.0226
  Min Cost:       $0.0198
  Max Cost:       $0.0256

Token Summary:
  Total Tokens:   46,892
  Average Tokens: 15,631

Quality Summary:
  Average Quality: 83.7/100
  Min Quality:     78.0/100
  Max Quality:     88.0/100

Cost Efficiency:
  Average Cost per Quality Point: $0.00027
```

### Cost Optimization Tips

**1. Use Haiku for Simple Tasks**
- Claude 3.5 Haiku: $0.80/1M input tokens
- Claude 3.5 Sonnet: $3.00/1M input tokens
- 10x cost reduction for similar quality

**2. Reduce Search Results**
```python
# In config.py
search_results_per_query: int = 3  # Default
search_results_per_query: int = 2  # 33% cost reduction
```

**3. Optimize Prompts**
- Shorter prompts = fewer input tokens
- Focused questions = shorter output
- Remove unnecessary context

**4. Adjust Quality Target**
```python
# In quality/checker.py
target_quality_score: float = 85.0  # Default (2-3 iterations)
target_quality_score: float = 75.0  # Lower target (1-2 iterations)
```

**5. Selective Agent Execution**
- Only run agents needed for your use case
- Skip specialists if not needed
- Custom workflows with fewer agents

### When to Use

- Budget planning
- Cost optimization
- ROI analysis
- Comparing research approaches

---

## Advanced Usage

### Observability Integration

Track research sessions with AgentOps:

```python
from src.company_researcher.observability import track_research_session
from src.company_researcher.workflows.parallel_agent_research import research_company

# Track research with observability
with track_research_session(company_name="Tesla", tags=["production"]):
    result = research_company("Tesla")
    # Automatically tracked in AgentOps dashboard
```

**Benefits**:
- Session replay
- Performance metrics
- Error debugging
- Cost tracking

**Setup**: See [INSTALLATION.md - Observability](INSTALLATION.md#observability)

### Quality Foundation

Use source tracking and quality scoring:

```python
from src.company_researcher.quality.source_tracker import SourceTracker
from src.company_researcher.quality.source_assessor import SourceQualityAssessor
from src.company_researcher.quality.models import Source, ResearchFact

# Initialize tracker
tracker = SourceTracker()

# Assess source quality
assessor = SourceQualityAssessor()
source = Source(
    url="https://www.sec.gov/...",
    title="Tesla 10-K Filing"
)
assessor.assess_source(source)
# source.quality = OFFICIAL, quality_score = 100

# Track fact
fact = ResearchFact(
    content="Tesla revenue: $81.5B in 2023",
    source=source,
    extracted_by="financial"
)
assessor.assess_fact(fact)
# fact.confidence = HIGH

tracker.add_fact(fact)

# Generate quality report
report = tracker.calculate_quality_score()
print(f"Overall Quality: {report.overall_score}/100")
```

**Benefits**:
- Source attribution (100%)
- Automatic confidence levels
- Multi-factor quality scoring
- Quality improvement tracking

### Custom State Management

Create custom state for specialized workflows:

```python
from typing import TypedDict, Annotated
from langgraph.graph import add

class CustomState(TypedDict):
    """Custom state with additional fields."""
    # Standard fields
    company_name: str
    search_results: Annotated[list, add]

    # Custom fields
    sentiment_score: float
    risk_level: str
    compliance_status: dict
```

### Parallel Workflows

Run multiple research workflows concurrently:

```python
import asyncio
from src.company_researcher.workflows.parallel_agent_research import research_company

async def parallel_research(companies: list):
    """Research multiple companies concurrently."""
    tasks = [
        asyncio.to_thread(research_company, company)
        for company in companies
    ]
    results = await asyncio.gather(*tasks)
    return dict(zip(companies, results))

# Execute
companies = ["Microsoft", "Tesla", "Stripe"]
results = asyncio.run(parallel_research(companies))
```

---

## Next Steps

- [Architecture Documentation](ARCHITECTURE.md) - System design
- [Implementation Guide](IMPLEMENTATION.md) - Code walkthrough
- [Agent Development Guide](AGENT_DEVELOPMENT.md) - Creating agents
- [API Reference](API_REFERENCE.md) - Complete API docs

For questions or issues, see [FAQ](FAQ.md) or [Troubleshooting](TROUBLESHOOTING.md).
