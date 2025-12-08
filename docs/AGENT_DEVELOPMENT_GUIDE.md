# Agent Development Guide

This guide documents the architecture patterns for creating agents in the Company Researcher system.

## Overview

The codebase supports three primary patterns for implementing agents:

| Pattern | Use Case | Base Class | Example |
|---------|----------|------------|---------|
| **BaseSpecialistAgent** | Standard analysis agents with search results | `BaseSpecialistAgent[T]` + `ParsingMixin` | BrandAuditorAgent |
| **@agent_node Decorator** | Simple agents with boilerplate reduction | `@agent_node` decorator | ProductAgent |
| **Custom Class** | Complex agents with external APIs | Custom implementation | EnhancedFinancialAgent |

---

## Pattern 1: BaseSpecialistAgent (Recommended)

Use this pattern for specialist agents that:

- Take `company_name` and `search_results` as input
- Generate structured analysis output
- Don't require external API integrations

### Implementation Steps

#### 1. Define Your Result Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class MyAnalysisResult:
    """Result container for your analysis."""
    company_name: str
    score: float = 0.0
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analysis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "score": self.score,
            "insights": self.insights,
            "recommendations": self.recommendations
        }
```

#### 2. Define Your Prompt

```python
MY_ANALYSIS_PROMPT = """You are an expert analyst...

**COMPANY:** {company_name}

**AVAILABLE DATA:**
{search_results}

**TASK:** Perform comprehensive analysis.

**STRUCTURE YOUR ANALYSIS:**

### 1. Overview
...

### 2. Score
**Score:** [0-100]

### 3. Insights
1. [Insight 1]
2. [Insight 2]
...

### 4. Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
...

Begin your analysis:"""
```

#### 3. Create Your Agent Class

```python
from typing import List, Dict, Any
from ..base.specialist import BaseSpecialistAgent, ParsingMixin
from ...types import YourEnums  # Import from centralized types.py

class MyAnalysisAgent(BaseSpecialistAgent[MyAnalysisResult], ParsingMixin):
    """
    My Analysis Agent for [purpose].

    Inherits from:
    - BaseSpecialistAgent: Common agent functionality
    - ParsingMixin: Standardized extraction methods
    """

    # Required class attribute
    agent_name = "my_analysis"

    def _get_prompt(self, company_name: str, formatted_results: str) -> str:
        """Build the analysis prompt."""
        return MY_ANALYSIS_PROMPT.format(
            company_name=company_name,
            search_results=formatted_results
        )

    def _parse_analysis(
        self,
        company_name: str,
        analysis: str
    ) -> MyAnalysisResult:
        """Parse LLM analysis into structured result."""
        result = MyAnalysisResult(company_name=company_name)

        # Use ParsingMixin methods for extraction
        result.score = self.extract_score(analysis, "Score", default=50.0)
        result.insights = self.extract_list_items(analysis, "Insight", max_items=5)
        result.recommendations = self.extract_list_items(analysis, "Recommendation", max_items=5)
        result.analysis = analysis

        return result
```

#### 4. Create Node Function for Workflow Integration

```python
from ...state import OverallState
from ..base import get_agent_logger, create_empty_result
from ...config import get_config
from ...llm.client_factory import calculate_cost

def my_analysis_agent_node(state: OverallState) -> Dict[str, Any]:
    """Node function for workflow integration."""
    logger = get_agent_logger("my_analysis")
    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    with logger.agent_run(company_name):
        if not search_results:
            logger.no_data()
            return create_empty_result("my_analysis")

        logger.analyzing(len(search_results))

        agent = MyAnalysisAgent(config)
        result = agent.analyze(company_name, search_results)
        cost = calculate_cost(500, 1000)  # Estimate

        logger.info(f"Score: {result.score}")
        logger.complete(cost=cost)

        return {
            "agent_outputs": {
                "my_analysis": {
                    **result.to_dict(),
                    "analysis": result.analysis,
                    "cost": cost
                }
            },
            "total_cost": cost
        }
```

---

## Pattern 2: @agent_node Decorator

Use this pattern for simpler agents where you want maximum boilerplate reduction.

### Implementation

```python
from ..base import agent_node

@agent_node(
    agent_name="my_simple_agent",
    max_tokens=1000,
    temperature=0.0,
    max_sources=15,
    content_truncate_length=500
)
def my_simple_agent_node(
    state,
    logger,
    client,
    config,
    node_config,
    formatted_results,
    company_name
):
    """Simple agent using decorator pattern."""

    prompt = f"""Analyze {company_name} based on:
    {formatted_results}

    Provide your analysis..."""

    # The decorator handles LLM call boilerplate
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=node_config["max_tokens"],
        temperature=node_config["temperature"],
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse and return results
    analysis = response.content[0].text

    return {
        "agent_outputs": {
            "my_simple": {
                "analysis": analysis,
                "company_name": company_name
            }
        }
    }
```

---

## Pattern 3: Custom Class (External APIs)

Use this pattern for agents that integrate with external data sources like financial APIs,
competitor analysis tools, or other third-party services.

**Examples**: `EnhancedFinancialAgent`, `CompetitorScoutAgent`, `EnhancedMarketAgent`

### When to Use This Pattern

- Agent needs to fetch data from **external APIs** before LLM analysis
- Agent has **complex data gathering** logic (multiple sources)
- Agent requires **domain-specific helper functions**
- The complexity is in the **data pipeline**, not the LLM interaction

### Standard Interface

All custom agents should follow this interface for consistency:

```python
from typing import Optional, Callable, Any, Dict, List
from ...llm.client_factory import get_anthropic_client
from ...config import get_config
from ..base import get_agent_logger, create_empty_result

class MyEnhancedAgent:
    """Agent with external API integrations."""

    def __init__(
        self,
        search_tool: Optional[Callable] = None,
        llm_client: Optional[Any] = None
    ):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()
        # Initialize external clients
        self.external_api = MyExternalAPIClient()

    async def analyze(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform analysis with external data."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return my_enhanced_agent_node(state)


def create_my_enhanced_agent(
    search_tool: Callable = None,
    llm_client: Any = None
) -> MyEnhancedAgent:
    """Factory function to create agent instance."""
    return MyEnhancedAgent(search_tool=search_tool, llm_client=llm_client)
```

### Full Implementation Example

```python
"""
Enhanced Agent with External API Integration.

Integrates:
- External API data
- Web search results
- LLM analysis
"""

from typing import Dict, Any, Optional, Callable, List
import logging

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ...state import OverallState
from ..base import get_agent_logger, create_empty_result

logger = logging.getLogger(__name__)


# ==============================================================================
# Agent Class
# ==============================================================================

class MyEnhancedAgent:
    """Enhanced agent with external API integration."""

    def __init__(
        self,
        search_tool: Optional[Callable] = None,
        llm_client: Optional[Any] = None
    ):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform enhanced analysis."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return my_enhanced_agent_node(state)


def create_my_enhanced_agent(
    search_tool: Callable = None,
    llm_client: Any = None
) -> MyEnhancedAgent:
    """Factory function."""
    return MyEnhancedAgent(search_tool=search_tool, llm_client=llm_client)


# ==============================================================================
# Prompt
# ==============================================================================

ENHANCED_PROMPT = """You are an expert analyst with access to comprehensive data.

Company: {company_name}

**EXTERNAL DATA:**
{external_data_summary}

**SEARCH RESULTS:**
{search_results}

**TASK:** Provide comprehensive analysis combining all data sources.

Begin your analysis:"""


# ==============================================================================
# Node Function
# ==============================================================================

def my_enhanced_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced Agent Node with external data integration.

    Steps:
    1. Gather data from external APIs
    2. Combine with search results
    3. Generate LLM analysis
    4. Return structured output
    """
    logger = get_agent_logger("my_enhanced")
    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    with logger.agent_run(company_name):
        if not search_results:
            logger.no_data()
            return create_empty_result("my_enhanced")

        logger.analyzing(len(search_results))

        # 1. Gather external data
        external_data = gather_external_data(company_name)

        # 2. Create prompt
        prompt = create_analysis_prompt(
            company_name, external_data, search_results
        )

        # 3. Call LLM
        client = get_anthropic_client()
        response = client.messages.create(
            model=config.llm_model,
            max_tokens=config.llm_max_tokens,
            temperature=config.llm_temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = safe_extract_text(response, agent_name="my_enhanced")
        cost = calculate_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        logger.complete(cost=cost)

        # 4. Return structured output
        return {
            "agent_outputs": {
                "my_enhanced": {
                    "analysis": analysis,
                    "data_sources": external_data.get("sources_used", []),
                    "cost": cost,
                    "tokens": {
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens
                    }
                }
            },
            "total_cost": cost
        }


# ==============================================================================
# Helper Functions (Domain-Specific)
# ==============================================================================

def gather_external_data(company_name: str) -> Dict[str, Any]:
    """Gather data from external APIs."""
    data = {"sources_used": []}

    # Example: Fetch from external API
    try:
        # api_result = external_api.fetch(company_name)
        # data["external"] = api_result
        # data["sources_used"].append("external_api")
        pass
    except Exception as e:
        logger.warning(f"External API error: {e}")

    return data


def create_analysis_prompt(
    company_name: str,
    external_data: Dict[str, Any],
    search_results: List[Dict[str, Any]]
) -> str:
    """Create comprehensive analysis prompt."""
    # Format external data summary
    data_summary = format_external_data(external_data)

    # Format search results
    formatted_results = format_search_results(search_results)

    return ENHANCED_PROMPT.format(
        company_name=company_name,
        external_data_summary=data_summary,
        search_results=formatted_results
    )


def format_external_data(data: Dict[str, Any]) -> str:
    """Format external data for prompt."""
    # Domain-specific formatting
    return "External data summary..."


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for prompt."""
    if not results:
        return "No search results available."

    formatted = []
    for i, result in enumerate(results[:15], 1):
        formatted.append(
            f"Source {i}: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')[:400]}..."
        )
    return "\n\n".join(formatted)
```

### Key Differences from Other Patterns

| Aspect | BaseSpecialistAgent | @agent_node | Custom Class |
|--------|---------------------|-------------|--------------|
| External APIs | No | No | Yes |
| Data Gathering | Simple | Simple | Complex |
| Helper Functions | Few | None | Many |
| Code Reuse | High | Medium | Low |
| When to Use | Standard analysis | Simple extraction | API integrations |

---

## ParsingMixin Methods

The `ParsingMixin` provides standardized extraction methods:

### extract_list_items

```python
# Extract numbered or bulleted list items
items = self.extract_list_items(
    text=analysis,
    keyword="Recommendation",  # Section keyword
    max_items=5,
    min_length=10
)
```

### extract_score

```python
# Extract numeric scores from analysis
score = self.extract_score(
    text=analysis,
    label="Score",  # Label before the number
    default=50.0
)
```

### extract_section

```python
# Extract a section of text
section = self.extract_section(
    text=analysis,
    header="Investment Thesis",
    max_length=1000
)
```

### extract_keyword_list

```python
# Extract items containing a keyword
items = self.extract_keyword_list(
    text=analysis,
    keyword="risk",
    max_items=5
)
```

---

## Using Centralized Enums

Always import enums from `types.py` instead of defining locally:

```python
# Good - import from centralized location
from ...types import (
    BrandStrength,
    BrandHealth,
    LeadScore,
    BuyingStage,
    SocialPlatform,
    EngagementLevel
)

# Bad - don't define enums in agent files
class BrandStrength(str, Enum):  # DON'T DO THIS
    ...
```

---

## Configuration

Agents should use centralized configuration from `config.py`:

```python
from ...config import get_config

config = get_config()

# Access agent-specific settings
max_tokens = config.brand_auditor_max_tokens
temperature = config.analyst_temperature

# Access global settings
model = config.llm_model
api_key = config.anthropic_api_key
```

---

## Testing Your Agent

```python
# tests/unit/agents/test_my_agent.py
import pytest
from src.company_researcher.agents.specialized.my_agent import MyAnalysisAgent

def test_agent_creation():
    agent = MyAnalysisAgent()
    assert agent.agent_name == "my_analysis"

def test_parse_analysis():
    agent = MyAnalysisAgent()
    analysis = """
    ### Score
    **Score:** 75

    ### Insights
    1. First insight
    2. Second insight
    """
    result = agent._parse_analysis("TestCo", analysis)
    assert result.score == 75.0
    assert len(result.insights) >= 1
```

---

## Directory Structure

```
agents/
├── base/
│   ├── __init__.py          # Exports get_agent_logger, create_empty_result, agent_node
│   ├── node.py               # @agent_node decorator
│   ├── specialist.py         # BaseSpecialistAgent, ParsingMixin
│   └── search_formatting.py  # SearchResultFormatter
├── core/
│   ├── analyst.py
│   ├── researcher.py
│   └── synthesizer.py
├── financial/
│   ├── financial.py          # @agent_node pattern
│   ├── enhanced_financial.py # Custom class pattern
│   └── investment_analyst.py # ParsingMixin pattern
├── market/
│   ├── market.py             # @agent_node pattern
│   └── competitor_scout.py   # Custom class pattern
├── specialized/
│   ├── brand_auditor.py      # BaseSpecialistAgent pattern
│   ├── sales_intelligence.py # BaseSpecialistAgent pattern
│   ├── social_media.py       # BaseSpecialistAgent pattern
│   └── product.py            # @agent_node pattern
└── research/
    ├── deep_research.py
    └── reasoning.py
```

---

## Checklist for New Agents

- [ ] Choose appropriate pattern (BaseSpecialistAgent, decorator, or custom)
- [ ] Define result dataclass with `to_dict()` method
- [ ] Create analysis prompt with clear structure
- [ ] Import enums from `types.py` (not local definitions)
- [ ] Use `ParsingMixin` for extraction methods
- [ ] Create node function for workflow integration
- [ ] Use centralized config for parameters
- [ ] Add factory function for external instantiation
- [ ] Write unit tests
- [ ] Add to agent `__init__.py` exports
