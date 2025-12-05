# Observability & Monitoring

**Source:** `agentops/` + LangSmith patterns

---

## Overview

Production systems need observability to:
- ✅ Debug failures
- ✅ Monitor performance
- ✅ Track costs
- ✅ Replay sessions
- ✅ Optimize quality

---

## AgentOps Integration

### What is AgentOps?

**AgentOps** is an observability platform specifically for AI agents:
- Session replay (see exactly what happened)
- LLM call tracking (every API call logged)
- Cost tracking (real-time spend monitoring)
- Error analysis (why did it fail?)
- Performance metrics (how long did it take?)

### Benefits

```python
Without AgentOps:
- "It failed" → No idea why
- "How much did that cost?" → No idea
- "Which LLM calls were made?" → No idea
- "Can I replay what happened?" → No

With AgentOps:
- "It failed" → See exact error, full context, all LLM calls
- "How much?" → $0.28, broken down by model
- "Which LLM calls?" → 12 calls, see prompts & responses
- "Replay?" → Yes, step-by-step replay in dashboard
```

---

## Quick Start (2 Lines of Code!)

### Basic Integration

```python
import agentops

# Initialize (at app start)
agentops.init(api_key="your_api_key")

# ... your agent code ...

# End session (when done)
agentops.end_session('Success')
```

That's it! AgentOps automatically tracks:
- All LLM calls (Claude, GPT, Gemini, etc.)
- Tool usage
- Agent decisions
- Errors
- Costs
- Timing

---

## Advanced Integration

### Decorator-Based Instrumentation

```python
from agentops.sdk.decorators import session, agent, operation

@session  # Root-level session
def research_company(company_name: str):
    """Main research workflow"""

    researcher = CompanyResearcher()
    result = researcher.research(company_name)

    if result["quality_score"] >= 0.85:
        agentops.end_session('Success')
    else:
        agentops.end_session('LowQuality')

    return result


@agent  # Agent-level tracking
class CompanyResearcher:
    """Research agent with automatic tracking"""

    @operation(name="web_search")
    async def search_web(self, query: str):
        """Tracked search operation"""
        results = await tavily.search(query)
        return results

    @operation(name="extract_info")
    def extract_information(self, content: str):
        """Tracked extraction operation"""
        data = llm.extract(content)
        return data

    @operation(name="quality_check")
    def check_quality(self, data: dict):
        """Tracked quality check"""
        score = calculate_quality(data)
        return score

    def research(self, company_name: str):
        """Main research method"""

        # All operations automatically tracked
        results = await self.search_web(f"{company_name} overview")
        data = self.extract_information(results)
        quality = self.check_quality(data)

        return {"data": data, "quality_score": quality}
```

### What Gets Tracked

```
Session: research_company("Tesla")
├─ Agent: CompanyResearcher
│  ├─ Operation: web_search
│  │  ├─ LLM Call: Generate queries (Claude)
│  │  │  Cost: $0.02
│  │  │  Tokens: 150 in, 50 out
│  │  ├─ Tool Call: Tavily search
│  │  │  Cost: $0.01
│  │  └─ Duration: 2.3s
│  ├─ Operation: extract_info
│  │  ├─ LLM Call: Extract structured data (Claude)
│  │  │  Cost: $0.15
│  │  │  Tokens: 3000 in, 500 out
│  │  └─ Duration: 4.1s
│  └─ Operation: quality_check
│     ├─ LLM Call: Quality assessment (Claude)
│     │  Cost: $0.05
│     │  Tokens: 1000 in, 100 out
│     └─ Duration: 1.5s
└─ Total
   Cost: $0.23
   Duration: 7.9s
   Status: Success
```

---

## Dashboard Features

### 1. Session Replay

**See exactly what happened:**
```
Timeline View:
00:00 - Session started
00:01 - web_search operation started
00:02 - LLM call: "Generate search queries for Tesla"
00:03 - Response: ["Tesla revenue 2024", "Tesla products", ...]
00:04 - Tavily search executed
00:05 - web_search operation completed
00:06 - extract_info operation started
...
```

### 2. Cost Tracking

**Real-time spend monitoring:**
```
Cost Breakdown:
- Claude 3.5 Sonnet: $0.18 (78%)
- GPT-4o-mini: $0.03 (13%)
- Tavily API: $0.02 (9%)
Total: $0.23

Daily Spend: $127.50
Monthly Spend: $3,420.00
```

### 3. Performance Metrics

**Identify bottlenecks:**
```
Operation Duration:
- web_search: 2.3s
- extract_info: 4.1s ← Slowest
- quality_check: 1.5s

LLM Call Latency:
- Average: 1.8s
- p50: 1.2s
- p95: 4.5s
- p99: 6.2s
```

### 4. Error Analysis

**Debug failures:**
```
Error: RateLimitError in extract_info
Stack Trace: ...
Context:
  - Company: Tesla
  - Operation: extract_info
  - LLM: claude-3-5-sonnet
  - Previous operations: web_search (success)
  - Input: [3000 tokens of content]

Recommendations:
- Add retry logic with exponential backoff
- Consider using GPT-4o-mini for extraction (cheaper, faster)
```

---

## Implementation for Company Researcher

### Complete Instrumentation

```python
# src/company_researcher/monitoring.py
import agentops
import os
from functools import wraps

# Initialize AgentOps
agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"),
    tags=["company_research", "production"]
)

def track_research(func):
    """Decorator to track research sessions"""

    @wraps(func)
    @agentops.record_session
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)

            # End session based on result
            if result.get("status") == "success":
                agentops.end_session('Success')
            elif result.get("status") == "low_quality":
                agentops.end_session('LowQuality')
            else:
                agentops.end_session('Error')

            return result

        except Exception as e:
            agentops.end_session('Error', error=str(e))
            raise

    return wrapper


@track_research
async def research_company(company_name: str, config: dict):
    """Main research entry point with tracking"""

    # Tag this session
    agentops.add_tags([f"company:{company_name}"])

    # Track custom metrics
    agentops.record(
        event_type="research_started",
        data={"company": company_name}
    )

    # Conduct research
    supervisor = SupervisorWorkflow(config)
    result = await supervisor.research(company_name)

    # Track completion
    agentops.record(
        event_type="research_completed",
        data={
            "company": company_name,
            "quality_score": result["quality_score"],
            "cost": result["total_cost"],
            "duration": result["duration_seconds"]
        }
    )

    return result
```

### Multi-Agent Tracking

```python
# Each agent is tracked separately
from agentops.sdk.decorators import agent, operation

@agent
class FinancialAgent:
    """Financial analysis agent"""

    @operation(name="get_stock_data")
    async def get_stock_data(self, ticker: str):
        data = await alpha_vantage.get_quote(ticker)
        return data

    @operation(name="analyze_financials")
    def analyze(self, data: dict):
        analysis = llm.analyze(data)
        return analysis


@agent
class MarketAnalyst:
    """Market analysis agent"""

    @operation(name="research_market_size")
    async def research_market_size(self, industry: str):
        results = await tavily.search(f"{industry} market size 2024")
        return results

    @operation(name="analyze_market")
    def analyze(self, results: dict):
        analysis = llm.analyze_market(results)
        return analysis


# In AgentOps dashboard, you'll see:
# - FinancialAgent (separate view)
#   - get_stock_data operations
#   - analyze_financials operations
# - MarketAnalyst (separate view)
#   - research_market_size operations
#   - analyze_market operations
```

---

## Cost Optimization

### Track & Optimize Spend

```python
class CostOptimizer:
    """Monitor and optimize LLM costs"""

    def __init__(self):
        self.cost_tracker = {}

    def track_llm_call(self, model: str, tokens_in: int, tokens_out: int):
        """Track individual LLM call cost"""

        # Pricing (per 1M tokens)
        pricing = {
            "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00}
        }

        prices = pricing[model]
        cost = (
            (tokens_in / 1_000_000) * prices["input"] +
            (tokens_out / 1_000_000) * prices["output"]
        )

        # Track
        if model not in self.cost_tracker:
            self.cost_tracker[model] = {"calls": 0, "cost": 0.0}

        self.cost_tracker[model]["calls"] += 1
        self.cost_tracker[model]["cost"] += cost

        # Log to AgentOps
        agentops.record(
            event_type="llm_cost",
            data={
                "model": model,
                "cost": cost,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out
            }
        )

        return cost

    def get_recommendations(self) -> list[str]:
        """Get cost optimization recommendations"""

        recommendations = []

        # Check if using expensive models for simple tasks
        if "claude-3-5-sonnet" in self.cost_tracker:
            sonnet_calls = self.cost_tracker["claude-3-5-sonnet"]["calls"]
            total_calls = sum(t["calls"] for t in self.cost_tracker.values())

            if sonnet_calls / total_calls > 0.7:
                recommendations.append(
                    "💡 70%+ calls use Claude Sonnet. "
                    "Consider GPT-4o-mini for simple tasks (20x cheaper)"
                )

        # Check total spend
        total_cost = sum(t["cost"] for t in self.cost_tracker.values())
        if total_cost > 10.0:
            recommendations.append(
                f"⚠️ High cost: ${total_cost:.2f}. "
                f"Consider caching or reducing LLM calls."
            )

        return recommendations
```

---

## Alerts & Notifications

### Set Up Alerts

```python
# In AgentOps dashboard, configure:

# 1. Cost Alerts
- Alert when daily spend > $100
- Alert when single session costs > $5

# 2. Error Alerts
- Alert on any error
- Alert if error rate > 5%

# 3. Performance Alerts
- Alert if average session > 5 minutes
- Alert if p95 latency > 10 seconds

# 4. Quality Alerts
- Alert if quality score < 80%
- Alert if completeness < 90%
```

---

## Production Monitoring Stack

### Recommended Stack

```yaml
Observability:
  AgentOps:
    - Session replay
    - LLM tracking
    - Cost monitoring
    - Error analysis

  LangSmith (optional):
    - LangChain-specific debugging
    - Prompt optimization
    - Evaluation datasets

  Prometheus + Grafana:
    - System metrics (CPU, memory)
    - Request rate
    - Response time
    - Error rate

  Sentry:
    - Error tracking
    - Stack traces
    - User impact
```

### Metrics Dashboard

```python
# Key metrics to track

Reliability:
  - Success rate: % of successful sessions
  - Error rate: % of failed sessions
  - Retry rate: % of sessions needing retries

Performance:
  - Average duration: seconds per research
  - p95 duration: 95th percentile
  - Agent coordination overhead: time in supervisor

Quality:
  - Average quality score: 0-100
  - Approval rate: % passing quality gate
  - Source quality: average source score

Cost:
  - Cost per research: dollars
  - Daily spend: dollars
  - Monthly burn rate: dollars

Usage:
  - Researches per day: count
  - Unique companies: count
  - API requests: count
```

---

## Implementation Roadmap

### Week 1-4 (MVP)
```python
# Basic logging
- Python logging to console
- Track basic metrics (time, cost)
```

### Week 5-8 (Enhancement)
```python
# Add AgentOps
- 2-line integration
- Session tracking
- Cost monitoring
```

### Week 9-12 (Production)
```python
# Full observability
- AgentOps decorators
- Custom metrics
- Alerts configured
- Prometheus + Grafana
```

---

## Code Templates

### Template: Instrumented Workflow

```python
import agentops
from agentops.sdk.decorators import session, agent, operation

@session
async def research_workflow(company_name: str):
    """Main workflow with tracking"""

    # Add context
    agentops.add_tags([f"company:{company_name}"])

    try:
        # Run research
        result = await execute_research(company_name)

        # Record metrics
        agentops.record(
            event_type="research_complete",
            data={
                "quality": result["quality_score"],
                "cost": result["cost"],
                "duration": result["duration"]
            }
        )

        # Success
        agentops.end_session('Success')
        return result

    except Exception as e:
        # Failure
        agentops.end_session('Error', error=str(e))
        raise
```

---

## Benefits Summary

### Development
- ✅ Debug 10x faster (session replay)
- ✅ Find bottlenecks easily (performance metrics)
- ✅ Optimize prompts (see what works)

### Production
- ✅ Monitor costs in real-time
- ✅ Alert on errors immediately
- ✅ Track quality metrics
- ✅ Prove ROI to stakeholders

### Business
- ✅ Understand unit economics
- ✅ Optimize spending
- ✅ Demonstrate reliability
- ✅ Data-driven improvements

---

## Next Steps

1. **Week 5:** Add basic AgentOps integration (2 lines!)
2. **Week 6:** Add decorators for detailed tracking
3. **Week 7:** Set up alerts and dashboards
4. **Week 8:** Optimize based on metrics

---

## References

- **AgentOps Docs:** https://docs.agentops.ai
- **LangSmith:** https://smith.langchain.com
- **Reference:** `agentops/` in external repos
