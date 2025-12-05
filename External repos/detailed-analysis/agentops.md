# AgentOps - Detailed Analysis

**Repository:** agentops/
**Type:** Observability & DevTool Platform
**Last Updated:** 2025-12-05
**Priority:** ⚡ HIGH (Essential for Production)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Capabilities](#core-capabilities)
3. [Extractable Patterns](#extractable-patterns)
4. [Integration Examples](#integration-examples)
5. [Implementation Guide](#implementation-guide)

---

## Overview

AgentOps is an open-source observability and monitoring platform specifically designed for AI agents. It provides:

- **Session Replay:** Step-by-step visualization of agent execution
- **Cost Tracking:** Monitor LLM API spend across providers
- **Performance Metrics:** Track latency, token usage, success rates
- **Framework Integration:** Native support for CrewAI, AG2, LangChain, LlamaIndex
- **Self-Hosted:** Can run on your own infrastructure

**Key Value:** Add comprehensive agent monitoring with just 2-3 lines of code.

---

## Core Capabilities

### 1. Session Tracking & Replay

**What It Does:**
- Records every step of agent execution
- Creates visual execution graphs
- Enables debugging complex multi-step workflows
- Stores session metadata and outcomes

**Use Cases:**
- Debugging failed agent runs
- Understanding agent decision-making
- Optimizing agent workflows
- Training and documentation

### 2. Decorator-Based Instrumentation

**What It Does:**
- Python decorators for zero-boilerplate monitoring
- Automatic span creation and tracking
- Hierarchical span relationships
- Input/output recording

**Decorators Available:**
```python
@session      # Root span for entire workflow
@agent        # Agent-level tracking
@operation    # Individual operations
@task         # Task-level tracking
@workflow     # Multi-operation workflows
```

### 3. Multi-Framework Integration

**Supported Frameworks:**
- ✅ OpenAI Agents SDK (Python & TypeScript)
- ✅ CrewAI (automatic with AGENTOPS_API_KEY)
- ✅ AG2/AutoGen
- ✅ LangChain (callback handler)
- ✅ LlamaIndex
- ✅ Camel AI
- ✅ Cohere, Anthropic, Mistral

### 4. Cost Management

**Tracks:**
- LLM API costs per session
- Token usage breakdown
- Cost per agent/operation
- Cumulative spend tracking

### 5. Performance Analytics

**Metrics:**
- Event latency analysis
- Agent workflow pricing
- Success/failure rates
- Tool usage statistics

---

## Extractable Patterns

### Pattern 1: Decorator-Based Instrumentation

```python
# Extract this pattern for your own observability
from agentops.sdk.decorators import session, agent, operation

@session
def my_research_workflow(topic):
    """Root session for entire workflow"""
    agent = ResearchAgent()
    return agent.research(topic)

@agent
class ResearchAgent:
    """Agent-level tracking"""

    @operation
    def search_web(self, query):
        """Operation-level tracking"""
        results = tavily_search(query)
        return results

    @operation
    def extract_data(self, sources):
        """Another operation"""
        data = extract(sources)
        return data

    def research(self, topic):
        sources = self.search_web(topic)
        data = self.extract_data(sources)
        return data
```

**What to Extract:**
- Decorator pattern for automatic instrumentation
- Span hierarchy (session → agent → operation)
- Automatic input/output capture
- Exception handling within decorators

### Pattern 2: Session Management

```python
# Extract session lifecycle management
import agentops

# Initialize
agentops.init(api_key="<YOUR_API_KEY>")

# Session runs automatically with decorators
# OR manual control:
session = agentops.start_session(tags=["research", "production"])

try:
    result = perform_research()
    session.end_session("Success")
except Exception as e:
    session.end_session("Failure", end_state_reason=str(e))
```

**What to Extract:**
- Session lifecycle hooks
- Tag-based organization
- Success/failure tracking
- Error state capture

### Pattern 3: Custom Attributes

```python
# Add custom metadata to spans
@operation
def analyze_sentiment(text):
    # Custom attributes for better tracking
    agentops.record({
        "input_length": len(text),
        "model": "gpt-4",
        "temperature": 0.7,
        "custom_metric": calculate_complexity(text)
    })

    result = llm.analyze(text)

    agentops.record({
        "output_length": len(result),
        "sentiment": result.sentiment
    })

    return result
```

**What to Extract:**
- Custom attribute logging
- Pre/post operation metrics
- Domain-specific tracking

### Pattern 4: Multi-Agent Tracking

```python
# Track interactions between multiple agents
@session
def multi_agent_workflow():
    researcher = ResearchAgent(name="Researcher")
    analyst = AnalystAgent(name="Analyst")
    writer = WriterAgent(name="Writer")

    # Each agent tracked separately
    data = researcher.gather_data()
    analysis = analyst.analyze(data)
    report = writer.write_report(analysis)

    return report

@agent
class ResearchAgent:
    def __init__(self, name):
        self.name = name
        agentops.set_agent_name(name)

    @operation
    def gather_data(self):
        # Operation tracked under "Researcher" agent
        pass
```

**What to Extract:**
- Multi-agent coordination tracking
- Agent naming and identification
- Cross-agent communication patterns

---

## Integration Examples

### Example 1: Basic Integration (2 Lines)

```python
import agentops

# Line 1: Initialize
agentops.init("<YOUR_API_KEY>")

# Your agent code here (automatically tracked)
def my_agent():
    llm_response = openai.ChatCompletion.create(...)
    return llm_response

result = my_agent()

# Line 2: End session
agentops.end_session('Success')
```

**Automatically Tracks:**
- All OpenAI API calls
- Anthropic calls
- Cohere calls
- LiteLLM calls

### Example 2: CrewAI Integration

```bash
# Install
pip install 'crewai[agentops]'

# Set environment variable
export AGENTOPS_API_KEY=<YOUR_KEY>
```

```python
# No code changes needed - automatic!
from crewai import Agent, Task, Crew

agent = Agent(
    role="Researcher",
    goal="Research AI agents",
    backstory="Expert researcher"
)

task = Task(description="Research latest AI trends", agent=agent)

crew = Crew(agents=[agent], tasks=[task])

# Automatically tracked by AgentOps
result = crew.kickoff()
```

### Example 3: LangChain Integration

```python
from agentops.integration.callbacks.langchain import LangchainCallbackHandler

# Initialize callback
handler = LangchainCallbackHandler(
    api_key=AGENTOPS_API_KEY,
    tags=['LangChain Example']
)

# Add to LLM
llm = ChatOpenAI(
    callbacks=[handler],
    model='gpt-3.5-turbo'
)

# Add to agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    callbacks=[handler]  # Track agent execution
)

result = agent.run("Research AI agents")
```

### Example 4: Custom Agent with Full Instrumentation

```python
import agentops
from agentops.sdk.decorators import session, agent, operation

@agent
class CustomResearchAgent:
    def __init__(self, name):
        self.name = name

    @operation
    async def search_web(self, query):
        """Search operation with custom tracking"""
        agentops.record({
            "operation": "web_search",
            "query": query,
            "timestamp": datetime.now()
        })

        results = await tavily.search(query)

        agentops.record({
            "results_count": len(results),
            "sources": [r.url for r in results]
        })

        return results

    @operation
    async def extract_data(self, sources, schema):
        """Extraction with schema tracking"""
        agentops.record({
            "operation": "extraction",
            "source_count": len(sources),
            "schema": schema.schema_json()
        })

        extracted = await extractor.extract(sources, schema)

        agentops.record({
            "extracted_fields": len(extracted.dict()),
            "completeness": calculate_completeness(extracted)
        })

        return extracted

    @operation
    async def quality_check(self, data):
        """Quality assessment with scoring"""
        agentops.record({"operation": "quality_check"})

        score = await assess_quality(data)

        agentops.record({
            "quality_score": score,
            "passed": score >= 0.7
        })

        return score

@session
async def research_workflow(topic):
    """Complete workflow with session tracking"""
    agentops.set_tags(["research", "production", topic])

    agent = CustomResearchAgent("ResearchBot")

    try:
        # All operations tracked hierarchically
        sources = await agent.search_web(topic)
        data = await agent.extract_data(sources, CompanySchema)
        quality = await agent.quality_check(data)

        if quality < 0.7:
            agentops.end_session('Failure', 'Quality too low')
            return None

        agentops.end_session('Success')
        return data

    except Exception as e:
        agentops.end_session('Failure', str(e))
        raise
```

---

## What You Can Extract

### 1. Instrumentation Architecture

```python
# Extract this decorator pattern
class Instrumenter:
    """Wrapper for automatic function instrumentation"""

    def __init__(self, name, span_type):
        self.name = name
        self.span_type = span_type

    def __call__(self, func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_id = self.start_span(
                name=func.__name__,
                type=self.span_type,
                inputs={"args": args, "kwargs": kwargs}
            )

            try:
                result = await func(*args, **kwargs)
                self.end_span(span_id, outputs={"result": result})
                return result

            except Exception as e:
                self.end_span(span_id, error=str(e))
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar for sync functions
            pass

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

# Use it
operation = Instrumenter("operation", "operation")

@operation
def my_function():
    pass
```

### 2. Span Hierarchy

```python
# Extract span management
class SpanManager:
    def __init__(self):
        self.spans = {}
        self.current_span = None
        self.root_span = None

    def start_span(self, name, span_type, parent_id=None):
        span_id = generate_id()

        span = {
            "id": span_id,
            "name": name,
            "type": span_type,
            "parent_id": parent_id or self.current_span,
            "start_time": datetime.now(),
            "attributes": {}
        }

        self.spans[span_id] = span

        if not self.root_span:
            self.root_span = span_id

        self.current_span = span_id

        return span_id

    def end_span(self, span_id, **attributes):
        span = self.spans[span_id]
        span["end_time"] = datetime.now()
        span["duration"] = (
            span["end_time"] - span["start_time"]
        ).total_seconds()
        span["attributes"].update(attributes)

        # Restore parent as current
        self.current_span = span["parent_id"]

    def get_hierarchy(self):
        """Build tree from flat span list"""
        # Build execution graph
        pass
```

### 3. Cost Tracking

```python
# Extract cost calculation
class CostTracker:
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
    }

    def __init__(self):
        self.total_cost = 0
        self.costs_by_model = {}
        self.costs_by_operation = {}

    def track_llm_call(self, model, input_tokens, output_tokens, operation_id):
        costs = self.MODEL_COSTS.get(model, {"input": 0, "output": 0})

        cost = (
            (input_tokens / 1000) * costs["input"] +
            (output_tokens / 1000) * costs["output"]
        )

        self.total_cost += cost

        if model not in self.costs_by_model:
            self.costs_by_model[model] = 0
        self.costs_by_model[model] += cost

        if operation_id not in self.costs_by_operation:
            self.costs_by_operation[operation_id] = 0
        self.costs_by_operation[operation_id] += cost

        return cost

    def get_summary(self):
        return {
            "total": self.total_cost,
            "by_model": self.costs_by_model,
            "by_operation": self.costs_by_operation
        }
```

### 4. Session Replay Data Structure

```python
# Extract session data model
class Session:
    def __init__(self, session_id, tags=None):
        self.session_id = session_id
        self.tags = tags or []
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "running"
        self.spans = []
        self.metadata = {}
        self.cost = 0
        self.token_usage = {"input": 0, "output": 0}

    def add_span(self, span):
        self.spans.append(span)

        # Update costs and tokens
        if "cost" in span:
            self.cost += span["cost"]
        if "tokens" in span:
            self.token_usage["input"] += span["tokens"].get("input", 0)
            self.token_usage["output"] += span["tokens"].get("output", 0)

    def end(self, status, reason=None):
        self.end_time = datetime.now()
        self.status = status
        self.metadata["end_reason"] = reason
        self.metadata["duration"] = (
            self.end_time - self.start_time
        ).total_seconds()

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "tags": self.tags,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration": self.metadata.get("duration"),
            "cost": self.cost,
            "token_usage": self.token_usage,
            "spans": self.spans,
            "metadata": self.metadata
        }
```

---

## Implementation Guide

### Week 1: Basic Integration
```python
# Day 1-2: Install and basic setup
pip install agentops

# Day 3-4: Add to existing agent
import agentops
agentops.init(API_KEY)
# ... your agent code ...
agentops.end_session('Success')

# Day 5: View in dashboard
# Go to app.agentops.ai
# Analyze first sessions
```

### Week 2: Decorator Pattern
```python
# Day 1-3: Add decorators
@session
def my_workflow():
    pass

@agent
class MyAgent:
    @operation
    def my_operation(self):
        pass

# Day 4-5: Custom attributes
agentops.record({"custom": "data"})
```

### Week 3: Advanced Features
```python
# Multi-agent tracking
# Cost optimization
# Performance analysis
```

### Week 4: Production
```python
# Self-host AgentOps
# Configure retention policies
# Set up alerts
```

---

## Dashboard Features to Replicate

### 1. Session Replay Viewer
- Timeline visualization
- Span hierarchy tree
- Input/output inspection
- Error highlighting

### 2. Analytics Dashboard
- Cost over time
- Token usage trends
- Success rate metrics
- Latency distribution

### 3. Agent Comparison
- Compare multiple runs
- A/B test results
- Performance regression detection

---

## Key Takeaways

1. **Decorator Pattern:** Simple, elegant instrumentation
2. **Hierarchical Spans:** Clear execution tracking
3. **Automatic Integration:** Minimal code changes
4. **Cost Tracking:** Essential for production
5. **Self-Hosted Option:** Privacy and control

---

## Next Steps

1. **Immediate:**
   - Sign up for AgentOps (free tier)
   - Add to one agent
   - View first dashboard

2. **This Week:**
   - Add decorators to all agents
   - Configure custom attributes
   - Set up cost tracking

3. **This Month:**
   - Analyze performance patterns
   - Optimize based on metrics
   - Consider self-hosting

---

**Related Documentation:**
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [langchain-reference Analysis](./langchain-reference.md)
- [Implementation Guide](../EXTRACTION-GUIDE.md)
