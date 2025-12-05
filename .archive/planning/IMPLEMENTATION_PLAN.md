# Company Researcher System - Detailed Implementation Plan

**Project Duration:** 8-12 weeks
**Target:** Production-ready multi-agent company research system
**Based On:** LangGraph + Open Deep Research architecture

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [Detailed Agent Specifications](#detailed-agent-specifications)
5. [Data Flow & State Management](#data-flow--state-management)
6. [Quality Assurance Strategy](#quality-assurance-strategy)
7. [Deployment & Scaling](#deployment--scaling)
8. [Success Metrics](#success-metrics)

---

## Architecture Overview

### System Architecture (Inspired by Open Deep Research)

```
┌────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                      │
│  REST API  │  WebSocket  │  CLI Interface  │  Web Dashboard    │
└──────────────────────────┬─────────────────────────────────────┘
                           │
┌──────────────────────────┴─────────────────────────────────────┐
│                    Orchestration Layer                          │
│                   (LangGraph StateGraph)                        │
│                                                                 │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │ Clarification│ -->  │   Research   │ -->  │  Synthesis   │ │
│  │    Node      │      │ Coordinator  │      │    Node      │ │
│  └─────────────┘      └──────┬───────┘      └──────────────┘ │
│                               │                                 │
│  ┌────────────────────────────┴────────────────────────────┐  │
│  │         Multi-Agent Research Layer                       │  │
│  │   (Supervisor Pattern - 14 Specialized Agents)          │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Deep    │ │Financial │ │  Market  │ │Competitor│  │  │
│  │  │ Research │ │  Agent   │ │ Analyst  │ │  Scout   │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Brand   │ │  Sales   │ │Investment│ │  Social  │  │  │
│  │  │ Auditor  │ │  Agent   │ │  Agent   │ │  Media   │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Sector  │ │  Logic   │ │ Insight  │ │  Report  │  │  │
│  │  │ Analyst  │ │  Critic  │ │Generator │ │  Writer  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐                             │  │
│  │  │ Reasoning│ │ Generic  │                             │  │
│  │  │  Agent   │ │ Research │                             │  │
│  │  └──────────┘ └──────────┘                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                   Data & Tool Layer                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Tavily  │  │  Alpha   │  │ BuiltWith│  │ LinkedIn │   │
│  │  Search  │  │  Vantage │  │  Tech    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Glassdoor│  │  Reddit  │  │  Twitter │  │  YouTube │   │
│  │   API    │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   SEC    │  │  Crunch  │  │ App Store│                  │
│  │  Edgar   │  │  base    │  │  Reviews │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                  Persistence Layer                           │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL   │  │   Qdrant     │  │   Redis      │    │
│  │  (Metadata)   │  │  (Vector DB) │  │  (Cache)     │    │
│  └───────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│              Observability Layer                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  AgentOps    │  │  LangSmith   │  │  Prometheus  │     │
│  │  (Tracking)  │  │  (Debug)     │  │  (Metrics)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Framework
```yaml
Framework:
  - LangGraph: 0.2.45+ (workflow orchestration)
  - LangChain: 0.3.7+ (LLM abstraction)
  - Pydantic: 2.9+ (data validation)

LLM Providers:
  Primary: Anthropic Claude 3.5 Sonnet (reasoning, extraction)
  Secondary: OpenAI GPT-4o-mini (summarization, cost-effective)
  Fallback: Google Gemini 1.5 Pro (backup)

State Management:
  - Python dataclasses
  - Pydantic models
  - TypedDict for complex states
```

### Data & Tools
```yaml
Search & Web:
  - Tavily API (primary search)
  - Anthropic native search (backup)
  - Playwright (web scraping)
  - BeautifulSoup4 (HTML parsing)

Financial Data:
  - Alpha Vantage (stock data)
  - SEC Edgar API (filings)
  - Yahoo Finance (market data)

Social & Reviews:
  - Reddit API (sentiment)
  - Twitter/X API (brand monitoring)
  - App Store Connect API (app reviews)
  - Glassdoor API (employer data)

Tech Intelligence:
  - BuiltWith API (tech stack)
  - Wappalyzer (technologies)
  - GitHub API (open source activity)

Business Data:
  - Crunchbase API (funding)
  - LinkedIn API (people/org data)
  - Clearbit (enrichment)
```

### Storage & Caching
```yaml
Database:
  - PostgreSQL 16+ (metadata, research history)
  - Qdrant (vector search, semantic memory)
  - Redis (caching, rate limiting)

Memory:
  - LangMem (long-term learning)
  - Embeddings: OpenAI text-embedding-3-small
```

### Observability
```yaml
Monitoring:
  - AgentOps (agent tracking, session replay)
  - LangSmith (LLM debugging)
  - Prometheus (system metrics)
  - Grafana (visualization)

Logging:
  - Structlog (structured logging)
  - Sentry (error tracking)
```

### API & Interface
```yaml
Backend:
  - FastAPI (REST API)
  - WebSocket (real-time updates)
  - Celery (background tasks)

Frontend (Future):
  - Next.js 15+
  - React 19+
  - Tailwind CSS
  - shadcn/ui components

CLI:
  - Typer (command-line interface)
  - Rich (terminal formatting)
```

---

## Phase-by-Phase Implementation

### Phase 1: Foundation & Basic Workflow (Weeks 1-2)

**Goal:** Get a single company research working end-to-end

#### 1.1 Project Setup
```bash
# Create project structure
company-researcher-system/
├── src/
│   ├── company_researcher/
│   │   ├── __init__.py
│   │   ├── agents/          # Agent definitions
│   │   ├── workflows/       # LangGraph workflows
│   │   ├── tools/           # Tool integrations
│   │   ├── state.py         # State schemas
│   │   ├── config.py        # Configuration
│   │   └── prompts.py       # All prompts
│   └── api/                 # FastAPI application
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── configs/
│   ├── agents.yaml
│   └── models.yaml
├── outputs/                 # Research reports
├── pyproject.toml
├── README.md
└── .env.example
```

#### 1.2 Core Dependencies
```toml
# pyproject.toml
[project]
name = "company-researcher-system"
version = "0.1.0"
dependencies = [
    "langgraph>=0.2.45",
    "langchain>=0.3.7",
    "langchain-anthropic>=0.3.0",
    "langchain-openai>=0.3.0",
    "pydantic>=2.9.0",
    "tavily-python>=0.5.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "asyncio>=3.4.3",
    "aiohttp>=3.10.0",
    "python-dotenv>=1.0.0",
    "structlog>=24.4.0",
    "rich>=13.9.0",
    "typer>=0.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "agentops>=0.3.0",
    "langsmith>=0.1.0",
]
```

#### 1.3 Basic State Schema
```python
# src/company_researcher/state.py
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal
import operator

@dataclass
class InputState:
    """External API input"""
    company_name: str
    industry: str | None = None
    focus_areas: list[str] = field(default_factory=list)  # e.g., ["financial", "competitive"]
    depth: Literal["quick", "standard", "deep"] = "standard"

@dataclass
class ResearchState:
    """Internal workflow state"""
    # Input
    company_name: str
    industry: str | None = None
    focus_areas: list[str] = field(default_factory=list)
    depth: str = "standard"

    # Research planning
    research_plan: dict[str, Any] | None = None
    search_queries: list[str] = field(default_factory=list)

    # Research execution
    search_results: Annotated[list, operator.add] = field(default_factory=list)
    research_notes: Annotated[list, operator.add] = field(default_factory=list)

    # Extraction
    extracted_data: dict[str, Any] = field(default_factory=dict)

    # Quality check
    quality_score: float = 0.0
    completeness_score: float = 0.0
    missing_areas: list[str] = field(default_factory=list)
    is_satisfactory: bool = False

    # Metadata
    iteration: int = 0
    max_iterations: int = 3
    total_cost: float = 0.0
    sources: Annotated[list, operator.add] = field(default_factory=list)

@dataclass
class OutputState:
    """External API output"""
    company_name: str
    report: dict[str, Any]
    metadata: dict[str, Any]
    sources: list[dict[str, str]]
```

#### 1.4 Simple Research Workflow (3-Phase Pattern)
```python
# src/company_researcher/workflows/basic_research.py
from langgraph.graph import StateGraph, START, END
from company_researcher.state import ResearchState
from company_researcher.agents.researcher import BasicResearcher
from langchain_anthropic import ChatAnthropic
from tavily import TavilyClient
import asyncio

class BasicResearchWorkflow:
    """Simple 3-phase research workflow"""

    def __init__(self, config: dict):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.0
        )
        self.tavily = TavilyClient(api_key=config["tavily_api_key"])

    def generate_queries(self, state: ResearchState) -> dict:
        """Phase 1: Generate targeted search queries"""
        prompt = f"""Generate 5 targeted search queries to research {state.company_name}.

Company: {state.company_name}
Industry: {state.industry or "Unknown"}
Focus areas: {", ".join(state.focus_areas) if state.focus_areas else "General overview"}

Generate queries that will find:
1. Company overview and mission
2. Financial information (revenue, funding)
3. Products and services
4. Competitive landscape
5. Recent news and developments

Return as JSON array: ["query1", "query2", ...]"""

        response = self.llm.invoke(prompt)
        queries = eval(response.content)  # In production, use structured output

        return {
            "search_queries": queries,
            "iteration": state.iteration + 1
        }

    async def conduct_research(self, state: ResearchState) -> dict:
        """Phase 2: Execute searches in parallel"""

        async def search_single(query: str):
            result = await asyncio.to_thread(
                self.tavily.search,
                query=query,
                max_results=3
            )
            return result

        # Parallel search execution
        search_tasks = [search_single(q) for q in state.search_queries]
        results = await asyncio.gather(*search_tasks)

        # Take notes on results
        notes = self.llm.invoke(f"""Analyze these search results and take notes:

Results: {results}

Focus on:
- Key facts about the company
- Financial metrics
- Products/services
- Market position
- Recent developments

Return concise notes.""").content

        # Track sources
        sources = []
        for result in results:
            for item in result.get("results", []):
                sources.append({
                    "url": item["url"],
                    "title": item["title"],
                    "retrieved_at": item.get("published_date", "")
                })

        return {
            "search_results": [results],
            "research_notes": [notes],
            "sources": sources
        }

    def extract_information(self, state: ResearchState) -> dict:
        """Phase 3: Extract structured information"""

        # Define extraction schema
        schema = {
            "company_overview": {
                "name": "string",
                "industry": "string",
                "founded": "string",
                "headquarters": "string",
                "description": "string"
            },
            "financial_metrics": {
                "revenue": "string",
                "funding": "string",
                "employees": "string"
            },
            "products_services": ["string"],
            "key_people": [{"name": "string", "role": "string"}],
            "competitors": ["string"]
        }

        prompt = f"""Extract structured information from these research notes:

Notes: {state.research_notes}

Extract according to this schema:
{schema}

Return valid JSON matching the schema."""

        response = self.llm.invoke(prompt)
        extracted = eval(response.content)  # Use structured output in production

        return {"extracted_data": extracted}

    def reflect_on_quality(self, state: ResearchState) -> dict:
        """Phase 4: Quality check and decide if more research needed"""

        prompt = f"""Evaluate the quality and completeness of this research:

Extracted Data: {state.extracted_data}
Iteration: {state.iteration} / {state.max_iterations}

Assess:
1. Completeness (0-100): Are all key areas covered?
2. Quality (0-100): Is the information specific and useful?
3. Missing areas: What critical information is missing?

Return JSON:
{{
  "completeness_score": 0-100,
  "quality_score": 0-100,
  "missing_areas": ["area1", "area2"],
  "is_satisfactory": true/false,
  "follow_up_queries": ["query1", "query2"] (if not satisfactory)
}}"""

        response = self.llm.invoke(prompt)
        reflection = eval(response.content)

        # Check if we should continue
        is_satisfactory = (
            reflection["is_satisfactory"] or
            state.iteration >= state.max_iterations
        )

        return {
            "completeness_score": reflection["completeness_score"] / 100,
            "quality_score": reflection["quality_score"] / 100,
            "missing_areas": reflection["missing_areas"],
            "is_satisfactory": is_satisfactory,
            "search_queries": reflection.get("follow_up_queries", [])
        }

    def build_graph(self) -> StateGraph:
        """Build the workflow graph"""

        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("generate_queries", self.generate_queries)
        workflow.add_node("conduct_research", self.conduct_research)
        workflow.add_node("extract_information", self.extract_information)
        workflow.add_node("reflect_on_quality", self.reflect_on_quality)

        # Add edges
        workflow.add_edge(START, "generate_queries")
        workflow.add_edge("generate_queries", "conduct_research")
        workflow.add_edge("conduct_research", "extract_information")
        workflow.add_edge("extract_information", "reflect_on_quality")

        # Conditional routing
        def should_continue(state: ResearchState) -> str:
            if state.is_satisfactory:
                return END
            else:
                return "conduct_research"  # Loop back for more research

        workflow.add_conditional_edges(
            "reflect_on_quality",
            should_continue
        )

        return workflow.compile()

# Usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()

    config = {
        "tavily_api_key": os.getenv("TAVILY_API_KEY")
    }

    workflow = BasicResearchWorkflow(config)
    app = workflow.build_graph()

    # Run research
    result = app.invoke(ResearchState(
        company_name="Tesla",
        industry="Automotive",
        focus_areas=["financial", "products"]
    ))

    print(f"\n=== Research Complete ===")
    print(f"Company: {result.company_name}")
    print(f"Quality: {result.quality_score:.1%}")
    print(f"Completeness: {result.completeness_score:.1%}")
    print(f"Iterations: {result.iteration}")
    print(f"\n=== Extracted Data ===")
    print(result.extracted_data)
    print(f"\n=== Sources ({len(result.sources)}) ===")
    for source in result.sources[:5]:
        print(f"- {source['title']}: {source['url']}")
```

**Phase 1 Deliverables:**
- ✅ Project structure set up
- ✅ Basic 3-phase workflow working
- ✅ Can research 1 company end-to-end
- ✅ Quality reflection loop implemented
- ✅ Source tracking working

**Time Estimate:** 1-2 weeks

---

### Phase 2: Multi-Agent Supervisor Architecture (Weeks 3-4)

**Goal:** Implement supervisor pattern with multiple specialized researchers

#### 2.1 Supervisor Pattern Implementation
```python
# src/company_researcher/workflows/supervisor_research.py
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import Literal

@dataclass
class SupervisorState:
    """Supervisor workflow state"""
    company_name: str
    industry: str | None = None

    # Supervisor planning
    research_plan: dict[str, Any] | None = None
    assigned_agents: list[str] = field(default_factory=list)

    # Agent results
    agent_results: dict[str, Any] = field(default_factory=dict)

    # Synthesis
    synthesized_report: dict[str, Any] | None = None

    # Metadata
    iteration: int = 0
    is_complete: bool = False

class SupervisorWorkflow:
    """Multi-agent supervisor workflow"""

    def __init__(self, config: dict):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.config = config

        # Agent registry
        self.agents = {
            "deep_researcher": DeepResearchAgent(config),
            "financial_agent": FinancialAgent(config),
            "market_analyst": MarketAnalystAgent(config),
            "competitor_scout": CompetitorScoutAgent(config),
        }

    def create_research_plan(self, state: SupervisorState) -> dict:
        """Supervisor creates research plan and assigns agents"""

        prompt = f"""You are a research supervisor coordinating a team.

Task: Research {state.company_name} in {state.industry or "unknown industry"}

Available agents:
- deep_researcher: General background research, web scraping
- financial_agent: Financial metrics, revenue, funding
- market_analyst: Market size, trends, positioning
- competitor_scout: Competitive landscape, tech stack

Create a research plan:
1. Which agents should work on this?
2. What specific tasks should each agent do?
3. In what order (parallel or sequential)?

Return JSON:
{{
  "assigned_agents": ["agent1", "agent2"],
  "tasks": {{
    "agent1": "specific task description",
    "agent2": "specific task description"
  }},
  "execution_mode": "parallel" or "sequential"
}}"""

        response = self.llm.invoke(prompt)
        plan = eval(response.content)

        return {
            "research_plan": plan,
            "assigned_agents": plan["assigned_agents"]
        }

    async def execute_research(self, state: SupervisorState) -> dict:
        """Execute research with assigned agents"""

        plan = state.research_plan

        if plan["execution_mode"] == "parallel":
            # Parallel execution
            tasks = []
            for agent_name in state.assigned_agents:
                agent = self.agents[agent_name]
                task_desc = plan["tasks"][agent_name]
                tasks.append(agent.research(state.company_name, task_desc))

            results = await asyncio.gather(*tasks)

        else:
            # Sequential execution
            results = []
            for agent_name in state.assigned_agents:
                agent = self.agents[agent_name]
                task_desc = plan["tasks"][agent_name]
                result = await agent.research(state.company_name, task_desc)
                results.append(result)

        # Organize results by agent
        agent_results = {}
        for agent_name, result in zip(state.assigned_agents, results):
            agent_results[agent_name] = result

        return {"agent_results": agent_results}

    def synthesize_results(self, state: SupervisorState) -> dict:
        """Synthesize all agent results into final report"""

        prompt = f"""Synthesize research from multiple agents into a comprehensive report.

Company: {state.company_name}

Agent Results:
{state.agent_results}

Create a structured report with:
1. Executive Summary
2. Company Overview
3. Financial Analysis
4. Market Position
5. Competitive Landscape
6. Key Insights
7. Recommendations

Return as structured JSON."""

        response = self.llm.invoke(prompt)
        report = eval(response.content)

        return {
            "synthesized_report": report,
            "is_complete": True
        }

    def build_graph(self) -> StateGraph:
        """Build supervisor workflow"""

        workflow = StateGraph(SupervisorState)

        workflow.add_node("create_plan", self.create_research_plan)
        workflow.add_node("execute_research", self.execute_research)
        workflow.add_node("synthesize", self.synthesize_results)

        workflow.add_edge(START, "create_plan")
        workflow.add_edge("create_plan", "execute_research")
        workflow.add_edge("execute_research", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow.compile()
```

#### 2.2 Agent Base Class
```python
# src/company_researcher/agents/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseResearchAgent(ABC):
    """Base class for all research agents"""

    def __init__(self, config: dict):
        self.config = config
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()

    @abstractmethod
    def _initialize_llm(self):
        """Initialize LLM for this agent"""
        pass

    @abstractmethod
    def _initialize_tools(self):
        """Initialize tools for this agent"""
        pass

    @abstractmethod
    async def research(self, company_name: str, task: str) -> dict:
        """Execute research task"""
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Agent identifier"""
        pass

    @property
    @abstractmethod
    def agent_description(self) -> str:
        """What this agent does"""
        pass
```

**Phase 2 Deliverables:**
- ✅ Supervisor pattern implemented
- ✅ Agent base class defined
- ✅ 4 basic agents working (deep, financial, market, competitor)
- ✅ Parallel agent execution
- ✅ Result synthesis

**Time Estimate:** 2 weeks

---

### Phase 3: Specialized Research Agents (Weeks 5-7)

**Goal:** Implement all 14 specialized agents

#### 3.1 Deep Research Agent
```python
# src/company_researcher/agents/deep_researcher.py
from company_researcher.agents.base import BaseResearchAgent
from tavily import TavilyClient
from playwright.async_api import async_playwright

class DeepResearchAgent(BaseResearchAgent):
    """Handles deep web research with anti-bot navigation"""

    @property
    def agent_name(self) -> str:
        return "deep_researcher"

    @property
    def agent_description(self) -> str:
        return "Conducts deep web research, navigates complex sites, extracts comprehensive data"

    def _initialize_llm(self):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.0
        )

    def _initialize_tools(self):
        return {
            "tavily": TavilyClient(api_key=self.config["tavily_api_key"]),
            "playwright": None  # Initialized per request
        }

    async def research(self, company_name: str, task: str) -> dict:
        """Execute deep research"""

        # Step 1: Generate targeted queries
        queries = self._generate_queries(company_name, task)

        # Step 2: Web search
        search_results = await self._parallel_search(queries)

        # Step 3: Visit top results with Playwright (anti-bot)
        detailed_content = await self._scrape_results(search_results)

        # Step 4: Extract and structure information
        structured_data = self._extract_information(detailed_content, task)

        return {
            "agent": self.agent_name,
            "task": task,
            "data": structured_data,
            "sources": self._extract_sources(search_results, detailed_content),
            "confidence": self._calculate_confidence(structured_data)
        }

    def _generate_queries(self, company_name: str, task: str) -> list[str]:
        """Generate targeted search queries"""
        prompt = f"""Generate search queries for: {task}

Company: {company_name}

Generate 3-5 specific queries that will find high-quality information.
Return as JSON array: ["query1", "query2", ...]"""

        response = self.llm.invoke(prompt)
        return eval(response.content)

    async def _parallel_search(self, queries: list[str]) -> list[dict]:
        """Execute searches in parallel"""
        import asyncio

        async def search_single(query):
            return await asyncio.to_thread(
                self.tools["tavily"].search,
                query=query,
                max_results=5
            )

        tasks = [search_single(q) for q in queries]
        return await asyncio.gather(*tasks)

    async def _scrape_results(self, search_results: list[dict]) -> list[dict]:
        """Scrape top URLs with Playwright"""

        # Get top 10 URLs
        urls = []
        for result_set in search_results:
            for item in result_set.get("results", [])[:3]:
                urls.append(item["url"])

        urls = list(set(urls))[:10]  # Deduplicate, max 10

        # Scrape with Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            content = []
            for url in urls:
                try:
                    await page.goto(url, timeout=10000)

                    # Extract main content
                    text = await page.evaluate('''() => {
                        // Remove scripts, styles
                        const unwanted = document.querySelectorAll('script, style, nav, footer');
                        unwanted.forEach(el => el.remove());

                        // Get main content
                        const main = document.querySelector('main') || document.body;
                        return main.innerText;
                    }''')

                    content.append({
                        "url": url,
                        "content": text[:5000],  # Limit length
                        "title": await page.title()
                    })

                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")

            await browser.close()

        return content

    def _extract_information(self, content: list[dict], task: str) -> dict:
        """Extract structured information from scraped content"""

        combined_content = "\n\n---\n\n".join([
            f"Source: {c['title']}\n{c['content']}"
            for c in content
        ])

        prompt = f"""Extract information relevant to: {task}

Content:
{combined_content}

Extract key facts, metrics, and insights.
Return as structured JSON with relevant fields."""

        response = self.llm.invoke(prompt)
        return eval(response.content)

    def _extract_sources(self, search_results, scraped_content) -> list[dict]:
        """Track all sources"""
        sources = []

        for result_set in search_results:
            for item in result_set.get("results", []):
                sources.append({
                    "url": item["url"],
                    "title": item["title"],
                    "type": "search_result"
                })

        for content in scraped_content:
            sources.append({
                "url": content["url"],
                "title": content["title"],
                "type": "scraped_page"
            })

        return sources

    def _calculate_confidence(self, data: dict) -> float:
        """Calculate confidence score based on data quality"""
        # Implement confidence calculation
        # Based on: source quality, data completeness, cross-verification
        return 0.85  # Placeholder
```

#### 3.2 Financial Agent
```python
# src/company_researcher/agents/financial_agent.py
import aiohttp
from alpha_vantage.timeseries import TimeSeries
from sec_edgar_downloader import Downloader

class FinancialAgent(BaseResearchAgent):
    """Analyzes financial performance and metrics"""

    @property
    def agent_name(self) -> str:
        return "financial_agent"

    @property
    def agent_description(self) -> str:
        return "Analyzes revenue, profit, growth, SEC filings, funding rounds"

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        # Use cheaper model for data extraction
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

    def _initialize_tools(self):
        return {
            "alpha_vantage": TimeSeries(
                key=self.config["alpha_vantage_api_key"],
                output_format="json"
            ),
            "sec_downloader": Downloader(
                "CompanyResearcher",
                "research@example.com"
            )
        }

    async def research(self, company_name: str, task: str) -> dict:
        """Execute financial research"""

        # Try to get ticker symbol
        ticker = await self._get_ticker_symbol(company_name)

        if ticker:
            # Public company - get stock data
            financial_data = await self._get_stock_data(ticker)
            sec_data = await self._get_sec_filings(ticker)
        else:
            # Private company - search for funding data
            financial_data = await self._search_funding_data(company_name)
            sec_data = None

        # Analyze metrics
        analysis = self._analyze_financials(financial_data, sec_data)

        return {
            "agent": self.agent_name,
            "task": task,
            "data": {
                "is_public": ticker is not None,
                "ticker": ticker,
                "financial_metrics": financial_data,
                "sec_filings": sec_data,
                "analysis": analysis
            },
            "sources": self._track_sources(ticker, sec_data),
            "confidence": self._calculate_confidence(financial_data)
        }

    async def _get_ticker_symbol(self, company_name: str) -> str | None:
        """Search for stock ticker"""
        # Use search API or LLM to find ticker
        prompt = f"What is the stock ticker symbol for {company_name}? Reply with ONLY the ticker or 'NONE' if private."
        response = self.llm.invoke(prompt)
        ticker = response.content.strip()
        return ticker if ticker != "NONE" else None

    async def _get_stock_data(self, ticker: str) -> dict:
        """Get stock data from Alpha Vantage"""
        try:
            data, meta = await asyncio.to_thread(
                self.tools["alpha_vantage"].get_quote_endpoint,
                symbol=ticker
            )

            return {
                "price": data["05. price"],
                "volume": data["06. volume"],
                "market_cap": data.get("09. market cap"),
                "pe_ratio": data.get("10. price-to-earnings ratio")
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_sec_filings(self, ticker: str) -> dict:
        """Download and analyze recent SEC filings"""
        try:
            # Download latest 10-K
            await asyncio.to_thread(
                self.tools["sec_downloader"].get,
                "10-K",
                ticker,
                limit=1
            )

            # Parse financial statements
            # (Implementation would parse XBRL or text)

            return {
                "latest_10k": "path/to/filing",
                "revenue": "extracted from filing",
                "net_income": "extracted from filing"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _search_funding_data(self, company_name: str) -> dict:
        """Search for funding information (private companies)"""

        # Search Crunchbase, news, press releases
        query = f"{company_name} funding round series revenue"

        async with aiohttp.ClientSession() as session:
            # Implementation would call Crunchbase API
            # or search news sources
            pass

        return {
            "total_funding": "search result",
            "latest_round": "search result",
            "valuation": "search result"
        }

    def _analyze_financials(self, financial_data: dict, sec_data: dict | None) -> dict:
        """Analyze financial health and trends"""

        prompt = f"""Analyze this financial data:

Financial Metrics: {financial_data}
SEC Data: {sec_data}

Provide:
1. Financial health assessment (1-10)
2. Growth trajectory
3. Key metrics trend
4. Risk factors
5. Opportunities

Return as structured JSON."""

        response = self.llm.invoke(prompt)
        return eval(response.content)
```

#### 3.3 Agent Implementation Summary

**Implement these 14 agents following the same pattern:**

1. **Deep Research Agent** ✅ (see above)
2. **Financial Agent** ✅ (see above)
3. **Market Analyst Agent**
   - Tools: Industry reports, market research APIs
   - Focus: TAM, market share, growth trends
4. **Competitor Scout Agent**
   - Tools: BuiltWith, Wappalyzer, GitHub API
   - Focus: Competitive landscape, tech stack
5. **Brand Auditor Agent**
   - Tools: Social media APIs, review sites
   - Focus: Brand perception, sentiment
6. **Sales Agent**
   - Tools: LinkedIn API, Glassdoor
   - Focus: Decision makers, pain points, culture
7. **Investment Agent**
   - Tools: Combine all agent data
   - Focus: Investment thesis, SWOT, recommendation
8. **Social Media Agent**
   - Tools: Twitter, Reddit, YouTube APIs
   - Focus: Engagement, sentiment, presence
9. **Sector Analyst Agent**
   - Tools: Industry-specific data sources
   - Focus: Sector trends, regulatory environment
10. **Logic Critic Agent**
    - Tools: Cross-referencing, fact-checking
    - Focus: Quality assurance, verification
11. **Insight Generator Agent**
    - Tools: All agent outputs
    - Focus: Synthesis, strategic insights
12. **Report Writer Agent**
    - Tools: All data
    - Focus: Generate markdown reports
13. **Reasoning Agent**
    - Tools: Claude Opus (best reasoning)
    - Focus: Complex logical analysis
14. **Generic Research Agent**
    - Tools: General search
    - Focus: Catch-all for misc research

**Phase 3 Deliverables:**
- ✅ All 14 agents implemented
- ✅ Agent-specific tool integrations
- ✅ Consistent agent interface
- ✅ Agent unit tests

**Time Estimate:** 3 weeks

---

### Phase 4: Memory & Learning System (Week 8)

**Goal:** Implement long-term memory with LangMem

#### 4.1 Memory Integration
```python
# src/company_researcher/memory/manager.py
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.postgres import AsyncPostgresStore

class ResearchMemoryManager:
    """Manages long-term research memory"""

    def __init__(self, config: dict):
        self.store = AsyncPostgresStore(
            connection_string=config["postgres_url"],
            index={
                "dims": 1536,
                "embed": "openai:text-embedding-3-small"
            }
        )

        self.manage_tool = create_manage_memory_tool(
            namespace=("company_research",)
        )

        self.search_tool = create_search_memory_tool(
            namespace=("company_research",)
        )

    async def store_research(
        self,
        company_name: str,
        research_data: dict,
        metadata: dict
    ):
        """Store completed research in memory"""

        namespace = ("company_research", company_name)
        key = metadata["research_id"]

        await self.store.put(
            namespace=namespace,
            key=key,
            value={
                "company_name": company_name,
                "data": research_data,
                "timestamp": metadata["timestamp"],
                "quality_score": metadata["quality_score"],
                "sources": metadata["sources"]
            }
        )

    async def search_past_research(
        self,
        query: str,
        limit: int = 5
    ) -> list[dict]:
        """Semantic search across past research"""

        results = await self.store.search(
            namespace=("company_research",),
            query=query,
            limit=limit
        )

        return results

    async def get_company_history(self, company_name: str) -> list[dict]:
        """Get all past research for a company"""

        results = await self.store.list(
            namespace=("company_research", company_name)
        )

        return results
```

**Phase 4 Deliverables:**
- ✅ LangMem integrated
- ✅ PostgreSQL + Qdrant set up
- ✅ Semantic search working
- ✅ Research history tracking

**Time Estimate:** 1 week

---

### Phase 5: Quality Assurance (Week 9)

**Goal:** Implement Logic Critic agent and quality scoring

#### 5.1 Quality Assurance System
```python
# src/company_researcher/quality/critic.py

class LogicCriticAgent(BaseResearchAgent):
    """Verifies facts and scores quality"""

    async def critique(self, research_data: dict, sources: list[dict]) -> dict:
        """Perform quality assurance"""

        # 1. Cross-reference facts
        verification = await self._verify_facts(research_data, sources)

        # 2. Check for contradictions
        contradictions = self._detect_contradictions(research_data)

        # 3. Score source quality
        source_scores = self._score_sources(sources)

        # 4. Calculate confidence
        confidence = self._calculate_confidence(
            verification,
            contradictions,
            source_scores
        )

        # 5. Identify gaps
        gaps = self._identify_gaps(research_data)

        return {
            "quality_score": confidence,
            "verification_results": verification,
            "contradictions": contradictions,
            "source_quality": source_scores,
            "missing_areas": gaps,
            "approved": confidence > 0.8 and len(contradictions) == 0
        }
```

**Phase 5 Deliverables:**
- ✅ Quality scoring implemented
- ✅ Fact verification working
- ✅ Contradiction detection
- ✅ Source quality scoring

**Time Estimate:** 1 week

---

### Phase 6: Report Generation (Week 10)

**Goal:** Generate professional markdown reports

#### 6.1 Report Writer Agent
```python
# src/company_researcher/agents/report_writer.py

class ReportWriterAgent(BaseResearchAgent):
    """Generates structured markdown reports"""

    async def write_reports(
        self,
        company_name: str,
        all_data: dict,
        output_dir: str
    ) -> dict:
        """Generate all report sections"""

        # Create output structure
        report_dir = Path(output_dir) / company_name
        report_dir.mkdir(parents=True, exist_ok=True)

        # Generate each section
        sections = {
            "00-Strategic-Context": [
                "Company-Overview.md",
                "Executive-Summary.md",
                "Key-People.md"
            ],
            "01-Market-Intelligence": [
                "Market-Size-Growth.md",
                "Key-Trends.md"
            ],
            "02-Competitive-Landscape": [
                "Direct-Competitors.md",
                "Competitive-Advantages.md"
            ],
            "03-Financial-Analysis": [
                "Revenue-Analysis.md",
                "Growth-Metrics.md"
            ],
            "99-Sources": [
                "Source-Index.md"
            ]
        }

        for section_dir, files in sections.items():
            section_path = report_dir / section_dir
            section_path.mkdir(exist_ok=True)

            for file in files:
                content = await self._generate_section(
                    file.replace(".md", "").replace("-", " "),
                    all_data
                )

                (section_path / file).write_text(content)

        return {"report_dir": str(report_dir)}

    async def _generate_section(self, section_name: str, data: dict) -> str:
        """Generate one report section"""

        prompt = f"""Generate a professional markdown report section.

Section: {section_name}
Data: {data}

Write a comprehensive, well-structured markdown document.
Include:
- Clear headings
- Bullet points for lists
- Tables for structured data
- Proper citations [Source Name](URL)

Be professional, concise, and data-driven."""

        response = self.llm.invoke(prompt)
        return response.content
```

**Phase 6 Deliverables:**
- ✅ Report writer implemented
- ✅ 20+ markdown templates
- ✅ Professional formatting
- ✅ Source citations

**Time Estimate:** 1 week

---

### Phase 7: Production Features (Weeks 11-12)

**Goal:** API, monitoring, deployment

#### 7.1 FastAPI Backend
```python
# src/api/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Company Researcher API")

class ResearchRequest(BaseModel):
    company_name: str
    industry: str | None = None
    focus_areas: list[str] = []
    depth: str = "standard"

class ResearchResponse(BaseModel):
    research_id: str
    status: str
    company_name: str
    estimated_time_seconds: int

@app.post("/research", response_model=ResearchResponse)
async def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """Start a new company research"""

    research_id = str(uuid.uuid4())

    # Add to background queue
    background_tasks.add_task(
        execute_research,
        research_id,
        request.company_name,
        request.industry,
        request.focus_areas,
        request.depth
    )

    return ResearchResponse(
        research_id=research_id,
        status="processing",
        company_name=request.company_name,
        estimated_time_seconds=180  # 2-5 minutes
    )

@app.get("/research/{research_id}")
async def get_research_status(research_id: str):
    """Get research status and results"""

    # Check database for status
    # Return results if complete
    pass

@app.get("/research/{research_id}/download")
async def download_research(research_id: str):
    """Download research as ZIP"""
    pass
```

#### 7.2 AgentOps Integration
```python
# src/company_researcher/monitoring/instrumentation.py
import agentops
from agentops.sdk.decorators import session, agent, operation

agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"),
    tags=["company_research", "production"]
)

@session
def research_workflow(company_name: str):
    """Instrumented research workflow"""
    # All LLM calls, tool usage automatically tracked
    pass
```

**Phase 7 Deliverables:**
- ✅ FastAPI REST API
- ✅ Background task processing
- ✅ AgentOps monitoring
- ✅ Docker deployment
- ✅ Cost tracking

**Time Estimate:** 2 weeks

---

## Success Metrics

### Technical Metrics
```yaml
Performance:
  - Average research time: < 5 minutes
  - Agent coordination overhead: < 10%
  - Success rate: > 95%
  - Parallel agent execution: Yes

Quality:
  - Quality score: > 0.85 average
  - Completeness: > 90% of expected sections
  - Source quality: > 80% authoritative sources
  - Accuracy: > 95% verified facts

Cost:
  - Per research cost: < $0.50
  - Monthly infrastructure: < $500
  - LLM API costs: < $0.40 per research
```

### Business Metrics
```yaml
Product:
  - Beta users: 50-100 in Month 1
  - Paying customers: 100 by Month 6
  - Monthly ARR: $29,900 by Month 6

User Satisfaction:
  - NPS: > 50
  - Retention: > 90%
  - Usage: 80% active monthly
```

---

## Next Steps

### Immediate Actions (This Week)
1. Set up project repository
2. Initialize Python environment
3. Configure API keys (Tavily, Anthropic, OpenAI)
4. Implement Phase 1 basic workflow
5. Test with 3-5 companies

### Month 1 Goals
- Complete Phases 1-2
- Have supervisor pattern working
- 4-6 agents operational
- Can research companies comprehensively

### Month 2-3 Goals
- Complete all 14 agents
- Memory system working
- Quality assurance implemented
- Report generation polished

### Month 3+ Goals
- Production deployment
- Beta user testing
- API monetization
- Scale to paying customers

---

## Questions to Resolve

1. **Which LLM provider for primary model?**
   - Recommendation: Anthropic Claude (best for research reasoning)
   - Alternative: OpenAI GPT-4o (faster, cheaper)

2. **Deployment platform?**
   - Recommendation: AWS/GCP with Docker
   - Alternative: Render/Railway for quick start

3. **Payment processing?**
   - Recommendation: Stripe
   - Alternative: LemonSqueezy

4. **Database choice?**
   - Recommendation: PostgreSQL + Qdrant
   - Alternative: Supabase (all-in-one)

---

## Resources Needed

### Development Tools
- GitHub repository
- API keys (Tavily, Anthropic, OpenAI, Alpha Vantage, etc.)
- Development database (PostgreSQL)
- Vector database (Qdrant or Pinecone)

### Team
- Solo developer can build Phase 1-3 (8 weeks)
- Consider contractor for frontend (Phases 7+)
- Consider DevOps help for production deployment

### Budget Estimate
```yaml
Development (Months 1-3):
  - API costs (testing): $200/month
  - Infrastructure (dev): $50/month
  - Total: $750

Beta Launch (Months 4-6):
  - API costs (usage): $500/month
  - Infrastructure (prod): $200/month
  - Marketing: $500/month
  - Total: $3,600

Total 6-month budget: $4,350
```

---

**This plan is based on proven patterns from Open Deep Research (production-grade), Company Researcher (validated approach), and the multi-agent architectures in the reference repositories.**

**You have everything needed to build this. Let's start with Phase 1!** 🚀
