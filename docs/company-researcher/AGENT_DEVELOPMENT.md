# Agent Development Guide

Step-by-step guide to creating new specialist agents for the Company Researcher system.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Table of Contents

- [Overview](#overview)
- [Agent Architecture](#agent-architecture)
- [Creating a New Agent](#creating-a-new-agent)
- [Agent Node Pattern](#agent-node-pattern)
- [Prompt Engineering for Agents](#prompt-engineering-for-agents)
- [Testing Agents](#testing-agents)
- [Integration with Workflow](#integration-with-workflow)
- [Example: News Agent](#example-news-agent)
- [Best Practices](#best-practices)

---

## Overview

### What is an Agent?

In the Company Researcher system, an **agent** is a specialized node in the LangGraph workflow that:

1. **Receives state** as input
2. **Performs a specific task** (search, analysis, synthesis)
3. **Returns state updates** as output
4. **Tracks its own costs** and metrics

Agents are **pure functions**: `(state) → {updates}`

### Types of Agents

| Type | Purpose | Example |
|------|---------|---------|
| **Researcher** | Find and gather sources | Researcher Agent |
| **Specialist** | Extract domain-specific data | Financial, Market, Product |
| **Synthesizer** | Combine multiple inputs | Synthesizer Agent |
| **Quality** | Evaluate and score | Quality Check |

### Current Agents (Phase 4)

1. **Researcher** (`agents/researcher.py`): Query generation + search execution
2. **Financial** (`agents/financial.py`): Revenue, profitability, funding
3. **Market** (`agents/market.py`): Market size, trends, competition
4. **Product** (`agents/product.py`): Products, services, technology
5. **Synthesizer** (`agents/synthesizer.py`): Combine all specialist insights

---

## Agent Architecture

### Agent Node Function Signature

```python
def agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Standard agent node signature.

    Args:
        state: Current workflow state (read-only)

    Returns:
        Dict with partial state updates
    """
```

### Input: OverallState

Agents receive the **entire workflow state** but should only read what they need:

```python
def my_agent_node(state: OverallState) -> Dict[str, Any]:
    # Read what you need
    company_name = state["company_name"]
    search_results = state.get("search_results", [])
    missing_info = state.get("missing_info", [])

    # Don't modify state directly!
    # Return updates instead
```

### Output: State Updates

Agents return a **dictionary of state updates**:

```python
return {
    # Agent-specific output
    "agent_outputs": {
        "my_agent": {
            "analysis": "...",
            "cost": 0.01,
            "data_extracted": True
        }
    },

    # Cost tracking
    "total_cost": 0.01,

    # Token tracking
    "total_tokens": {
        "input": 100,
        "output": 50
    }
}
```

LangGraph **merges these updates** into the overall state using the defined reducers.

---

## Creating a New Agent

### Step 1: Define the Agent's Purpose

**Example**: Create a **News Agent** that finds recent news and developments.

**Purpose**:
- Extract recent news (last 6 months)
- Identify major announcements
- Track product launches
- Note executive changes
- Summarize key developments

### Step 2: Create the Agent File

**File**: `src/company_researcher/agents/news.py`

```python
"""
News Agent - Extracts recent news and developments.

This agent specializes in:
- Recent news and announcements
- Product launches
- Executive changes
- Major developments
- Timeline of key events
"""

from typing import Dict, Any
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState
```

### Step 3: Write the Prompt

Add your agent's prompt to `prompts.py`:

```python
# File: src/company_researcher/prompts.py

NEWS_ANALYSIS_PROMPT = """You are a news analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL recent news and developments from these search results.

Focus on:
1. **Recent Announcements** (last 6 months): Product launches, partnerships, acquisitions
2. **Executive Changes**: New hires, departures, promotions
3. **Major Milestones**: Funding rounds, IPO, expansion
4. **Product News**: New features, releases, updates
5. **Industry Impact**: Awards, recognition, controversies

Requirements:
- Focus on recent information (2024-2025)
- Include specific dates when available
- Cite sources for each news item
- Note significance/impact of each development
- Chronological order (most recent first)

Output format:
## Recent Developments (2024-2025)

### [Date] - [Headline]
- **What**: [Description]
- **Significance**: [Why it matters]
- **Source**: [URL or source title]

Extract the news data now:"""
```

### Step 4: Implement the Agent Node

```python
# File: src/company_researcher/agents/news.py

from ..prompts import NEWS_ANALYSIS_PROMPT

def news_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    News Agent Node: Extract recent news and developments.

    This specialized agent focuses on recent announcements,
    product launches, and key developments.

    Args:
        state: Current workflow state

    Returns:
        State update with news analysis
    """
    print("\n" + "=" * 60)
    print("[AGENT: News] Analyzing recent developments...")
    print("=" * 60)

    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    # Extract inputs
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    # Validate inputs
    if not search_results:
        print("[News] WARNING: No search results to analyze!")
        return {
            "agent_outputs": {
                "news": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[News] Analyzing {len(search_results)} sources for news...")

    # Format search results
    formatted_results = "\n\n".join([
        f"Source {i+1}: {result.get('title', 'N/A')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"Content: {result.get('content', 'N/A')[:500]}..."
        for i, result in enumerate(search_results[:15])
    ])

    # Create prompt
    prompt = NEWS_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1000,  # More tokens for comprehensive news
        temperature=0.0,  # Deterministic for factual extraction
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract analysis
    news_analysis = response.content[0].text

    # Calculate cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[News] Analysis complete")
    print(f"[News] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # Track agent output
    agent_output = {
        "analysis": news_analysis,
        "data_extracted": True,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    # Return state updates
    # Reducers will handle merging/accumulation automatically
    return {
        "agent_outputs": {"news": agent_output},  # merge_dicts reducer
        "total_cost": cost,                        # add reducer
        "total_tokens": {                          # add_tokens reducer
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
```

### Step 5: Export the Agent

Add your agent to `agents/__init__.py`:

```python
# File: src/company_researcher/agents/__init__.py

from .researcher import researcher_agent_node
from .financial import financial_agent_node
from .market import market_agent_node
from .product import product_agent_node
from .synthesizer import synthesizer_agent_node
from .news import news_agent_node  # Add this line

__all__ = [
    "researcher_agent_node",
    "financial_agent_node",
    "market_agent_node",
    "product_agent_node",
    "synthesizer_agent_node",
    "news_agent_node",  # Add this line
]
```

---

## Agent Node Pattern

### Required Components

Every agent node should have:

1. **Logging**: Print agent status
2. **Config Access**: Get API keys and settings
3. **Input Extraction**: Read from state
4. **Input Validation**: Handle missing data gracefully
5. **LLM Call**: Perform the agent's task
6. **Cost Calculation**: Track costs
7. **State Updates**: Return partial updates

### Template

```python
def template_agent_node(state: OverallState) -> Dict[str, Any]:
    """Agent description"""

    # 1. Logging
    print("\n" + "=" * 60)
    print("[AGENT: Template] Starting...")
    print("=" * 60)

    # 2. Config access
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    # 3. Input extraction
    company_name = state["company_name"]
    data = state.get("search_results", [])

    # 4. Input validation
    if not data:
        print("[Template] WARNING: No data to analyze!")
        return {
            "agent_outputs": {
                "template": {
                    "analysis": "No data available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    # 5. LLM call
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text

    # 6. Cost calculation
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print(f"[Template] Agent complete - ${cost:.4f}")
    print("=" * 60)

    # 7. State updates
    return {
        "agent_outputs": {
            "template": {
                "analysis": result,
                "data_extracted": True,
                "cost": cost,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
        },
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
```

---

## Prompt Engineering for Agents

### Effective Prompt Structure

```python
AGENT_PROMPT = """You are a [role] reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: [Clear task description]

Focus on:
1. [Specific focus area 1]
2. [Specific focus area 2]
3. [Specific focus area 3]

Requirements:
- [Specific requirement 1]
- [Specific requirement 2]
- [Include sources/citations]
- [Note if data is missing]

Output format:
[Show exact format you want]

[Task instruction]:"""
```

### Prompt Engineering Tips

1. **Be Specific**:
   - Bad: "Analyze the company"
   - Good: "Extract revenue figures, funding rounds, and valuation with specific dates"

2. **Provide Structure**:
   - Give clear sections to fill
   - Show example format
   - Number your focus areas

3. **Require Sources**:
   - Always ask for citation
   - Request specific dates
   - Note when data is unavailable

4. **Control Output Format**:
   - Markdown for consistency
   - JSON for structured data
   - Bullet points for lists

5. **Set Temperature**:
   - `0.0` for factual extraction
   - `0.3-0.5` for creative synthesis
   - `0.7+` for query generation

### Example: Financial Agent Prompt

```python
FINANCIAL_ANALYSIS_PROMPT = """You are a financial analyst reviewing search results.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL financial data and metrics from these search results.

Focus on:
1. **Revenue**: Annual revenue, quarterly revenue, revenue growth
2. **Funding**: Total funding raised, valuation, recent rounds
3. **Profitability**: Operating income, net income, profit margins
4. **Market Value**: Market cap (if public), valuation (if private)

Requirements:
- Be specific with numbers and dates
- Include sources for each data point
- Note if data is missing or unavailable
- Format as bullet points

Output format:
- Revenue: [specific figures with years]
- Funding: [total raised, rounds, investors]
- Valuation/Market Cap: [amount and date]
- Profitability: [operating income, net income]

Extract the financial data now:"""
```

---

## Testing Agents

### Standalone Agent Testing

Create a test file to run your agent in isolation:

```python
# File: tests/test_news_agent.py

from company_researcher.state import create_initial_state
from company_researcher.agents.news import news_agent_node


def test_news_agent():
    """Test news agent with mock data"""

    # Create mock state
    state = create_initial_state("Tesla")

    # Add mock search results
    state["search_results"] = [
        {
            "title": "Tesla Announces Cybertruck Delivery",
            "url": "https://example.com/tesla-cybertruck",
            "content": "Tesla began Cybertruck deliveries in December 2024..."
        },
        {
            "title": "Elon Musk Discusses Q4 2024 Earnings",
            "url": "https://example.com/tesla-q4",
            "content": "Tesla reported Q4 2024 revenue of $25.2B..."
        }
    ]

    # Run agent
    updates = news_agent_node(state)

    # Check outputs
    assert "agent_outputs" in updates
    assert "news" in updates["agent_outputs"]
    assert updates["agent_outputs"]["news"]["data_extracted"] is True
    assert updates["total_cost"] > 0

    # Print analysis
    print("\n" + "=" * 60)
    print("NEWS ANALYSIS")
    print("=" * 60)
    print(updates["agent_outputs"]["news"]["analysis"])
    print(f"\nCost: ${updates['total_cost']:.4f}")


if __name__ == "__main__":
    test_news_agent()
```

Run the test:
```bash
python tests/test_news_agent.py
```

### Integration Testing

Test the agent in the full workflow:

```python
# File: tests/test_workflow_with_news.py

from company_researcher.workflows.parallel_agent_research import research_company


def test_workflow_with_news():
    """Test complete workflow with news agent"""

    # Run research
    result = research_company("Tesla")

    # Check that news agent ran
    # (After integrating news agent into workflow)

    assert result["success"]
    assert result["metrics"]["cost_usd"] < 0.20
    print(f"\nReport: {result['report_path']}")
```

---

## Integration with Workflow

### Step 1: Import the Agent

**File**: `workflows/parallel_agent_research.py`

```python
from ..agents import (
    researcher_agent_node,
    financial_agent_node,
    market_agent_node,
    product_agent_node,
    news_agent_node,  # Add this
    synthesizer_agent_node
)
```

### Step 2: Add Node to Graph

```python
def create_parallel_agent_workflow() -> StateGraph:
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add all nodes
    workflow.add_node("researcher", researcher_agent_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("product", product_agent_node)
    workflow.add_node("news", news_agent_node)  # Add this
    workflow.add_node("synthesizer", synthesizer_agent_node)
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("save_report", save_report_node)

    # ... edges ...
```

### Step 3: Add Edges (Parallel Execution)

```python
    # Fan out to specialists (PARALLEL)
    workflow.add_edge("researcher", "financial")
    workflow.add_edge("researcher", "market")
    workflow.add_edge("researcher", "product")
    workflow.add_edge("researcher", "news")  # Add this

    # Fan in to synthesizer (waits for all)
    workflow.add_edge("financial", "synthesizer")
    workflow.add_edge("market", "synthesizer")
    workflow.add_edge("product", "synthesizer")
    workflow.add_edge("news", "synthesizer")  # Add this
```

**Result**: News agent now runs in parallel with other specialists!

### Step 4: Update Synthesizer (Optional)

If you want the synthesizer to explicitly use news analysis:

```python
# File: agents/synthesizer.py

def synthesizer_agent_node(state: OverallState) -> Dict[str, Any]:
    agent_outputs = state.get("agent_outputs", {})

    financial_analysis = agent_outputs.get("financial", {}).get("analysis", "")
    market_analysis = agent_outputs.get("market", {}).get("analysis", "")
    product_analysis = agent_outputs.get("product", {}).get("analysis", "")
    news_analysis = agent_outputs.get("news", {}).get("analysis", "")  # Add this

    # Include news in synthesis prompt
    prompt = f"""
    Synthesize this company research:

    Financial Analysis:
    {financial_analysis}

    Market Analysis:
    {market_analysis}

    Product Analysis:
    {product_analysis}

    Recent News:
    {news_analysis}

    Create a comprehensive company overview...
    """
```

---

## Example: News Agent

Full implementation of the News Agent:

**File**: `src/company_researcher/agents/news.py`

```python
"""
News Agent - Extracts recent news and developments.

This agent specializes in:
- Recent announcements (last 6 months)
- Product launches and updates
- Executive changes and hires
- Major milestones and achievements
- Timeline of key developments
"""

from typing import Dict, Any
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState
from ..prompts import NEWS_ANALYSIS_PROMPT


def news_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    News Agent Node: Extract recent news and developments.

    Args:
        state: Current workflow state

    Returns:
        State update with news analysis
    """
    print("\n" + "=" * 60)
    print("[AGENT: News] Analyzing recent developments...")
    print("=" * 60)

    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[News] WARNING: No search results to analyze!")
        return {
            "agent_outputs": {
                "news": {
                    "analysis": "No search results available",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    print(f"[News] Analyzing {len(search_results)} sources...")

    # Format search results
    formatted_results = "\n\n".join([
        f"Source {i+1}: {result.get('title', 'N/A')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"Content: {result.get('content', 'N/A')[:500]}..."
        for i, result in enumerate(search_results[:15])
    ])

    # Create prompt
    prompt = NEWS_ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    news_analysis = response.content[0].text
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[News] Analysis complete")
    print(f"[News] Agent complete - ${cost:.4f}")
    print("=" * 60)

    return {
        "agent_outputs": {
            "news": {
                "analysis": news_analysis,
                "data_extracted": True,
                "cost": cost,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
        },
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
```

---

## Best Practices

### 1. Single Responsibility
Each agent should have ONE clear purpose:
- ✅ Good: "Extract financial metrics"
- ❌ Bad: "Extract financial metrics and analyze market trends"

### 2. Graceful Degradation
Always handle missing data:
```python
if not search_results:
    return {
        "agent_outputs": {
            "agent_name": {
                "analysis": "No data available",
                "data_extracted": False,
                "cost": 0.0
            }
        }
    }
```

### 3. Cost Awareness
Minimize costs:
- Limit input tokens (trim search results)
- Use appropriate max_tokens
- Use Haiku for simple tasks
- Cache common prompts (future)

### 4. Deterministic Extraction
Use `temperature=0.0` for factual extraction:
```python
response = client.messages.create(
    model=config.llm_model,
    temperature=0.0,  # Deterministic
    messages=[...]
)
```

### 5. Structured Output
Request structured output for easier parsing:
- Markdown sections
- JSON when needed
- Consistent formatting

### 6. Source Attribution
Always track sources:
```python
"Output format:\n"
"- Fact: [specific fact]\n"
"- Source: [URL or title]\n"
```

### 7. Logging
Log key information:
```python
print("[Agent] Starting...")
print(f"[Agent] Analyzing {len(data)} sources...")
print(f"[Agent] Agent complete - ${cost:.4f}")
```

### 8. Testing
Test agents independently before integration:
- Unit tests with mock data
- Integration tests in workflow
- Cost and performance testing

---

## Future Agent Ideas

From the [Master 20-Phase Plan](../planning/MASTER_20_PHASE_PLAN.md):

**Phases 7-10: Critical Specialists**
- Enhanced Financial Agent (Phase 7)
- Market Analyst Agent (Phase 8)
- Competitor Scout Agent (Phase 9)
- Logic Critic Agent (Phase 10)

**Phases 13-15: Additional Specialists**
- Deep Research Agent (Phase 13)
- Reasoning Agent (Phase 13)
- Brand Auditor Agent (Phase 14)
- Social Media Agent (Phase 14)
- Sales Intelligence Agent (Phase 15)
- Investment Scout Agent (Phase 15)

**Advanced Agents**
- Fact Verification Agent (Phase 16)
- Contradiction Detection Agent (Phase 16)
- Gap Identification Agent (Phase 17)
- Completeness Validator (Phase 17)

---

## Next Steps

1. **Try Creating an Agent**: Start with a simple agent like News
2. **Test Independently**: Use standalone tests first
3. **Integrate**: Add to workflow when ready
4. **Optimize**: Monitor costs and improve prompts
5. **Expand**: Create more specialized agents

**See Also**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Code structure
- [API_REFERENCE.md](API_REFERENCE.md) - Function signatures

---

**Last Updated**: December 5, 2025
**Version**: 0.4.0 (Phase 4 Complete)
