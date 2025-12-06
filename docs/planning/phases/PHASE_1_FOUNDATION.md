# Phase 1: Foundation - Observability & Stability

**Duration:** 2 weeks (Weeks 1-2)
**Effort:** 60-80 hours
**Team:** 1-2 developers
**Priority:** ⭐⭐⭐⭐⭐ Critical
**Status:** Ready to start

---

## 🎯 Objectives

Build the foundational infrastructure for professional-grade research system:
1. **Observability:** Full visibility into all operations
2. **Stability:** Robust error handling and recovery
3. **Efficiency:** Optimize resource usage
4. **Reliability:** Multiple providers with fallback

---

## 📋 Features to Implement

### Feature 1: LangSmith Observability ⭐⭐⭐⭐⭐
**Effort:** 4-6 hours
**Priority:** Critical

**What:** Integrate LangSmith for full tracing and monitoring

**Why:**
- Debug issues in production
- Track agent behavior
- Identify bottlenecks
- Monitor performance

**Implementation:**
```python
# 1. Environment setup (.env)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT="langai-research"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# 2. Code integration (src/infrastructure/observability/langsmith_config.py)
import os
from langchain.callbacks import LangChainTracer

def setup_langsmith():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    return LangChainTracer(project_name="langai-research")

# 3. Apply to all LLM calls
llm.invoke(prompt, config={"callbacks": [tracer]})
```

**Acceptance Criteria:**
- ✅ All agent calls visible in LangSmith dashboard
- ✅ Traces include input, output, latency
- ✅ Can filter by agent type
- ✅ Can search by company name

**Testing:**
- Run sample research
- Verify trace appears in dashboard
- Check all metadata captured

**Dependencies:** None

**Risks:** API key management

---

### Feature 2: Cost Tracking System ⭐⭐⭐⭐⭐
**Effort:** 6-8 hours
**Priority:** Critical

**What:** Track costs per research, per agent, per tool

**Why:**
- Budget control
- Identify expensive operations
- Optimize spending
- Report to stakeholders

**Implementation:**
```python
# src/infrastructure/cost_tracker.py
from langchain.callbacks import get_openai_callback
from dataclasses import dataclass
from typing import Dict

@dataclass
class CostReport:
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    breakdown: Dict[str, float]  # per agent/tool

class CostTracker:
    def __init__(self):
        self.costs = {}

    async def track_operation(self, operation_name: str, func):
        with get_openai_callback() as cb:
            result = await func()
            self.costs[operation_name] = {
                "tokens": cb.total_tokens,
                "cost": cb.total_cost
            }
            return result

    def get_report(self) -> CostReport:
        total_cost = sum(c["cost"] for c in self.costs.values())
        total_tokens = sum(c["tokens"] for c in self.costs.values())
        return CostReport(
            total_tokens=total_tokens,
            total_cost=total_cost,
            breakdown=self.costs
        )

# Usage in agents
cost_tracker = CostTracker()
result = await cost_tracker.track_operation(
    "financial_analysis",
    lambda: financial_agent.research(context)
)
report = cost_tracker.get_report()
print(f"Total cost: ${report.total_cost:.4f}")
```

**Acceptance Criteria:**
- ✅ Cost tracked for every LLM call
- ✅ Breakdown by agent type
- ✅ Total cost per research < $0.50
- ✅ Cost report in research output

**Testing:**
- Run research and verify cost report
- Check all agents tracked
- Validate cost calculations

**Dependencies:** None

---

### Feature 3: Multi-Provider Search Fallback ⭐⭐⭐⭐
**Effort:** 8-12 hours
**Priority:** High

**What:** Implement fallback chain for search providers

**Why:**
- Reliability (if Tavily fails)
- Rate limit handling
- Different providers for different queries
- No single point of failure

**Implementation:**
```python
# src/tools/search/manager.py
from enum import Enum
from typing import List, Optional

class SearchProvider(Enum):
    TAVILY = "tavily"
    BRAVE = "brave"
    DUCKDUCKGO = "duckduckgo"
    SERPER = "serper"

class SearchManager:
    def __init__(self):
        self.providers = [
            TavilySearch(),
            BraveSearch(),
            DuckDuckGoSearch(),
            SerperSearch()
        ]
        self.fallback_chain = [
            SearchProvider.TAVILY,
            SearchProvider.BRAVE,
            SearchProvider.DUCKDUCKGO
        ]

    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        for provider_type in self.fallback_chain:
            provider = self._get_provider(provider_type)
            try:
                results = await provider.search(query, max_results)
                if results:
                    logger.info(f"Search successful with {provider_type}")
                    return results
            except Exception as e:
                logger.warning(f"{provider_type} failed: {e}")
                continue

        raise SearchError("All search providers failed")

    def _get_provider(self, provider_type: SearchProvider):
        mapping = {
            SearchProvider.TAVILY: self.providers[0],
            SearchProvider.BRAVE: self.providers[1],
            SearchProvider.DUCKDUCKGO: self.providers[2],
        }
        return mapping[provider_type]

# src/tools/search/providers/brave.py
import aiohttp

class BraveSearch:
    def __init__(self):
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.endpoint = "https://api.search.brave.com/res/v1/web/search"

    async def search(self, query: str, max_results: int = 10):
        async with aiohttp.ClientSession() as session:
            headers = {"X-Subscription-Token": self.api_key}
            params = {"q": query, "count": max_results}
            async with session.get(
                self.endpoint,
                headers=headers,
                params=params
            ) as resp:
                data = await resp.json()
                return self._parse_results(data)

# src/tools/search/providers/duckduckgo.py
from duckduckgo_search import DDGS

class DuckDuckGoSearch:
    async def search(self, query: str, max_results: int = 10):
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                SearchResult(
                    title=r["title"],
                    url=r["link"],
                    snippet=r["body"]
                )
                for r in results
            ]
```

**Acceptance Criteria:**
- ✅ 3+ search providers configured
- ✅ Automatic fallback on failure
- ✅ Logs which provider succeeded
- ✅ No crashes on search failure

**Testing:**
- Disable Tavily, verify Brave fallback
- Disable all, verify graceful error
- Performance test with different providers

**Dependencies:**
- Brave API key
- DuckDuckGo library

---

### Feature 4: Error Handling Framework ⭐⭐⭐⭐
**Effort:** 6-8 hours
**Priority:** High

**What:** Comprehensive error handling with custom exceptions

**Why:**
- Clear error messages
- Graceful degradation
- Easy debugging
- Never crash completely

**Implementation:**
```python
# src/core/errors/exceptions.py
class ResearchError(Exception):
    """Base exception for all research errors"""
    pass

class AgentExecutionError(ResearchError):
    """Agent failed to execute"""
    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"Agent '{agent_name}' failed: {message}")

class ToolExecutionError(ResearchError):
    """Tool failed to execute"""
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")

class DataExtractionError(ResearchError):
    """Failed to extract data"""
    pass

class ValidationError(ResearchError):
    """Data validation failed"""
    pass

class PipelineError(ResearchError):
    """Pipeline execution failed"""
    pass

# src/core/errors/retry.py
import asyncio
from functools import wraps

def retry_on_failure(max_retries=3, delay=1.0, backoff=2.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# Usage in agents
@retry_on_failure(max_retries=3)
async def search_with_retry(query: str):
    return await search_manager.search(query)

# src/core/errors/fallback.py
class FallbackHandler:
    """Handle graceful degradation"""

    @staticmethod
    async def execute_with_fallback(
        primary_func,
        fallback_func,
        context: str = "operation"
    ):
        try:
            return await primary_func()
        except Exception as e:
            logger.warning(
                f"{context} failed with primary method: {e}. "
                f"Using fallback..."
            )
            try:
                return await fallback_func()
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                raise PipelineError(
                    f"Both primary and fallback failed for {context}"
                )

# Usage
result = await FallbackHandler.execute_with_fallback(
    primary_func=lambda: expensive_api_call(),
    fallback_func=lambda: cheaper_alternative(),
    context="financial_data_fetch"
)
```

**Acceptance Criteria:**
- ✅ Custom exception hierarchy
- ✅ Retry logic with backoff
- ✅ Fallback mechanisms
- ✅ Clear error messages

**Testing:**
- Test each exception type
- Verify retry logic
- Test fallback activation
- Check error logging

**Dependencies:** None

---

### Feature 5: Tool Singleton Pattern ⭐⭐⭐⭐
**Effort:** 4-6 hours
**Priority:** Medium

**What:** Reuse expensive tool instances across agents

**Why:**
- Reduce memory usage
- Faster agent initialization
- Share browser sessions
- Resource efficiency

**Implementation:**
```python
# src/tools/shared.py
import threading
from typing import Optional

# Singleton instances
_search_tool_instance: Optional[SearchTool] = None
_browser_tool_instance: Optional[BrowserTool] = None

# Thread-safe locks
_search_tool_lock = threading.Lock()
_browser_tool_lock = threading.Lock()

def get_shared_search_tool() -> SearchTool:
    """Get or create shared SearchTool (thread-safe)"""
    global _search_tool_instance
    if _search_tool_instance is None:
        with _search_tool_lock:
            # Double-check locking
            if _search_tool_instance is None:
                _search_tool_instance = SearchTool()
    return _search_tool_instance

def get_shared_browser_tool() -> BrowserTool:
    """Get or create shared BrowserTool (thread-safe)"""
    global _browser_tool_instance
    if _browser_tool_instance is None:
        with _browser_tool_lock:
            if _browser_tool_instance is None:
                _browser_tool_instance = BrowserTool()
    return _browser_tool_instance

def reset_shared_tools():
    """Reset all shared tools (for testing)"""
    global _search_tool_instance, _browser_tool_instance
    with _search_tool_lock:
        _search_tool_instance = None
    with _browser_tool_lock:
        _browser_tool_instance = None

# Usage in agents
class FinancialAgent:
    def __init__(self):
        # Reuse shared instances
        self.search = get_shared_search_tool()
        self.browser = get_shared_browser_tool()
```

**Acceptance Criteria:**
- ✅ Tools instantiated only once
- ✅ Thread-safe access
- ✅ 50% reduction in memory usage
- ✅ Faster agent initialization

**Testing:**
- Test concurrent access
- Verify single instance
- Measure memory reduction
- Benchmark initialization time

**Dependencies:** None

---

### Feature 6: Source Tracking ⭐⭐⭐⭐⭐
**Effort:** 6-8 hours
**Priority:** Critical

**What:** Track source URL, timestamp, quality for every fact

**Why:**
- Credibility
- Auditability
- Verification
- Compliance

**Implementation:**
```python
# src/core/models/source.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from enum import Enum

class SourceQuality(str, Enum):
    OFFICIAL = "official"          # Company website, SEC filings
    AUTHORITATIVE = "authoritative"  # Bloomberg, Reuters
    REPUTABLE = "reputable"         # Forbes, TechCrunch
    COMMUNITY = "community"         # Reddit, forums
    UNKNOWN = "unknown"

class Source(BaseModel):
    url: HttpUrl
    title: str
    retrieved_at: datetime
    quality: SourceQuality
    quality_score: float  # 0-100

class ResearchFact(BaseModel):
    content: str
    source: Source
    confidence: str  # "High", "Medium", "Low"
    verified: bool = False

    def to_markdown(self) -> str:
        return f"""
**Data:** {self.content}
**Source:** [{self.source.title}]({self.source.url})
**Retrieved:** {self.source.retrieved_at.strftime('%Y-%m-%d %H:%M:%S')}
**Quality:** {self.source.quality.value} ({self.source.quality_score}/100)
**Confidence:** {self.confidence}
"""

# src/quality/source_tracker.py
class SourceTracker:
    def __init__(self):
        self.sources = []

    def add_fact(
        self,
        content: str,
        url: str,
        title: str
    ) -> ResearchFact:
        source = Source(
            url=url,
            title=title,
            retrieved_at=datetime.utcnow(),
            quality=self._assess_quality(url),
            quality_score=self._calculate_score(url)
        )
        fact = ResearchFact(
            content=content,
            source=source,
            confidence=self._calculate_confidence(source)
        )
        self.sources.append(fact)
        return fact

    def _assess_quality(self, url: str) -> SourceQuality:
        domain = urlparse(url).netloc
        if any(d in domain for d in ["sec.gov", "ir.tesla.com"]):
            return SourceQuality.OFFICIAL
        elif any(d in domain for d in ["bloomberg.com", "reuters.com"]):
            return SourceQuality.AUTHORITATIVE
        elif any(d in domain for d in ["forbes.com", "techcrunch.com"]):
            return SourceQuality.REPUTABLE
        elif any(d in domain for d in ["reddit.com", "news.ycombinator.com"]):
            return SourceQuality.COMMUNITY
        return SourceQuality.UNKNOWN

    def _calculate_score(self, url: str) -> float:
        quality = self._assess_quality(url)
        scores = {
            SourceQuality.OFFICIAL: 95,
            SourceQuality.AUTHORITATIVE: 85,
            SourceQuality.REPUTABLE: 75,
            SourceQuality.COMMUNITY: 50,
            SourceQuality.UNKNOWN: 30
        }
        return scores[quality]

    def _calculate_confidence(self, source: Source) -> str:
        if source.quality_score >= 80:
            return "High"
        elif source.quality_score >= 60:
            return "Medium"
        return "Low"

    def generate_source_log(self) -> str:
        log = "# Source Log\n\n"
        for i, fact in enumerate(self.sources, 1):
            log += f"## Source {i}\n"
            log += fact.to_markdown()
            log += "\n---\n\n"
        return log
```

**Acceptance Criteria:**
- ✅ Every fact has source URL
- ✅ Timestamp recorded
- ✅ Quality assessment automated
- ✅ Source log generated

**Testing:**
- Add facts and verify tracking
- Check quality assessment
- Generate source log
- Validate markdown output

**Dependencies:** None

---

## 📅 Weekly Breakdown

### Week 1: Observability & Search

**Monday-Tuesday:**
- Set up LangSmith integration
- Implement cost tracking
- Write tests

**Wednesday-Thursday:**
- Implement multi-provider search
- Add Brave and DuckDuckGo providers
- Test fallback chain

**Friday:**
- Code review
- Documentation
- Demo to team

**Deliverables:**
- LangSmith dashboard accessible
- Cost tracking working
- 3 search providers operational

---

### Week 2: Stability & Optimization

**Monday-Tuesday:**
- Implement error handling framework
- Add retry logic
- Create fallback mechanisms

**Wednesday-Thursday:**
- Implement tool singleton pattern
- Add source tracking
- Write comprehensive tests

**Friday:**
- Phase 1 review
- Retrospective
- Phase 2 planning

**Deliverables:**
- Robust error handling
- Resource optimization
- Source tracking system

---

## 🎯 Success Criteria

### Observability
- ✅ 100% of operations visible in LangSmith
- ✅ Cost tracked per research
- ✅ Performance metrics available
- ✅ Error logs captured

### Reliability
- ✅ No crashes on search failure
- ✅ Graceful error messages
- ✅ Fallback mechanisms working
- ✅ 99% success rate

### Efficiency
- ✅ 50% reduction in memory usage
- ✅ Faster agent initialization
- ✅ Resource pooling working
- ✅ Cost per research < $0.50

### Quality
- ✅ All facts cite sources
- ✅ Quality scores assigned
- ✅ Source log generated
- ✅ Timestamps recorded

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/unit/test_cost_tracker.py
def test_cost_tracking():
    tracker = CostTracker()
    # Mock LLM call with known cost
    result = tracker.track_operation("test", mock_llm_call)
    assert tracker.costs["test"]["cost"] > 0

# tests/unit/test_search_manager.py
@pytest.mark.asyncio
async def test_fallback_chain():
    manager = SearchManager()
    # Disable Tavily
    manager.providers[0] = None
    results = await manager.search("test query")
    # Should fallback to Brave
    assert len(results) > 0
```

### Integration Tests
```python
# tests/integration/test_phase1.py
@pytest.mark.asyncio
async def test_full_research_with_observability():
    # Run research
    result = await run_research("Tesla", "Automotive")

    # Verify observability
    assert langsmith_has_trace("Tesla")

    # Verify cost tracking
    assert result.cost_report.total_cost < 0.50

    # Verify source tracking
    assert len(result.sources) > 0
```

### Manual Tests
- LangSmith dashboard accessibility
- Search provider fallback behavior
- Error message clarity
- Cost report accuracy

---

## 📊 Metrics to Track

**Performance:**
- Research completion time
- Agent initialization time
- Search latency

**Quality:**
- Source quality distribution
- Fact confidence levels
- Error recovery rate

**Cost:**
- Total cost per research
- Cost per agent
- Token usage

**Reliability:**
- Success rate
- Fallback activation rate
- Error frequency

---

## 🚧 Risks & Mitigation

**Risk 1: API Key Management**
- Impact: High
- Probability: Low
- Mitigation: Use environment variables, never commit keys

**Risk 2: LangSmith Performance**
- Impact: Medium
- Probability: Low
- Mitigation: Async tracing, batching, fallback to local logging

**Risk 3: Search Provider Rate Limits**
- Impact: Medium
- Probability: Medium
- Mitigation: Multiple providers, rate limiting, caching

**Risk 4: Integration Complexity**
- Impact: Medium
- Probability: Medium
- Mitigation: Incremental integration, comprehensive tests

---

## 📚 Resources

**Documentation to Create:**
- [ ] LangSmith setup guide
- [ ] Cost tracking user guide
- [ ] Search provider configuration
- [ ] Error handling best practices
- [ ] Tool singleton usage

**External Dependencies:**
- [ ] LangSmith account and API key
- [ ] Brave Search API key (optional)
- [ ] OpenAI/Anthropic API keys

**Tools & Libraries:**
- [ ] langchain
- [ ] langsmith
- [ ] duckduckgo-search
- [ ] aiohttp

---

## ✅ Phase 1 Checklist

### Setup
- [ ] Create feature branches
- [ ] Set up development environment
- [ ] Install dependencies
- [ ] Configure environment variables

### Implementation
- [ ] LangSmith integration
- [ ] Cost tracking system
- [ ] Multi-provider search
- [ ] Error handling framework
- [ ] Tool singleton pattern
- [ ] Source tracking system

### Testing
- [ ] Unit tests written
- [ ] Integration tests passed
- [ ] Manual testing completed
- [ ] Performance benchmarked

### Documentation
- [ ] Setup guides written
- [ ] API documentation updated
- [ ] Code comments added
- [ ] README updated

### Review
- [ ] Code review completed
- [ ] Team demo delivered
- [ ] Retrospective held
- [ ] Metrics analyzed

---

## 🎯 Definition of Done

Phase 1 is complete when:

1. **All features implemented and tested**
   - LangSmith working
   - Cost tracking operational
   - Search fallback functional
   - Error handling comprehensive
   - Tool singletons working
   - Source tracking active

2. **All tests passing**
   - Unit tests: 90%+ coverage
   - Integration tests: all passing
   - Manual tests: all scenarios covered

3. **Documentation complete**
   - Setup guides written
   - API docs updated
   - Code well-commented

4. **Team approval**
   - Code review passed
   - Demo accepted
   - Metrics meet targets

5. **Ready for Phase 2**
   - No blocking bugs
   - Performance acceptable
   - Foundation solid

---

**Next:** [Phase 2: Specialist Agents](PHASE_2_SPECIALISTS.md)
