# Memory & Learning Systems

**Source:** `langchain-reference/05-memory-learning/langmem/`

---

## Overview

Long-term memory allows agents to:
- Remember past research
- Learn from previous findings
- Avoid re-researching
- Make cross-company connections
- Improve over time

---

## Architecture

### Hot Path + Background Processing

```
┌─────────────────────────────────────────────────────────┐
│                    Hot Path (In-Conversation)            │
│                                                          │
│  User Request → Agent + Memory Tools → Response         │
│                    ↓                                      │
│              Store/Search Memories                       │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              Background Processing (Async)               │
│                                                          │
│  Conversation → Extract Key Info → Consolidate →        │
│      Update Knowledge Base → Memory Embeddings          │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Memory Store

```python
from langgraph.store.postgres import AsyncPostgresStore

store = AsyncPostgresStore(
    connection_string="postgresql://user:pass@localhost/db",
    index={
        "dims": 1536,  # OpenAI embedding dimension
        "embed": "openai:text-embedding-3-small"
    }
)
```

**Storage Options:**
- **InMemoryStore** - Development/testing
- **AsyncPostgresStore** - Production (recommended)
- **RedisStore** - Fast cache
- **Custom** - Roll your own

### 2. Memory Tools

```python
from langmem import create_manage_memory_tool, create_search_memory_tool

# Tool 1: Manage (Create/Update/Delete)
manage_tool = create_manage_memory_tool(
    namespace=("company_research",)
)

# Tool 2: Search (Semantic search)
search_tool = create_search_memory_tool(
    namespace=("company_research",)
)

# Give to agent
agent_tools = [manage_tool, search_tool, ...other_tools]
```

### 3. Memory Manager

```python
from langmem import create_memory_manager

memory_manager = create_memory_manager(
    store=store,
    namespace=("company_research",)
)

# Background: Extract and consolidate
await memory_manager.process_conversation(conversation_id)
```

---

## Implementation for Company Researcher

### Use Case 1: Remember Past Research

**Problem:** Re-researching same company wastes time/money

**Solution:**
```python
# Before starting research, check memory
async def check_past_research(company_name: str, store):
    """Check if we've researched this company before"""

    # Semantic search in memory
    past_research = await store.search(
        namespace=("company_research",),
        query=company_name,
        limit=5
    )

    if past_research:
        # Found past research
        most_recent = past_research[0]

        # Check if recent enough (< 30 days)
        age_days = (datetime.now() - most_recent.timestamp).days

        if age_days < 30:
            # Use cached research
            return {
                "use_cache": True,
                "data": most_recent.value,
                "age_days": age_days
            }
        else:
            # Re-research but use as context
            return {
                "use_cache": False,
                "context": most_recent.value,
                "age_days": age_days
            }

    return {"use_cache": False}
```

### Use Case 2: Cross-Company Insights

**Problem:** Can't learn patterns across companies

**Solution:**
```python
async def find_similar_companies(company_name: str, industry: str, store):
    """Find companies we've researched in same industry"""

    # Semantic search for similar companies
    similar = await store.search(
        namespace=("company_research",),
        query=f"{company_name} {industry}",
        limit=10
    )

    # Extract insights
    insights = []
    for company in similar:
        if company.value.get("industry") == industry:
            insights.append({
                "name": company.value["name"],
                "key_metrics": company.value["metrics"],
                "competitive_advantages": company.value["advantages"]
            })

    return insights


# Use insights
def analyze_with_context(company_data, similar_companies):
    """Analyze company with context from similar companies"""

    prompt = f"""Analyze {company_data['name']} in context of similar companies.

Target Company:
{company_data}

Similar Companies in {company_data['industry']}:
{similar_companies}

Questions:
1. How does this company compare to industry peers?
2. What unique advantages does it have?
3. What patterns do we see across this industry?
"""

    analysis = llm.invoke(prompt)
    return analysis
```

### Use Case 3: Source Quality Learning

**Problem:** Don't know which sources are reliable

**Solution:**
```python
class SourceQualityTracker:
    """Learn which sources provide quality information"""

    async def record_source_quality(
        self,
        source_url: str,
        quality_score: float,
        store
    ):
        """Track source quality over time"""

        # Store source quality
        await store.put(
            namespace=("source_quality",),
            key=source_url,
            value={
                "url": source_url,
                "quality_scores": [quality_score],
                "last_used": datetime.now()
            }
        )

    async def get_source_quality(self, source_url: str, store):
        """Get historical quality for a source"""

        source_data = await store.get(
            namespace=("source_quality",),
            key=source_url
        )

        if source_data:
            scores = source_data.value["quality_scores"]
            return sum(scores) / len(scores)  # Average

        return 0.5  # Default: neutral

    async def prioritize_sources(self, sources: list[str], store):
        """Sort sources by quality"""

        source_quality = []
        for source in sources:
            quality = await self.get_source_quality(source, store)
            source_quality.append((source, quality))

        # Sort by quality descending
        source_quality.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in source_quality]
```

---

## Memory Schema

### Research Memory Structure

```python
{
    "namespace": ("company_research", "Tesla"),
    "key": "2024-12-05T10:30:00",
    "value": {
        "company_name": "Tesla",
        "industry": "Automotive",
        "research_date": "2024-12-05",
        "data": {
            "overview": {...},
            "financial": {...},
            "competitive": {...}
        },
        "quality_score": 0.92,
        "completeness_score": 0.95,
        "sources": [
            {"url": "...", "quality": 0.95, "type": "official"},
            {"url": "...", "quality": 0.88, "type": "news"}
        ],
        "key_insights": [
            "Revenue growing 40% YoY",
            "Cybertruck production ramping",
            "FSD subscriptions increasing"
        ],
        "extraction_metadata": {
            "agents_used": ["financial", "market", "competitive"],
            "total_cost": 0.28,
            "total_time": 120
        }
    }
}
```

### Insight Memory Structure

```python
{
    "namespace": ("insights", "automotive"),
    "key": "insight_001",
    "value": {
        "insight": "EV companies with vertical integration show 20% higher margins",
        "supporting_companies": ["Tesla", "BYD", "Rivian"],
        "confidence": 0.85,
        "discovered_date": "2024-12-05",
        "relevance_count": 3  # How many companies support this
    }
}
```

---

## Implementation Roadmap

### Phase 1: Basic Memory (Week 8)
```python
# Store completed research
- Save research results to PostgreSQL
- Track basic metadata
- No semantic search yet
```

### Phase 2: Semantic Search (Week 9)
```python
# Add embeddings and search
- Embed research summaries
- Implement semantic search
- Find similar past research
```

### Phase 3: Source Quality Tracking (Week 10)
```python
# Learn from source quality
- Track source reliability over time
- Prioritize high-quality sources
- Avoid low-quality sources
```

### Phase 4: Cross-Company Insights (Week 11)
```python
# Learn patterns across companies
- Identify industry trends
- Compare companies in same sector
- Generate comparative insights
```

---

## Code Templates

### Template: Store Research Results

```python
async def store_research_results(
    company_name: str,
    research_data: dict,
    metadata: dict,
    store: AsyncPostgresStore
):
    """Store completed research in memory"""

    namespace = ("company_research", company_name)
    key = datetime.now().isoformat()

    await store.put(
        namespace=namespace,
        key=key,
        value={
            "company_name": company_name,
            "research_date": datetime.now(),
            "data": research_data,
            "metadata": metadata
        }
    )
```

### Template: Search Past Research

```python
async def search_past_research(
    query: str,
    limit: int,
    store: AsyncPostgresStore
) -> list[dict]:
    """Semantic search across all past research"""

    results = await store.search(
        namespace=("company_research",),
        query=query,
        limit=limit
    )

    return [
        {
            "company": result.value["company_name"],
            "date": result.value["research_date"],
            "data": result.value["data"],
            "relevance": result.score
        }
        for result in results
    ]
```

### Template: Background Consolidation

```python
async def consolidate_insights(store: AsyncPostgresStore):
    """Background task to extract cross-company insights"""

    # Get all recent research
    recent = await store.list(
        namespace=("company_research",),
        limit=100
    )

    # Extract insights using LLM
    prompt = f"""Analyze these {len(recent)} company research results.

Identify:
1. Common patterns
2. Industry trends
3. Success factors
4. Risk patterns

Research summaries:
{[r.value for r in recent]}

Return insights as JSON array."""

    insights = llm.invoke(prompt)

    # Store insights
    for idx, insight in enumerate(insights):
        await store.put(
            namespace=("insights",),
            key=f"insight_{idx}",
            value=insight
        )
```

---

## Performance Considerations

### Embeddings Cost

```python
# OpenAI text-embedding-3-small
Cost: $0.00002 per 1K tokens

# Embedding 1,000 companies @ 500 tokens each
Tokens: 500,000
Cost: $0.01

# Very cheap!
```

### Storage Cost

```python
# PostgreSQL
100 companies: ~10 MB
1,000 companies: ~100 MB
10,000 companies: ~1 GB

# PostgreSQL pricing (managed):
1 GB storage: ~$0.10/month

# Vector index (Qdrant):
1,000 vectors (1536 dims): ~6 MB
10,000 vectors: ~60 MB

# Also very cheap!
```

### Query Performance

```python
# Semantic search with embeddings
Latency: 10-50ms (with proper indexing)

# Can handle:
- 10,000+ companies
- Sub-second search
- Concurrent queries
```

---

## Benefits

### 1. Cost Savings
```python
# Without memory:
- Re-research Tesla every time: $0.30
- 10 requests: $3.00

# With memory:
- First research: $0.30
- Next 9 requests (cached): $0.00
- Total: $0.30

# Savings: 90%
```

### 2. Speed Improvement
```python
# Without memory:
- Full research: 2-5 minutes

# With memory (cache hit):
- Retrieve cached: 1-2 seconds

# Speedup: 100x
```

### 3. Quality Improvement
```python
# With memory:
- Learn which sources are reliable
- Improve over time
- Cross-company insights
- Pattern recognition
```

---

## Integration with Company Researcher

### Modified Research Workflow

```python
async def research_with_memory(company_name: str, store):
    """Research workflow with memory integration"""

    # 1. Check memory first
    cached = await check_past_research(company_name, store)

    if cached["use_cache"]:
        # Return cached results
        return cached["data"]

    # 2. Get similar companies for context
    similar = await find_similar_companies(company_name, store)

    # 3. Conduct research with context
    research_data = await conduct_research(
        company_name,
        context={"similar_companies": similar}
    )

    # 4. Store results in memory
    await store_research_results(company_name, research_data, store)

    # 5. Background: Extract insights
    asyncio.create_task(consolidate_insights(store))

    return research_data
```

---

## Next Steps

1. **Week 8:** Set up PostgreSQL + basic storage
2. **Week 9:** Add embeddings and semantic search
3. **Week 10:** Implement source quality tracking
4. **Week 11:** Build cross-company insight extraction
5. **Week 12:** Create memory dashboard (view past research)

---

## References

- **LangMem Docs:** `langchain-reference/05-memory-learning/langmem/`
- **Store Options:** PostgreSQL, Redis, InMemory
- **Embedding Models:** OpenAI, Cohere, custom
