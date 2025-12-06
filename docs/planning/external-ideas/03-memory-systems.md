# Memory Systems - 12 Advanced Memory Patterns

**Category:** Memory Systems
**Total Ideas:** 12
**Priority:** ⭐⭐⭐⭐⭐ CRITICAL (ideas #22-23), ⭐⭐⭐⭐ HIGH (ideas #24-33)
**Phase:** 2-3
**Total Effort:** 70-95 hours

---

## 📋 Overview

This document contains specifications for 12 memory system patterns extracted from langchain-reference repositories. These patterns enable persistent, scalable, and efficient memory management for AI agents.

**Source:** langchain-reference/05-memory-learning/

---

## 🎯 Memory Pattern Catalog

### Core Memory Architecture (Ideas #22-23)
1. [Dual-Layer Memory](#22-dual-layer-memory-) - Hot/cold storage pattern
2. [Context Engineering](#23-context-engineering-4-strategies-) - WRITE/SELECT/COMPRESS/ISOLATE

### User & Session Management (Ideas #24-28)
3. [User-Scoped Memory](#24-user-scoped-memory-) - Per-user isolation
4. [Memory Consolidation](#25-memory-consolidation-) - Pruning and optimization
5. [Semantic Search](#26-semantic-search-implementation-) - Vector similarity
6. [Memory Lifecycle](#27-memory-lifecycle-management-) - CRUD operations
7. [Cross-Session Persistence](#28-cross-session-persistence-) - State recovery

### Advanced Features (Ideas #29-33)
8. [Entity Tracking](#29-entity-tracking-) - Entity extraction and linking
9. [Fact Verification](#30-fact-verification-in-memory-) - Source attribution
10. [Memory Namespaces](#31-memory-namespaces-) - Topic isolation
11. [Memory Analytics](#32-memory-analytics-) - Usage statistics
12. [Memory Rollback](#33-memory-rollback-) - Versioning and undo

---

## 💾 Detailed Specifications

### 22. Dual-Layer Memory ⭐⭐⭐⭐⭐

**Priority:** CRITICAL
**Phase:** 2-3
**Effort:** Medium (10-15 hours)
**Source:** langchain-reference/05-memory-learning/langmem

#### What It Is

Two-tier memory architecture with hot (in-memory) and cold (persistent) storage layers for optimal performance and scalability.

#### Architecture

```python
class DualLayerMemory:
    """
    Hot Path: Fast in-memory access (LRU cache)
    Cold Path: Persistent vector storage (ChromaDB/Pinecone)
    """

    def __init__(self, hot_capacity: int = 100):
        # Hot layer - LRU cache
        self.hot_memory = LRUCache(max_size=hot_capacity)

        # Cold layer - Vector database
        self.cold_memory = VectorStore(
            collection_name="agent_memory",
            embedding_function=OpenAIEmbeddings(),
        )

        # Metadata tracking
        self.access_counts = {}
        self.last_access = {}

    async def remember(self, key: str, value: Any, metadata: dict = None):
        """Store in both layers"""

        # 1. Store in hot memory
        self.hot_memory.put(key, value)

        # 2. Store in cold memory with embeddings
        await self.cold_memory.add(
            id=key,
            content=value,
            metadata=metadata or {},
        )

        # 3. Track access
        self.access_counts[key] = 0
        self.last_access[key] = datetime.now()

    async def recall(self, query: str, k: int = 5) -> List[Memory]:
        """Retrieve memories"""

        # 1. Check hot memory first
        if query in self.hot_memory:
            self._track_access(query)
            return [self.hot_memory.get(query)]

        # 2. Query cold memory (semantic search)
        cold_results = await self.cold_memory.search(
            query=query,
            k=k,
        )

        # 3. Promote frequently accessed to hot
        for result in cold_results:
            if self._should_promote(result.id):
                self.hot_memory.put(result.id, result.content)

        return cold_results

    def _should_promote(self, key: str) -> bool:
        """Decide if cold memory should move to hot"""

        access_count = self.access_counts.get(key, 0)
        recency = (datetime.now() - self.last_access.get(key, datetime.min)).days

        # Promote if accessed 3+ times in last 7 days
        return access_count >= 3 and recency <= 7

    def _track_access(self, key: str):
        """Track memory access patterns"""

        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        self.last_access[key] = datetime.now()

    async def prune(self):
        """Clean up old/unused memories"""

        # Prune hot memory (automatic via LRU)
        # Hot memory self-prunes when capacity exceeded

        # Prune cold memory (manual cleanup)
        cutoff_date = datetime.now() - timedelta(days=90)

        old_memories = [
            key for key, access_time in self.last_access.items()
            if access_time < cutoff_date and self.access_counts.get(key, 0) < 2
        ]

        for key in old_memories:
            await self.cold_memory.delete(key)
            del self.access_counts[key]
            del self.last_access[key]
```

#### LRU Cache Implementation

```python
from collections import OrderedDict

class LRUCache:
    """Least Recently Used cache"""

    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key: str) -> Any:
        """Get and promote to most recent"""

        if key not in self.cache:
            return None

        # Move to end (most recent)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any):
        """Add or update, evict oldest if full"""

        if key in self.cache:
            # Update existing
            self.cache.move_to_end(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Evict oldest (first item)
                self.cache.popitem(last=False)

        self.cache[key] = value
```

#### Integration Example

```python
class ResearchAgent:
    """Agent with dual-layer memory"""

    def __init__(self):
        self.memory = DualLayerMemory(hot_capacity=50)

    async def research(self, company: str) -> dict:
        """Research with memory"""

        # 1. Check memory first
        cached_results = await self.memory.recall(
            query=f"research:{company}",
            k=3,
        )

        if cached_results and self._is_fresh(cached_results[0]):
            return cached_results[0].content

        # 2. Perform new research
        results = await self._do_research(company)

        # 3. Store in memory
        await self.memory.remember(
            key=f"research:{company}",
            value=results,
            metadata={
                "company": company,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
            },
        )

        return results

    def _is_fresh(self, memory: Memory) -> bool:
        """Check if memory is still fresh"""

        if not memory.metadata.get("timestamp"):
            return False

        timestamp = datetime.fromisoformat(memory.metadata["timestamp"])
        age_days = (datetime.now() - timestamp).days

        # Fresh if less than 7 days old
        return age_days < 7
```

#### Benefits

**Performance:**
- Hot memory: <1ms access time
- Cold memory: 10-50ms query time
- 100x faster than database-only

**Scalability:**
- Hot: 100-1000 items (MB scale)
- Cold: Millions of items (GB scale)
- Automatic promotion/demotion

**Cost Optimization:**
- Hot: Free (in-memory)
- Cold: ~$0.20/GB/month (Pinecone)
- 90%+ cost savings vs all-hot

#### Expected Impact

- **Speed:** 100x faster retrieval
- **Scale:** Unlimited storage
- **Cost:** 90% reduction
- **Hit Rate:** 80%+ (hot memory)

#### Dependencies

- Vector database (ChromaDB/Pinecone)
- Embedding model (OpenAI/local)
- LRU cache implementation

#### Next Steps

1. Implement LRU cache
2. Integrate vector database
3. Build promotion logic
4. Add pruning scheduler
5. Add to Phase 2 planning

---

### 23. Context Engineering (4 Strategies) ⭐⭐⭐⭐⭐

**Priority:** HIGH
**Phase:** 2-3
**Effort:** Medium (8-12 hours)
**Source:** langchain-reference/05-memory-learning/context_engineering

#### What It Is

Four complementary strategies to optimize context usage: WRITE, SELECT, COMPRESS, ISOLATE.

#### Strategy 1: WRITE - Format Optimization

**Goal:** Minimize tokens while maximizing information density.

```python
class ContextWriter:
    """Optimized context formatting"""

    @staticmethod
    def format_company_data(data: dict) -> str:
        """Compress company data to minimal tokens"""

        # Bad (verbose): 450 tokens
        verbose = f"""
        The company Tesla, Inc. is headquartered in Austin, Texas, USA.
        The company was founded in the year 2003 by Martin Eberhard and Marc Tarpenning.
        The current CEO is Elon Musk who joined in 2004.
        The company's main products include electric vehicles...
        """

        # Good (structured): 120 tokens
        structured = f"""
        Company: Tesla, Inc.
        HQ: Austin, TX, USA
        Founded: 2003 (Eberhard, Tarpenning)
        CEO: Elon Musk (since 2004)
        Products: EVs, batteries, solar
        Revenue: $96.7B (2023, +18.8% YoY)
        Employees: 127,855
        """

        # Best (abbreviated): 80 tokens
        abbreviated = {
            "name": "Tesla",
            "hq": "Austin,TX",
            "est": 2003,
            "ceo": "Musk",
            "rev": "$96.7B(+18.8%)",
            "emp": "127K",
        }

        return json.dumps(abbreviated, separators=(',', ':'))

    @staticmethod
    def format_table(data: List[dict]) -> str:
        """Markdown table format"""

        # Efficient table representation
        rows = [
            "Year|Rev|Growth",
            "-|-|-",
            *[f"{d['year']}|${d['rev']}B|{d['growth']}%" for d in data]
        ]

        return "\n".join(rows)
```

#### Strategy 2: SELECT - Relevance Filtering

**Goal:** Include only relevant information for current task.

```python
class ContextSelector:
    """Select most relevant context"""

    async def select_relevant_memories(
        self,
        query: str,
        all_memories: List[Memory],
        max_tokens: int = 2000,
    ) -> List[Memory]:
        """Select memories by relevance"""

        # 1. Score by relevance
        scored_memories = []
        for memory in all_memories:
            score = await self.calculate_relevance(query, memory)
            scored_memories.append((score, memory))

        # 2. Sort by score
        scored_memories.sort(reverse=True, key=lambda x: x[0])

        # 3. Select top memories within token budget
        selected = []
        total_tokens = 0

        for score, memory in scored_memories:
            memory_tokens = self.count_tokens(memory.content)

            if total_tokens + memory_tokens <= max_tokens:
                selected.append(memory)
                total_tokens += memory_tokens
            else:
                break

        return selected

    async def calculate_relevance(self, query: str, memory: Memory) -> float:
        """Multi-factor relevance scoring"""

        # Factor 1: Semantic similarity (60%)
        semantic_score = await self.semantic_similarity(query, memory.content)

        # Factor 2: Recency (20%)
        recency_score = self.recency_score(memory.metadata.get("timestamp"))

        # Factor 3: Access frequency (10%)
        frequency_score = memory.metadata.get("access_count", 0) / 100

        # Factor 4: Source quality (10%)
        quality_score = memory.metadata.get("quality", 0.5)

        # Weighted combination
        relevance = (
            semantic_score * 0.6 +
            recency_score * 0.2 +
            frequency_score * 0.1 +
            quality_score * 0.1
        )

        return relevance

    def recency_score(self, timestamp: str) -> float:
        """Score based on how recent memory is"""

        if not timestamp:
            return 0.0

        age_days = (datetime.now() - datetime.fromisoformat(timestamp)).days

        # Exponential decay: 1.0 (today) → 0.5 (30 days) → 0.1 (90 days)
        return math.exp(-age_days / 30)
```

#### Strategy 3: COMPRESS - Summarization

**Goal:** Reduce token count while preserving key information.

```python
class ContextCompressor:
    """Compress context via summarization"""

    async def compress_memories(
        self,
        memories: List[Memory],
        target_reduction: float = 0.5,
    ) -> str:
        """Compress memories to target ratio"""

        # 1. Combine all memory content
        combined = "\n\n".join([m.content for m in memories])
        original_tokens = self.count_tokens(combined)
        target_tokens = int(original_tokens * target_reduction)

        # 2. Extractive summarization (fast)
        key_sentences = self.extract_key_sentences(combined, target_tokens)

        # 3. If still too long, use LLM compression
        if self.count_tokens(key_sentences) > target_tokens:
            compressed = await self.llm_compress(key_sentences, target_tokens)
            return compressed

        return key_sentences

    def extract_key_sentences(self, text: str, target_tokens: int) -> str:
        """Extract most important sentences"""

        sentences = text.split(". ")

        # Score sentences by importance
        scored = []
        for sent in sentences:
            score = self.sentence_importance(sent)
            scored.append((score, sent))

        # Sort by score and select top sentences
        scored.sort(reverse=True, key=lambda x: x[0])

        selected = []
        total_tokens = 0

        for score, sent in scored:
            sent_tokens = self.count_tokens(sent)
            if total_tokens + sent_tokens <= target_tokens:
                selected.append(sent)
                total_tokens += sent_tokens

        return ". ".join(selected)

    def sentence_importance(self, sentence: str) -> float:
        """Score sentence importance"""

        score = 0.0

        # Numbers and metrics (high value)
        if re.search(r'\d+[%$MBK]', sentence):
            score += 2.0

        # Named entities (medium value)
        if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', sentence):
            score += 1.0

        # Keywords (variable value)
        keywords = ['revenue', 'profit', 'market', 'CEO', 'product', 'growth']
        for keyword in keywords:
            if keyword.lower() in sentence.lower():
                score += 0.5

        return score

    async def llm_compress(self, text: str, target_tokens: int) -> str:
        """Use LLM for intelligent compression"""

        prompt = f"""Compress this text to approximately {target_tokens} tokens
        while preserving all key facts, numbers, and insights:

        {text}

        Compressed version:"""

        compressed = await self.llm.invoke(prompt, max_tokens=target_tokens)
        return compressed.strip()
```

#### Strategy 4: ISOLATE - Context Separation

**Goal:** Separate different contexts to prevent interference.

```python
class ContextIsolation:
    """Isolate contexts by topic/project"""

    def __init__(self):
        self.contexts = {}  # namespace -> Context

    def create_namespace(self, namespace: str):
        """Create isolated context namespace"""

        if namespace not in self.contexts:
            self.contexts[namespace] = Context(
                namespace=namespace,
                memory=DualLayerMemory(),
                messages=[],
            )

    def add_to_context(self, namespace: str, message: dict):
        """Add message to specific context"""

        if namespace not in self.contexts:
            self.create_namespace(namespace)

        self.contexts[namespace].messages.append(message)

    def get_context(self, namespace: str) -> List[dict]:
        """Get isolated context"""

        if namespace not in self.contexts:
            return []

        return self.contexts[namespace].messages

    def switch_context(self, from_ns: str, to_ns: str):
        """Switch between contexts"""

        # Save current context state
        if from_ns in self.contexts:
            self.contexts[from_ns].save_state()

        # Load new context state
        if to_ns in self.contexts:
            self.contexts[to_ns].load_state()

    def merge_contexts(
        self,
        namespaces: List[str],
        target_ns: str,
    ):
        """Merge multiple contexts"""

        merged_messages = []

        for ns in namespaces:
            if ns in self.contexts:
                merged_messages.extend(self.contexts[ns].messages)

        # Sort by timestamp
        merged_messages.sort(key=lambda m: m.get("timestamp", 0))

        # Store in target namespace
        self.create_namespace(target_ns)
        self.contexts[target_ns].messages = merged_messages
```

#### Combined Usage Example

```python
class ContextManager:
    """Combines all 4 strategies"""

    def __init__(self):
        self.writer = ContextWriter()
        self.selector = ContextSelector()
        self.compressor = ContextCompressor()
        self.isolation = ContextIsolation()

    async def prepare_context(
        self,
        query: str,
        namespace: str,
        max_tokens: int = 3000,
    ) -> str:
        """Prepare optimized context"""

        # 1. ISOLATE: Get namespace-specific context
        raw_memories = self.isolation.get_context(namespace)

        # 2. SELECT: Filter by relevance
        relevant = await self.selector.select_relevant_memories(
            query=query,
            all_memories=raw_memories,
            max_tokens=max_tokens * 1.5,  # Allow 50% buffer for compression
        )

        # 3. COMPRESS: Reduce token count
        compressed = await self.compressor.compress_memories(
            memories=relevant,
            target_reduction=0.7,  # 30% of original
        )

        # 4. WRITE: Format for optimal token usage
        formatted = self.writer.format_company_data(compressed)

        return formatted
```

#### Expected Impact

**Token Reduction:**
- WRITE: 40-60% reduction
- SELECT: 50-70% reduction
- COMPRESS: 50-80% reduction
- Combined: 70-90% reduction

**Quality Preservation:**
- Key facts: 100% preserved
- Supporting details: 80%+ preserved
- Nuance: 60%+ preserved

**Cost Savings:**
- API costs: 70-90% reduction
- Latency: 40-60% improvement
- Context fit: 10x more information

#### Dependencies

- Embedding model
- Token counter
- LLM access (for compression)

#### Next Steps

1. Implement all 4 strategies
2. Build context manager
3. Test token reduction
4. Measure quality preservation
5. Add to Phase 2-3 planning

---

### 24-33. Additional Memory Features

Due to space constraints, here are concise specifications for the remaining 10 memory features:

---

### 24. User-Scoped Memory ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6-10 hours

Per-user isolated memory storage with cross-session persistence.

```
users/
  ├── user_123/
  │   ├── conversations.json
  │   ├── entities.json
  │   └── facts.json
```

---

### 25. Memory Consolidation ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8-10 hours

Periodic pruning, deduplication, and consolidation.

**Strategies:** Time-based, relevance-based, summarization, deduplication, quality-based

---

### 26. Semantic Search Implementation ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6-8 hours

Vector similarity search with hybrid (semantic + keyword) approach.

---

### 27. Memory Lifecycle Management ⭐⭐⭐

**Phase:** 3 | **Effort:** 4-6 hours

CRUD operations, expiration policies, archive strategies.

---

### 28. Cross-Session Persistence ⭐⭐⭐

**Phase:** 3 | **Effort:** 4-6 hours

Session management, state recovery, resume capability.

---

### 29. Entity Tracking ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6-8 hours

Entity extraction, entity linking, relationship mapping.

```python
{
    "entities": {
        "Tesla": {"type": "Company", "mentions": 45},
        "Elon Musk": {"type": "Person", "role": "CEO"},
    },
    "relationships": [
        ("Elon Musk", "CEO_OF", "Tesla"),
    ]
}
```

---

### 30. Fact Verification in Memory ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8-10 hours

Fact extraction, source attribution, verification status.

---

### 31. Memory Namespaces ⭐⭐⭐

**Phase:** 3 | **Effort:** 3-4 hours

Topic isolation, project separation, multi-tenant support.

---

### 32. Memory Analytics ⭐⭐⭐

**Phase:** 3 | **Effort:** 4-6 hours

Usage statistics, popular queries, memory growth tracking.

---

### 33. Memory Rollback ⭐⭐⭐

**Phase:** 3 | **Effort:** 3-4 hours

Versioning, undo capability, checkpoint/restore.

---

## 📊 Summary Statistics

### Total Ideas: 12
### Total Effort: 70-95 hours

### By Priority:
- ⭐⭐⭐⭐⭐ Critical: 2 ideas (Dual-Layer, Context Engineering)
- ⭐⭐⭐⭐ High: 7 ideas (User-Scoped through Fact Verification)
- ⭐⭐⭐ Medium: 3 ideas (Lifecycle, Namespaces, Rollback)

### By Phase:
- Phase 2: 2 ideas (22-23)
- Phase 3: 10 ideas (24-33)

### Implementation Order:
1. **Week 5:** Dual-Layer Memory (#22)
2. **Week 6:** Context Engineering (#23)
3. **Week 7:** User-Scoped (#24), Semantic Search (#26)
4. **Week 8:** Consolidation (#25), Entity Tracking (#29)
5. **Week 9:** Remaining features (#27-28, #30-33)

---

## 🎯 Integration Roadmap

### Phase 2 - Weeks 5-6 (Foundation)
1. Implement Dual-Layer Memory
2. Implement Context Engineering (all 4 strategies)
3. Test with research workflows

### Phase 3 - Weeks 7-8 (Enhancement)
1. Add User-Scoped Memory
2. Implement Semantic Search
3. Add Memory Consolidation
4. Add Entity Tracking

### Phase 3 - Week 9 (Advanced)
1. Complete remaining features
2. Integration testing
3. Performance optimization

---

## 🔗 Related Documents

- [01-architecture-patterns.md](01-architecture-patterns.md) - System architecture
- [02-agent-specialization.md](02-agent-specialization.md) - Agent implementations
- [07-context-optimization.md](07-context-optimization.md) - Additional context patterns
- [README.md](README.md) - Navigation hub

---

**Status:** ✅ Complete
**Total Features:** 12
**Ready for:** Phase 2-3 implementation
