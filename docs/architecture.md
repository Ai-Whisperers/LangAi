# Architecture Decisions & Design

## Overall Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
│              (Web, Mobile, CLI, API)                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               FastAPI Backend                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Routes                                   │  │
│  │  ├─ /chat                                     │  │
│  │  ├─ /search                                   │  │
│  │  ├─ /embed                                    │  │
│  │  └─ /health                                   │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Core Services                                │  │
│  │  ├─ LLM Router (smart model selection)       │  │
│  │  ├─ Embedding Service                        │  │
│  │  ├─ RAG Pipeline                             │  │
│  │  └─ Caching Layer (Redis)                    │  │
│  └──────────────────────────────────────────────┘  │
└──────────────┬──────────────────┬──────────────────┘
               │                  │
       ┌───────▼────────┐  ┌─────▼──────────────────┐
       │ Vector Store   │  │   LLM Providers        │
       │ ─────────────  │  │   ───────────────      │
       │ Phase 1: Chroma│  │   ├─ GPT-4 (OpenAI)   │
       │ Phase 2: Weaviate│ │   ├─ Claude (Anthropic)│
       └────────────────┘  │   └─ Llama (Local)     │
                           └────────────────────────┘
```

---

## Tech Stack Summary

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.10+
- **LLM Interface:** LiteLLM
- **Vector DB (Phase 1):** Chroma
- **Vector DB (Phase 2):** Weaviate
- **Caching:** Redis
- **Task Queue:** Celery (optional, for async processing)

### AI/ML
- **LLMs:** GPT-4, Claude, Llama 3
- **Embeddings:** OpenAI text-embedding-3-small or HuggingFace
- **Framework:** LangChain (for RAG pipelines)
- **Orchestration:** LangGraph (for multi-step agents)

### Infrastructure
- **Deployment:** Docker + Docker Compose
- **Monitoring:** Prometheus + Grafana (optional)
- **Logging:** Structured logging (JSON)
- **Rate Limiting:** slowapi

---

## Core Design Principles

### 1. Abstraction Over Implementation
**Why:** Easy to swap components (Chroma → Weaviate, GPT-4 → Claude)

```python
# Bad: Tightly coupled
from chromadb import Client
client = Client()
collection = client.create_collection("docs")

# Good: Abstracted
class VectorStore(ABC):
    @abstractmethod
    def search(self, query: str, limit: int) -> List[Document]:
        pass

class ChromaStore(VectorStore):
    # Implementation
    pass

class WeaviateStore(VectorStore):
    # Implementation
    pass

# Usage: easy to switch
store = ChromaStore()  # or WeaviateStore()
```

### 2. Smart Routing Over Hardcoding
**Why:** Optimize cost, latency, and quality automatically

```python
# Bad: Hardcoded model
response = openai.ChatCompletion.create(model="gpt-4", ...)

# Good: Smart routing
router = LLMRouter()
response = router.complete(
    prompt=prompt,
    sensitivity=Sensitivity.PUBLIC,
    complexity=Complexity.MODERATE
)
# Router chooses best model based on context
```

### 3. Caching Everywhere
**Why:** Reduce costs and latency

Cache these layers:
- **Embeddings** (same text = same embedding)
- **LLM responses** (same prompt = same answer)
- **Vector search results** (TTL: 1 hour)
- **API responses** (for deterministic endpoints)

### 4. Graceful Degradation
**Why:** System stays functional even when components fail

```python
# Fallback chain
GPT-4 fails → Try Claude
Claude fails → Try GPT-3.5
GPT-3.5 fails → Use local Llama
Llama fails → Return cached response or error
```

### 5. Observable & Debuggable
**Why:** Understand what's happening in production

Log these events:
- Model selection decisions
- Token usage per request
- Cache hit/miss rates
- Error rates per model
- Latency per component

---

## Key Architectural Patterns

### Pattern 1: RAG Pipeline

```python
def rag_query(user_question: str) -> str:
    """Retrieval-Augmented Generation pipeline"""

    # Step 1: Embed user question
    query_embedding = embed(user_question)  # OpenAI or HuggingFace

    # Step 2: Search vector store
    relevant_docs = vector_store.search(query_embedding, limit=5)

    # Step 3: Rerank results (optional, improves quality)
    reranked_docs = reranker.rerank(user_question, relevant_docs)

    # Step 4: Build context
    context = "\n\n".join([doc.content for doc in reranked_docs[:3]])

    # Step 5: Generate answer with LLM
    prompt = f"""Answer the question based on this context:

Context:
{context}

Question: {user_question}

Answer:"""

    response = llm_router.complete(
        prompt=prompt,
        complexity=Complexity.MODERATE
    )

    return response
```

### Pattern 2: Streaming Responses

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream LLM responses token-by-token"""

    async def generate():
        response = completion(
            model="gpt-4",
            messages=[{"role": "user", "content": request.message}],
            stream=True  # Enable streaming
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Pattern 3: Background Processing

```python
from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379")

@celery.task
def process_document_batch(documents: List[str]):
    """Process large document batches in background"""

    embeddings = []
    for doc in documents:
        embedding = embed(doc)
        embeddings.append(embedding)

    vector_store.batch_add(documents, embeddings)

# In API
@app.post("/documents/upload")
async def upload_documents(files: List[UploadFile]):
    documents = [await f.read() for f in files]

    # Queue for background processing
    task = process_document_batch.delay(documents)

    return {"task_id": task.id, "status": "processing"}
```

---

## Data Flow Examples

### Example 1: Simple Chat

```
User: "What is Python?"
    ↓
FastAPI receives request
    ↓
LLM Router decides: GPT-3.5 (simple question)
    ↓
Check cache: MISS
    ↓
Call OpenAI API
    ↓
Cache response (24h TTL)
    ↓
Return to user

Cost: $0.002 per 1K tokens
Latency: ~500ms
```

### Example 2: RAG Query

```
User: "What did we discuss about pricing last week?"
    ↓
FastAPI receives request
    ↓
Embed query (OpenAI text-embedding-3-small)
    ↓
Search Chroma (finds 5 relevant conversation snippets)
    ↓
Build context from top 3 results
    ↓
LLM Router decides: Claude (moderate complexity)
    ↓
Generate answer with context
    ↓
Return to user

Cost: $0.02 (embedding) + $0.15 (Claude) = $0.17 per 1K tokens
Latency: ~100ms (embed) + ~50ms (search) + ~1500ms (LLM) = ~1.6s
```

### Example 3: Sensitive Data Query

```
User: "Analyze this confidential customer contract..."
    ↓
FastAPI receives request
    ↓
Detect sensitivity: CONFIDENTIAL (keyword matching)
    ↓
LLM Router decides: Llama (local, privacy-first)
    ↓
Process locally (no API call)
    ↓
Return to user

Cost: $0 (local inference)
Latency: ~2-3s (local GPU)
Data leaks: ZERO (never leaves server)
```

---

## Configuration Strategy

### Environment-Based Config

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"  # development, staging, production

    # Vector Store
    VECTOR_STORE: str = "chroma"  # chroma, weaviate
    CHROMA_PATH: str = "./chroma_db"
    WEAVIATE_URL: str = "http://localhost:8080"

    # LLMs
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Caching
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Monitoring
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Feature Flags

```python
# features.py
FEATURE_FLAGS = {
    "use_reranker": True,
    "enable_caching": True,
    "use_streaming": True,
    "enable_monitoring": True,
    "use_hybrid_search": False,  # Requires Weaviate
}

def is_enabled(feature: str) -> bool:
    return FEATURE_FLAGS.get(feature, False)
```

---

## Security Considerations

### 1. API Key Management
- ✅ Store in environment variables (`.env`)
- ✅ Never commit to git (add `.env` to `.gitignore`)
- ✅ Use different keys for dev/staging/prod
- ✅ Rotate keys regularly

### 2. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request):
    # Only 10 requests per minute per IP
    pass
```

### 3. Input Validation
```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    temperature: float = Field(0.7, ge=0, le=2)

    @validator("message")
    def sanitize_message(cls, v):
        # Remove potential injection attempts
        dangerous_patterns = ["<script>", "DROP TABLE", "'; --"]
        for pattern in dangerous_patterns:
            if pattern.lower() in v.lower():
                raise ValueError("Invalid input detected")
        return v
```

### 4. Data Privacy
```python
# Automatic PII detection
def contains_pii(text: str) -> bool:
    """Detect personally identifiable information"""
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',              # Credit card
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email
    ]

    for pattern in pii_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Auto-route to local model if PII detected
if contains_pii(user_input):
    model = "ollama/llama3"  # Local only
```

---

## Scalability Considerations

### Current Architecture (Single Server)
- **Good for:** < 100 concurrent users
- **Limits:** Single point of failure, vertical scaling only

### Future Architecture (Distributed)
```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┬───────┐
   │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│API 1│ │API 2│ │API 3│  (Horizontal scaling)
└──┬──┘ └──┬──┘ └──┬──┘
   │       │       │
   └───┬───┴───┬───┘
       │       │
   ┌───▼───┐ ┌─▼─────┐
   │ Redis │ │Weaviate│  (Shared state)
   │Cluster│ │Cluster │
   └───────┘ └────────┘
```

### Scaling Strategies
1. **API Layer:** Add more FastAPI instances behind load balancer
2. **Caching:** Redis Cluster for distributed caching
3. **Vector Store:** Weaviate cluster with replication
4. **LLMs:** Use multiple API keys, distribute load

---

## Monitoring & Observability

### Key Metrics to Track

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    "api_requests_total",
    "Total API requests",
    ["endpoint", "status"]
)

request_duration = Histogram(
    "api_request_duration_seconds",
    "Request duration",
    ["endpoint"]
)

# LLM metrics
llm_requests = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status"]
)

llm_tokens = Counter(
    "llm_tokens_total",
    "Total tokens used",
    ["model", "type"]  # prompt, completion
)

llm_cost = Gauge(
    "llm_cost_dollars",
    "Estimated LLM costs",
    ["model"]
)

# Cache metrics
cache_hits = Counter("cache_hits_total", "Cache hits")
cache_misses = Counter("cache_misses_total", "Cache misses")

# Vector store metrics
vector_search_duration = Histogram(
    "vector_search_duration_seconds",
    "Vector search duration"
)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check"""

    health = {
        "status": "healthy",
        "checks": {}
    }

    # Check Redis
    try:
        redis_client.ping()
        health["checks"]["redis"] = "ok"
    except:
        health["checks"]["redis"] = "fail"
        health["status"] = "degraded"

    # Check Vector Store
    try:
        vector_store.health_check()
        health["checks"]["vector_store"] = "ok"
    except:
        health["checks"]["vector_store"] = "fail"
        health["status"] = "degraded"

    # Check LLMs
    for model in ["gpt-4", "claude-3-sonnet-20240229", "ollama/llama3"]:
        try:
            completion(model=model, messages=[...], max_tokens=1)
            health["checks"][model] = "ok"
        except:
            health["checks"][model] = "fail"

    return health
```

---

## Deployment Strategy

### Phase 1: Development (Local)
```bash
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - ./chroma_db:/app/chroma_db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Phase 2: Staging (Cloud)
- Deploy to cloud (AWS, GCP, Azure)
- Use managed Redis
- Add monitoring (Datadog, New Relic)
- Enable SSL/TLS

### Phase 3: Production (Kubernetes)
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langai-api
  template:
    spec:
      containers:
      - name: api
        image: langai-api:latest
        ports:
        - containerPort: 8000
```

---

## Decision Log

### 2025-12-05: Initial Architecture

**Decisions:**
1. ✅ Use FastAPI for backend (async, fast, good docs)
2. ✅ Start with Chroma, migrate to Weaviate later
3. ✅ Use LiteLLM for unified LLM interface
4. ✅ Multiple LLMs (GPT-4, Claude, Llama) for flexibility
5. ✅ Redis for caching
6. ✅ Abstract components behind interfaces

**Rationale:**
- Optimize for fast iteration initially
- Easy migration path to production-grade stack
- Cost optimization through smart routing
- Privacy support through local models

**Risks & Mitigations:**
- Risk: Chroma may not scale
  - Mitigation: Abstract behind interface, plan migration
- Risk: Multiple LLMs increase complexity
  - Mitigation: Use LiteLLM unified interface
- Risk: Costs may spiral
  - Mitigation: Implement caching and monitoring from day 1

---

## Next Architecture Review

Schedule: **4 weeks from now**

Questions to answer:
- [ ] Is Chroma still meeting our needs?
- [ ] What's our actual cost per user?
- [ ] Are we hitting rate limits?
- [ ] Do we need distributed deployment?
- [ ] Should we add more local models?
