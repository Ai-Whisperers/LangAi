# Architecture Decision Records (ADR)

This document records significant architectural and technical decisions made during the development of the Company Researcher System.

---

## ADR Format

Each decision follows this structure:
- **Date:** When the decision was made
- **Context:** Problem or question we're addressing
- **Decision:** What we decided to do
- **Rationale:** Why we made this choice
- **Alternatives Considered:** Other options we evaluated
- **Consequences:** Trade-offs and implications

---

## Table of Contents

1. [ADR-001: LangGraph for Orchestration](#adr-001-langgraph-for-orchestration)
2. [ADR-002: Claude 3.5 Sonnet as Primary LLM](#adr-002-claude-35-sonnet-as-primary-llm)
3. [ADR-003: Supervisor Pattern for Agent Coordination](#adr-003-supervisor-pattern-for-agent-coordination)
4. [ADR-004: PostgreSQL + Qdrant for Persistence](#adr-004-postgresql--qdrant-for-persistence)
5. [ADR-005: FastAPI for API Layer](#adr-005-fastapi-for-api-layer)
6. [ADR-006: Tavily for Web Search](#adr-006-tavily-for-web-search)

---

## ADR-001: LangGraph for Orchestration

**Date:** 2025-12-05

**Context:**
We need a framework to orchestrate complex multi-agent workflows with state management, error handling, and observability.

**Decision:**
Use LangGraph (LangChain's graph-based orchestration framework).

**Rationale:**
- **State Management:** Built-in StateGraph with type-safe state handling
- **Control Flow:** Explicit graph-based workflow definition (nodes, edges, conditional routing)
- **Observability:** Native integration with LangSmith for debugging
- **Streaming:** Built-in support for streaming responses
- **Checkpointing:** Built-in state persistence for resumability
- **Active Development:** Strong community and regular updates

**Alternatives Considered:**

1. **Custom Orchestration**
   - ❌ More control but high maintenance burden
   - ❌ Would need to build state management, checkpointing, observability

2. **CrewAI**
   - ✅ Simpler for basic multi-agent tasks
   - ❌ Less flexible for complex routing
   - ❌ Weaker state management

3. **AutoGen**
   - ✅ Good for conversational agents
   - ❌ Less suited for structured research workflows
   - ❌ Harder to control agent behavior

**Consequences:**
- ✅ Reduced development time for orchestration logic
- ✅ Built-in debugging and monitoring
- ⚠️ Learning curve for LangGraph concepts
- ⚠️ Dependency on LangChain ecosystem

---

## ADR-002: Claude 3.5 Sonnet as Primary LLM

**Date:** 2025-12-05

**Context:**
We need to select a primary LLM for research tasks, analysis, and synthesis.

**Decision:**
Use Claude 3.5 Sonnet (Anthropic) as the primary model for all agents.

**Rationale:**
- **Context Window:** 200K tokens - handle large research documents
- **Quality:** Superior reasoning and analysis capabilities
- **Cost:** $3/MTok input, $15/MTok output - reasonable for quality
- **Tool Use:** Excellent function calling and structured output
- **Long-Form Writing:** Strong at synthesis and report generation
- **Rate Limits:** 50 requests/min - sufficient for parallel agents

**Alternatives Considered:**

1. **GPT-4 Turbo**
   - ✅ Comparable quality
   - ❌ 128K context (vs 200K)
   - ❌ Higher cost ($10/MTok input, $30/MTok output)

2. **GPT-3.5 Turbo**
   - ✅ Much cheaper ($0.50/$1.50 per MTok)
   - ❌ Lower quality reasoning
   - ❌ 16K context window

3. **Open Source (Llama 3, Mixtral)**
   - ✅ No per-token cost
   - ❌ Requires hosting infrastructure
   - ❌ Lower quality for complex reasoning

**Consequences:**
- ✅ High-quality research output
- ✅ Large context for document analysis
- ⚠️ Cost ~$0.30-$0.50 per company research
- ⚠️ Anthropic API dependency

---

## ADR-003: Supervisor Pattern for Agent Coordination

**Date:** 2025-12-05

**Context:**
We need to coordinate 14 specialized agents for company research. Two main patterns: Supervisor (centralized) vs Swarm (decentralized).

**Decision:**
Use the Supervisor pattern with a central coordinator agent.

**Rationale:**
- **Strategic Control:** Central oversight for research quality
- **Resource Management:** Efficient allocation of expensive API calls
- **Context Management:** Supervisor maintains overall research context
- **Error Handling:** Centralized retry and fallback logic
- **Cost Control:** Better tracking and limits per research request

**Alternatives Considered:**

1. **Swarm Pattern**
   - ✅ More autonomous and parallel
   - ❌ Harder to control costs (agents call each other freely)
   - ❌ Risk of redundant work
   - ❌ Harder to ensure report coherence

2. **Sequential Pipeline**
   - ✅ Simple and predictable
   - ❌ No parallelization opportunities
   - ❌ Slower execution

**Consequences:**
- ✅ Better cost control
- ✅ Higher quality coordination
- ⚠️ Single point of failure (supervisor)
- ⚠️ Supervisor complexity increases over time

---

## ADR-004: PostgreSQL + Qdrant for Persistence

**Date:** 2025-12-05

**Context:**
We need storage for:
- Research results and metadata (structured data)
- Memory and past research (vector search)
- Session state (checkpointing)

**Decision:**
- **PostgreSQL:** Structured data, metadata, state checkpointing
- **Qdrant:** Vector embeddings for semantic memory search

**Rationale:**

**PostgreSQL:**
- ✅ Robust relational database for structured data
- ✅ Native LangGraph checkpointing support
- ✅ JSONB for flexible schemas
- ✅ Well-understood and widely deployed

**Qdrant:**
- ✅ Purpose-built for vector search
- ✅ Fast semantic similarity search
- ✅ Open source and self-hostable
- ✅ Good Python client

**Alternatives Considered:**

1. **Single Database (PostgreSQL + pgvector)**
   - ✅ Simpler architecture
   - ❌ Slower vector search at scale
   - ❌ Less optimized for embeddings

2. **Pinecone (managed vector DB)**
   - ✅ Fully managed
   - ❌ Cost scales with usage
   - ❌ Vendor lock-in

3. **Weaviate**
   - ✅ Good vector search
   - ❌ Heavier than Qdrant
   - ❌ More complex setup

**Consequences:**
- ✅ Best-in-class for each use case
- ✅ Scalable vector search
- ⚠️ Two databases to maintain
- ⚠️ Complexity in deployment

---

## ADR-005: FastAPI for API Layer

**Date:** 2025-12-05

**Context:**
We need a web API framework for HTTP and WebSocket endpoints.

**Decision:**
Use FastAPI for the API layer.

**Rationale:**
- **Performance:** Async/await native, high throughput
- **Type Safety:** Pydantic models for request/response validation
- **Documentation:** Auto-generated OpenAPI/Swagger docs
- **WebSocket:** Built-in WebSocket support for streaming
- **Ecosystem:** Great integration with Python async libraries
- **Developer Experience:** Excellent error messages and debugging

**Alternatives Considered:**

1. **Flask**
   - ✅ Simple and mature
   - ❌ No native async support
   - ❌ Manual validation

2. **Django + DRF**
   - ✅ Batteries included
   - ❌ Heavier than needed
   - ❌ Slower async support

**Consequences:**
- ✅ Fast development
- ✅ Type-safe API contracts
- ✅ Great for streaming responses
- ⚠️ Learning curve for FastAPI patterns

---

## ADR-006: Tavily for Web Search

**Date:** 2025-12-05

**Context:**
Agents need to search the web for company information. Options: Google, Bing, DuckDuckGo, Tavily.

**Decision:**
Use Tavily API as primary search tool.

**Rationale:**
- **LLM-Optimized:** Results formatted for LLM consumption
- **Clean Content:** Removes ads, extracts main content
- **Cost:** $0.001 per search (very cheap)
- **Rate Limits:** 1000 requests/min
- **Relevance:** Better than generic search for research tasks

**Alternatives Considered:**

1. **Google Custom Search API**
   - ✅ High quality results
   - ❌ $5 per 1000 queries (5x more expensive)
   - ❌ Not optimized for LLMs

2. **Bing Search API**
   - ✅ Decent quality
   - ❌ More expensive
   - ❌ Complex result format

3. **DuckDuckGo (Free)**
   - ✅ Free
   - ❌ Rate limits
   - ❌ No API key required but unreliable

**Consequences:**
- ✅ Cost-effective
- ✅ LLM-friendly results
- ✅ Reliable and fast
- ⚠️ Dependency on Tavily service
- ⚠️ Limited to 1000 searches/min

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date:** YYYY-MM-DD

**Context:**
[What problem or question are we addressing?]

**Decision:**
[What did we decide to do?]

**Rationale:**
[Why did we make this choice?]
- Point 1
- Point 2

**Alternatives Considered:**

1. **Alternative 1**
   - ✅ Pros
   - ❌ Cons

2. **Alternative 2**
   - ✅ Pros
   - ❌ Cons

**Consequences:**
- ✅ Positive impact
- ⚠️ Trade-offs
- ❌ Negative impact
```
