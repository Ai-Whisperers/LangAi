# LangChain Reference - Detailed Analysis

**Repository:** langchain-reference/
**Total Repos:** 60+
**Last Updated:** 2025-12-05
**Priority:** 🔥 HIGHEST

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Priority Repositories](#priority-repositories)
4. [Extractable Patterns](#extractable-patterns)
5. [Code Examples](#code-examples)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

The langchain-reference directory contains 60+ carefully organized LangChain repositories covering every aspect of building production-ready AI agents. This is your PRIMARY resource for:

- Research agent architectures
- Memory management systems
- Context optimization
- Multi-agent coordination
- Production deployment patterns
- Tool integration (MCP)
- RAG implementations

---

## Repository Structure

```
langchain-reference/
├── 01-research-agents/          # 9 repos - Company, market, competitor research
├── 02-deep-agents/              # 4 repos - Advanced agent frameworks
├── 03-multi-agent-patterns/     # 2 repos - Supervisor & swarm patterns
├── 04-production-apps/          # 6 repos - Production-ready applications
├── 05-memory-learning/          # 5 repos - Memory systems & learning
├── 06-mcp-integration/          # 4 repos - Model Context Protocol
├── 07-evaluation-testing/       # 3 repos - Evaluation & testing tools
├── 08-templates-starters/       # 3 repos - Project templates
├── 09-tools-utilities/          # 9 repos - Tools & code generation
├── 10-docs-tutorials/           # 5 repos - Documentation & tutorials
├── 11-langsmith/                # 3 repos - LangSmith SDKs & tools
└── 12-llama-meta/               # 2 repos - Meta LLaMA integrations
```

---

## Priority Repositories

### 🔥 MUST STUDY (Top 5)

#### 1. **open_deep_research** ⭐⭐⭐⭐⭐
**Path:** `04-production-apps/open_deep_research`
**Stars:** 9.8k
**Priority:** START HERE

**What It Is:**
- Most comprehensive production research agent
- Multi-model orchestration (GPT-4, Claude, etc.)
- MCP support for tool integration
- Benchmarked #6 on research quality leaderboard

**What You Can Learn:**
- Production agent architecture patterns
- Multi-model routing and orchestration
- Report generation (Markdown, JSON)
- Quality benchmarking techniques
- Error handling for long-running tasks

**What You Can Extract:**
```python
# Architecture patterns
- State machine design for research phases
- Multi-model selection logic
- Report generation templates
- Quality scoring mechanisms
- Error recovery strategies

# Key Files to Study:
graph.py           # State machine implementation
models.py          # Multi-model orchestration
report_gen.py      # Report generation
quality_check.py   # Quality scoring
```

**Code Snippet to Extract:**
```python
# Multi-model orchestration pattern
class ModelRouter:
    def select_model(self, task_type, complexity):
        if task_type == "reasoning" and complexity == "high":
            return "claude-3-opus"
        elif task_type == "search":
            return "gpt-4-turbo"
        # ... routing logic
```

**Use This For:**
- Building your research-workflow-system architecture
- Implementing multi-model orchestration
- Creating benchmarked quality systems

---

#### 2. **company-researcher** ⭐⭐⭐⭐⭐
**Path:** `01-research-agents/company-researcher`
**Stars:** 211
**Priority:** STUDY SECOND

**What It Is:**
- Clean 3-phase research workflow
- Search → Extract → Reflect pattern
- Easy to understand and adapt
- Production-ready JSON schema extraction

**What You Can Learn:**
- How to structure multi-phase workflows
- Clean state transitions
- JSON schema extraction from unstructured data
- Quality reflection mechanisms

**What You Can Extract:**
```python
# 3-Phase Workflow Pattern
Phase 1: Search
  - Tavily search integration
  - Query optimization
  - Source collection

Phase 2: Extract
  - JSON schema definition
  - Structured extraction from sources
  - Data validation

Phase 3: Reflect
  - Quality assessment
  - Gap identification
  - Iterative improvement

# Key Files:
workflow.py        # 3-phase state machine
extractors.py      # JSON extraction logic
schemas.py         # Pydantic schemas
quality.py         # Reflection & scoring
```

**Code Snippet to Extract:**
```python
# 3-phase workflow state machine
class ResearchWorkflow:
    def __init__(self):
        self.phases = ["search", "extract", "reflect"]

    async def search_phase(self, query):
        sources = await self.search_engine.search(query)
        return self.validate_sources(sources)

    async def extract_phase(self, sources):
        data = await self.extractor.extract(sources, schema)
        return self.validate_extraction(data)

    async def reflect_phase(self, data):
        quality_score = await self.reflector.assess(data)
        if quality_score < threshold:
            return self.search_phase(improved_query)
        return data
```

**Use This For:**
- Your research agent core workflow
- JSON extraction patterns
- Iterative quality improvement

---

#### 3. **langmem** ⭐⭐⭐⭐⭐
**Path:** `05-memory-learning/langmem`
**Stars:** 1.2k
**Priority:** CRITICAL FOR MEMORY

**What It Is:**
- Production memory management system
- Hot path (in-memory) + persistent storage
- Semantic search capabilities
- Cross-session memory

**What You Can Learn:**
- Memory architecture patterns
- Hot vs cold storage strategies
- Semantic search implementation
- Memory retrieval optimization

**What You Can Extract:**
```python
# Memory System Architecture
Components:
├── Hot Path Memory (in-memory cache)
├── Persistent Storage (vector DB)
├── Semantic Search (embeddings)
├── Memory Consolidation (pruning)
└── Retrieval Strategies (relevance scoring)

# Key Files:
memory_manager.py   # Core memory orchestration
hot_path.py         # In-memory cache
persistent.py       # Vector DB integration
semantic_search.py  # Embedding + search
consolidation.py    # Memory pruning
```

**Code Snippet to Extract:**
```python
# Dual-layer memory architecture
class MemoryManager:
    def __init__(self):
        self.hot_memory = InMemoryCache(max_size=100)
        self.cold_memory = VectorStore(collection="memories")

    async def store(self, memory_item):
        # Always store in hot path
        self.hot_memory.add(memory_item)

        # Async persist to cold storage
        await self.cold_memory.add(
            text=memory_item.text,
            embedding=await self.embed(memory_item.text),
            metadata=memory_item.metadata
        )

    async def retrieve(self, query, k=5):
        # Check hot path first
        hot_results = self.hot_memory.search(query)
        if len(hot_results) >= k:
            return hot_results[:k]

        # Supplement with cold storage
        cold_results = await self.cold_memory.semantic_search(
            query, k=k-len(hot_results)
        )
        return hot_results + cold_results
```

**Use This For:**
- Cross-topic memory in research system
- User-scoped persistent storage
- Semantic memory search

---

#### 4. **context_engineering** ⭐⭐⭐⭐
**Path:** `05-memory-learning/context_engineering`
**Stars:** 133
**Priority:** OPTIMIZATION

**What It Is:**
- Token optimization techniques
- 4 core strategies: Write, Select, Compress, Isolate
- Context window management
- Prompt compression patterns

**What You Can Learn:**
- How to manage large context windows
- Token reduction techniques
- Selective information retrieval
- Context isolation strategies

**What You Can Extract:**
```python
# 4 Context Engineering Strategies

1. WRITE - Optimize how you write context
   - Structured formats (JSON, tables)
   - Abbreviated notation
   - Remove redundancy

2. SELECT - Choose what to include
   - Relevance scoring
   - Recency weighting
   - Importance ranking

3. COMPRESS - Reduce token count
   - Summarization
   - Entity extraction
   - Key point extraction

4. ISOLATE - Separate contexts
   - Multi-turn conversations
   - Context switching
   - Namespace isolation

# Key Files:
write_optimizer.py   # Structured formatting
selector.py          # Relevance scoring
compressor.py        # Summarization
isolator.py          # Context separation
```

**Code Snippet to Extract:**
```python
# Context optimizer with 4 strategies
class ContextEngineer:
    def optimize_context(self, raw_context, max_tokens=4000):
        # 1. WRITE: Structure the context
        structured = self.structure(raw_context)

        # 2. SELECT: Choose relevant parts
        selected = self.select_relevant(
            structured,
            query=self.current_query,
            top_k=10
        )

        # 3. COMPRESS: Reduce token count
        if self.count_tokens(selected) > max_tokens:
            compressed = self.compress(selected, max_tokens)
        else:
            compressed = selected

        # 4. ISOLATE: Separate by namespace
        isolated = self.isolate_contexts(compressed)

        return isolated

    def compress(self, content, max_tokens):
        # Extractive summarization
        sentences = self.split_sentences(content)
        scored = [(s, self.score_importance(s)) for s in sentences]
        sorted_sentences = sorted(scored, key=lambda x: x[1], reverse=True)

        result = []
        token_count = 0
        for sent, score in sorted_sentences:
            sent_tokens = self.count_tokens(sent)
            if token_count + sent_tokens <= max_tokens:
                result.append(sent)
                token_count += sent_tokens

        return " ".join(result)
```

**Use This For:**
- Managing context in long research sessions
- Token cost optimization
- Selective memory retrieval

---

#### 5. **memory-agent** ⭐⭐⭐⭐
**Path:** `05-memory-learning/memory-agent`
**Stars:** 383
**Priority:** PERSISTENCE

**What It Is:**
- User-scoped persistent memory
- Cross-session storage
- Store-based architecture
- Memory retrieval patterns

**What You Can Learn:**
- User-scoped memory isolation
- Persistent storage patterns
- Memory lifecycle management
- Query-based retrieval

**What You Can Extract:**
```python
# User-Scoped Memory Architecture

Storage Pattern:
users/
  ├── user_123/
  │   ├── conversations/
  │   ├── entities/
  │   └── facts/
  └── user_456/
      ├── conversations/
      ├── entities/
      └── facts/

# Key Files:
user_memory.py      # User-scoped storage
store.py            # Persistence layer
retrieval.py        # Query patterns
lifecycle.py        # Memory management
```

**Code Snippet to Extract:**
```python
# User-scoped memory with persistence
class UserMemoryAgent:
    def __init__(self, user_id, storage_path):
        self.user_id = user_id
        self.storage = PersistentStore(f"{storage_path}/{user_id}")
        self.conversations = []
        self.entities = {}
        self.facts = []

    async def remember(self, content, content_type="conversation"):
        memory_item = {
            "content": content,
            "type": content_type,
            "timestamp": datetime.now(),
            "user_id": self.user_id
        }

        # Store in appropriate collection
        if content_type == "conversation":
            self.conversations.append(memory_item)
        elif content_type == "entity":
            self.entities[content["name"]] = memory_item
        elif content_type == "fact":
            self.facts.append(memory_item)

        # Persist to storage
        await self.storage.save(content_type, memory_item)

    async def recall(self, query, content_type=None, limit=10):
        # Query-based retrieval
        if content_type:
            collection = getattr(self, f"{content_type}s")
        else:
            # Search across all types
            collection = (
                self.conversations +
                list(self.entities.values()) +
                self.facts
            )

        # Semantic search
        results = await self.semantic_search(query, collection, limit)
        return results
```

**Use This For:**
- User-specific memory in research system
- Persistent cross-session storage
- Entity and fact tracking

---

### ⚡ VERY USEFUL (Next 10)

#### 6. **data-enrichment**
**Path:** `04-production-apps/data-enrichment`
**Stars:** 209

**Extract:**
- Web research patterns
- Data extraction workflows
- Source validation

#### 7. **langgraph-supervisor-py**
**Path:** `03-multi-agent-patterns/langgraph-supervisor-py`
**Stars:** 1.4k

**Extract:**
- Supervisor coordination pattern
- Agent delegation logic
- Task routing

```python
# Supervisor pattern
class SupervisorAgent:
    def __init__(self, workers):
        self.workers = workers

    async def delegate(self, task):
        # Analyze task
        task_type = await self.analyze_task(task)

        # Select appropriate worker
        worker = self.select_worker(task_type)

        # Delegate and monitor
        result = await worker.execute(task)

        # Validate result
        if not self.validate(result):
            # Re-delegate or escalate
            return await self.handle_failure(task, result)

        return result
```

#### 8. **langgraph-swarm-py**
**Path:** `03-multi-agent-patterns/langgraph-swarm-py`
**Stars:** 1.3k

**Extract:**
- Swarm collaboration pattern
- Peer-to-peer agent communication
- Consensus mechanisms

```python
# Swarm pattern
class SwarmAgent:
    def __init__(self, agent_id, peers):
        self.agent_id = agent_id
        self.peers = peers

    async def collaborate(self, task):
        # Share task with peers
        peer_responses = await asyncio.gather(*[
            peer.process(task) for peer in self.peers
        ])

        # Aggregate responses
        consensus = self.reach_consensus(peer_responses)

        return consensus
```

#### 9. **openevals**
**Path:** `07-evaluation-testing/openevals`
**Stars:** 822

**Extract:**
- LLM evaluation functions
- Quality scoring rubrics
- Automated evaluation patterns

```python
# Evaluation pattern
class ResearchEvaluator:
    def evaluate(self, output, expected):
        scores = {
            "accuracy": self.score_accuracy(output, expected),
            "completeness": self.score_completeness(output, expected),
            "relevance": self.score_relevance(output, expected),
            "coherence": self.score_coherence(output)
        }
        return scores
```

#### 10. **web-explorer**
**Path:** `01-research-agents/web-explorer`
**Stars:** 387

**Extract:**
- Interactive web research
- URL scraping patterns
- Content extraction

#### 11. **multi-modal-researcher**
**Path:** `01-research-agents/multi-modal-researcher`
**Stars:** 582

**Extract:**
- Text + image research
- Multi-modal processing
- Visual data extraction

#### 12. **rag-research-agent-template**
**Path:** `01-research-agents/rag-research-agent-template`
**Stars:** 278

**Extract:**
- RAG implementation pattern
- Document retrieval
- Context injection

#### 13. **langchain-extract**
**Path:** `09-tools-utilities/langchain-extract`
**Stars:** 1.2k

**Extract:**
- Structured data extraction
- Schema-based extraction
- Validation patterns

#### 14. **deepagents**
**Path:** `02-deep-agents/deepagents`
**Stars:** 6.8k

**Extract:**
- Planning mechanisms
- Subagent hierarchies
- Filesystem backend patterns

#### 15. **langchain-mcp-adapters**
**Path:** `06-mcp-integration/langchain-mcp-adapters`
**Stars:** 3.2k

**Extract:**
- MCP tool integration
- Tool adapter patterns
- External tool orchestration

---

## Extractable Patterns

### 1. Research Workflow Patterns

```python
# Pattern: Multi-phase research workflow
class ResearchWorkflow:
    phases = ["search", "extract", "analyze", "synthesize", "reflect"]

    async def execute(self, query):
        state = {"query": query, "sources": [], "data": {}}

        for phase in self.phases:
            state = await self.execute_phase(phase, state)

            # Quality check after each phase
            if not self.validate_phase(phase, state):
                state = await self.retry_phase(phase, state)

        return state["result"]
```

### 2. Memory Management Patterns

```python
# Pattern: Dual-layer memory with semantic search
class MemorySystem:
    def __init__(self):
        self.hot_memory = InMemoryCache()  # Fast access
        self.cold_memory = VectorStore()   # Persistent

    async def store_memory(self, item):
        # Hot path
        self.hot_memory.add(item)

        # Cold storage (async)
        await self.cold_memory.add_with_embedding(item)

    async def retrieve_relevant(self, query, k=5):
        # Check hot memory first
        hot_results = self.hot_memory.search(query)

        # Supplement with semantic search
        if len(hot_results) < k:
            cold_results = await self.cold_memory.semantic_search(
                query, k - len(hot_results)
            )
            return hot_results + cold_results

        return hot_results[:k]
```

### 3. Multi-Agent Coordination Patterns

```python
# Pattern: Supervisor + Worker
class SupervisorWorkerSystem:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.workers = {
            "researcher": ResearchWorker(),
            "analyst": AnalystWorker(),
            "writer": WriterWorker()
        }

    async def process_task(self, task):
        # Supervisor analyzes and delegates
        plan = await self.supervisor.create_plan(task)

        results = []
        for step in plan:
            worker = self.workers[step.worker_type]
            result = await worker.execute(step)
            results.append(result)

        # Supervisor synthesizes
        final_result = await self.supervisor.synthesize(results)
        return final_result
```

```python
# Pattern: Swarm collaboration
class SwarmSystem:
    def __init__(self, agents):
        self.agents = agents

    async def collaborative_solve(self, problem):
        # All agents work on problem
        solutions = await asyncio.gather(*[
            agent.solve(problem) for agent in self.agents
        ])

        # Vote or consensus
        best_solution = self.reach_consensus(solutions)
        return best_solution
```

### 4. Context Optimization Patterns

```python
# Pattern: Selective context with compression
class ContextOptimizer:
    def optimize(self, full_context, query, max_tokens):
        # 1. Select relevant sections
        relevant = self.select_relevant_sections(
            full_context, query, threshold=0.7
        )

        # 2. Rank by importance
        ranked = self.rank_by_importance(relevant, query)

        # 3. Compress if needed
        if self.count_tokens(ranked) > max_tokens:
            compressed = self.compress_content(ranked, max_tokens)
        else:
            compressed = ranked

        return compressed

    def compress_content(self, content, max_tokens):
        # Extractive summarization
        # Keep most important sentences until token limit
        pass
```

### 5. Quality Assessment Patterns

```python
# Pattern: Multi-criteria quality scoring
class QualityAssessor:
    criteria = ["accuracy", "completeness", "relevance", "coherence"]

    async def assess(self, output, expected=None):
        scores = {}

        for criterion in self.criteria:
            scores[criterion] = await self.score_criterion(
                output, criterion, expected
            )

        # Weighted average
        weights = {"accuracy": 0.3, "completeness": 0.3,
                   "relevance": 0.25, "coherence": 0.15}

        overall = sum(scores[c] * weights[c] for c in self.criteria)

        return {
            "overall": overall,
            "breakdown": scores,
            "pass": overall >= 0.7
        }
```

---

## Code Examples

### Example 1: Complete Research Agent

```python
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

# Define state
class ResearchState(TypedDict):
    query: str
    sources: List[str]
    extracted_data: Dict
    analysis: str
    report: str
    quality_score: float

# Create workflow
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("search", search_node)
workflow.add_node("extract", extract_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("reflect", reflect_node)
workflow.add_node("write_report", write_report_node)

# Add edges
workflow.add_edge("search", "extract")
workflow.add_edge("extract", "analyze")
workflow.add_edge("analyze", "reflect")

# Conditional edge for quality
def should_retry(state):
    return "search" if state["quality_score"] < 0.7 else "write_report"

workflow.add_conditional_edges(
    "reflect",
    should_retry,
    {"search": "search", "write_report": "write_report"}
)

workflow.add_edge("write_report", END)

# Set entry point
workflow.set_entry_point("search")

# Compile
app = workflow.compile()

# Run
result = await app.ainvoke({"query": "Research AI agents"})
```

### Example 2: Memory-Enabled Agent

```python
from langchain.memory import ConversationBufferMemory
from langchain.memory.vectorstore import VectorStoreRetrieverMemory

class MemoryEnabledAgent:
    def __init__(self, user_id):
        # Hot memory
        self.short_term = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

        # Cold memory
        self.long_term = VectorStoreRetrieverMemory(
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            memory_key="long_term_context"
        )

    async def process(self, user_input):
        # Retrieve relevant long-term memories
        long_term_context = self.long_term.load_memory_variables(
            {"input": user_input}
        )

        # Get short-term conversation history
        short_term_context = self.short_term.load_memory_variables({})

        # Combine contexts
        full_context = {
            **short_term_context,
            **long_term_context
        }

        # Process with LLM
        response = await self.llm.ainvoke(full_context)

        # Save to both memories
        self.short_term.save_context(
            {"input": user_input},
            {"output": response}
        )
        self.long_term.save_context(
            {"input": user_input},
            {"output": response}
        )

        return response
```

### Example 3: Multi-Agent Supervisor

```python
from langgraph.graph import StateGraph
from langchain.agents import AgentExecutor

class SupervisorSystem:
    def __init__(self):
        self.workers = {
            "researcher": self.create_researcher(),
            "analyst": self.create_analyst(),
            "writer": self.create_writer()
        }

        self.supervisor = self.create_supervisor()

    def create_graph(self):
        workflow = StateGraph(TeamState)

        # Add supervisor node
        workflow.add_node("supervisor", self.supervisor_node)

        # Add worker nodes
        for name, agent in self.workers.items():
            workflow.add_node(name, agent)

        # Conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.should_continue,
            {name: name for name in self.workers.keys()} | {"END": END}
        )

        # Workers report back to supervisor
        for name in self.workers.keys():
            workflow.add_edge(name, "supervisor")

        workflow.set_entry_point("supervisor")

        return workflow.compile()

    async def supervisor_node(self, state):
        # Supervisor decides next action
        response = await self.supervisor.ainvoke(state)
        return {"next_worker": response.next_worker, "task": response.task}

    def should_continue(self, state):
        if state["next_worker"] == "FINISH":
            return "END"
        return state["next_worker"]
```

---

## Implementation Roadmap

### Week 1-2: Foundation
```
Day 1-3: Study open_deep_research
  - Read README
  - Run examples
  - Study graph.py architecture
  - Extract state machine pattern

Day 4-7: Study company-researcher
  - Understand 3-phase workflow
  - Extract JSON schema patterns
  - Study quality reflection
  - Build prototype 3-phase workflow

Week 2: Build Your First Agent
  - Implement basic research workflow
  - Add search capability (Tavily)
  - Add extraction (JSON schema)
  - Add reflection/quality check
```

### Week 3-4: Memory System
```
Day 1-5: Study langmem + memory-agent
  - Understand hot/cold storage
  - Study semantic search
  - Extract dual-layer pattern
  - Study user-scoped storage

Day 6-10: Implement Memory
  - Build hot path (in-memory cache)
  - Add cold storage (vector DB)
  - Implement semantic search
  - Add user-scoped isolation

Day 11-14: Study context_engineering
  - Learn 4 optimization strategies
  - Extract compression patterns
  - Implement context optimization
```

### Week 5-6: Multi-Agent Patterns
```
Day 1-7: Study supervisor pattern
  - langgraph-supervisor-py
  - Extract delegation logic
  - Build supervisor prototype

Day 8-14: Study swarm pattern
  - langgraph-swarm-py
  - Extract collaboration logic
  - Build swarm prototype
```

### Week 7-8: Production & Tools
```
Day 1-5: Tools & Integration
  - langchain-mcp-adapters
  - langchain-extract
  - Tool adapter patterns

Day 6-10: Evaluation
  - openevals
  - Quality scoring
  - Automated evaluation

Day 11-14: Polish & Deploy
  - Error handling
  - Monitoring
  - Documentation
```

---

## Quick Commands

```bash
# Navigate to priority repos
cd langchain-reference/04-production-apps/open_deep_research
cd langchain-reference/01-research-agents/company-researcher
cd langchain-reference/05-memory-learning/langmem
cd langchain-reference/05-memory-learning/context_engineering

# Search for specific patterns
grep -r "StateGraph" --include="*.py"
grep -r "memory" --include="*.py"
grep -r "quality" --include="*.py"

# Find all graph implementations
find . -name "*graph*.py"

# Find all memory implementations
find . -name "*memory*.py"
```

---

## Next Steps

1. **Start Immediately:**
   - Clone open_deep_research
   - Read the README
   - Run the examples
   - Study the architecture

2. **This Week:**
   - Extract 3-phase workflow from company-researcher
   - Build prototype research agent
   - Test with sample queries

3. **Next Week:**
   - Implement memory system from langmem
   - Add semantic search
   - Integrate with research agent

4. **Continuous:**
   - Study one repo per week
   - Extract and adapt patterns
   - Build incrementally

---

**Related Documentation:**
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [agentops Analysis](./agentops.md)
- [Extraction Guide](../EXTRACTION-GUIDE.md)
