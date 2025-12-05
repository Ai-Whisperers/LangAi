# External Repositories - Extraction Guide

**Purpose:** Step-by-step guide for extracting code patterns and implementing them in your project
**Last Updated:** 2025-12-05

---

## 📋 Table of Contents

1. [Extraction Strategy](#extraction-strategy)
2. [Phase-by-Phase Roadmap](#phase-by-phase-roadmap)
3. [Priority Extraction List](#priority-extraction-list)
4. [Code Extraction Templates](#code-extraction-templates)
5. [Testing Extracted Code](#testing-extracted-code)
6. [Integration Checklist](#integration-checklist)

---

## Extraction Strategy

### Principles

1. **Extract > Adapt > Integrate**
   - Don't copy-paste blindly
   - Understand the pattern first
   - Adapt to your architecture
   - Integrate incrementally

2. **Start Small, Build Up**
   - Extract one pattern at a time
   - Test thoroughly before moving on
   - Build on working foundations

3. **Document as You Go**
   - Note what you extracted and why
   - Document adaptations made
   - Track what worked and what didn't

---

## Phase-by-Phase Roadmap

### Phase 1: Research Architecture (Weeks 1-2)

**Goal:** Build core research agent with 3-phase workflow

#### Week 1: Foundation

**Day 1-2: Study open_deep_research**
```bash
cd langchain-reference/04-production-apps/open_deep_research
cat README.md

# Key files to read:
- graph.py          # State machine
- models.py         # Multi-model routing
- report_gen.py     # Report generation
```

**Extract:**
1. State machine pattern
2. Multi-model routing logic
3. Report generation templates

**Create in your project:**
```
research-workflow-system/
├── core/
│   ├── state_machine.py    # Extracted from graph.py
│   ├── model_router.py     # Extracted from models.py
│   └── report_gen.py       # Extracted from report_gen.py
└── tests/
    ├── test_state_machine.py
    ├── test_model_router.py
    └── test_report_gen.py
```

**Day 3-4: Study company-researcher**
```bash
cd langchain-reference/01-research-agents/company-researcher
```

**Extract:**
1. 3-phase workflow (search → extract → reflect)
2. JSON schema extraction
3. Quality reflection mechanism

**Create:**
```python
# core/workflows/research_workflow.py
from enum import Enum

class ResearchPhase(Enum):
    SEARCH = "search"
    EXTRACT = "extract"
    REFLECT = "reflect"

class ThreePhaseWorkflow:
    def __init__(self):
        self.current_phase = ResearchPhase.SEARCH

    async def execute(self, query):
        # Phase 1: Search
        sources = await self.search_phase(query)

        # Phase 2: Extract
        data = await self.extract_phase(sources)

        # Phase 3: Reflect
        quality = await self.reflect_phase(data, query)

        if quality < 0.7:
            # Retry with improved query
            return await self.execute(self.improve_query(query, data))

        return data
```

**Day 5-7: Build Prototype**
```bash
# Create basic research agent
# Test with sample queries
# Document results
```

**Deliverable:** Working 3-phase research agent

#### Week 2: Enhancement

**Day 1-3: Add Tavily Search**
```python
# Install
pip install tavily-python

# Integrate (extracted pattern from company-researcher)
from tavily import TavilyClient

class SearchPhase:
    def __init__(self, api_key):
        self.tavily = TavilyClient(api_key=api_key)

    async def search(self, query, max_results=10):
        response = self.tavily.search(
            query=query,
            max_results=max_results,
            include_domains=["edu", "gov", "org"]  # Quality sources
        )
        return response["results"]
```

**Day 4-5: Add JSON Extraction**
```python
# Extracted from company-researcher
from pydantic import BaseModel, Field
from openai import OpenAI

class CompanyData(BaseModel):
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    founded: int = Field(description="Year founded")
    description: str = Field(description="Company description")

class JSONExtractor:
    def __init__(self, llm):
        self.llm = llm

    async def extract(self, sources, schema: BaseModel):
        context = "\n\n".join([s["content"] for s in sources])

        response = await self.llm.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract structured data from context"},
                {"role": "user", "content": f"Context:\n{context}\n\nExtract data according to schema."}
            ],
            response_format=schema
        )

        return response.choices[0].message.parsed
```

**Day 6-7: Add Quality Reflection**
```python
# Extracted pattern
class QualityReflector:
    def __init__(self, llm):
        self.llm = llm

    async def assess(self, data, query):
        prompt = f"""
        Query: {query}
        Data extracted: {data.json()}

        Assess the quality of this data on a scale of 0-1:
        - Is it accurate?
        - Is it complete?
        - Is it relevant?
        - Are there gaps?

        Return JSON: {{"score": 0.0-1.0, "gaps": ["..."], "suggestions": ["..."]}}
        """

        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

**Deliverable:** Enhanced research agent with search, extraction, and reflection

---

### Phase 2: Memory System (Weeks 3-4)

**Goal:** Add persistent memory and semantic search

#### Week 3: Memory Architecture

**Day 1-3: Study langmem**
```bash
cd langchain-reference/05-memory-learning/langmem
```

**Extract:**
1. Dual-layer memory (hot + cold)
2. Semantic search implementation
3. Memory consolidation

**Implement:**
```python
# core/memory/memory_manager.py
from typing import List, Dict
import chromadb

class MemoryManager:
    def __init__(self):
        # Hot path - in-memory cache
        self.hot_memory = {}
        self.hot_memory_max_size = 100

        # Cold path - persistent vector store
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(
            name="research_memories",
            metadata={"hnsw:space": "cosine"}
        )

    async def store(self, item: Dict, embedding: List[float]):
        # Add to hot memory
        item_id = item["id"]
        self.hot_memory[item_id] = item

        # Persist to cold storage
        self.collection.add(
            ids=[item_id],
            embeddings=[embedding],
            metadatas=[item],
            documents=[item["text"]]
        )

        # Prune hot memory if needed
        if len(self.hot_memory) > self.hot_memory_max_size:
            self._prune_hot_memory()

    async def recall(self, query_embedding: List[float], k: int = 5):
        # Search vector store
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        return results
```

**Day 4-5: Study context_engineering**
```bash
cd langchain-reference/05-memory-learning/context_engineering
```

**Extract:**
1. WRITE: Structured formatting
2. SELECT: Relevance scoring
3. COMPRESS: Token reduction
4. ISOLATE: Context separation

**Implement:**
```python
# core/memory/context_optimizer.py
class ContextOptimizer:
    def optimize(self, memories: List[Dict], query: str, max_tokens: int):
        # 1. WRITE: Structure the memories
        structured = [self._structure_memory(m) for m in memories]

        # 2. SELECT: Score and filter by relevance
        scored = [(m, self._score_relevance(m, query)) for m in structured]
        sorted_memories = sorted(scored, key=lambda x: x[1], reverse=True)

        # 3. COMPRESS: Reduce to fit token limit
        selected_memories = []
        token_count = 0

        for memory, score in sorted_memories:
            memory_tokens = self._count_tokens(memory)
            if token_count + memory_tokens <= max_tokens:
                selected_memories.append(memory)
                token_count += memory_tokens

        # 4. ISOLATE: Separate by namespace
        isolated = self._isolate_by_namespace(selected_memories)

        return isolated
```

**Day 6-7: Integration**
```python
# Integrate memory with research workflow
class MemoryEnabledResearchAgent:
    def __init__(self):
        self.workflow = ThreePhaseWorkflow()
        self.memory = MemoryManager()
        self.context_optimizer = ContextOptimizer()

    async def research(self, query):
        # Recall relevant memories
        query_embedding = await self.embed(query)
        memories = await self.memory.recall(query_embedding, k=10)

        # Optimize context
        context = self.context_optimizer.optimize(
            memories,
            query,
            max_tokens=4000
        )

        # Run workflow with context
        result = await self.workflow.execute(query, context)

        # Store new memory
        result_embedding = await self.embed(result["text"])
        await self.memory.store(result, result_embedding)

        return result
```

**Deliverable:** Research agent with persistent memory

#### Week 4: User-Scoped Storage

**Day 1-3: Study memory-agent**
```bash
cd langchain-reference/05-memory-learning/memory-agent
```

**Extract:**
1. User-scoped isolation
2. Cross-session persistence
3. Memory lifecycle management

**Implement:**
```python
# core/memory/user_memory.py
class UserMemoryManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def get_user_memory(self, user_id: str):
        user_path = f"{self.storage_path}/{user_id}"

        # Create if doesn't exist
        if not os.path.exists(user_path):
            os.makedirs(user_path)

        return UserMemory(user_id, user_path)

class UserMemory:
    def __init__(self, user_id: str, storage_path: str):
        self.user_id = user_id
        self.storage_path = storage_path

        # User-specific collections
        self.conversations_file = f"{storage_path}/conversations.json"
        self.entities_file = f"{storage_path}/entities.json"
        self.facts_file = f"{storage_path}/facts.json"

        self._load()

    def _load(self):
        self.conversations = self._load_json(self.conversations_file)
        self.entities = self._load_json(self.entities_file)
        self.facts = self._load_json(self.facts_file)
```

**Day 4-7: Full Integration**
- Combine all memory components
- Add to research workflow
- Test cross-session persistence

**Deliverable:** Complete memory system with user isolation

---

### Phase 3: Observability (Week 5)

**Goal:** Add comprehensive monitoring

**Day 1-3: AgentOps Integration**
```bash
pip install agentops
```

**Extract from agentops/**
1. Decorator pattern
2. Session management
3. Cost tracking

**Implement:**
```python
# Add to research agent
import agentops
from agentops.sdk.decorators import session, agent, operation

@agent
class ResearchAgent:
    @operation
    async def search(self, query):
        # Automatically tracked
        pass

    @operation
    async def extract(self, sources):
        # Automatically tracked
        pass

@session
async def research_workflow(topic):
    agentops.set_tags(["research", topic])

    agent = ResearchAgent()
    result = await agent.research(topic)

    agentops.end_session('Success')
    return result
```

**Day 4-5: Custom Metrics**
```python
# Add custom tracking
@operation
async def extract_data(sources):
    agentops.record({
        "source_count": len(sources),
        "extraction_start": datetime.now()
    })

    data = await extractor.extract(sources)

    agentops.record({
        "fields_extracted": len(data.dict()),
        "extraction_duration": (datetime.now() - start).total_seconds()
    })

    return data
```

**Deliverable:** Fully instrumented agent with observability

---

### Phase 4: Multi-Agent Patterns (Week 6)

**Goal:** Add multi-agent coordination

**Day 1-3: Supervisor Pattern**
```bash
cd langchain-reference/03-multi-agent-patterns/langgraph-supervisor-py
```

**Extract:**
```python
# core/coordination/supervisor.py
class SupervisorAgent:
    def __init__(self, workers: Dict[str, Agent]):
        self.workers = workers

    async def delegate(self, task):
        # Analyze task
        analysis = await self.analyze_task(task)

        # Select worker
        worker_name = analysis["recommended_worker"]
        worker = self.workers[worker_name]

        # Execute
        result = await worker.execute(task)

        # Validate
        if not await self.validate(result, task):
            # Retry or escalate
            return await self.handle_failure(task, result)

        return result
```

**Day 4-5: Swarm Pattern**
```bash
cd langchain-reference/03-multi-agent-patterns/langgraph-swarm-py
```

**Extract:**
```python
# core/coordination/swarm.py
class SwarmCoordination:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    async def collaborate(self, task):
        # All agents work on task
        results = await asyncio.gather(*[
            agent.process(task) for agent in self.agents
        ])

        # Reach consensus
        consensus = await self.aggregate_results(results)

        return consensus
```

**Deliverable:** Multi-agent coordination capabilities

---

### Phase 5: Production Readiness (Weeks 7-8)

**Day 1-5: Evaluation**
```bash
cd langchain-reference/07-evaluation-testing/openevals
cd oreilly-ai-agents/notebooks/
```

**Extract:**
1. Rubric evaluation
2. Quality scoring
3. Automated testing

**Day 6-10: Security**
```bash
cd Agent-Wiz/
```

**Extract:**
1. Workflow visualization
2. Threat assessment
3. Security checklist

**Day 11-14: Deployment**
```bash
cd agentcloud/
```

**Extract:**
1. Docker setup
2. Microservice architecture
3. Production patterns

**Deliverable:** Production-ready agent system

---

## Priority Extraction List

### MUST EXTRACT (Immediate)

| # | Pattern | Source | Priority | Complexity |
|---|---------|--------|----------|------------|
| 1 | 3-phase workflow | company-researcher | 🔥 HIGH | Low |
| 2 | State machine | open_deep_research | 🔥 HIGH | Medium |
| 3 | Dual-layer memory | langmem | 🔥 HIGH | Medium |
| 4 | AgentOps decorators | agentops | ⚡ MEDIUM | Low |
| 5 | JSON extraction | company-researcher | 🔥 HIGH | Low |
| 6 | Quality reflection | company-researcher | 🔥 HIGH | Low |
| 7 | Context optimization | context_engineering | ⚡ MEDIUM | Medium |
| 8 | User-scoped storage | memory-agent | ⚡ MEDIUM | Low |

### SHOULD EXTRACT (Next Month)

| # | Pattern | Source | Priority | Complexity |
|---|---------|--------|----------|------------|
| 9 | Supervisor coordination | langgraph-supervisor | ⚡ MEDIUM | Medium |
| 10 | Swarm collaboration | langgraph-swarm | ⚡ MEDIUM | Medium |
| 11 | Multi-model routing | open_deep_research | ⚡ MEDIUM | Medium |
| 12 | Report generation | open_deep_research | 💡 LOW | Low |
| 13 | Rubric evaluation | oreilly/openevals | ⚡ MEDIUM | Low |
| 14 | Tool selection testing | oreilly | 💡 LOW | Low |
| 15 | MCP integration | langchain-mcp-adapters | 💡 LOW | High |

### NICE TO HAVE (Future)

| # | Pattern | Source | Priority | Complexity |
|---|---------|--------|----------|------------|
| 16 | Threat modeling | Agent-Wiz | 💡 LOW | Medium |
| 17 | Workflow visualization | Agent-Wiz | 💡 LOW | Low |
| 18 | Docker deployment | agentcloud | 💡 LOW | Medium |
| 19 | Socket.io streaming | agentcloud | 💡 LOW | Medium |
| 20 | Plan & Execute | oreilly | ⚡ MEDIUM | Medium |

---

## Code Extraction Templates

### Template 1: Extract Function Pattern

```python
# 1. Read original code
# SOURCE: langchain-reference/01-research-agents/company-researcher/workflow.py

def original_function(input):
    # Original implementation
    pass

# 2. Extract and adapt
# TARGET: research-workflow-system/core/workflows/research.py

class ExtractedPattern:
    """
    Extracted from: company-researcher/workflow.py
    Adaptations:
    - Changed input format
    - Added error handling
    - Integrated with our memory system
    """

    def __init__(self):
        self.memory = MemoryManager()  # Our integration

    async def adapted_function(self, input):
        # Adapted implementation
        pass
```

### Template 2: Extract Class Pattern

```python
# SOURCE: langchain-reference/05-memory-learning/langmem/memory.py

# 1. Extract class structure
class OriginalClass:
    def __init__(self):
        pass

    def method1(self):
        pass

    def method2(self):
        pass

# 2. Adapt to your architecture
# TARGET: research-workflow-system/core/memory/manager.py

class AdaptedClass:
    """
    Based on: langmem/memory.py::OriginalClass

    Adaptations:
    - Added async support
    - Integrated with ChromaDB instead of Qdrant
    - Added custom embedding model
    """

    def __init__(self, config):
        self.config = config
        # Your initialization

    async def method1(self):
        # Adapted implementation
        pass
```

### Template 3: Extract Pattern (No Direct Code)

```python
# Sometimes you extract the pattern, not the code

# PATTERN: Dual-layer memory (from langmem)
# CONCEPT: Fast in-memory cache + persistent vector store

# YOUR IMPLEMENTATION:
class YourImplementation:
    """
    Pattern extracted from: langmem
    Implemented using: Redis (hot) + Pinecone (cold)
    """

    def __init__(self):
        self.hot_cache = redis.Redis()  # Your choice
        self.cold_store = pinecone.Index()  # Your choice

    # Implement the pattern with your tools
```

---

## Testing Extracted Code

### Test Template

```python
# tests/test_extracted_pattern.py
import pytest
from core.workflows.research import ExtractedPattern

class TestExtractedPattern:
    @pytest.fixture
    def pattern(self):
        return ExtractedPattern()

    @pytest.mark.asyncio
    async def test_basic_functionality(self, pattern):
        """Test that extracted pattern works"""
        result = await pattern.adapted_function("test input")
        assert result is not None

    @pytest.mark.asyncio
    async def test_edge_cases(self, pattern):
        """Test edge cases"""
        # Test empty input
        result = await pattern.adapted_function("")
        assert result == expected_empty_result

    @pytest.mark.asyncio
    async def test_integration(self, pattern):
        """Test integration with your system"""
        # Test that it works with your other components
        pass
```

---

## Integration Checklist

### Before Integration

- [ ] Understand the pattern completely
- [ ] Read the source code thoroughly
- [ ] Run the original examples
- [ ] Document what you're extracting
- [ ] Plan how it fits in your architecture

### During Integration

- [ ] Create new file for extracted code
- [ ] Adapt to your coding style
- [ ] Add type hints and documentation
- [ ] Handle errors appropriately
- [ ] Write tests as you go

### After Integration

- [ ] Run all tests
- [ ] Update documentation
- [ ] Document source and adaptations
- [ ] Review with team (if applicable)
- [ ] Commit with clear message

### Commit Message Template

```
feat: Add [pattern name] from [source]

Extracted [pattern] from [repo]/[file]

Changes:
- [What you extracted]
- [How you adapted it]
- [Why you made those choices]

Source: [link to original file]
Tests: [describe test coverage]
```

---

## Troubleshooting

### Pattern Doesn't Work in Your Codebase

**Problem:** Extracted code doesn't work as expected

**Solutions:**
1. Check dependencies - are you missing required libraries?
2. Review context - does it depend on other code you didn't extract?
3. Check configuration - does it need specific settings?
4. Simplify - can you extract a smaller piece first?

### Performance Issues

**Problem:** Extracted code is slower than expected

**Solutions:**
1. Profile the code - where is the bottleneck?
2. Check async/await usage - are you blocking?
3. Review database calls - are you making too many queries?
4. Consider the original use case - was it designed for your scale?

### Integration Conflicts

**Problem:** Extracted code conflicts with existing code

**Solutions:**
1. Use namespacing - put extracted code in its own module
2. Rename conflicting functions/classes
3. Consider an adapter pattern
4. Refactor gradually

---

## Next Steps

1. **Start with Phase 1** - Build research workflow foundation
2. **Extract incrementally** - One pattern at a time
3. **Test thoroughly** - Don't move on until it works
4. **Document everything** - Future you will thank you
5. **Iterate** - Improve extracted patterns over time

---

**Related:**
- [Repository Overview](./REPOSITORY-ANALYSIS-OVERVIEW.md)
- [Extraction Checklist](./EXTRACTION-CHECKLIST.md)
- [Detailed Analysis Files](./detailed-analysis/)
